# MagicFace — 基于人脸识别的智能考勤系统

> 基于 Python 3.8 + Django 4.2 + face_recognition + dlib 的全栈人脸识别考勤管理系统，支持活体检测、多摄像头接入、考勤报表与 CSV 导出。

---

## 功能特性

| 模块 | 说明 |
|------|------|
| **人脸录入** | 管理员填写姓名/工号，通过摄像头拍照或上传本地图片完成录入；自动提取 128 维特征向量；防重复工号及重复人脸校验 |
| **在线签到** | 网页摄像头实时识别，每 2 秒自动扫描；基于帧间像素差的活体检测，防止照片欺骗；根据规则自动判断正常/迟到 |
| **IP 摄像头** | 支持手机 IP Webcam 应用作为摄像头，服务端代理解决跨域问题 |
| **人员管理** | 查看/删除已录入人员（含照片、工号、录入时间），删除时级联清除考勤记录 |
| **考勤报表** | 按日/周签到人次柱状图、出勤状态环形饼图（ECharts）、分页明细表格、CSV 导出 |
| **考勤规则** | 可配置签到截止时间、是否允许重复签到，修改后立即生效 |
| **权限控制** | 签到页公开访问；录入、管理、报表等功能需管理员登录 |

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Python 3.8 · Django 4.2.29 (LTS) |
| 人脸识别 | face_recognition 1.3.0 · dlib 20.0.0 |
| 图像处理 | OpenCV 4.13 · Pillow 10.4 · NumPy 1.24 |
| 数据库 | SQLite3（可无缝迁移至 PostgreSQL / MySQL） |
| 前端 | Bootstrap 5.3.2 · Apache ECharts 5 · WebRTC |

---

## 目录结构

```
MagicFace/
├── magicface/               # Django 项目配置（settings / urls / wsgi）
├── attendance/              # 核心业务应用
│   ├── models.py            # Person · Attendance · AttendanceRule
│   ├── views.py             # 14 个视图函数
│   ├── urls.py              # 路由配置
│   └── services/
│       └── face_service.py  # 人脸特征提取 & 比对
├── templates/               # HTML 模板（base / home / checkin / enrollment …）
├── static/js/               # camera.js · enrollment.js · report.js
├── media/                   # 用户上传文件（运行时生成）
├── thesis/                  # 毕业设计论文（Markdown + Word）
├── requirements.txt
└── manage.py
```

---

## 快速开始

### 1. 环境准备

```bash
# Linux 需先安装编译依赖（dlib 需要 cmake）
sudo apt install -y cmake build-essential libopenblas-dev liblapack-dev

# 创建并激活虚拟环境
python3.8 -m venv .venv
source .venv/bin/activate       # Linux / macOS
# .venv\Scripts\activate        # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
# 或使用 uv（更快）：
# uv pip install -r requirements.txt
```

> dlib 编译耗时较长（5~15 分钟），请耐心等待。

### 3. 初始化数据库

```bash
python manage.py migrate
python manage.py createsuperuser   # 创建管理员账号
```

### 4. 启动服务

```bash
python manage.py runserver
```

浏览器访问 **http://127.0.0.1:8000/**

---

## 使用流程

```
管理员登录
    │
    ├─ 【人脸录入】填写姓名/工号 → 摄像头拍照或上传照片 → 提交
    │
    ├─ 【在线签到】站在摄像头前 → 系统自动识别 → 显示签到结果
    │
    ├─ 【人员管理】查看已录入人员列表，可删除人员
    │
    ├─ 【考勤报表】查看统计图表，按需导出 CSV
    │
    └─ 【考勤设置】配置签到截止时间和重复签到规则
```

- **签到页（公开）**：http://127.0.0.1:8000/checkin/
- **管理后台**：http://127.0.0.1:8000/admin/

---

## IP 摄像头配置

手机安装 [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam) 后，在签到页切换为「IP摄像头」模式，填入手机显示的 IP 地址即可。服务端通过 `/checkin/frame/` 代理转发，解决浏览器跨域限制。

---

## 数据模型

```
Person          Attendance          AttendanceRule（单例）
─────────       ──────────────      ────────────────────
id              id                  id = 1
name            person_id (FK)      checkin_deadline
employee_id     check_in_time       allow_repeat
face_encoding   status              updated_at
photo           source
created_at
```

---

## 注意事项

- **光照**：建议在光线充足的环境下使用，弱光会降低识别准确率
- **正面入镜**：录入和签到时请保持正面朝向摄像头，侧脸会影响识别效果
- **iOS Safari**：摄像头访问需要 HTTPS，本地开发可通过局域网 IP + 端口访问
- **生产部署**：建议迁移至 PostgreSQL，并使用 Nginx + Gunicorn 部署

---

## 论文

本项目附有完整毕业设计论文，位于 `thesis/` 目录：

- `thesis.md` — Markdown 格式论文原文
- `MagicFace毕业设计论文.docx` — 标准 Word 格式论文（含封面、目录、图表）

---

## License

MIT
