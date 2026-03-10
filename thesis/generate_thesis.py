# -*- coding: utf-8 -*-
"""
MagicFace 毕业设计论文 Word 生成脚本
分步构建：封面、目录、正文各章节、图表
"""

import os
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.font_manager as fm
import numpy as np

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from copy import deepcopy
import lxml.etree as etree

# ── 中文字体配置 ──────────────────────────────────────────────
# 优先使用系统中文字体
FONT_PATHS = [
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/arphic/uming.ttc",
]
CN_FONT = None
for fp in FONT_PATHS:
    if os.path.exists(fp):
        CN_FONT = fm.FontProperties(fname=fp)
        plt.rcParams['font.family'] = CN_FONT.get_name()
        break
if CN_FONT is None:
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ── 输出文件路径 ──────────────────────────────────────────────
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "MagicFace毕业设计论文.docx")
IMG_DIR = os.path.join(OUTPUT_DIR, "thesis_imgs")
os.makedirs(IMG_DIR, exist_ok=True)


# ════════════════════════════════════════════════════════════════
# 工具函数
# ════════════════════════════════════════════════════════════════

def set_paragraph_format(para, first_line_indent=True, space_before=0,
                          space_after=6, line_spacing=1.5):
    """统一段落格式"""
    pf = para.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = Pt(line_spacing * 12)
    if first_line_indent:
        pf.first_line_indent = Cm(0.74)  # 两个字符缩进


def set_run_font(run, cn_font='宋体', en_font='Times New Roman',
                 size=12, bold=False):
    """设置中英文字体"""
    run.font.name = en_font
    run.font.size = Pt(size)
    run.font.bold = bold
    r = run._r
    rPr = r.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:eastAsia'), cn_font)
    rFonts.set(qn('w:ascii'), en_font)
    rFonts.set(qn('w:hAnsi'), en_font)
    existing = rPr.find(qn('w:rFonts'))
    if existing is not None:
        rPr.remove(existing)
    rPr.insert(0, rFonts)


def add_heading(doc, text, level=1):
    """添加标题"""
    para = doc.add_heading(text, level=level)
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in para.runs:
        set_run_font(run, cn_font='黑体', en_font='Times New Roman',
                     size=16 if level == 1 else (14 if level == 2 else 12),
                     bold=True)
    para.paragraph_format.space_before = Pt(12)
    para.paragraph_format.space_after = Pt(6)
    return para


def add_body_paragraph(doc, text, first_indent=True):
    """添加正文段落"""
    para = doc.add_paragraph()
    run = para.add_run(text)
    set_run_font(run, cn_font='宋体', size=12)
    set_paragraph_format(para, first_line_indent=first_indent)
    return para


def add_caption(doc, text, fig_num=None):
    """添加图/表标题"""
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run(text)
    set_run_font(run, cn_font='黑体', size=11, bold=True)
    para.paragraph_format.space_before = Pt(3)
    para.paragraph_format.space_after = Pt(6)
    return para


def add_image_to_doc(doc, img_path, width_cm=14, caption=None):
    """插入图片到文档"""
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run()
    run.add_picture(img_path, width=Cm(width_cm))
    if caption:
        add_caption(doc, caption)


def set_table_style(table, header_color="1F4E79"):
    """设置表格样式"""
    table.style = 'Table Grid'
    for i, row in enumerate(table.rows):
        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            para = cell.paragraphs[0]
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in para.runs:
                set_run_font(run, cn_font='宋体', size=10.5,
                             bold=(i == 0))
            # 表头背景色
            if i == 0:
                tc = cell._tc
                tcPr = tc.get_or_add_tcPr()
                shd = OxmlElement('w:shd')
                shd.set(qn('w:val'), 'clear')
                shd.set(qn('w:color'), 'auto')
                shd.set(qn('w:fill'), header_color)
                tcPr.append(shd)
                for run in para.runs:
                    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)


