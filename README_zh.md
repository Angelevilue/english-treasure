# 英语宝典 (English Treasure)

> 覆盖全学段的英语学习 App — 单词速记 · 语法分析 · 跟读语感，从小学到考研一站搞定。

## ✨ 核心功能

| 模块 | 功能 | 状态 |
|---|---|---|
| **单词速记** | SM-2 间隔重复算法，闪卡翻面学习，5 个词库（小学→雅思）| ✅ 可用 |
| **语法分析** | DeepSeek + LangChain 智能语法分析，结构化标注（主谓宾/从句/时态）| ✅ 可用 |
| **跟读语感** | KTV 式逐句跟读，手动导航，讯飞语音评测多维度打分 | ✅ UI 就绪 · 🟡 讯飞认证待修复 |
| **用户系统** | 手机号注册/登录，JWT 认证，学段切换（小学→海思）| ✅ 可用 |

## 🛠 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Flutter 3.44 (Dart) · Riverpod · GoRouter |
| 后端 | Python FastAPI (异步) |
| LLM 编排 | LangChain ≥1.0 + LangGraph ≥1.0 |
| 大模型 | DeepSeek v4 Flash（思考模式已关闭） |
| 语音评测 | 讯飞云端语音评测 API (ISE) |
| 数据库 | PostgreSQL 16 (端口 5433) + Redis 7 (端口 6380) |
| 本地存储 | SQLite (sqflite) |
| ORM | SQLAlchemy 2.0 (异步) |
| 对象存储 | MinIO (端口 9002) |
| 部署 | Docker + Nginx |
| 测试 | pytest (6 个 auth 用例全部通过) |

## 📁 项目结构

```
english-treasure/
├── backend/                        # FastAPI 后端
│   ├── app/
│   │   ├── api/                    # REST API 路由 (14 个端点)
│   │   │   ├── auth.py             # 注册/登录/学段切换 (6 端点)
│   │   │   ├── vocab.py            # 词库/闪卡/SM-2 复习 (4 端点)
│   │   │   ├── grammar.py          # 知识库树/AI 分析 (3 端点)
│   │   │   └── speak.py            # 素材/跟读评测 (3 端点)
│   │   ├── chains/
│   │   │   └── grammar_chain.py    # DeepSeek 语法分析链
│   │   ├── models/                 # 7 个 SQLAlchemy 模型
│   │   ├── schemas/                # Pydantic 请求/响应
│   │   ├── services/
│   │   │   ├── sm2.py              # SM-2 间隔重复算法
│   │   │   └── iflytek.py          # 讯飞 WebSocket 评测
│   │   └── core/                   # config / database / security
│   ├── alembic/                    # 数据库迁移 (1 个 revision)
│   ├── tests/                      # pytest (6 用例全通过)
│   ├── seed_data.py                # 种子数据 (50 词 + 20 语法 + 13 句)
│   ├── .env / .env.example         # 环境变量
│   ├── requirements.txt            # 固定版本依赖
│   └── pyproject.toml
│
├── frontend/                       # Flutter 前端
│   └── lib/
│       ├── main.dart               # 应用入口
│       ├── core/                   # router / providers / api_client / theme
│       └── features/
│           ├── auth/               # 登录/注册
│           ├── vocab/              # 词库 + 闪卡翻面学习
│           ├── grammar/            # 知识库树 + DeepSeek AI 弹窗
│           ├── speak/              # 素材列表 + 逐句跟读 + 评分卡片
│           └── profile/            # 学段切换 + 退出登录
│
├── docs/
│   ├── 英语宝典_PRD_终稿.md
│   └── 技术选型.md
│
├── docker-compose.yml              # PostgreSQL + Redis + MinIO
├── README.md                       # English version
├── README_zh.md                    # 本文件
└── .gitignore
```

## 🚀 快速开始

### 前置条件

