# -*- coding: utf-8 -*-
# 第四章 系统设计  +  第五章 系统实现

def add_chapter4(doc):
    add_heading(doc, '第四章  系统设计', level=1)

    add_heading(doc, '4.1  系统总体设计', level=2)

    add_heading(doc, '4.1.1  系统架构设计', level=3)
    add_body_paragraph(doc,
        '本系统采用 B/S（浏览器/服务器）三层架构，各层职责分离，层间通过标准接口通信。'
        '表示层负责用户交互和界面渲染；业务逻辑层负责处理请求、执行人脸识别算法和业务规则；'
        '数据存储层负责持久化数据。系统整体架构如图 4-1 所示：')
    add_image_to_doc(doc, arch_img, width_cm=14,
                     caption='图 4-1  MagicFace 系统三层架构图')

    add_heading(doc, '4.1.2  Django MVT 架构说明', level=3)
    add_body_paragraph(doc,
        'Django 采用 MVT（Model-View-Template）架构模式，与传统 MVC 的对应关系为：'
        'Model（模型层）对应 MVC 的 Model，定义数据库表结构，封装数据操作逻辑；'
        'View（视图层）对应 MVC 的 Controller，处理 HTTP 请求，调用模型和服务层完成业务逻辑，'
        '返回响应；Template（模板层）对应 MVC 的 View，定义 HTML 页面结构，通过模板标签'
        '动态渲染数据。本项目使用模板继承（base.html）统一所有页面的导航栏和页脚布局。')

    add_heading(doc, '4.2  模块详细设计', level=2)

    add_heading(doc, '4.2.1  人脸识别服务模块设计', level=3)
    add_body_paragraph(doc,
        '人脸识别服务（face_service.py）是系统的核心技术组件，封装了所有与人脸识别相关的操作。'
        '该模块对外提供两个核心函数：extract_face_encoding() 用于从图像中提取128维人脸特征向量；'
        'match_face() 用于将待识别人脸特征与人员库进行批量比对，返回匹配人员的数据库ID。')
    add_body_paragraph(doc,
        '人脸特征提取流程为：接受 PIL Image 或文件对象作为输入，转换为 RGB 格式的 NumPy 数组，'
        '调用 face_recognition.face_locations() 检测人脸区域，若检测到人脸则调用 '
        'face_recognition.face_encodings() 提取128维特征向量并返回，否则返回 None。')
    add_body_paragraph(doc,
        '人脸比对算法采用欧氏距离度量：将所有已知人员特征向量组成矩阵，调用 '
        'face_recognition.compare_faces() 函数计算待识别特征与每个已知特征的欧氏距离，'
        '当距离小于阈值 TOLERANCE=0.5 时判定为同一人。阈值0.5是在识别准确率与误识率之间的'
        '平衡点，经过实验验证在正常光照条件下效果最优。')

    add_heading(doc, '4.2.2  签到模块设计', level=3)
    add_body_paragraph(doc,
        '签到功能是系统最核心的业务流程，设计时考虑了活体检测、重复签到防控、迟到判定等多种'
        '业务规则。完整的签到流程如图 4-2 所示：')
    add_image_to_doc(doc, checkin_img, width_cm=10,
                     caption='图 4-2  签到功能流程图')

    add_heading(doc, '4.2.3  活体检测算法设计', level=3)
    add_body_paragraph(doc,
        '活体检测是防止用户使用他人照片进行欺骗签到的重要安全机制。本系统采用基于帧间差异的'
        '轻量级活体检测算法，在浏览器端（JavaScript）执行，不增加服务器负担。算法核心原理为：'
        '连续采集3帧图像，将每帧转换为灰度图，计算相邻两帧之间的平均像素绝对差（MAD）。'
        '若差异值低于阈值（2.0），说明画面完全静止，可能是静态照片，拒绝签到；'
        '若差异值高于阈值，说明画面存在运动（如人脸的微小抖动），判定为真实活体。')
    add_body_paragraph(doc,
        '该算法虽然相对简单，但在工程实践中对于防止静态照片欺骗具有良好效果，计算开销极小'
        '（仅需对约5万像素点做差值运算），不影响签到响应速度。')

    add_heading(doc, '4.2.4  人脸录入模块设计', level=3)
    add_body_paragraph(doc,
        '人脸录入模块设计时重点考虑了数据完整性和防重复注册两个问题。录入流程如图 4-3 所示。'
        '系统在保存人员记录之前会进行两重校验：首先校验工号唯一性（数据库层面的 UNIQUE 约束）；'
        '其次将待录入人脸特征与所有已录入人员进行比对，若相似度超过阈值则判定为重复录入，'
        '防止同一人以不同工号多次注册以规避考勤。')
    add_image_to_doc(doc, enrollment_img, width_cm=10,
                     caption='图 4-3  人脸录入流程图')

    add_heading(doc, '4.3  数据库设计', level=2)

    add_heading(doc, '4.3.1  实体关系图', level=3)
    add_body_paragraph(doc,
        '系统包含三个主要数据实体：Person（人员信息）、Attendance（考勤记录）和 '
        'AttendanceRule（考勤规则）。Person 与 Attendance 之间是一对多关系（一个人员'
        '对应多条考勤记录），AttendanceRule 为全局单例配置表。实体关系图如图 4-4 所示：')
    add_image_to_doc(doc, er_img, width_cm=15,
                     caption='图 4-4  数据库实体关系图（ER 图）')

    add_heading(doc, '4.3.2  数据表设计', level=3)
    add_body_paragraph(doc, '各数据表的字段设计如下：')

    # Person 表
    add_body_paragraph(doc, '（1）Person 表（人员信息表）', first_indent=False)
    p_headers = ['字段名', '数据类型', '约束', '说明']
    p_rows = [
        ['id', 'INTEGER', 'PK, AUTO', '主键'],
        ['name', 'VARCHAR(100)', 'NOT NULL', '姓名'],
        ['employee_id', 'VARCHAR(50)', 'UNIQUE, NOT NULL', '工号/学号'],
        ['face_encoding', 'JSON', 'NOT NULL', '128维人脸特征向量'],
        ['photo', 'VARCHAR(200)', 'NULL', '照片文件路径'],
        ['created_at', 'DATETIME', 'NOT NULL, AUTO', '录入时间（自动）'],
    ]
    t1 = doc.add_table(rows=len(p_rows)+1, cols=4)
    t1.style = 'Table Grid'
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(p_headers):
        cell = t1.rows[0].cells[j]
        cell.paragraphs[0].clear()
        run = cell.paragraphs[0].add_run(h)
        set_run_font(run, cn_font='黑体', size=10.5, bold=True)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), '1F4E79')
        tcPr.append(shd)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for i, row_data in enumerate(p_rows):
        for j, val in enumerate(row_data):
            cell = t1.rows[i+1].cells[j]
            cell.paragraphs[0].clear()
            run = cell.paragraphs[0].add_run(val)
            set_run_font(run, cn_font='宋体', size=10)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_caption(doc, '表 4-1  Person 人员信息表字段设计')

    # Attendance 表
    add_body_paragraph(doc, '（2）Attendance 表（考勤记录表）', first_indent=False)
    a_rows = [
        ['id', 'INTEGER', 'PK, AUTO', '主键'],
        ['person_id', 'INTEGER', 'FK → Person.id, CASCADE', '关联人员'],
        ['check_in_time', 'DATETIME', 'NOT NULL, AUTO', '签到时间（自动）'],
        ['status', 'VARCHAR(20)', "DEFAULT 'normal'", '状态：normal / late'],
        ['source', 'VARCHAR(50)', "DEFAULT 'web_camera'", '签到来源'],
    ]
    t2 = doc.add_table(rows=len(a_rows)+1, cols=4)
    t2.style = 'Table Grid'
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(p_headers):
        cell = t2.rows[0].cells[j]
        cell.paragraphs[0].clear()
        run = cell.paragraphs[0].add_run(h)
        set_run_font(run, cn_font='黑体', size=10.5, bold=True)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), '375623')
        tcPr.append(shd)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for i, row_data in enumerate(a_rows):
        for j, val in enumerate(row_data):
            cell = t2.rows[i+1].cells[j]
            cell.paragraphs[0].clear()
            run = cell.paragraphs[0].add_run(val)
            set_run_font(run, cn_font='宋体', size=10)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_caption(doc, '表 4-2  Attendance 考勤记录表字段设计')

    add_heading(doc, '4.4  接口设计', level=2)
    add_body_paragraph(doc,
        '系统采用前后端半分离设计：页面由 Django 模板渲染，数据交互通过 JSON API 完成。'
        '主要 URL 路由设计如下表所示：')

    api_headers = ['URL', 'HTTP方法', '是否需要认证', '功能说明']
    api_rows = [
        ['/', 'GET', '否', '首页'],
        ['/login/', 'GET/POST', '否', '管理员登录'],
        ['/enrollment/', 'GET', '是', '人脸录入页面'],
        ['/enrollment/upload/', 'POST', '是', '提交人脸录入'],
        ['/checkin/', 'GET', '否', '签到页面（公开）'],
        ['/checkin/submit/', 'POST', '否', '提交人脸签到'],
        ['/checkin/frame/', 'GET', '否', 'IP摄像头代理（防CORS）'],
        ['/persons/', 'GET', '是', '人员列表管理'],
        ['/api/person/<pk>/delete/', 'POST', '是', '删除人员'],
        ['/settings/', 'GET', '是', '考勤规则配置页'],
        ['/api/settings/save/', 'POST', '是', '保存考勤规则'],
        ['/report/', 'GET', '是', '考勤报表页面'],
        ['/api/attendance/stats/', 'GET', '是', '统计图表数据API'],
        ['/api/attendance/detail/', 'GET', '是', '考勤明细分页API'],
        ['/api/attendance/summary/', 'GET', '是', '今日出勤概览API'],
        ['/api/attendance/export/', 'GET', '是', '导出CSV文件'],
    ]
    t3 = doc.add_table(rows=len(api_rows)+1, cols=4)
    t3.style = 'Table Grid'
    t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(api_headers):
        cell = t3.rows[0].cells[j]
        cell.paragraphs[0].clear()
        run = cell.paragraphs[0].add_run(h)
        set_run_font(run, cn_font='黑体', size=10, bold=True)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), '1F4E79')
        tcPr.append(shd)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for i, row_data in enumerate(api_rows):
        for j, val in enumerate(row_data):
            cell = t3.rows[i+1].cells[j]
            cell.paragraphs[0].clear()
            run = cell.paragraphs[0].add_run(val)
            set_run_font(run, cn_font='宋体', size=9.5)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            if i % 2 == 0:
                tc = cell._tc
                tcPr = tc.get_or_add_tcPr()
                shd = OxmlElement('w:shd')
                shd.set(qn('w:val'), 'clear')
                shd.set(qn('w:color'), 'auto')
                shd.set(qn('w:fill'), 'DCE6F1')
                tcPr.append(shd)
    add_caption(doc, '表 4-3  系统 URL 路由接口设计')