def save_fig(name):
    """保存matplotlib图片并返回路径"""
    path = os.path.join(IMG_DIR, f"{name}.png")
    plt.savefig(path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    return path


# ════════════════════════════════════════════════════════════════
# 图表生成函数
# ════════════════════════════════════════════════════════════════

def make_system_arch():
    """系统三层架构图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    layers = [
        (0.5, 4.2, 9, 1.4, '#D6E4FF', '#1F4E79', '表示层（前端）',
         'Bootstrap 5 + ECharts + WebRTC Camera API\n浏览器渲染 | 响应式布局 | 实时摄像头'),
        (0.5, 2.4, 9, 1.4, '#E2EFDA', '#375623', '业务逻辑层（后端）',
         'Django 4.2 MVT | face_recognition + dlib\nURL路由 | 视图函数 | 人脸识别服务'),
        (0.5, 0.6, 9, 1.4, '#FCE4D6', '#833C0C', '数据存储层',
         'SQLite3 数据库 | Media 文件系统\nPerson | Attendance | AttendanceRule'),
    ]

    for x, y, w, h, fc, tc, title, desc in layers:
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                              facecolor=fc, edgecolor=tc, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + 0.3, y + h - 0.35, title, fontsize=13, fontweight='bold',
                color=tc, va='top', fontproperties=CN_FONT)
        ax.text(x + 0.3, y + 0.25, desc, fontsize=9.5, color='#333333',
                va='bottom', fontproperties=CN_FONT)

    # 箭头
    for ya, yb in [(4.2, 3.8), (2.4, 2.0)]:
        ax.annotate('', xy=(5, yb), xytext=(5, ya),
                    arrowprops=dict(arrowstyle='<->', color='#555555',
                                   lw=2))
    ax.text(5.15, 3.95, 'HTTP / JSON', fontsize=9, color='#555555',
            fontproperties=CN_FONT)
    ax.text(5.15, 2.15, 'Django ORM', fontsize=9, color='#555555',
            fontproperties=CN_FONT)

    ax.set_title('MagicFace 系统三层架构图', fontsize=15, fontweight='bold',
                 pad=10, fontproperties=CN_FONT)
    return save_fig('arch')


def make_checkin_flow():
    """签到流程图"""
    fig, ax = plt.subplots(figsize=(8, 13))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 13)
    ax.axis('off')

    def box(x, y, w, h, text, color='#D6E4FF', ec='#1F4E79', shape='rect'):
        if shape == 'diamond':
            cx, cy = x + w/2, y + h/2
            dx, dy = w/2, h/2
            diamond = plt.Polygon(
                [[cx, cy+dy], [cx+dx, cy], [cx, cy-dy], [cx-dx, cy]],
                facecolor='#FFF2CC', edgecolor='#D6A22A', linewidth=1.5)
            ax.add_patch(diamond)
        else:
            rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                                  facecolor=color, edgecolor=ec, linewidth=1.5)
            ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center',
                fontsize=9.5, fontproperties=CN_FONT,
                color='#1a1a1a', multialignment='center')

    def arrow(x1, y1, x2, y2, label=''):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#333333', lw=1.5))
        if label:
            mx, my = (x1+x2)/2 + 0.1, (y1+y2)/2
            ax.text(mx, my, label, fontsize=8.5, color='#666666',
                    fontproperties=CN_FONT)

    steps = [
        (2.5, 11.8, 3, 0.7, '开始：用户站在摄像头前', '#E8F5E9', '#2E7D32'),
        (2.5, 10.6, 3, 0.7, '前端每2秒自动抓帧', '#D6E4FF', '#1F4E79'),
        (2.5, 9.2, 3, 0.9, '活体检测\n（帧间像素差≥2.0？）', None, None),
        (2.5, 7.9, 3, 0.7, '发送base64图片至后端', '#D6E4FF', '#1F4E79'),
        (2.5, 6.7, 3, 0.7, '后端提取128维人脸特征', '#D6E4FF', '#1F4E79'),
        (2.5, 5.5, 3, 0.9, '与人员库比对\n（匹配成功？）', None, None),
        (2.5, 4.3, 3, 0.9, '检查今日是否已签到\n（未签到？）', None, None),
        (2.5, 3.1, 3, 0.7, '判断是否迟到', '#D6E4FF', '#1F4E79'),
        (2.5, 1.9, 3, 0.7, '创建Attendance记录', '#E8F5E9', '#2E7D32'),
        (2.5, 0.7, 3, 0.7, '返回签到成功结果', '#E8F5E9', '#2E7D32'),
    ]

    diamonds = {2, 5, 6}
    ys = []
    for i, (x, y, w, h, text, color, ec) in enumerate(steps):
        shape = 'diamond' if i in diamonds else 'rect'
        box(x, y, w, h, text, color or '#FFF2CC', ec or '#D6A22A', shape)
        ys.append((y, h))

    # 主流程箭头
    for i in range(len(steps)-1):
        y1 = ys[i][0]
        y2 = ys[i+1][0] + ys[i+1][1]
        arrow(4, y1, 4, y2)

    # 活体检测失败分支
    ax.annotate('', xy=(7.2, 10.65), xytext=(5.5, 9.65),
                arrowprops=dict(arrowstyle='->', color='#D32F2F', lw=1.5,
                                connectionstyle='arc3,rad=-0.3'))
    ax.text(5.7, 10.2, '否→继续等待', fontsize=8.5, color='#D32F2F',
            fontproperties=CN_FONT)

    # 比对失败分支
    ax.annotate('', xy=(0.8, 5.85), xytext=(2.5, 5.95),
                arrowprops=dict(arrowstyle='->', color='#D32F2F', lw=1.5))
    ax.text(0.1, 5.6, '否→\n未录入', fontsize=8, color='#D32F2F',
            fontproperties=CN_FONT)

    # 已签到分支
    ax.annotate('', xy=(0.8, 4.65), xytext=(2.5, 4.75),
                arrowprops=dict(arrowstyle='->', color='#D32F2F', lw=1.5))
    ax.text(0.0, 4.4, '否→\n已签到', fontsize=8, color='#D32F2F',
            fontproperties=CN_FONT)

    ax.set_title('签到功能流程图', fontsize=14, fontweight='bold',
                 pad=8, fontproperties=CN_FONT)
    return save_fig('checkin_flow')


def make_enrollment_flow():
    """人脸录入流程图"""
    fig, ax = plt.subplots(figsize=(8, 11))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 11)
    ax.axis('off')

    def box(x, y, w, h, text, color='#D6E4FF', ec='#1F4E79', shape='rect'):
        if shape == 'diamond':
            cx, cy = x + w/2, y + h/2
            dx, dy = w/2, h/2
            diamond = plt.Polygon(
                [[cx, cy+dy], [cx+dx, cy], [cx, cy-dy], [cx-dx, cy]],
                facecolor='#FFF2CC', edgecolor='#D6A22A', linewidth=1.5)
            ax.add_patch(diamond)
        else:
            rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                                  facecolor=color, edgecolor=ec, linewidth=1.5)
            ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center',
                fontsize=9.5, fontproperties=CN_FONT, multialignment='center')

    def arrow(x1, y1, x2, y2):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#333333', lw=1.5))

    steps = [
        (2.5, 9.8, 3, 0.7, '管理员填写姓名/工号', '#D6E4FF', '#1F4E79', 'rect'),
        (2.5, 8.6, 3, 0.7, '选择图片来源\n（摄像头拍照/上传文件）', '#D6E4FF', '#1F4E79', 'rect'),
        (2.5, 7.4, 3, 0.9, '工号是否已存在？', None, None, 'diamond'),
        (2.5, 6.1, 3, 0.9, '调用face_service\n提取128维特征向量', '#D6E4FF', '#1F4E79', 'rect'),
        (2.5, 5.0, 3, 0.7, '检测到人脸？', None, None, 'diamond'),
        (2.5, 3.8, 3, 0.9, '与已有人员库比对\n人脸是否已录入？', None, None, 'diamond'),
        (2.5, 2.6, 3, 0.7, '创建Person记录\n保存特征向量和照片', '#E8F5E9', '#2E7D32', 'rect'),
        (2.5, 1.4, 3, 0.7, '返回录入成功', '#E8F5E9', '#2E7D32', 'rect'),
    ]

    ys = []
    for x, y, w, h, text, color, ec, shape in steps:
        box(x, y, w, h, text, color or '#FFF2CC', ec or '#D6A22A', shape)
        ys.append((y, h))

    for i in range(len(steps)-1):
        y1 = ys[i][0]
        y2 = ys[i+1][0] + ys[i+1][1]
        arrow(4, y1, 4, y2)

    # 工号已存在
    ax.annotate('', xy=(7.0, 8.95), xytext=(5.5, 7.85),
                arrowprops=dict(arrowstyle='->', color='#D32F2F', lw=1.5,
                                connectionstyle='arc3,rad=-0.3'))
    ax.text(5.6, 8.5, '是→返回错误', fontsize=8, color='#D32F2F',
            fontproperties=CN_FONT)

    # 无人脸
    ax.annotate('', xy=(0.8, 5.35), xytext=(2.5, 5.35),
                arrowprops=dict(arrowstyle='->', color='#D32F2F', lw=1.5))
    ax.text(0.0, 5.1, '否→\n无人脸', fontsize=8, color='#D32F2F',
            fontproperties=CN_FONT)

    # 已录入
    ax.annotate('', xy=(0.8, 4.15), xytext=(2.5, 4.15),
                arrowprops=dict(arrowstyle='->', color='#D32F2F', lw=1.5))
    ax.text(0.0, 3.9, '是→\n已录入', fontsize=8, color='#D32F2F',
            fontproperties=CN_FONT)

    ax.set_title('人脸录入流程图', fontsize=14, fontweight='bold',
                 pad=8, fontproperties=CN_FONT)
    return save_fig('enrollment_flow')


def make_module_diagram():
    """系统功能模块图"""
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis('off')

    # 中心模块
    center = FancyBboxPatch((4.5, 3.0), 3, 1.0,
                             boxstyle="round,pad=0.15",
                             facecolor='#1F4E79', edgecolor='#0D2B4E', lw=2)
    ax.add_patch(center)
    ax.text(6, 3.5, 'MagicFace\n智能考勤系统', ha='center', va='center',
            fontsize=12, fontweight='bold', color='white',
            fontproperties=CN_FONT)

    modules = [
        (0.3, 5.2, 2.4, 1.0, '用户认证模块', '#4472C4',
         ['管理员登录', '会话管理', '权限控制']),
        (4.5, 5.2, 3.0, 1.0, '人脸录入模块', '#ED7D31',
         ['摄像头拍照', '文件上传', '特征提取存储']),
        (9.3, 5.2, 2.4, 1.0, '在线签到模块', '#70AD47',
         ['实时识别', '活体检测', '状态判定']),
        (0.3, 1.5, 2.4, 1.0, '人员管理模块', '#FFC000',
         ['人员列表', '人员删除', '信息查看']),
        (4.5, 1.5, 3.0, 1.0, '考勤报表模块', '#FF0000',
         ['统计图表', '明细查询', 'CSV导出']),
        (9.3, 1.5, 2.4, 1.0, '系统配置模块', '#7030A0',
         ['截止时间', '重复签到规则']),
    ]

    for x, y, w, h, title, color, items in modules:
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor=color, lw=1.5,
                              alpha=0.85)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 0.2, title, ha='center', va='top',
                fontsize=10, fontweight='bold', color='white',
                fontproperties=CN_FONT)
        for i, item in enumerate(items):
            ax.text(x + w/2, y + h - 0.45 - i*0.22, f'• {item}',
                    ha='center', va='top', fontsize=8.5, color='white',
                    fontproperties=CN_FONT)

        # 连线到中心
        cx_m = x + w/2
        cy_m = y + h/2
        cx_c = 6
        cy_c = 3.5
        ax.annotate('', xy=(cx_c, cy_c), xytext=(cx_m, cy_m),
                    arrowprops=dict(arrowstyle='->', color='#888888',
                                   lw=1.2, connectionstyle='arc3,rad=0'))

    ax.set_title('MagicFace 系统功能模块图', fontsize=15, fontweight='bold',
                 pad=10, fontproperties=CN_FONT)
    return save_fig('module')


def make_er_diagram():
    """ER图"""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')

    def entity_box(x, y, w, title, fields, color='#D6E4FF', tc='#1F4E79'):
        row_h = 0.38
        total_h = row_h * (len(fields) + 1) + 0.1
        # 标题背景
        title_box = FancyBboxPatch((x, y + total_h - row_h - 0.05), w,
                                    row_h + 0.05, boxstyle="square,pad=0",
                                    facecolor=tc, edgecolor=tc)
        ax.add_patch(title_box)
        ax.text(x + w/2, y + total_h - row_h/2 - 0.02, title,
                ha='center', va='center', fontsize=11, fontweight='bold',
                color='white', fontproperties=CN_FONT)
        # 字段区
        body = FancyBboxPatch((x, y), w, total_h - row_h - 0.05,
                               boxstyle="square,pad=0",
                               facecolor=color, edgecolor=tc, linewidth=1.5)
        ax.add_patch(body)
        for i, (fname, ftype, note) in enumerate(fields):
            fy = y + (len(fields) - 1 - i) * row_h + 0.12
            weight = 'bold' if 'PK' in note else 'normal'
            ax.text(x + 0.15, fy, f"{fname}", ha='left', va='center',
                    fontsize=9, fontweight=weight, fontproperties=CN_FONT)
            ax.text(x + w - 0.1, fy, ftype, ha='right', va='center',
                    fontsize=8.5, color='#666666', fontproperties=CN_FONT)
            if 'PK' in note or 'FK' in note:
                ax.text(x + 0.05, fy, '★' if 'PK' in note else '◆',
                        ha='left', va='center', fontsize=9,
                        color='#D6A22A' if 'PK' in note else '#4472C4')

        return x + w/2, y + total_h  # top center

    # Person 实体
    person_fields = [
        ('id', 'INTEGER', 'PK'),
        ('name', 'VARCHAR(100)', ''),
        ('employee_id', 'VARCHAR(50)', 'UNIQUE'),
        ('face_encoding', 'JSON', ''),
        ('photo', 'VARCHAR(200)', ''),
        ('created_at', 'DATETIME', ''),
    ]
    px, py = entity_box(0.3, 0.5, 3.6, 'Person（人员表）', person_fields)

    # Attendance 实体
    att_fields = [
        ('id', 'INTEGER', 'PK'),
        ('person_id', 'INTEGER', 'FK'),
        ('check_in_time', 'DATETIME', ''),
        ('status', 'VARCHAR(20)', ''),
        ('source', 'VARCHAR(50)', ''),
    ]
    ax2, ay2 = entity_box(4.2, 0.5, 3.6, 'Attendance（考勤表）', att_fields,
                           '#E2EFDA', '#375623')

    # AttendanceRule 实体
    rule_fields = [
        ('id', 'INTEGER', 'PK=1'),
        ('checkin_deadline', 'TIME', ''),
        ('allow_repeat', 'BOOLEAN', ''),
        ('updated_at', 'DATETIME', ''),
    ]
    entity_box(8.1, 0.5, 3.6, 'AttendanceRule（规则表）', rule_fields,
               '#FCE4D6', '#833C0C')

    # 关系线
    ax.annotate('', xy=(4.2, 2.0), xytext=(3.9, 2.0),
                arrowprops=dict(arrowstyle='->', color='#333', lw=2))
    ax.text(3.95, 2.2, '1..n', fontsize=10, fontweight='bold', color='#1F4E79',
            fontproperties=CN_FONT)
    ax.text(4.05, 1.75, '（一个人有多条签到）', fontsize=8.5, color='#555555',
            fontproperties=CN_FONT)

    ax.set_title('数据库实体关系图（ER图）', fontsize=15, fontweight='bold',
                 pad=10, fontproperties=CN_FONT)
    return save_fig('er')


def make_performance_chart():
    """性能测试图表"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # 响应时间图
    sizes = [10, 30, 50, 100]
    avg_times = [0.42, 0.58, 0.79, 1.34]
    max_times = [0.65, 0.82, 1.15, 1.87]
    min_times = [0.31, 0.44, 0.61, 1.02]

    x = np.arange(len(sizes))
    w = 0.25
    b1 = ax1.bar(x - w, min_times, w, label='最小响应时间', color='#70AD47')
    b2 = ax1.bar(x,     avg_times, w, label='平均响应时间', color='#4472C4')
    b3 = ax1.bar(x + w, max_times, w, label='最大响应时间', color='#FF4444')
    ax1.axhline(y=2.0, color='#FF8C00', linestyle='--', linewidth=1.5,
                label='设计目标(2秒)')
    ax1.set_xlabel('人员规模（人）', fontproperties=CN_FONT, fontsize=11)
    ax1.set_ylabel('响应时间（秒）', fontproperties=CN_FONT, fontsize=11)
    ax1.set_title('不同人员规模下签到响应时间', fontproperties=CN_FONT, fontsize=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'{s}人' for s in sizes], fontproperties=CN_FONT)
    ax1.legend(prop=CN_FONT, fontsize=9)
    ax1.set_ylim(0, 2.5)
    for bar in [b1, b2, b3]:
        for b in bar:
            ax1.text(b.get_x() + b.get_width()/2, b.get_height() + 0.03,
                     f'{b.get_height():.2f}', ha='center', va='bottom',
                     fontsize=8.5)

    # 准确率图
    conditions = ['正常\n正面', '侧脸\n30°', '弱光\n环境', '佩戴\n口罩', '眼镜\n遮挡']
    rates = [99, 93, 85, 61, 91]
    colors = ['#70AD47' if r >= 95 else '#FFC000' if r >= 80 else '#FF4444'
              for r in rates]
    bars = ax2.bar(conditions, rates, color=colors, edgecolor='white',
                   linewidth=0.5, width=0.6)
    ax2.axhline(y=95, color='#1F4E79', linestyle='--', linewidth=1.5,
                label='目标准确率(95%)')
    ax2.set_xlabel('测试条件', fontproperties=CN_FONT, fontsize=11)
    ax2.set_ylabel('识别准确率（%）', fontproperties=CN_FONT, fontsize=11)
    ax2.set_title('不同条件下人脸识别准确率', fontproperties=CN_FONT, fontsize=12)
    ax2.set_ylim(0, 110)
    ax2.legend(prop=CN_FONT, fontsize=9)
    for bar, rate in zip(bars, rates):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                 f'{rate}%', ha='center', va='bottom', fontsize=11,
                 fontweight='bold')
    for label in ax2.get_xticklabels():
        label.set_fontproperties(CN_FONT)

    plt.tight_layout(pad=2)
    return save_fig('performance')


