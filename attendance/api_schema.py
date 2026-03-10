# -*- coding: utf-8 -*-
"""
MagicFace OpenAPI 3.0 规范
访问 /api/docs/ 查看 Swagger UI
访问 /api/schema.json 获取原始 JSON
"""

SCHEMA = {
    "openapi": "3.0.3",
    "info": {
        "title": "MagicFace 智能考勤系统 API",
        "description": (
            "基于人脸识别的考勤管理系统后端接口文档。\n\n"
            "**认证说明**：标注 🔒 的接口需要管理员登录（Session Cookie），"
            "未登录时返回 302 重定向至 `/login/`。\n\n"
            "**CSRF 说明**：所有 POST 请求需携带 `X-CSRFToken` 请求头，"
            "Token 值从 Cookie `csrftoken` 中读取。"
        ),
        "version": "1.0.0",
        "contact": {"name": "MagicFace", "url": "https://github.com/your/magicface"},
        "license": {"name": "MIT"},
    },
    "servers": [{"url": "http://127.0.0.1:8000", "description": "本地开发服务器"}],
    "tags": [
        {"name": "人脸录入", "description": "人员注册与人脸特征提取"},
        {"name": "在线签到", "description": "人脸识别签到（无需登录）"},
        {"name": "人员管理", "description": "已录入人员的查看与删除 🔒"},
        {"name": "考勤报表", "description": "统计图表、明细查询、数据导出 🔒"},
        {"name": "系统配置", "description": "考勤规则配置 🔒"},
    ],

    # ─── Components ──────────────────────────────────────────────────────────
    "components": {
        "schemas": {
            "BaseResponse": {
                "type": "object",
                "properties": {
                    "ok": {"type": "boolean", "description": "是否成功"},
                    "msg": {"type": "string", "description": "提示信息"},
                },
                "required": ["ok", "msg"],
            },
            "CheckinSuccess": {
                "allOf": [{"$ref": "#/components/schemas/BaseResponse"}],
                "properties": {
                    "name": {"type": "string", "example": "张三"},
                    "employee_id": {"type": "string", "example": "2021001"},
                    "status": {"type": "string", "enum": ["normal", "late"], "description": "normal=正常，late=迟到"},
                    "status_label": {"type": "string", "example": "正常"},
                    "photo_url": {"type": "string", "format": "uri", "example": "/media/persons/zhangsan.jpg"},
                    "check_in_time": {"type": "string", "format": "date-time", "example": "2024-03-11 09:00:01"},
                },
            },
            "EnrollSuccess": {
                "allOf": [{"$ref": "#/components/schemas/BaseResponse"}],
                "properties": {
                    "id": {"type": "integer", "description": "新建人员的数据库 ID", "example": 5},
                },
            },
            "AttendanceRecord": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "example": "张三"},
                    "employee_id": {"type": "string", "example": "2021001"},
                    "check_in_time": {"type": "string", "example": "2024-03-11 09:01:23"},
                    "status": {"type": "string", "enum": ["normal", "late"]},
                    "status_label": {"type": "string", "example": "正常"},
                    "source": {"type": "string", "example": "web_camera"},
                },
            },
            "StatsItem": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "example": "2024-03-11"},
                    "count": {"type": "integer", "example": 12},
                },
            },
        },
        "parameters": {
            "DaysQuery": {
                "name": "days",
                "in": "query",
                "description": "统计最近 N 天，默认 14",
                "required": False,
                "schema": {"type": "integer", "default": 14, "minimum": 1, "maximum": 365},
            },
            "PageQuery": {
                "name": "page",
                "in": "query",
                "description": "页码（从 1 开始）",
                "schema": {"type": "integer", "default": 1, "minimum": 1},
            },
            "PageSizeQuery": {
                "name": "page_size",
                "in": "query",
                "description": "每页条数（1-100）",
                "schema": {"type": "integer", "default": 10, "minimum": 1, "maximum": 100},
            },
        },
        "securitySchemes": {
            "sessionAuth": {
                "type": "apiKey",
                "in": "cookie",
                "name": "sessionid",
                "description": "Django Session Cookie，通过 `/login/` 登录后自动设置",
            },
            "csrfToken": {
                "type": "apiKey",
                "in": "header",
                "name": "X-CSRFToken",
                "description": "CSRF Token，从 Cookie `csrftoken` 中读取",
            },
        },
    },

    # ─── Paths ───────────────────────────────────────────────────────────────
    "paths": {

        # ── 人脸录入 ────────────────────────────────────────────────────────
        "/enrollment/upload/": {
            "post": {
                "tags": ["人脸录入"],
                "summary": "提交人脸录入",
                "description": (
                    "🔒 **需要管理员登录**\n\n"
                    "支持两种提交方式：\n"
                    "1. **表单文件上传**（`multipart/form-data`）：上传本地照片文件\n"
                    "2. **摄像头拍照**（`application/json`）：提交 base64 编码图片\n\n"
                    "系统自动提取 128 维人脸特征向量并存储。提交前会校验：\n"
                    "- 工号唯一性（重复工号报错）\n"
                    "- 人脸唯一性（同一张脸已录入则报错）"
                ),
                "security": [{"sessionAuth": [], "csrfToken": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "required": ["name", "employee_id", "photo"],
                                "properties": {
                                    "name": {"type": "string", "description": "姓名", "example": "张三"},
                                    "employee_id": {"type": "string", "description": "工号/学号", "example": "2021001"},
                                    "photo": {"type": "string", "format": "binary", "description": "照片文件（JPG/PNG）"},
                                },
                            }
                        },
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["name", "employee_id", "image"],
                                "properties": {
                                    "name": {"type": "string", "example": "张三"},
                                    "employee_id": {"type": "string", "example": "2021001"},
                                    "image": {
                                        "type": "string",
                                        "description": "base64 编码图片（可含 data:image/jpeg;base64, 前缀）",
                                        "example": "data:image/jpeg;base64,/9j/4AAQ...",
                                    },
                                },
                            }
                        },
                    },
                },
                "responses": {
                    "200": {
                        "description": "录入结果",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/EnrollSuccess"},
                                "examples": {
                                    "success": {
                                        "summary": "录入成功",
                                        "value": {"ok": True, "msg": "张三 录入成功", "id": 5},
                                    },
                                    "dup_id": {
                                        "summary": "工号已存在",
                                        "value": {"ok": False, "msg": "工号 2021001 已存在"},
                                    },
                                    "dup_face": {
                                        "summary": "人脸已录入",
                                        "value": {"ok": False, "msg": "该人脸已被 李四（2021002）录入，请勿重复录入"},
                                    },
                                    "no_face": {
                                        "summary": "未检测到人脸",
                                        "value": {"ok": False, "msg": "未检测到人脸，请上传清晰正面照"},
                                    },
                                },
                            }
                        },
                    },
                    "302": {"description": "未登录，重定向至 /login/"},
                },
            }
        },

        # ── 在线签到 ────────────────────────────────────────────────────────
        "/checkin/submit/": {
            "post": {
                "tags": ["在线签到"],
                "summary": "提交人脸签到",
                "description": (
                    "**无需登录**，接收摄像头拍摄的 base64 图片，进行人脸识别并创建签到记录。\n\n"
                    "处理流程：\n"
                    "1. 解码 base64 图片\n"
                    "2. 提取 128 维人脸特征\n"
                    "3. 与人员库全量比对\n"
                    "4. 检查今日是否已签到（受考勤规则控制）\n"
                    "5. 判断是否迟到（与签到截止时间比较）\n"
                    "6. 创建 Attendance 记录并返回结果"
                ),
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["image"],
                                "properties": {
                                    "image": {
                                        "type": "string",
                                        "description": "base64 编码图片（可含 data URI 前缀）",
                                        "example": "data:image/jpeg;base64,/9j/4AAQ...",
                                    }
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "签到结果",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CheckinSuccess"},
                                "examples": {
                                    "success_normal": {
                                        "summary": "签到成功（正常）",
                                        "value": {
                                            "ok": True, "msg": "签到成功",
                                            "name": "张三", "employee_id": "2021001",
                                            "status": "normal", "status_label": "正常",
                                            "photo_url": "/media/persons/zhangsan.jpg",
                                            "check_in_time": "2024-03-11 08:55:30",
                                        },
                                    },
                                    "success_late": {
                                        "summary": "签到成功（迟到）",
                                        "value": {
                                            "ok": True, "msg": "签到成功（迟到）",
                                            "name": "张三", "employee_id": "2021001",
                                            "status": "late", "status_label": "迟到",
                                            "photo_url": "/media/persons/zhangsan.jpg",
                                            "check_in_time": "2024-03-11 09:30:00",
                                        },
                                    },
                                    "already_checked": {
                                        "summary": "今日已签到",
                                        "value": {
                                            "ok": False, "msg": "张三 今日已签到，无需重复签到",
                                            "name": "张三", "employee_id": "2021001",
                                        },
                                    },
                                    "no_face": {
                                        "summary": "未检测到人脸",
                                        "value": {"ok": False, "msg": "未检测到人脸，请正对摄像头"},
                                    },
                                    "not_found": {
                                        "summary": "未匹配到人员",
                                        "value": {"ok": False, "msg": "未匹配到已录入人员"},
                                    },
                                },
                            }
                        },
                    }
                },
            }
        },

        "/checkin/frame/": {
            "get": {
                "tags": ["在线签到"],
                "summary": "IP 摄像头快照代理",
                "description": "代理获取 IP Webcam 快照图片，解决浏览器跨域（CORS）限制。",
                "parameters": [
                    {
                        "name": "url",
                        "in": "query",
                        "required": True,
                        "description": "IP 摄像头快照地址，如 `http://192.168.1.100:8080/shot.jpg`",
                        "schema": {"type": "string", "format": "uri"},
                    }
                ],
                "responses": {
                    "200": {"description": "JPEG 图片数据", "content": {"image/jpeg": {}}},
                    "400": {"description": "URL 参数缺失或格式非法"},
                    "502": {"description": "代理请求失败（摄像头离线）"},
                },
            }
        },

        # ── 人员管理 ────────────────────────────────────────────────────────
        "/api/person/{pk}/delete/": {
            "post": {
                "tags": ["人员管理"],
                "summary": "删除人员",
                "description": "🔒 删除指定人员及其全部关联考勤记录（级联删除）。",
                "security": [{"sessionAuth": [], "csrfToken": []}],
                "parameters": [
                    {
                        "name": "pk",
                        "in": "path",
                        "required": True,
                        "description": "人员数据库 ID",
                        "schema": {"type": "integer"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "删除结果",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/BaseResponse"},
                                "examples": {
                                    "success": {"value": {"ok": True, "msg": "已删除"}},
                                    "not_found": {"value": {"ok": False, "msg": "人员不存在"}},
                                },
                            }
                        },
                    },
                    "302": {"description": "未登录"},
                },
            }
        },

        # ── 考勤报表 ────────────────────────────────────────────────────────
        "/api/attendance/stats/": {
            "get": {
                "tags": ["考勤报表"],
                "summary": "考勤统计（图表数据）",
                "description": "🔒 按日或周聚合签到人次，用于 ECharts 柱状图渲染。",
                "security": [{"sessionAuth": []}],
                "parameters": [
                    {
                        "name": "period",
                        "in": "query",
                        "description": "聚合粒度：`day`=按天，`week`=按周",
                        "schema": {"type": "string", "enum": ["day", "week"], "default": "day"},
                    },
                    {"$ref": "#/components/parameters/DaysQuery"},
                ],
                "responses": {
                    "200": {
                        "description": "统计数据",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "ok": {"type": "boolean"},
                                        "data": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/StatsItem"},
                                        },
                                    },
                                },
                                "example": {
                                    "ok": True,
                                    "data": [
                                        {"date": "2024-03-09", "count": 10},
                                        {"date": "2024-03-10", "count": 13},
                                        {"date": "2024-03-11", "count": 8},
                                    ],
                                },
                            }
                        },
                    }
                },
            }
        },

        "/api/attendance/detail/": {
            "get": {
                "tags": ["考勤报表"],
                "summary": "考勤明细（分页）",
                "description": "🔒 获取指定时间范围内的考勤明细列表，支持分页。",
                "security": [{"sessionAuth": []}],
                "parameters": [
                    {"$ref": "#/components/parameters/DaysQuery"},
                    {"$ref": "#/components/parameters/PageQuery"},
                    {"$ref": "#/components/parameters/PageSizeQuery"},
                ],
                "responses": {
                    "200": {
                        "description": "分页考勤明细",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "ok": {"type": "boolean"},
                                        "data": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/AttendanceRecord"},
                                        },
                                        "total": {"type": "integer", "example": 56},
                                        "page": {"type": "integer", "example": 1},
                                        "page_size": {"type": "integer", "example": 10},
                                        "total_pages": {"type": "integer", "example": 6},
                                    },
                                }
                            }
                        },
                    }
                },
            }
        },

        "/api/attendance/summary/": {
            "get": {
                "tags": ["考勤报表"],
                "summary": "出勤概览",
                "description": "🔒 返回正常签到、迟到、缺勤人数，用于饼图渲染。",
                "security": [{"sessionAuth": []}],
                "parameters": [{"$ref": "#/components/parameters/DaysQuery"}],
                "responses": {
                    "200": {
                        "description": "出勤概览数据",
                        "content": {
                            "application/json": {
                                "example": {
                                    "ok": True,
                                    "total_persons": 30,
                                    "normal": 22,
                                    "late": 4,
                                    "checked_persons": 26,
                                    "absent_persons": 4,
                                }
                            }
                        },
                    }
                },
            }
        },

        "/api/attendance/export/": {
            "get": {
                "tags": ["考勤报表"],
                "summary": "导出考勤明细 CSV",
                "description": "🔒 导出指定天数内的全部考勤记录，文件编码 UTF-8 with BOM（Excel 兼容）。",
                "security": [{"sessionAuth": []}],
                "parameters": [{"$ref": "#/components/parameters/DaysQuery"}],
                "responses": {
                    "200": {
                        "description": "CSV 文件下载",
                        "content": {"text/csv": {}},
                        "headers": {
                            "Content-Disposition": {
                                "schema": {"type": "string"},
                                "example": 'attachment; filename="attendance_20240301_20240311.csv"',
                            }
                        },
                    }
                },
            }
        },

        # ── 系统配置 ────────────────────────────────────────────────────────
        "/api/settings/save/": {
            "post": {
                "tags": ["系统配置"],
                "summary": "保存考勤规则",
                "description": "🔒 更新全局考勤规则（单例，修改后立即生效）。",
                "security": [{"sessionAuth": [], "csrfToken": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["checkin_deadline"],
                                "properties": {
                                    "checkin_deadline": {
                                        "type": "string",
                                        "pattern": r"^\d{2}:\d{2}$",
                                        "description": "签到截止时间，格式 HH:MM",
                                        "example": "09:00",
                                    },
                                    "allow_repeat": {
                                        "type": "boolean",
                                        "description": "是否允许同一人当天重复签到",
                                        "default": False,
                                    },
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "保存结果",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/BaseResponse"},
                                "examples": {
                                    "success": {"value": {"ok": True, "msg": "保存成功"}},
                                    "invalid_time": {"value": {"ok": False, "msg": "时间格式错误，请使用 HH:MM"}},
                                },
                            }
                        },
                    }
                },
            }
        },
    },
}
