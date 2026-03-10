import json
import base64
import urllib.request
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Person, Attendance
from .services.face_service import extract_face_encoding, match_face


def home(request):
    return render(request, 'home.html')


@ensure_csrf_cookie
def enrollment(request):
    return render(request, 'enrollment.html')


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
        img_for_encoding = Image.open(io.BytesIO(img_data)).convert('RGB')
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
    Attendance.objects.create(person=person, source='web_camera')
    return JsonResponse({
        'ok': True,
        'msg': '签到成功',
        'name': person.name,
        'employee_id': person.employee_id,
    })


def checkin_frame(request):
    """代理 IP Webcam 快照，避免 CORS"""
    url = request.GET.get('url', '').strip()
    if not url or not url.startswith(('http://', 'https://')):
        return HttpResponse(status=400)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'MagicFace/1.0'})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = r.read()
        return HttpResponse(data, content_type='image/jpeg')
    except Exception:
        return HttpResponse(status=502)


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


def attendance_detail(request):
    """考勤明细 API：返回签到记录列表"""
    days = int(request.GET.get('days', 14))
    end = datetime.now()
    start = end - timedelta(days=days)
    records = Attendance.objects.filter(
        check_in_time__gte=start, check_in_time__lte=end
    ).select_related('person').order_by('-check_in_time')
    data = [
        {
            'name': r.person.name,
            'employee_id': r.person.employee_id,
            'check_in_time': r.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
            'source': r.source,
        }
        for r in records
    ]
    return JsonResponse({'ok': True, 'data': data})
