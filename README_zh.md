# 英语宝典 (English Treasure)

> 覆盖全学段的英语学习 App — 单词速记 · 语法分析 · 跟读语感，从小学到考研一站搞定。

## ✨ 核心功能

| 模块 | 功能 | 状态 |
|---|---|---|
| **单词速记** | SM-2 间隔重复、闪卡翻面、四选一答题模式、5 个词库、换批新词 | ✅ 可用 |
| **语法分析** | DeepSeek + LangChain 智能语法分析，结构化标注（主谓宾/从句/时态）| ✅ 可用 |
| **跟读语感** | KTV 式逐句跟读，手动导航，讯飞语音评测多维度打分 | ✅ UI 就绪 · 🟡 讯飞认证 |
| **个人中心** | 学习统计（累计词汇/已掌握/连续打卡/正确率），学段切换 | ✅ 可用 |
| **用户系统** | 手机号注册/登录，JWT 持久化（刷新不丢失）| ✅ 可用 |

## 🛠 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Flutter 3.44 (Dart) · Riverpod · GoRouter |
| 后端 | Python FastAPI (异步) |
| LLM 编排 | LangChain ≥1.0 + LangGraph ≥1.0 |
| 大模型 | DeepSeek v4 Flash（`extra_body` 关闭思考模式） |
| 语音评测 | 讯飞云端语音评测 API (ISE WebSocket) |
| 数据库 | PostgreSQL 16 (端口 5433) + Redis 7 (端口 6380) |
| ORM | SQLAlchemy 2.0 (异步) |
| 对象存储 | MinIO (端口 9002) |
| 测试 | pytest (6/6 通过) |

## 📁 项目结构

```
english-treasure/
├── backend/                        # FastAPI 后端
│   ├── app/
│   │   ├── api/                    # REST API 路由 (17 个端点)
│   │   │   ├── auth.py             # 注册/登录/学段切换 (6)
│   │   │   ├── vocab.py            # 词库/闪卡/SM-2/答题 (7)
│   │   │   ├── grammar.py          # 知识库树/AI 分析 (3)
│   │   │   ├── speak.py            # 素材/跟读评测 (3)
│   │   │   └── stats.py            # 学习统计概览 (1)
│   │   ├── chains/grammar_chain.py # DeepSeek 语法分析链
│   │   ├── models/                 # 7 个 SQLAlchemy 模型
│   │   ├── schemas/                # Pydantic 请求/响应
│   │   ├── services/
│   │   │   ├── sm2.py              # SM-2 间隔重复算法
│   │   │   └── iflytek.py          # 讯飞 WebSocket 评测
│   │   └── core/                   # config / database / security
│   ├── alembic/                    # 数据库迁移
│   ├── tests/                      # pytest (6 用例)
│   ├── seed_data.py                # 种子数据 (50 词/20 语法/13 句)
│   ├── requirements.txt            # 固定版本依赖
│   └── pyproject.toml
│
├── frontend/                       # Flutter 前端
│   └── lib/
│       ├── main.dart               # 入口 + checkAuth 启动检查
│       ├── core/                   # router / providers / api_client / theme
│       └── features/
│           ├── auth/               # 登录/注册
│           ├── vocab/              # 闪卡翻面 + 四选一答题
│           ├── grammar/            # 知识库树 + AI 对话弹窗
│           ├── speak/              # 素材列表 + 逐句跟读
│           └── profile/            # 实时统计 + 学段切换
│
├── docs/
│   ├── 英语宝典_PRD_终稿.md
│   └── 技术选型.md
│
├── docker-compose.yml              # PostgreSQL + Redis + MinIO
├── README.md / README_zh.md
└── .gitignore
```

## 🚀 快速开始

### 前置条件

- Python ≥3.11 · Flutter SDK ≥3.2 · Docker
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
# 填入 DEEPSEEK_API_KEY、IFLYTEK_* 等
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
```

## 📡 API 接口

| 方法 | 端点 | 认证 | 说明 |
|---|---|---|---|
| `POST` | `/api/auth/register/phone` | — | 手机号注册 |
| `POST` | `/api/auth/login/phone` | — | 手机号登录 |
| `GET` | `/api/auth/me` | ✅ | 当前用户信息 |
| `PUT` | `/api/auth/me/stage` | ✅ | 切换学段 |
| `GET` | `/api/vocab/banks` | — | 词库列表 |
| `GET` | `/api/vocab/flashcards` | ✅ | 今日闪卡（+ `?force_new=true`） |
| `POST` | `/api/vocab/flashcards/review` | ✅ | 提交 SM-2 复习评分 |
| `GET` | `/api/vocab/quiz` | ✅ | 生成选择题（英选中/中选英） |
| `POST` | `/api/vocab/quiz/submit` | ✅ | 提交答题结果 |
| `GET` | `/api/grammar/topics` | — | 语法知识库树 |
| `POST` | `/api/grammar/analyze` | ✅ | AI 语法分析 |
| `GET` | `/api/speak/materials` | — | 跟读素材列表 |
| `GET` | `/api/speak/materials/{id}` | — | 素材详情（含逐句） |
| `POST` | `/api/speak/evaluate` | ✅ | 录音评测 |
| `GET` | `/api/stats/overview` | ✅ | 学习统计概览 |

## 🧪 测试

```bash
cd backend
python -m pytest tests/ -v
# 6 passed
```

## 🔧 已知问题

| 问题 | 状态 |
|---|---|
| 讯飞 API 返回 401 | 🟡 需确认控制台 APPID 及服务开通 |
| Web 端真实录音 | 🟡 当前测试 WAV，需接入 MediaRecorder |
| 插件 SPM 警告 | 🟢 不影响使用 |

## 📄 许可证

待定
