import csv
import json
import base64
import urllib.request
from datetime import datetime, timedelta, time as dtime
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required

from .models import Person, Attendance, AttendanceRule
from .services.face_service import extract_face_encoding, match_face
from .api_schema import SCHEMA


def schema_json(request):
    """返回 OpenAPI 3.0 JSON 规范"""
    return JsonResponse(SCHEMA, json_dumps_params={"ensure_ascii": False, "indent": 2})


def swagger_ui(request):
    """渲染 Swagger UI 页面"""
    return render(request, "swagger.html")


def home(request):
    return render(request, 'home.html')


@login_required
@ensure_csrf_cookie
def enrollment(request):
    return render(request, 'enrollment.html')


@login_required
@require_http_methods(['POST'])
def enrollment_upload(request):
    """上传照片或在线拍照，提取人脸特征并保存"""
    name = ''
    employee_id = ''
    img_for_encoding = None
    photo_file = None

    if request.content_type and 'application/json' in request.content_type:
        # 在线拍照：JSON + base64
        data = json.loads(request.body) if request.body else {}
        name = data.get('name', '').strip()
        employee_id = data.get('employee_id', '').strip()
        img_b64 = data.get('image')
        if not img_b64:
            return JsonResponse({'ok': False, 'msg': '未收到图片'})
        try:
            img_data = base64.b64decode(img_b64.split(',')[-1] if ',' in img_b64 else img_b64)
        except Exception:
            return JsonResponse({'ok': False, 'msg': '图片格式错误'})
        from PIL import Image
        import io
        from django.core.files.base import ContentFile
        img_for_encoding = Image.open(io.BytesIO(img_data)).convert('RGB')
        photo_file = ContentFile(img_data, name=f'{employee_id or "capture"}.jpg')
    else:
        # 上传照片：FormData
        photo_file = request.FILES.get('photo')
        name = request.POST.get('name', '').strip()
        employee_id = request.POST.get('employee_id', '').strip()
        if photo_file:
            img_for_encoding = photo_file

    if not all([name, employee_id]):
        return JsonResponse({'ok': False, 'msg': '请填写姓名、工号'})
    if not img_for_encoding:
        return JsonResponse({'ok': False, 'msg': '请上传照片或拍照'})
    if Person.objects.filter(employee_id=employee_id).exists():
        return JsonResponse({'ok': False, 'msg': f'工号 {employee_id} 已存在'})

    encoding = extract_face_encoding(img_for_encoding)
    if encoding is None:
        return JsonResponse({'ok': False, 'msg': '未检测到人脸，请上传清晰正面照'})
    existing = Person.objects.exclude(face_encoding__isnull=True).exclude(face_encoding=[])
    if existing.exists():
        known_encodings = [p.face_encoding for p in existing]
        known_ids = [p.id for p in existing]
        matched_id = match_face(known_encodings, known_ids, encoding)
        if matched_id is not None:
            matched = Person.objects.get(id=matched_id)
            return JsonResponse({
                'ok': False,
                'msg': f'该人脸已被 {matched.name}（{matched.employee_id}）录入，请勿重复录入',
            })
    person = Person.objects.create(
        name=name,
        employee_id=employee_id,
        face_encoding=encoding,
        photo=photo_file,
    )
    return JsonResponse({'ok': True, 'msg': f'{person.name} 录入成功', 'id': person.id})


@ensure_csrf_cookie
def checkin(request):
    return render(request, 'checkin.html')


@require_http_methods(['POST'])
def checkin_submit(request):
    """接收摄像头拍照，匹配人脸并记录签到"""
    data = json.loads(request.body) if request.body else {}
    img_b64 = data.get('image')
    if not img_b64:
        return JsonResponse({'ok': False, 'msg': '未收到图片'})
    try:
        img_data = base64.b64decode(img_b64.split(',')[-1] if ',' in img_b64 else img_b64)
    except Exception:
        return JsonResponse({'ok': False, 'msg': '图片格式错误'})
    from PIL import Image
    import io
    img = Image.open(io.BytesIO(img_data)).convert('RGB')
    encoding = extract_face_encoding(img)
    if encoding is None:
        return JsonResponse({'ok': False, 'msg': '未检测到人脸，请正对摄像头'})
    persons = Person.objects.exclude(face_encoding__isnull=True).exclude(face_encoding=[])
    known_encodings = [p.face_encoding for p in persons]
    known_ids = [p.id for p in persons]
    person_id = match_face(known_encodings, known_ids, encoding)
    if person_id is None:
        return JsonResponse({'ok': False, 'msg': '未匹配到已录入人员'})
    person = Person.objects.get(id=person_id)
    rule = AttendanceRule.get()
    today = datetime.now().date()
    if not rule.allow_repeat and Attendance.objects.filter(person=person, check_in_time__date=today).exists():
        return JsonResponse({
            'ok': False,
            'msg': f'{person.name} 今日已签到，无需重复签到',
            'name': person.name,
            'employee_id': person.employee_id,
        })
    now = datetime.now()
    status = 'late' if now.time() > rule.checkin_deadline else 'normal'
    record = Attendance.objects.create(person=person, source='web_camera', status=status)
    status_text = '（迟到）' if status == 'late' else ''
    return JsonResponse({
        'ok': True,
        'msg': f'签到成功{status_text}',
        'name': person.name,
        'employee_id': person.employee_id,
        'status': status,
        'status_label': record.get_status_display(),
        'photo_url': person.photo.url if person.photo else '',
        'check_in_time': record.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
    })


