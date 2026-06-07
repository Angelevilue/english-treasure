# English Treasure (英语宝典)

> An all-in-one English learning app covering word memorization, grammar analysis, and speaking practice for learners from elementary school to postgraduate entrance exams.

## ✨ Features

| Module | Function | Status |
|---|---|---|
| **Vocabulary** | SM-2 spaced repetition, flashcard flip learning, 5 word banks (Elementary→IELTS) | ✅ Working |
| **Grammar** | DeepSeek + LangChain AI analysis with structured output (SVO/clauses/tense) | ✅ Working |
| **Speaking** | KTV-style shadowing with manual navigation, iFlytek multi-dimension scoring | ✅ UI Ready · 🟡 iFlytek auth pending |
| **Auth** | Phone registration/login, JWT, study stage switching (Elementary→Overseas) | ✅ Working |

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Flutter 3.44 (Dart) · Riverpod · GoRouter |
| Backend | Python FastAPI (async) |
| LLM Orchestration | LangChain ≥1.0 + LangGraph ≥1.0 |
| LLM | DeepSeek v4 Flash (thinking mode disabled) |
| Speech Evaluation | iFlytek ISE API (WebSocket) |
| Database | PostgreSQL 16 (port 5433) + Redis 7 (port 6380) |
| Local Storage | SQLite (sqflite) |
| ORM | SQLAlchemy 2.0 (async) |
| Object Storage | MinIO (port 9002) |
| Deployment | Docker + Nginx |
| Testing | pytest (6/6 auth tests passing) |

## 📁 Project Structure

```
english-treasure/
├── backend/                        # FastAPI Backend
│   ├── app/
│   │   ├── api/                    # REST API routes (14 endpoints)
│   │   │   ├── auth.py             # Register/login/stage switch (6 endpoints)
│   │   │   ├── vocab.py            # Word banks, flashcards, SM-2 (4 endpoints)
│   │   │   ├── grammar.py          # Knowledge tree, AI analysis (3 endpoints)
│   │   │   └── speak.py            # Materials, pronunciation eval (3 endpoints)
│   │   ├── chains/
│   │   │   └── grammar_chain.py    # DeepSeek grammar analysis chain
│   │   ├── models/                 # 7 SQLAlchemy models
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── sm2.py              # SM-2 spaced repetition algorithm
│   │   │   └── iflytek.py          # iFlytek WebSocket evaluation
│   │   └── core/                   # config / database / security
│   ├── alembic/                    # DB migrations (1 revision)
│   ├── tests/                      # pytest (6 tests passing)
│   ├── seed_data.py                # Seed data (50 words + 20 grammar + 13 sentences)
│   ├── .env / .env.example         # Environment variables
│   ├── requirements.txt            # Pinned dependencies
│   └── pyproject.toml
│
├── frontend/                       # Flutter App
│   └── lib/
│       ├── main.dart               # App entry point
│       ├── core/                   # router / providers / api_client / theme
│       └── features/
│           ├── auth/               # Login / Register
│           ├── vocab/              # Word banks + flashcard flip learning
│           ├── grammar/            # Knowledge tree + DeepSeek AI dialog
│           ├── speak/              # Materials + per-sentence practice + score card
│           └── profile/            # Stage switch + logout
│
├── docs/
│   ├── 英语宝典_PRD_终稿.md        # PRD (Chinese)
│   └── 技术选型.md                 # Tech decisions (Chinese)
│
├── docker-compose.yml              # PostgreSQL + Redis + MinIO
├── README.md                       # This file
├── README_zh.md                    # Chinese version
└── .gitignore
```

## 🚀 Quick Start

### Prerequisites

- Python ≥3.11
- Flutter SDK ≥3.2
- Docker & Docker Compose
- [DeepSeek API Key](https://platform.deepseek.com/)
- [iFlytek API Key](https://www.xfyun.cn/) (enable "Speech Evaluation" English service)

### 1. Start Infrastructure

```bash
docker compose up -d
# PostgreSQL :5433 | Redis :6380 | MinIO :9002
```

### 2. Configure Environment

```bash
cp backend/.env.example backend/.env
# Edit backend/.env:
#   DEEPSEEK_API_KEY=sk-xxx
#   DEEPSEEK_MODEL=deepseek-v4-flash
#   IFLYTEK_APP_ID=xxx
#   IFLYTEK_API_KEY=xxx
#   IFLYTEK_API_SECRET=xxx
```

### 3. Install Dependencies + Migrate + Seed

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
python seed_data.py
```

### 4. Start Backend

```bash
uvicorn app.main:app --reload --port 8080
```

API Docs: http://localhost:8080/docs

### 5. Start Frontend

```bash
cd frontend
flutter create --project-name english_treasure .
flutter pub get
flutter run -d chrome
# or: flutter run -d macos
```

> **API Base URL**: Frontend defaults to `http://localhost:8080`. Edit `frontend/lib/core/providers.dart:7` if needed.

## 📡 API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/register/phone` | — | Register with phone |
| `POST` | `/api/auth/login/phone` | — | Login with phone |
| `GET` | `/api/auth/me` | ✅ | Current user profile |
| `PUT` | `/api/auth/me/stage` | ✅ | Switch study stage |
| `GET` | `/api/vocab/banks` | — | List word banks |
| `GET` | `/api/vocab/flashcards` | ✅ | Today's flashcard tasks |
| `POST` | `/api/vocab/flashcards/review` | ✅ | Submit review score |
| `GET` | `/api/grammar/topics` | — | Grammar knowledge tree |
| `POST` | `/api/grammar/analyze` | ✅ | AI grammar analysis |
| `GET` | `/api/speak/materials` | — | List speaking materials |
| `GET` | `/api/speak/materials/{id}` | — | Material with sentences |
| `POST` | `/api/speak/evaluate` | ✅ | Submit audio for evaluation |

## 🧪 Testing

```bash
cd backend
python -m pytest tests/ -v
# 6 passed — register/login/duplicate/wrong-password/stage-switch/unauthorized
```

## 🔧 Known Issues & Roadmap

| Issue | Status | Plan |
|---|---|---|
| iFlytek returns 401 | 🟡 Pending | Verify APPID and service enabled in console |
| Real browser audio recording | 🟡 Pending | Test WAV placeholder works; need MediaRecorder or native app |
| Plugin SPM warnings | 🟢 Non-blocking | `record`/`flutter_tts` SPM compatibility — next Flutter version |
| Thinking mode | ✅ Fixed | `ChatDeepSeek(extra_body={"thinking": {"type": "disabled"}})` |

## 📝 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DEEPSEEK_API_KEY` | Yes | DeepSeek API key |
| `DEEPSEEK_MODEL` | Yes | `deepseek-v4-flash` |
| `IFLYTEK_APP_ID` | Yes | iFlytek application ID |
| `IFLYTEK_API_KEY` | Yes | iFlytek API key |
| `IFLYTEK_API_SECRET` | Yes | iFlytek API secret |
| `DATABASE_URL` | Yes | PostgreSQL connection (port 5433) |
| `REDIS_URL` | Yes | Redis connection (port 6380) |
| `SECRET_KEY` | Yes | JWT signing secret (≥32 chars) |

## 📄 License

TBD
