# -*- coding: utf-8 -*-
# 第一章 引言  +  第二章 开发工具  +  第三章 系统分析

def add_chapter1(doc):
    add_heading(doc, '第一章  引言', level=1)

    add_heading(doc, '1.1  研究背景', level=2)
    add_body_paragraph(doc,
        '进入21世纪以来，互联网技术与人工智能技术的深度融合推动了各行各业的数字化转型。'
        '在企业和高校的日常管理中，考勤管理是保障组织秩序、提升管理效率的重要环节。'
        '传统考勤方式主要包括手工签到、刷卡考勤和指纹打卡等，然而这些方式存在较多局限性：'
        '手工签到容易出现代签、漏签等违规行为；刷卡考勤依赖物理卡片，存在忘带或借卡的问题；'
        '指纹打卡对于皮肤受损人员识别效果差，且存在卫生方面的顾虑，尤其在疫情防控背景下，'
        '非接触式考勤的需求愈发迫切。')
    add_body_paragraph(doc,
        '与此同时，以深度学习为基础的计算机视觉技术取得了突破性进展。人脸识别作为生物特征识别的'
        '重要分支，具有非接触、高效便捷、难以伪造等天然优势，已在门禁系统、金融支付、公共安全等'
        '众多场景中得到广泛应用。将人脸识别技术引入考勤管理领域，构建一套智能化、自动化的人脸识别'
        '考勤系统，是信息技术与管理实践相结合的重要探索方向。')

    add_heading(doc, '1.2  研究意义', level=2)
    add_body_paragraph(doc,
        '本研究的意义主要体现在以下几个方面：')
    add_body_paragraph(doc,
        '在实用价值方面，基于人脸识别的考勤系统能够有效解决代签、漏签等管理漏洞，降低考勤管理的'
        '人力成本，提升考勤数据的准确性和实时性。同时，系统支持多终端（PC摄像头、手机摄像头）接入，'
        '部署灵活，适合多种应用场景。')
    add_body_paragraph(doc,
        '在技术研究方面，本项目将深度学习人脸识别算法与 Web 系统工程化开发相结合，探索了活体检测、'
        '人脸特征存储与高效比对等关键技术的实现路径，为后续相关研究提供了工程参考。')
    add_body_paragraph(doc,
        '在安全与隐私方面，系统采用局域网部署方案，人脸特征数据以128维数值向量形式存储而非原始图像，'
        '兼顾了识别精度与数据安全性，有效降低了隐私泄露风险。')

    add_heading(doc, '1.3  国内外研究现状', level=2)
    add_body_paragraph(doc,
        '人脸识别技术的研究始于20世纪60年代，Bledsoe 等人开展了早期的人工标注辅助识别实验。'
        '1991年，Turk 和 Pentland 提出的 PCA 特征脸（Eigenface）算法标志着自动人脸识别研究的'
        '正式起步。进入21世纪后，基于局部二值模式（LBP）、主动外观模型（AAM）的传统机器学习方法'
        '逐渐成熟。')
    add_body_paragraph(doc,
        '2012年，深度卷积神经网络（CNN）在 ImageNet 竞赛中展现出碾压性优势，此后 DeepFace'
        '（Facebook，2014）、FaceNet（Google，2015）、ArcFace（2019）等深度学习人脸识别方法'
        '相继提出，识别精度在标准数据集上已超越人类水平（LFW数据集准确率达99.83%）。dlib 库由 '
        'Davis King 开发，其内置的人脸关键点检测（68点）和基于深度残差网络的人脸特征提取模型，'
        '在精度与速度之间取得了良好平衡，被广泛应用于工程项目中。face_recognition 库对 dlib '
        '进行了封装，提供了简洁的 Python API，进一步降低了人脸识别的开发门槛。')
    add_body_paragraph(doc,
        '在考勤系统领域，国内外已有多种商业化人脸考勤产品，如海康威视、大华等厂商的人脸门禁一体机，'
        '钉钉、企业微信等平台的人脸打卡功能。这些产品功能完善但成本较高，且依赖云端服务，数据隐私'
        '存在一定风险。学术界也有诸多基于 OpenCV、TensorFlow 的考勤系统研究，但多停留在算法验证'
        '层面，缺乏完整的工程化实现。本系统针对中小规模应用场景，以开源技术栈实现了完整的考勤管理'
        '闭环，在功能完整性、部署便捷性和数据安全性方面具有一定优势。')

    add_heading(doc, '1.4  研究内容与方法', level=2)
    add_body_paragraph(doc,
        '本文的主要研究内容包括：基于 dlib 深度残差网络的128维人脸特征提取方法研究；人脸比对阈值'
        '设定与识别准确率优化；基于帧间像素差的轻量级活体检测算法设计；Django MVT 架构下的 Web '
        '考勤系统全栈实现；以及系统的功能测试与性能评估。')
    add_body_paragraph(doc,
        '研究方法以工程实践为主，结合文献调研、原型设计、迭代开发和测试验证，遵循软件工程的需求分析'
        '→ 系统设计 → 编码实现 → 测试优化的完整开发流程。')