def add_chapter5(doc):
    add_heading(doc, '第五章  系统实现', level=1)

    add_heading(doc, '5.1  项目结构', level=2)
    add_body_paragraph(doc,
        '系统按照 Django 项目规范进行目录组织，核心业务代码集中于 attendance 应用模块，'
        '模板文件统一存放于根目录下的 templates 文件夹，前端 JavaScript 逻辑位于 static/js/ 目录。'
        '项目整体结构清晰，各模块职责明确，便于维护和扩展：')

    code_struct = (
        'MagicFace/\n'
        '├── magicface/               # Django 项目配置包\n'
        '│   ├── settings.py          # 全局配置（数据库、时区、媒体路径）\n'
        '│   ├── urls.py              # 根 URL 路由\n'
        '│   └── wsgi.py              # WSGI 生产入口\n'
        '├── attendance/              # 核心业务应用\n'
        '│   ├── models.py            # 三个数据模型\n'
        '│   ├── views.py             # 所有视图函数（14个路由处理器）\n'
        '│   ├── urls.py              # 应用路由（14条）\n'
        '│   └── services/\n'
        '│       └── face_service.py  # 人脸识别核心服务\n'
        '├── templates/               # HTML 模板（8个页面）\n'
        '├── static/js/               # 前端 JavaScript\n'
        '│   ├── camera.js            # 签到摄像头 + 活体检测逻辑\n'
        '│   ├── enrollment.js        # 录入摄像头逻辑\n'
        '│   └── report.js            # ECharts 图表 + 分页逻辑\n'
        '├── media/                   # 用户上传文件（运行时生成）\n'
        '├── requirements.txt         # Python 依赖声明\n'
        '└── manage.py                # Django 管理工具'
    )
    p_code = doc.add_paragraph()
    run_code = p_code.add_run(code_struct)
    set_run_font(run_code, cn_font='Courier New', en_font='Courier New', size=9)
    p_code.paragraph_format.left_indent = Cm(1)
    p_code.paragraph_format.space_before = Pt(6)
    p_code.paragraph_format.space_after = Pt(6)

    add_heading(doc, '5.2  数据模型实现', level=2)

    add_heading(doc, '5.2.1  Person 模型', level=3)
    add_body_paragraph(doc,
        'Person 模型定义了人员的基本信息和人脸特征存储方式。其中 face_encoding 字段使用 '
        'Django 的 JSONField，将128维浮点数组序列化为 JSON 格式存储到数据库，读取时自动'
        '反序列化为 Python 列表，可直接传入 NumPy 数组进行向量运算，无需额外的序列化/反序列化代码。'
        'employee_id 字段设置了数据库级别的 UNIQUE 约束，从数据库层面保证工号唯一性。')

    add_heading(doc, '5.2.2  AttendanceRule 单例模型', level=3)
    add_body_paragraph(doc,
        'AttendanceRule 模型实现了数据库级别的单例模式：通过重写 save() 方法强制 pk=1，'
        '确保无论何时保存都只更新 id=1 的那条记录；提供 get() 类方法，通过 get_or_create(pk=1) '
        '获取唯一实例（首次访问时自动创建默认配置）。这种设计避免了使用全局变量或缓存带来的并发安全问题，'
        '所有配置修改直接持久化到数据库，服务重启后配置不丢失。')

    add_heading(doc, '5.3  人脸识别服务实现', level=2)
    add_body_paragraph(doc,
        '人脸识别服务模块（face_service.py）封装了人脸特征提取和人脸比对两个核心操作，'
        '通过清晰的函数接口对上层视图屏蔽了底层算法细节，提高了代码的可维护性和可测试性。')
    add_body_paragraph(doc,
        '特征提取函数 extract_face_encoding() 接受 PIL Image 或文件对象作为输入，'
        '统一转换为 RGB 格式的 NumPy 数组后传入 face_recognition 库进行处理。'
        '返回值为128维浮点列表（可直接存入数据库 JSONField）或 None（未检测到人脸）。')
    add_body_paragraph(doc,
        '人脸比对函数 match_face() 接受已知人员特征向量列表、对应 ID 列表和待比对特征向量，'
        '调用 face_recognition.compare_faces() 进行批量向量距离计算，遍历匹配结果返回第一个'
        '匹配人员的 ID。批量计算利用了 NumPy 的向量化运算，相比逐一比较效率提升显著。')

    add_heading(doc, '5.4  签到视图实现', level=2)
    add_body_paragraph(doc,
        '签到提交视图 checkin_submit() 是系统中逻辑最复杂的视图函数，按顺序执行以下处理步骤：'
        '①解析请求体中的 base64 编码图片数据，通过 PIL.Image 解码为图像对象；'
        '②调用 face_service.extract_face_encoding() 提取人脸特征；'
        '③从数据库加载所有人员特征向量，调用 match_face() 进行比对；'
        '④检查该人员今日是否已有签到记录（结合考勤规则中的 allow_repeat 设置）；'
        '⑤比较当前时间与考勤规则中的 checkin_deadline 判定迟到状态；'
        '⑥创建 Attendance 记录并返回 JSON 格式的签到结果。')
    add_body_paragraph(doc,
        '视图函数中的每个步骤在失败时都会立即返回包含错误原因的 JSON 响应，'
        '前端根据响应中的 success 字段决定显示成功提示还是错误提示，'
        '实现了友好的用户反馈机制。')

    add_heading(doc, '5.5  前端活体检测实现', level=2)
    add_body_paragraph(doc,
        '活体检测逻辑在浏览器端的 camera.js 中实现，利用 HTML5 Canvas API 进行帧图像处理。'
        '系统维护一个长度为3的帧缓冲区，每次新帧加入时计算与上一帧的平均像素差值。'
        '计算时对图像进行降采样（每16个字节取1个像素的 RGB 三通道差值），在保证检测精度的'
        '同时大幅降低了计算量，确保不影响签到的实时响应。')
    add_body_paragraph(doc,
        '当活体检测通过后，系统将当前帧以 JPEG 格式（质量80%）转换为 base64 字符串，'
        '通过 fetch API 以 POST 方式发送至后端 /checkin/submit/ 接口。'
        '签到成功后前端自动暂停5秒再继续扫描，防止同一人连续触发多次签到。')

    add_heading(doc, '5.6  考勤报表实现', level=2)
    add_body_paragraph(doc,
        '报表模块采用前后端分离设计，后端提供三个独立的数据 API：统计图表数据（按日/周聚合）、'
        '考勤明细分页数据、今日出勤概览数据。前端 report.js 在页面加载后通过 fetch API 异步'
        '请求这三个接口，获取数据后分别渲染 ECharts 图表和 HTML 表格。')
    add_body_paragraph(doc,
        '统计图表包含两种可视化：签到人次趋势柱状图（支持按最近7天/最近7周切换，直观展示考勤规律）'
        '和今日出勤状态环形饼图（展示正常签到、迟到、未签到三类人员比例）。'
        '考勤明细表格支持分页显示（每页5条），并提供 CSV 导出功能，导出时携带当前时间范围参数，'
        '确保导出数据与当前查看视图一致。')

    add_heading(doc, '5.7  界面设计', level=2)
    add_body_paragraph(doc,
        '系统界面采用简洁的现代化设计风格，以白色和深蓝色（#1F4E79）为主色调，使用 Bootstrap 5 '
        '的组件和栅格系统构建响应式布局，支持在1920px宽屏到375px手机屏幕之间自适应。')
    add_body_paragraph(doc,
        '基础模板（base.html）定义了所有页面共用的顶部导航栏（含系统名称、功能导航链接和登录状态）'
        '和底部页脚，各功能页面通过 Django 模板继承机制复用布局，减少重复代码。')
    add_body_paragraph(doc,
        '签到页面是系统使用频率最高的页面，界面设计以摄像头预览区为核心，占据页面主体空间，'
        '实时显示人脸框引导用户对准摄像头。签到成功时以绿色卡片展示签到人员的照片、姓名和状态，'
        '视觉反馈清晰直观。报表页面通过 ECharts 图表与数据表格的组合，实现了数据的多维度展示。')