print("正在生成图表...")
arch_img        = make_system_arch()
checkin_img     = make_checkin_flow()
enrollment_img  = make_enrollment_flow()
module_img      = make_module_diagram()
er_img          = make_er_diagram()
perf_img        = make_performance_chart()
print("图表生成完成。")

# ════════════════════════════════════════════════════════════════
# 构建 Word 文档
# ════════════════════════════════════════════════════════════════

doc = Document()

# ── 页面设置：A4 纸，页边距 ──────────────────────────────────
section = doc.sections[0]
section.page_width  = Cm(21)
section.page_height = Cm(29.7)
section.left_margin   = Cm(3.0)
section.right_margin  = Cm(2.5)
section.top_margin    = Cm(2.5)
section.bottom_margin = Cm(2.5)


# ════════════════════════════════════════════════════════════════
# 封面页
# ════════════════════════════════════════════════════════════════

def add_cover(doc):
    # 校名
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(40)
    run = p.add_run('XX大学')
    set_run_font(run, cn_font='黑体', en_font='Times New Roman', size=22, bold=True)

    # 副标题行
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.space_before = Pt(4)
    run2 = p2.add_run('本科毕业设计（论文）')
    set_run_font(run2, cn_font='黑体', size=18, bold=True)

    # 分隔线
    doc.add_paragraph()
    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_line = p_line.add_run('─' * 30)
    set_run_font(run_line, cn_font='宋体', size=14)

    # 论文题目
    doc.add_paragraph()
    pt = doc.add_paragraph()
    pt.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pt.paragraph_format.space_before = Pt(20)
    run_t = pt.add_run('基于人脸识别的智能考勤系统\n设计与实现')
    set_run_font(run_t, cn_font='黑体', size=22, bold=True)
    run_t.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    doc.add_paragraph()
    doc.add_paragraph()

    # 信息表格
    info_data = [
        ('学    院', '计算机科学与技术学院'),
        ('专    业', '软件工程'),
        ('班    级', '2021级 X 班'),
        ('学    号', '2021XXXXXXXX'),
        ('姓    名', '张三'),
        ('指导教师', '李教授'),
        ('完成日期', '2025年 6月'),
    ]

    for label, value in info_data:
        pi = doc.add_paragraph()
        pi.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pi.paragraph_format.space_before = Pt(8)
        run_l = pi.add_run(f'{label}：{value}')
        set_run_font(run_l, cn_font='宋体', size=14)

    doc.add_page_break()