def add_chapter2(doc):
    add_heading(doc, '第二章  开发工具和技术介绍', level=1)

    add_heading(doc, '2.1  后端开发技术', level=2)

    add_heading(doc, '2.1.1  Python 3.8', level=3)
    add_body_paragraph(doc,
        'Python 是一种解释型、面向对象的高级编程语言，以其简洁的语法、丰富的第三方库生态系统和'
        '强大的科学计算能力，成为人工智能和 Web 开发领域的主流语言。本项目选用 Python 3.8 版本，'
        '该版本稳定性强，与主要依赖库（dlib、face_recognition）的兼容性好。Python 3.8 引入了'
        '赋值表达式（海象运算符 :=）、f-string 调试支持等新特性，进一步提升了开发效率。')

    add_heading(doc, '2.1.2  Django 4.2 Web 框架', level=3)
    add_body_paragraph(doc,
        'Django 是一个高级 Python Web 框架，遵循 MVT（Model-View-Template）架构模式，秉承'
        '"不重复造轮子"的设计哲学，内置了大量开箱即用的功能组件。Django 的核心特性包括：ORM '
        '对象关系映射（通过 Python 类定义数据库模型，自动生成并执行 SQL）；内置认证系统（提供完整'
        '的用户注册、登录、权限管理功能）；Admin 后台（自动根据模型生成功能完备的管理界面）；'
        '灵活的 URL 路由配置机制；Django Template Language 模板引擎；以及 CSRF 防护、XSS '
        '过滤、SQL 注入防护等内置安全机制。Django 4.2 是长期支持版本（LTS），具有更好的异步支持'
        '和性能优化，维护周期至2026年4月。')

    add_heading(doc, '2.1.3  face_recognition 库', level=3)
    add_body_paragraph(doc,
        'face_recognition 是由 Adam Geitgey 开发的开源人脸识别库，基于 dlib 进行封装，提供了'
        '简单易用的 Python API。其核心功能包括：人脸检测（定位图像中的人脸区域）；人脸关键点提取'
        '（识别68个面部特征点，覆盖眉毛、眼睛、鼻子、嘴巴、下颌线）；人脸特征编码（生成128维特征'
        '向量，唯一表示一张人脸）；以及人脸比对（计算两个特征向量的欧氏距离，判断是否为同一人）。'
        'face_recognition 在 Labeled Faces in the Wild 基准数据集上的准确率达到 99.38%。')

    add_heading(doc, '2.1.4  dlib 深度学习库', level=3)
    add_body_paragraph(doc,
        'dlib 是一个包含机器学习算法和计算机视觉工具的 C++ 工具库，提供 Python 接口。其人脸识别'
        '模块基于深度残差神经网络（ResNet-34），通过度量学习（Metric Learning）训练，能够将人脸'
        '图像映射到128维欧氏空间中，使得同一人的不同图像距离尽量接近，不同人的图像距离尽量远离。'
        'dlib 的人脸检测采用基于 HOG 特征的线性 SVM 分类器，在 CPU 上即可实现实时检测，无需 GPU。')

    add_heading(doc, '2.1.5  OpenCV 图像处理库', level=3)
    add_body_paragraph(doc,
        'OpenCV（Open Source Computer Vision Library）是一个开源的计算机视觉和机器学习软件库，'
        '提供了2500多个优化算法。本项目使用 opencv-python 4.13 进行图像格式转换（BGR ↔ RGB）'
        '和预处理操作，为人脸识别算法提供标准格式的输入数据。OpenCV 采用 C++ 实现核心算法并提供'
        'Python 绑定，具有极高的运行效率。')

    add_heading(doc, '2.2  数据库技术', level=2)
    add_body_paragraph(doc,
        'SQLite 是一个轻量级的嵌入式关系型数据库，其数据库以单个文件形式存储，无需独立的服务器'
        '进程，非常适合开发、测试和小规模部署场景。Django 内置对 SQLite 的完整支持，通过 ORM '
        '操作数据库无需额外配置。本项目使用 SQLite3 作为数据存储方案，主要基于以下考虑：零配置'
        '（无需安装和配置数据库服务）；轻量化（数据库文件体积小，便于备份和迁移）；可靠性（SQLite '
        '支持 ACID 事务，数据安全有保障）；可扩展性（在需要时可方便迁移至 MySQL、PostgreSQL 等'
        '生产级数据库，Django ORM 层无需修改业务代码）。')

    add_heading(doc, '2.3  前端开发技术', level=2)

    add_heading(doc, '2.3.1  Bootstrap 5.3', level=3)
    add_body_paragraph(doc,
        'Bootstrap 是目前最流行的 CSS 前端框架，提供了丰富的 UI 组件（导航栏、卡片、表格、模态框等）'
        '和响应式栅格系统。本项目使用 Bootstrap 5.3.2 构建移动端自适应的管理界面，大幅减少了前端'
        '样式开发工作量。Bootstrap 5 采用 Flexbox 布局，移除了对 jQuery 的依赖，提升了性能。')

    add_heading(doc, '2.3.2  Apache ECharts 5', level=3)
    add_body_paragraph(doc,
        'Apache ECharts 是百度捐献给 Apache 软件基金会的开源数据可视化库，提供折线图、柱状图、'
        '饼图、散点图等丰富图表类型，支持大数据量渲染和流畅的交互动画。本项目使用 ECharts 5 实现'
        '考勤统计数据的可视化展示，包括签到人次趋势柱状图和出勤状态环形饼图，直观呈现考勤数据规律。')

    add_heading(doc, '2.3.3  WebRTC 摄像头接口', level=3)
    add_body_paragraph(doc,
        'WebRTC（Web Real-Time Communication）是浏览器内置的实时通信 API，允许网页直接访问用户'
        '摄像头和麦克风，无需安装插件。本项目通过 navigator.mediaDevices.getUserMedia() API '
        '调用本地摄像头，在浏览器端完成视频流采集，并通过 HTML5 Canvas 截取帧图像（转换为 base64 '
        '编码）发送至后端进行人脸识别。')

    add_heading(doc, '2.4  开发工具汇总', level=2)
    add_body_paragraph(doc, '系统开发过程中使用的主要工具和技术版本汇总如下表所示：')

    headers = ['工具/框架', '版本', '用途']
    rows = [
        ['Python', '3.8.x', '后端主要开发语言'],
        ['Django', '4.2.29（LTS）', 'Web 框架，路由/视图/ORM'],
        ['face_recognition', '1.3.0', '人脸识别核心库'],
        ['dlib', '20.0.0', '深度学习底层支撑'],
        ['opencv-python', '4.13.0.92', '图像格式转换与处理'],
        ['numpy', '1.24.4', '人脸特征向量数值计算'],
        ['Pillow', '10.4.0', '图像文件读写'],
        ['SQLite', '3.x（内置）', '轻量级关系型数据库'],
        ['Bootstrap', '5.3.2', '前端 UI 响应式框架'],
        ['ECharts', '5.x', '数据可视化图表库'],
        ['Git', '-', '版本控制工具'],
    ]
    tbl = doc.add_table(rows=len(rows)+1, cols=3)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    # 表头
    for j, h in enumerate(headers):
        cell = tbl.rows[0].cells[j]
        cell.paragraphs[0].clear()
        run = cell.paragraphs[0].add_run(h)
        set_run_font(run, cn_font='黑体', size=11, bold=True)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), '1F4E79')
        tcPr.append(shd)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    # 数据行
    for i, row_data in enumerate(rows):
        for j, val in enumerate(row_data):
            cell = tbl.rows[i+1].cells[j]
            cell.paragraphs[0].clear()
            run = cell.paragraphs[0].add_run(val)
            set_run_font(run, cn_font='宋体', size=10.5)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            if i % 2 == 0:
                tc = cell._tc
                tcPr = tc.get_or_add_tcPr()
                shd = OxmlElement('w:shd')
                shd.set(qn('w:val'), 'clear')
                shd.set(qn('w:color'), 'auto')
                shd.set(qn('w:fill'), 'DCE6F1')
                tcPr.append(shd)
    tbl.style = 'Table Grid'
    add_caption(doc, '表 2-1  开发工具与技术版本汇总')


