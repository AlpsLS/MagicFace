# MagicFace - 人脸考勤/签到管理系统

基于 Python 3.8 + Django + face_recognition + OpenCV 的人脸识别考勤系统。

## 功能

- **人脸录入**：管理员上传员工/学生照片，系统提取 128 维特征向量存入数据库
- **在线签到**：网页摄像头拍照，后端匹配人脸并记录签到时间
- **考勤报表**：每日/每周出勤统计，ECharts 图表展示

## 环境要求

- Python 3.8
- venv

## 安装

```bash
# 使用 venv 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS

# 安装依赖
uv pip install -r requirements.txt
# 或 pip install -r requirements.txt
```

> 注意：`face_recognition` 依赖 `dlib`，Linux 需安装 `cmake`、`build-essential` 等编译工具。

## 运行

```bash
python manage.py migrate
python manage.py createsuperuser   # 创建管理员（可选）
python manage.py runserver
```

访问 http://127.0.0.1:8000/

## 使用说明

1. **人脸录入**：填写姓名、工号，上传清晰正面照，系统自动提取特征
2. **在线签到**：允许摄像头权限后，点击「拍照签到」进行人脸识别
3. **考勤报表**：查看按日/按周的签到人次统计
4. **管理后台**：http://127.0.0.1:8000/admin/ 管理人员与考勤记录