- Python ≥3.11
- Flutter SDK ≥3.2
- Docker & Docker Compose
- [DeepSeek API Key](https://platform.deepseek.com/)
- [讯飞 API Key](https://www.xfyun.cn/)（需开通「语音评测」英文版服务）

### 1. 启动基础设施

```bash
docker compose up -d
# PostgreSQL :5433 | Redis :6380 | MinIO :9002
```

### 2. 配置环境变量

```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env:
#   DEEPSEEK_API_KEY=sk-xxx
#   DEEPSEEK_MODEL=deepseek-v4-flash
#   IFLYTEK_APP_ID=xxx
#   IFLYTEK_API_KEY=xxx
#   IFLYTEK_API_SECRET=xxx
```

### 3. 安装依赖 + 迁移 + 种子数据

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
python seed_data.py
```

### 4. 启动后端

```bash
uvicorn app.main:app --reload --port 8080
```

API 文档: http://localhost:8080/docs

### 5. 启动前端

```bash
cd frontend
flutter create --project-name english_treasure .
flutter pub get
flutter run -d chrome
# 或 flutter run -d macos
```

> **API 地址**：前端默认连接 `http://localhost:8080`。如需修改，编辑 `frontend/lib/core/providers.dart:7`。

## 📡 API 接口

| 方法 | 端点 | 认证 | 说明 |
|---|---|---|---|
| `POST` | `/api/auth/register/phone` | — | 手机号注册 |
| `POST` | `/api/auth/login/phone` | — | 手机号登录 |
| `GET` | `/api/auth/me` | ✅ | 当前用户信息 |
| `PUT` | `/api/auth/me/stage` | ✅ | 切换学段 |
| `GET` | `/api/vocab/banks` | — | 词库列表 |
| `GET` | `/api/vocab/flashcards` | ✅ | 今日闪卡任务 |
| `POST` | `/api/vocab/flashcards/review` | ✅ | 提交复习评分 |
| `GET` | `/api/grammar/topics` | — | 语法知识库树 |
| `POST` | `/api/grammar/analyze` | ✅ | AI 语法分析/改错 |
| `GET` | `/api/speak/materials` | — | 跟读素材列表 |
| `GET` | `/api/speak/materials/{id}` | — | 素材详情（含逐句） |
| `POST` | `/api/speak/evaluate` | ✅ | 录音评测 |

## 🧪 测试

```bash
cd backend
python -m pytest tests/ -v
# 6 passed — 注册/登录/重复注册/错误密码/学段切换/未授权
```

## 🔧 已知问题与计划

| 问题 | 状态 | 计划 |
|---|---|---|
| 讯飞 API 返回 401 | 🟡 待确认 | 需确认控制台 APPID 及服务开通状态 |
| Web 端真实录音 | 🟡 待实现 | 当前发送测试 WAV，需接入 MediaRecorder 或原生 App |
| 前端版本依赖警告 | 🟢 无影响 | `record`/`flutter_tts` 等包 SPM 兼容性，下个版本修复 |
| 思考模式控制 | ✅ 已修复 | `ChatDeepSeek(extra_body={"thinking": {"type": "disabled"}})` |

## 📝 环境变量

| 变量 | 必填 | 说明 |
|---|---|---|
| `DEEPSEEK_API_KEY` | 是 | DeepSeek API 密钥 |
| `DEEPSEEK_MODEL` | 是 | `deepseek-v4-flash` |
| `IFLYTEK_APP_ID` | 是 | 讯飞应用 ID |
| `IFLYTEK_API_KEY` | 是 | 讯飞 API Key |
| `IFLYTEK_API_SECRET` | 是 | 讯飞 API Secret |
| `DATABASE_URL` | 是 | PostgreSQL 连接 (端口 5433) |
| `REDIS_URL` | 是 | Redis 连接 (端口 6380) |
| `SECRET_KEY` | 是 | JWT 密钥（≥32 字符） |

## 📄 许可证

待定