def add_chapter3(doc):
    add_heading(doc, '第三章  系统分析', level=1)

    add_heading(doc, '3.1  系统目标', level=2)
    add_body_paragraph(doc,
        '本系统旨在为中小型企业和学校提供一套基于人脸识别的智能考勤管理解决方案，实现以下目标：')
    goals = [
        ('便捷性目标', '用户无需携带任何证件或设备，仅凭本人面部即可完成考勤签到，签到过程无需接触，操作简单直观；'),
        ('准确性目标', '系统人脸识别准确率不低于95%，能够有效区分不同人员，避免误认；'),
        ('防作弊目标', '系统具备基础活体检测能力，能够识别照片欺骗攻击，确保签到的真实性；'),
        ('管理目标', '管理员能够便捷地进行人员信息管理、考勤规则配置、历史记录查询和数据统计分析；'),
        ('可用性目标', '系统界面友好，响应及时，正常签到流程在2秒内完成；'),
        ('安全目标', '管理功能需要身份验证，人脸特征数据安全存储，防止未授权访问。'),
    ]
    for title, content in goals:
        p = doc.add_paragraph(style='List Bullet')
        run_t = p.add_run(title + '：')
        set_run_font(run_t, cn_font='黑体', size=12, bold=True)
        run_c = p.add_run(content)
        set_run_font(run_c, cn_font='宋体', size=12)

    add_heading(doc, '3.2  系统对象分析', level=2)
    add_body_paragraph(doc, '系统的主要使用对象分为两类：')
    add_body_paragraph(doc,
        '普通用户（签到人员）：主要操作为在签到页面通过摄像头进行人脸识别签到。技术要求仅需使用'
        '有摄像头的设备访问系统网页，无需任何专业知识。权限范围仅可访问签到功能，无法查看他人信息'
        '或修改系统配置。')
    add_body_paragraph(doc,
        '管理员：主要操作包括人员注册录入、考勤记录查询、报表分析、规则配置等。权限范围涵盖全部'
        '系统功能，包括人员管理、考勤查询、数据导出、规则设置，以及 Django Admin 超级管理后台。')

    add_heading(doc, '3.3  可行性分析', level=2)

    add_heading(doc, '3.3.1  技术可行性', level=3)
    add_body_paragraph(doc,
        '本项目所采用的核心技术均已成熟并广泛应用于工业界：face_recognition + dlib 方案已在 '
        'GitHub 获得超过5万 Star，在学术和工业界均有大量验证，技术成熟度高；Python + Django 是'
        '成熟的全栈 Web 开发方案，有完整的官方文档和社区支持；Bootstrap 和 ECharts 均是业界主流'
        '前端框架，文档完善，使用广泛；系统对硬件要求不高，普通 PC 或服务器即可运行，摄像头为普通'
        'USB 或 IP 网络摄像头。综上，技术层面完全可行。')

    add_heading(doc, '3.3.2  经济可行性', level=3)
    add_body_paragraph(doc,
        '系统开发所使用的所有技术组件均为开源免费软件，无需购买商业授权；部署环境为普通 PC 服务器'
        '或云服务器，成本低廉；与商业人脸考勤设备（通常数千元/台）相比，本系统仅需普通摄像头（数十'
        '至百余元），大幅降低了硬件投入；系统维护简单，无需专业运维人员。因此，经济可行性良好。')

    add_heading(doc, '3.3.3  操作可行性', level=3)
    add_body_paragraph(doc,
        '系统采用 B/S（浏览器/服务器）架构，用户只需通过浏览器即可使用全部功能，无需安装客户端'
        '软件；界面设计简洁直观，签到操作仅需站在摄像头前等待系统自动识别，操作门槛极低；管理界面'
        '采用表单化操作，符合用户的操作习惯。因此，操作可行性良好。')

    add_heading(doc, '3.4  功能需求分析', level=2)
    add_body_paragraph(doc,
        '根据对用户需求的调研和分析，系统需实现以下六大功能模块：')

    modules_desc = [
        ('用户认证模块', '管理员登录/注销功能；未认证用户访问受保护页面时自动重定向至登录页；密码验证和会话管理。'),
        ('人脸录入模块', '支持填写姓名和工号/学号信息；支持通过摄像头实时拍照或上传本地照片录入人脸；'
                        '自动提取并存储128维人脸特征向量；重复工号校验和重复人脸校验。'),
        ('人脸签到模块', '支持调用本地摄像头或 IP 网络摄像头进行实时视频流签到；活体检测防止照片欺骗；'
                        '自动扫描每隔固定时间自动尝试识别；根据配置的截止时间自动判断正常/迟到；防重复签到。'),
        ('人员管理模块', '已录入人员列表查看（含姓名、工号、照片、录入时间）；删除人员功能（同时删除关联考勤记录）。'),
        ('考勤报表模块', '按日期范围查询考勤记录；考勤人次统计图表（按日/按周）；出勤状态分布饼图；'
                        '分页明细列表；CSV 格式数据导出。'),
        ('考勤规则配置模块', '签到截止时间设置；是否允许重复签到开关；规则修改后立即生效。'),
    ]
    for mod_name, mod_desc in modules_desc:
        p = doc.add_paragraph(style='List Number')
        r1 = p.add_run(mod_name + '：')
        set_run_font(r1, cn_font='黑体', size=12, bold=True)
        r2 = p.add_run(mod_desc)
        set_run_font(r2, cn_font='宋体', size=12)

    doc.add_paragraph()
    add_body_paragraph(doc, '系统功能模块整体结构如图 3-1 所示：')
    add_image_to_doc(doc, module_img, width_cm=15,
                     caption='图 3-1  MagicFace 系统功能模块图')

    add_heading(doc, '3.5  非功能需求分析', level=2)
    add_body_paragraph(doc,
        '性能需求：单次人脸识别响应时间不超过2秒；系统支持50人以内的人员规模，识别准确率不低于95%。')
    add_body_paragraph(doc,
        '安全需求：管理功能使用 Django 内置认证系统保护；API 接口具有 CSRF 防护；人脸特征以数值'
        '向量而非原始图像形式存储，降低数据泄露风险。')
    add_body_paragraph(doc,
        '可用性需求：界面在 PC 端和移动端均可正常使用；系统 7×24 小时可用；关键操作具有明确的反馈提示。')
    add_body_paragraph(doc,
        '可维护性需求：代码遵循 Python PEP8 规范；模块化设计，各功能模块低耦合；数据库可方便迁移'
        '至其他关系型数据库（MySQL、PostgreSQL 等）。')