def checkin_frame(request):
    """代理 IP Webcam 快照，避免 CORS。
    策略：
    1. 优先探测常见快照路径（静态图片，快速）
    2. 全部失败后，尝试从 MJPEG 视频流中提取第一帧（兜底）
    """
    from urllib.parse import urlparse

    url = request.GET.get('url', '').strip()
    if not url or not url.startswith(('http://', 'https://')):
        return HttpResponse(status=400)

    HEADERS = {'User-Agent': 'Mozilla/5.0 (MagicFace IP Webcam Proxy)'}

    # ── 阶段1：快照路径探测 ──────────────────────────────────────
    SNAPSHOT_PATHS = [
        '/shot.jpg',        # IP Webcam (Android)
        '/snapshot.jpg',    # 通用
        '/jpeg',            # 部分软件
        '/capture',         # 部分软件
        '/cam/1/frame.jpg', # DroidCam
        '/photo.jpg',
        '/image.jpg',
        '/frame.jpg',
    ]

    parsed = urlparse(url)
    # url 已含具体文件路径时直接请求，否则逐一拼接探测
    if parsed.path and parsed.path != '/' and '.' in parsed.path.split('/')[-1]:
        snapshot_candidates = [url]
    else:
        base = url.rstrip('/')
        snapshot_candidates = [base + p for p in SNAPSHOT_PATHS]

    for candidate in snapshot_candidates:
        try:
            req = urllib.request.Request(candidate, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=3) as r:
                content_type = r.headers.get('Content-Type', '')
                data = r.read()
            if data and ('image' in content_type or data[:2] in (b'\xff\xd8', b'\x89P')):
                return HttpResponse(data, content_type='image/jpeg')
        except Exception:
            continue

    # ── 阶段2：MJPEG 流取帧（兜底）──────────────────────────────
    STREAM_PATHS = [
        '/video',           # IP Webcam (Android)
        '/mjpeg',           # 通用
        '/stream',          # 通用
        '/mjpegfeed',       # 部分软件
        '/cam/1/stream',    # DroidCam
        '/videostream.cgi', # 部分网络摄像头
    ]

    base = url.rstrip('/')
    # url 已含路径时视为流地址直接尝试，否则逐一拼接
    if parsed.path and parsed.path != '/':
        stream_candidates = [url]
    else:
        stream_candidates = [base + p for p in STREAM_PATHS]

    for stream_url in stream_candidates:
        try:
            req = urllib.request.Request(stream_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=5) as r:
                content_type = r.headers.get('Content-Type', '')
                # 确认是 MJPEG 流
                if 'multipart' not in content_type and 'mjpeg' not in content_type:
                    continue
                buf = b''
                # 最多读取 500KB，足够包含一帧
                while len(buf) < 512_000:
                    chunk = r.read(4096)
                    if not chunk:
                        break
                    buf += chunk
                    # 寻找完整 JPEG 帧（SOI=\xff\xd8, EOI=\xff\xd9）
                    start = buf.find(b'\xff\xd8')
                    if start == -1:
                        continue
                    end = buf.find(b'\xff\xd9', start)
                    if end != -1:
                        frame = buf[start:end + 2]
                        return HttpResponse(frame, content_type='image/jpeg')
        except Exception:
            continue

    return HttpResponse(status=502)


@login_required
@ensure_csrf_cookie
def report(request):
    return render(request, 'report.html')


