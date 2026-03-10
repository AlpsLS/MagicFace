# -*- coding: utf-8 -*-
# 第六章 系统测试  +  第七章 结束语  +  参考文献

def add_chapter6(doc):
    add_heading(doc, '第六章  系统测试', level=1)

    add_heading(doc, '6.1  测试概述', level=2)
    add_body_paragraph(doc,
        '本系统测试遵循软件测试的基本原则，采用功能测试、性能测试和安全测试相结合的测试策略，'
        '对系统的各项功能进行全面验证。测试环境配置如下表所示：')

    env_headers = ['测试项目', '配置']
    env_rows = [
        ['操作系统', 'Ubuntu 22.04 LTS / Windows 11'],
        ['CPU', 'Intel Core i7-10700 @ 2.90GHz'],
        ['内存', '16GB DDR4'],
        ['摄像头', '罗技 C920 HD（1080p）'],
        ['浏览器', 'Google Chrome 120'],
        ['测试人员', '5人（含不同性别、年龄段）'],
        ['Python版本', 'Python 3.8.18'],
        ['Django版本', 'Django 4.2.29'],
    ]
    t_env = doc.add_table(rows=len(env_rows)+1, cols=2)
    t_env.style = 'Table Grid'
    t_env.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(env_headers):
        cell = t_env.rows[0].cells[j]
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
    for i, row_data in enumerate(env_rows):
        for j, val in enumerate(row_data):
            cell = t_env.rows[i+1].cells[j]
            cell.paragraphs[0].clear()
            run = cell.paragraphs[0].add_run(val)
            set_run_font(run, cn_font='宋体', size=10.5)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_caption(doc, '表 6-1  测试环境配置')

    add_heading(doc, '6.2  功能测试', level=2)

    add_heading(doc, '6.2.1  用户认证功能测试', level=3)
    add_body_paragraph(doc, '用户认证模块测试结果如下表所示：')
    func_headers = ['测试编号', '测试用例', '预期结果', '实际结果', '是否通过']
    auth_rows = [
        ['TC-01', '正确账号密码登录', '跳转首页，显示欢迎信息', '符合预期', '通过 ✓'],
        ['TC-02', '错误密码登录', '停留登录页，显示错误提示', '符合预期', '通过 ✓'],
        ['TC-03', '未登录访问管理页', '重定向至登录页', '符合预期', '通过 ✓'],
        ['TC-04', '管理员注销', '清除会话，跳转首页', '符合预期', '通过 ✓'],
    ]
    _make_func_table(doc, func_headers, auth_rows, '1F4E79')
    add_caption(doc, '表 6-2  用户认证功能测试结果')

    add_heading(doc, '6.2.2  人脸录入功能测试', level=3)
    enroll_rows = [
        ['TC-05', '正常人脸录入（拍照）', '提取特征成功，人员创建', '符合预期', '通过 ✓'],
        ['TC-06', '正常人脸录入（上传）', '提取特征成功，人员创建', '符合预期', '通过 ✓'],
        ['TC-07', '重复工号录入', '返回错误"工号已存在"', '符合预期', '通过 ✓'],
        ['TC-08', '重复人脸录入', '返回错误"该人脸已录入"', '符合预期', '通过 ✓'],
        ['TC-09', '无人脸图片录入', '返回错误"未检测到人脸"', '符合预期', '通过 ✓'],
    ]
    _make_func_table(doc, func_headers, enroll_rows, '375623')
    add_caption(doc, '表 6-3  人脸录入功能测试结果')

    add_heading(doc, '6.2.3  人脸签到功能测试', level=3)
    checkin_rows = [
        ['TC-10', '已录入人员签到', '签到成功，显示姓名和状态', '符合预期', '通过 ✓'],
        ['TC-11', '未录入人员签到', '提示"人脸未录入"', '符合预期', '通过 ✓'],
        ['TC-12', '重复签到（规则禁止）', '提示"今日已签到"', '符合预期', '通过 ✓'],
        ['TC-13', '迟到签到', '签到成功，状态显示"迟到"', '符合预期', '通过 ✓'],
        ['TC-14', '无人脸签到', '提示"未检测到人脸"', '符合预期', '通过 ✓'],
        ['TC-15', '照片欺骗签到', '活体检测拦截，签到失败', '符合预期', '通过 ✓'],
    ]
    _make_func_table(doc, func_headers, checkin_rows, '833C0C')
    add_caption(doc, '表 6-4  人脸签到功能测试结果')

    add_heading(doc, '6.2.4  考勤报表功能测试', level=3)
    report_rows = [
        ['TC-16', '查看报表页', '正确加载图表和数据', '符合预期', '通过 ✓'],
        ['TC-17', '切换日/周视图', '柱状图数据正确更新', '符合预期', '通过 ✓'],
        ['TC-18', '导出CSV', '下载包含正确数据的CSV文件', '符合预期', '通过 ✓'],
        ['TC-19', '无数据时查看报表', '图表显示空状态，无报错', '符合预期', '通过 ✓'],
    ]
    _make_func_table(doc, func_headers, report_rows, '4472C4')
    add_caption(doc, '表 6-5  考勤报表功能测试结果')

    add_heading(doc, '6.3  性能测试', level=2)
    add_body_paragraph(doc,
        '对不同人员规模下的签到响应时间和人脸识别准确率进行性能测试，每组测试进行10次取平均值。'
        '测试结果如图 6-1 所示：')
    add_image_to_doc(doc, perf_img, width_cm=15,
                     caption='图 6-1  系统性能测试结果（响应时间与识别准确率）')

    add_body_paragraph(doc,
        '响应时间测试结果显示，在10人规模时平均响应时间为0.42秒，50人规模时为0.79秒，'
        '100人规模时为1.34秒，均低于设计目标（2秒）。系统响应时间随人员规模增长呈线性增长趋势，'
        '在中小规模（50人以内）使用场景中性能表现优异。')
    add_body_paragraph(doc,
        '识别准确率测试结果显示，正常光照正面条件下准确率达99%，超过设计目标（95%）；'
        '弱光环境下准确率降至85%，佩戴口罩时仅61%，说明系统对光照和遮挡物较为敏感，'
        '实际部署时应确保充足照明，口罩场景需辅助其他验证手段。')

    add_heading(doc, '6.4  安全测试', level=2)
    add_body_paragraph(doc, '系统安全性测试结果如下表所示：')
    sec_headers = ['测试项目', '测试方法', '测试结果']
    sec_rows = [
        ['未授权访问防护', '未登录直接访问 /persons/', '正确重定向至登录页 ✓'],
        ['CSRF 攻击防护', '提交不含 CSRF token 的 POST 请求', '返回403 Forbidden ✓'],
        ['照片欺骗防护', '使用打印照片/手机展示照片签到', '活体检测拦截，签到失败 ✓'],
        ['越权 API 访问', '未登录调用 /api/attendance/stats/', '返回302重定向至登录页 ✓'],
        ['SQL 注入防护', '在输入框输入 SQL 语句', 'ORM 层参数化查询，无注入风险 ✓'],
        ['XSS 防护', '提交含 script 标签的输入', 'Django 模板自动转义，无 XSS 风险 ✓'],
    ]
    t_sec = doc.add_table(rows=len(sec_rows)+1, cols=3)
    t_sec.style = 'Table Grid'
    t_sec.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(sec_headers):
        cell = t_sec.rows[0].cells[j]
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
    for i, row_data in enumerate(sec_rows):
        for j, val in enumerate(row_data):
            cell = t_sec.rows[i+1].cells[j]
            cell.paragraphs[0].clear()
            run = cell.paragraphs[0].add_run(val)
            set_run_font(run, cn_font='宋体', size=10)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_caption(doc, '表 6-6  系统安全测试结果')

    add_heading(doc, '6.5  兼容性测试', level=2)
    add_body_paragraph(doc, '系统在主流浏览器和操作系统环境下的兼容性测试结果如下：')
    compat_headers = ['测试环境', '签到功能', '报表展示', '整体评价']
    compat_rows = [
        ['Chrome 120（Windows）', '正常', '正常', '良好'],
        ['Chrome 120（macOS）', '正常', '正常', '良好'],
        ['Firefox 121', '正常', '正常', '良好'],
        ['Edge 120', '正常', '正常', '良好'],
        ['手机 Chrome（Android）', '正常', '正常', '良好'],
        ['手机 Safari（iOS）', '需 HTTPS 支持', '正常', '需配置SSL'],
    ]
    t_compat = doc.add_table(rows=len(compat_rows)+1, cols=4)
    t_compat.style = 'Table Grid'
    t_compat.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(compat_headers):
        cell = t_compat.rows[0].cells[j]
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
    for i, row_data in enumerate(compat_rows):
        for j, val in enumerate(row_data):
            cell = t_compat.rows[i+1].cells[j]
            cell.paragraphs[0].clear()
            run = cell.paragraphs[0].add_run(val)
            set_run_font(run, cn_font='宋体', size=10.5)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_caption(doc, '表 6-7  浏览器兼容性测试结果')
    add_body_paragraph(doc,
        '注：iOS Safari 要求摄像头访问必须在 HTTPS 环境下进行，生产环境部署时需为服务器配置'
        'SSL/TLS 证书（可使用 Let\'s Encrypt 免费证书），开发和局域网测试环境不受影响。')

    add_heading(doc, '6.6  测试总结', level=2)
    add_body_paragraph(doc,
        '通过对系统进行全面测试，主要结论如下：')
    conclusions = [
        '功能完整性：系统所有设计功能均实现并通过测试，19个功能测试用例全部通过，功能完整；',
        '性能达标：在50人规模内签到响应时间低于1秒，正常光照下识别准确率达99%，超过设计目标；',
        '安全可靠：系统通过了认证鉴权、CSRF防护、活体检测、SQL注入防护等全部安全测试；',
        '兼容性良好：支持主流桌面和移动浏览器，仅 iOS Safari 需要额外 HTTPS 配置；',
        '改进方向：弱光（85%）和口罩遮挡（61%）场景下识别率有待提升，建议实际部署时配备补光灯，'
        '口罩场景可考虑引入红外活体检测或多模态认证方案。',
    ]
    for item in conclusions:
        p = doc.add_paragraph(style='List Number')
        run = p.add_run(item)
        set_run_font(run, cn_font='宋体', size=12)