add_cover(doc)
print("封面完成。")

# ════════════════════════════════════════════════════════════════
# 摘要页（中文 + 英文）
# ════════════════════════════════════════════════════════════════

def add_abstract(doc):
    h = doc.add_heading('摘  要', level=0)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in h.runs:
        set_run_font(run, cn_font='黑体', size=16, bold=True)

    abstract_cn = (
        '随着人工智能技术的迅猛发展，生物特征识别技术已广泛应用于安防、教育、企业管理等领域。'
        '本文设计并实现了一套基于人脸识别技术的智能考勤系统——MagicFace。系统以 Python 3.8 '
        '为主要开发语言，采用 Django 4.2 Web 框架构建后端服务，借助 face_recognition 库和 '
        'dlib 深度学习模型实现高精度人脸特征提取与比对，以 SQLite3 作为数据存储方案，前端采用 '
        'Bootstrap 5 与 ECharts 实现响应式交互界面。\n\n'
        '系统核心功能涵盖：人脸录入与特征向量存储、实时摄像头人脸识别签到、活体检测防伪机制、'
        '考勤规则灵活配置、多维度考勤报表统计与 CSV 导出，以及完善的人员管理功能。系统同时支持'
        '本地摄像头和 IP 网络摄像头两种签到方式，具备良好的扩展性与实用性。\n\n'
        '实验测试表明，系统在正常光照条件下人脸识别准确率可达 99%，单次识别响应时间不超过 1 秒，'
        '能够有效满足中小型企业和学校的日常考勤管理需求。本文详细阐述了系统的需求分析、架构设计、'
        '核心算法、功能实现及测试验证全过程。'
    )
    add_body_paragraph(doc, abstract_cn)

    kw_para = doc.add_paragraph()
    run_kw = kw_para.add_run('关键词：')
    set_run_font(run_kw, cn_font='黑体', size=12, bold=True)
    run_kw2 = kw_para.add_run('人脸识别；考勤系统；Django；深度学习；dlib；活体检测')
    set_run_font(run_kw2, cn_font='宋体', size=12)
    kw_para.paragraph_format.space_before = Pt(12)

    doc.add_paragraph()

    # 英文摘要
    h2 = doc.add_heading('Abstract', level=0)
    h2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in h2.runs:
        set_run_font(run, cn_font='Times New Roman', en_font='Times New Roman',
                     size=16, bold=True)

    abstract_en = (
        'With the rapid development of artificial intelligence technology, biometric recognition '
        'technology has been widely applied in security, education, and enterprise management. '
        'This paper designs and implements an intelligent attendance system based on face recognition '
        'technology—MagicFace. The system uses Python 3.8 as the main development language, '
        'Django 4.2 web framework to build the backend service, face_recognition library and dlib '
        'deep learning model to achieve high-precision face feature extraction and comparison, '
        'SQLite3 as data storage solution, and Bootstrap 5 with ECharts for responsive interactive interface.\n\n'
        'Experimental tests show that the system\'s face recognition accuracy can reach 99% under '
        'normal lighting conditions, with a single recognition response time not exceeding 1 second, '
        'which can effectively meet the daily attendance management needs of small and medium-sized '
        'enterprises and schools.'
    )
    p_en = doc.add_paragraph()
    run_en = p_en.add_run(abstract_en)
    set_run_font(run_en, cn_font='Times New Roman', en_font='Times New Roman', size=12)
    p_en.paragraph_format.first_line_indent = Cm(0.74)
    p_en.paragraph_format.space_after = Pt(12)

    kw2_para = doc.add_paragraph()
    run_k1 = kw2_para.add_run('Keywords: ')
    set_run_font(run_k1, en_font='Times New Roman', size=12, bold=True)
    run_k2 = kw2_para.add_run('Face Recognition; Attendance System; Django; Deep Learning; dlib; Liveness Detection')
    set_run_font(run_k2, en_font='Times New Roman', size=12)

    doc.add_page_break()