def attendance_stats(request):
    """考勤统计 API：按日/周聚合"""
    period = request.GET.get('period', 'day')  # day | week
    days = int(request.GET.get('days', 14))
    end = datetime.now()
    start = end - timedelta(days=days)
    records = Attendance.objects.filter(check_in_time__gte=start, check_in_time__lte=end)
    if period == 'day':
        from django.db.models.functions import TruncDate
        from django.db.models import Count
        qs = records.annotate(date=TruncDate('check_in_time')).values('date').annotate(count=Count('id')).order_by('date')
        data = [{'date': str(r['date']), 'count': r['count']} for r in qs]
    else:
        from django.db.models.functions import TruncWeek
        from django.db.models import Count
        qs = records.annotate(week=TruncWeek('check_in_time')).values('week').annotate(count=Count('id')).order_by('week')
        data = [{'date': str(r['week']), 'count': r['count']} for r in qs]
    return JsonResponse({'ok': True, 'data': data})


@login_required
def persons(request):
    """人员列表页"""
    person_list = Person.objects.all().order_by('-created_at')
    return render(request, 'persons.html', {'persons': person_list})


@login_required
@require_http_methods(['POST'])
def person_delete(request, pk):
    """删除人员"""
    try:
        person = Person.objects.get(pk=pk)
        person.delete()
        return JsonResponse({'ok': True, 'msg': '已删除'})
    except Person.DoesNotExist:
        return JsonResponse({'ok': False, 'msg': '人员不存在'})


def attendance_detail(request):
    """考勤明细 API：支持分页"""
    days = int(request.GET.get('days', 14))
    page = max(int(request.GET.get('page', 1)), 1)
    page_size = min(max(int(request.GET.get('page_size', 10)), 1), 100)
    end = datetime.now()
    start = end - timedelta(days=days)
    qs = Attendance.objects.filter(
        check_in_time__gte=start, check_in_time__lte=end
    ).select_related('person').order_by('-check_in_time')
    total = qs.count()
    offset = (page - 1) * page_size
    records = qs[offset:offset + page_size]
    data = [
        {
            'name': r.person.name,
            'employee_id': r.person.employee_id,
            'check_in_time': r.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': r.status,
            'status_label': r.get_status_display(),
            'source': r.source,
        }
        for r in records
    ]
    return JsonResponse({
        'ok': True, 'data': data,
        'total': total, 'page': page, 'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size if total else 1,
    })


@login_required
@ensure_csrf_cookie
def settings_page(request):
    """考勤规则配置页面"""
    rule = AttendanceRule.get()
    return render(request, 'settings.html', {'rule': rule})


@login_required
@require_http_methods(['POST'])
def settings_save(request):
    """保存考勤规则"""
    data = json.loads(request.body) if request.body else {}
    deadline_str = data.get('checkin_deadline', '').strip()
    allow_repeat = data.get('allow_repeat', False)
    if not deadline_str:
        return JsonResponse({'ok': False, 'msg': '请填写签到截止时间'})
    try:
        parts = deadline_str.split(':')
        deadline = dtime(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return JsonResponse({'ok': False, 'msg': '时间格式错误，请使用 HH:MM'})
    rule = AttendanceRule.get()
    rule.checkin_deadline = deadline
    rule.allow_repeat = bool(allow_repeat)
    rule.save()
    return JsonResponse({'ok': True, 'msg': '保存成功'})


@login_required
def attendance_summary(request):
    """出勤概览 API：正常/迟到/缺勤人数"""
    days = int(request.GET.get('days', 14))
    end = datetime.now()
    start = end - timedelta(days=days)
    total_persons = Person.objects.count()
    records = Attendance.objects.filter(check_in_time__gte=start, check_in_time__lte=end)
    normal_count = records.filter(status='normal').count()
    late_count = records.filter(status='late').count()
    checked_persons = records.values('person').distinct().count()
    absent_persons = total_persons - checked_persons
    return JsonResponse({
        'ok': True,
        'total_persons': total_persons,
        'normal': normal_count,
        'late': late_count,
        'checked_persons': checked_persons,
        'absent_persons': max(absent_persons, 0),
    })


@login_required
def attendance_export(request):
    """导出考勤明细为 CSV"""
    days = int(request.GET.get('days', 14))
    end = datetime.now()
    start = end - timedelta(days=days)
    records = Attendance.objects.filter(
        check_in_time__gte=start, check_in_time__lte=end
    ).select_related('person').order_by('-check_in_time')

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="attendance_{start.strftime("%Y%m%d")}_{end.strftime("%Y%m%d")}.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['姓名', '工号/学号', '签到时间', '状态', '来源'])
    for r in records:
        writer.writerow([
            r.person.name,
            r.person.employee_id,
            r.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
            r.get_status_display(),
            r.source,
        ])
    return response