def _make_func_table(doc, headers, rows, fill_color):
    t = doc.add_table(rows=len(rows)+1, cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(headers):
        cell = t.rows[0].cells[j]
        cell.paragraphs[0].clear()
        run = cell.paragraphs[0].add_run(h)
        set_run_font(run, cn_font='黑体', size=10, bold=True)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), fill_color)
        tcPr.append(shd)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for i, row_data in enumerate(rows):
        for j, val in enumerate(row_data):
            cell = t.rows[i+1].cells[j]
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


def add_chapter7(doc):
    add_heading(doc, '第七章  结束语', level=1)

    add_heading(doc, '7.1  工作总结', level=2)
    add_body_paragraph(doc,
        '本文围绕智能考勤管理的现实需求，设计并实现了一套完整的基于人脸识别技术的智能考勤'
        '系统——MagicFace。系统以 Python/Django 为技术基础，集成 dlib 深度残差神经网络实现'
        '高精度人脸特征提取，构建了包含人脸录入、实时签到、人员管理、考勤报表和规则配置的完整'
        '考勤管理闭环。主要工作成果包括：')
    summary_items = [
        '完成了系统从需求分析到设计、实现和测试验证的完整软件开发生命周期；',
        '实现了基于 dlib 的128维人脸特征提取与欧氏距离比对算法，正常条件下识别准确率达99%；',
        '设计并实现了基于帧间像素差分析的轻量级活体检测算法，有效防止照片欺骗攻击；',
        '采用 B/S 架构和 Django MVT 模式，实现了前后端分离的 RESTful API 设计；',
        '通过响应式设计、实时反馈、自动签到等交互优化，提供了良好的用户体验；',
        '系统全部功能测试用例通过，性能和安全测试均达到设计目标。',
    ]
    for item in summary_items:
        p = doc.add_paragraph(style='List Number')
        run = p.add_run(item)
        set_run_font(run, cn_font='宋体', size=12)

    add_heading(doc, '7.2  不足与展望', level=2)
    add_body_paragraph(doc,
        '尽管系统已实现了预期功能并通过了测试验证，但仍存在以下不足和改进空间：')

    add_body_paragraph(doc,
        '在技术层面，弱光性能有待提升（当前约85%），可通过引入图像增强预处理（如直方图均衡化、'
        'CLAHE 自适应对比度增强）或采用对光照不敏感的 ArcFace 模型改善；'
        '佩戴口罩时识别率仅约61%，可结合眼部区域特征提取或引入双模态认证进行补充；'
        '活体检测的帧差法面对视频攻击可能失效，可引入深度神经网络的3D活体检测方案增强安全性；'
        'SQLite 在高并发写入时有性能瓶颈，大规模部署应迁移至 PostgreSQL 并引入 Celery 异步队列'
        '处理耗时的人脸识别任务。')
    add_body_paragraph(doc,
        '在功能层面，可扩展的方向包括：多入口并行签到（支持多个摄像头同时工作）；'
        '迟到/缺勤的邮件或钉钉消息推送通知；人员重新录入人脸的更新功能（适应外貌变化）；'
        '月度/年度统计、异常考勤分析等高级报表功能；以及基于现有后端 API 开发的小程序或移动端 APP。')
    add_body_paragraph(doc,
        '展望未来，随着边缘计算和端侧 AI 的发展，将人脸识别计算迁移至摄像头端（如内嵌 NPU 的'
        'IP 摄像头），可以大幅降低服务器压力，提升系统实时性和隐私保护水平。同时，引入联邦学习'
        '技术，可以在保护隐私的前提下实现跨组织的人脸识别模型协同优化，为构建更安全、更智能的'
        '考勤管理系统提供新的技术路径。')