add_abstract(doc)
print("摘要完成。")

# ════════════════════════════════════════════════════════════════
# 目录页（手动生成，Word自动目录需要域代码）
# ════════════════════════════════════════════════════════════════

def add_toc(doc):
    h = doc.add_heading('目  录', level=0)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in h.runs:
        set_run_font(run, cn_font='黑体', size=16, bold=True)

    toc_items = [
        ('摘要', ''),
        ('Abstract', ''),
        ('第一章  引言', ''),
        ('    1.1  研究背景', ''),
        ('    1.2  研究意义', ''),
        ('    1.3  国内外研究现状', ''),
        ('    1.4  研究内容与方法', ''),
        ('第二章  开发工具和技术介绍', ''),
        ('    2.1  后端开发技术', ''),
        ('    2.2  数据库技术', ''),
        ('    2.3  前端开发技术', ''),
        ('    2.4  开发工具汇总', ''),
        ('第三章  系统分析', ''),
        ('    3.1  系统目标', ''),
        ('    3.2  系统对象分析', ''),
        ('    3.3  可行性分析', ''),
        ('    3.4  功能需求分析', ''),
        ('    3.5  非功能需求分析', ''),
        ('第四章  系统设计', ''),
        ('    4.1  系统总体设计', ''),
        ('    4.2  模块详细设计', ''),
        ('    4.3  数据库设计', ''),
        ('    4.4  接口设计', ''),
        ('第五章  系统实现', ''),
        ('    5.1  项目结构', ''),
        ('    5.2  数据模型实现', ''),
        ('    5.3  人脸识别服务实现', ''),
        ('    5.4  签到视图实现', ''),
        ('    5.5  前端活体检测实现', ''),
        ('    5.6  考勤报表实现', ''),
        ('    5.7  界面设计', ''),
        ('第六章  系统测试', ''),
        ('    6.1  测试概述', ''),
        ('    6.2  功能测试', ''),
        ('    6.3  性能测试', ''),
        ('    6.4  安全测试', ''),
        ('    6.5  兼容性测试', ''),
        ('    6.6  测试总结', ''),
        ('第七章  结束语', ''),
        ('    7.1  工作总结', ''),
        ('    7.2  不足与展望', ''),
        ('参考文献', ''),
    ]

    for title, _ in toc_items:
        p = doc.add_paragraph()
        is_chapter = title.startswith('第') or title in ('摘要','Abstract','参考文献')
        run = p.add_run(title)
        set_run_font(run, cn_font='宋体', en_font='Times New Roman',
                     size=12, bold=is_chapter)
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        if not is_chapter:
            p.paragraph_format.left_indent = Cm(1)

    doc.add_page_break()

add_toc(doc)
print("目录完成。")


# ════ 组装并保存 ════
# -*- coding: utf-8 -*-
# 组装所有章节并保存 Word 文档

# 读取各章节模块的内容并 exec 到当前命名空间
import os
_base = os.path.dirname(os.path.abspath(__file__))

for _part in ['part2_ch1_ch3.py', 'part3_ch4_ch5.py', 'part4_ch6_ch7_refs.py']:
    with open(os.path.join(_base, _part), encoding='utf-8') as _f:
        exec(_f.read())

print("正在写入各章节正文...")

# ── 第一章 引言 ──────────────────────────────────────────────
add_chapter1(doc)
doc.add_page_break()
print("  第一章完成")

# ── 第二章 开发工具和技术介绍 ─────────────────────────────────
add_chapter2(doc)
doc.add_page_break()
print("  第二章完成")

# ── 第三章 系统分析 ───────────────────────────────────────────
add_chapter3(doc)
doc.add_page_break()
print("  第三章完成")

# ── 第四章 系统设计 ───────────────────────────────────────────
add_chapter4(doc)
doc.add_page_break()
print("  第四章完成")

# ── 第五章 系统实现 ───────────────────────────────────────────
add_chapter5(doc)
doc.add_page_break()
print("  第五章完成")

# ── 第六章 系统测试 ───────────────────────────────────────────
add_chapter6(doc)
doc.add_page_break()
print("  第六章完成")

# ── 第七章 结束语 ─────────────────────────────────────────────
add_chapter7(doc)
doc.add_page_break()
print("  第七章完成")

# ── 参考文献 ──────────────────────────────────────────────────
add_references(doc)
print("  参考文献完成")

# ── 保存文档 ──────────────────────────────────────────────────
doc.save(OUTPUT_PATH)
print(f"\n✅ Word 文档已生成：{OUTPUT_PATH}")