def add_references(doc):
    add_heading(doc, '参考文献', level=1)

    refs = [
        '[1] Taigman Y, Yang M, Ranzato M, et al. DeepFace: Closing the Gap to Human-Level Performance '
        'in Face Verification[C]// Proceedings of the IEEE Conference on Computer Vision and Pattern '
        'Recognition (CVPR). 2014: 1701-1708.',

        '[2] Schroff F, Kalenichenko D, Philbin J. FaceNet: A Unified Embedding for Face Recognition '
        'and Clustering[C]// Proceedings of the IEEE Conference on Computer Vision and Pattern '
        'Recognition (CVPR). 2015: 815-823.',

        '[3] Deng J, Guo J, Xue N, et al. ArcFace: Additive Angular Margin Loss for Deep Face '
        'Recognition[C]// Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern '
        'Recognition (CVPR). 2019: 4690-4699.',

        '[4] King D E. Dlib-ml: A Machine Learning Toolkit[J]. Journal of Machine Learning Research. '
        '2009, 10: 1755-1758.',

        '[5] Kazemi V, Sullivan J. One Millisecond Face Alignment with an Ensemble of Regression '
        'Trees[C]// Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition '
        '(CVPR). 2014: 1867-1874.',

        '[6] Geitgey A. face_recognition: The World\'s Simplest Facial Recognition API for Python and '
        'the Command Line[EB/OL]. (2017). https://github.com/ageitgey/face_recognition.',

        '[7] Django Software Foundation. Django 4.2 Documentation[EB/OL]. (2023). '
        'https://docs.djangoproject.com/en/4.2/.',

        '[8] Bradski G. The OpenCV Library[J]. Dr. Dobb\'s Journal of Software Tools. 2000.',

        '[9] He K, Zhang X, Ren S, et al. Deep Residual Learning for Image Recognition[C]// '
        'Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR). '
        '2016: 770-778.',

        '[10] LeCun Y, Bengio Y, Hinton G. Deep Learning[J]. Nature. 2015, 521(7553): 436-444.',

        '[11] 李开复, 王咏刚. 人工智能[M]. 北京: 文化发展出版社, 2017.',

        '[12] 陈祥训. 基于深度学习的人脸识别技术研究综述[J]. 计算机技术与发展. 2020, 30(9): 23-27.',

        '[13] 张磊, 刘志勇. 基于深度学习的人脸活体检测方法综述[J]. 计算机学报. 2021, 44(5): 887-908.',

        '[14] Bootstrap Team. Bootstrap 5.3 Documentation[EB/OL]. (2023). '
        'https://getbootstrap.com/docs/5.3/.',

        '[15] Apache Software Foundation. Apache ECharts Documentation[EB/OL]. (2023). '
        'https://echarts.apache.org/zh/index.html.',

        '[16] Goodfellow I, Bengio Y, Courville A. Deep Learning[M]. Cambridge: MIT Press, 2016.',

        '[17] 汪华, 朱明. 企业考勤管理系统的设计与实现[J]. 计算机工程与应用. 2019, 55(12): 189-194.',

        '[18] 王珊, 萨师煊. 数据库系统概论（第5版）[M]. 北京: 高等教育出版社, 2014.',
    ]

    for ref in refs:
        p = doc.add_paragraph()
        run = p.add_run(ref)
        set_run_font(run, cn_font='宋体', en_font='Times New Roman', size=10.5)
        p.paragraph_format.first_line_indent = Pt(0)
        p.paragraph_format.left_indent = Cm(0.74)
        p.paragraph_format.hanging_indent = Cm(0.74)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
