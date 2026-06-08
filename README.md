# English Treasure (英语宝典)

> An all-in-one English learning app covering word memorization, grammar analysis, and speaking practice — from elementary school to postgraduate exams.

## ✨ Features

| Module | Function | Status |
|---|---|---|
| **Vocabulary** | SM-2 spaced repetition, flashcard flip + quiz (4-choice), 5 word banks, force-new batch | ✅ Working |
| **Grammar** | DeepSeek + LangChain AI analysis with structured output (SVO/clauses/tense) | ✅ Working |
| **Speaking** | KTV-style shadowing with manual navigation, iFlytek multi-dimension scoring | ✅ UI Ready · 🟡 iFlytek auth |
| **Profile** | Learning stats (total vocab, mastered, streak, accuracy), stage switching | ✅ Working |
| **Auth** | Phone registration/login, JWT persistence across page refresh | ✅ Working |

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Flutter 3.44 (Dart) · Riverpod · GoRouter |
| Backend | Python FastAPI (async) |
| LLM Orchestration | LangChain ≥1.0 + LangGraph ≥1.0 |
| LLM | DeepSeek v4 Flash (thinking mode disabled via `extra_body`) |
| Speech Evaluation | iFlytek ISE API (WebSocket) |
| Database | PostgreSQL 16 (port 5433) + Redis 7 (port 6380) |
| ORM | SQLAlchemy 2.0 (async) |
| Object Storage | MinIO (port 9002) |
| Testing | pytest (6/6 passing) |

## 📁 Project Structure

```
english-treasure/
├── backend/                        # FastAPI Backend
│   ├── app/
│   │   ├── api/                    # REST API routes (17 endpoints)
│   │   │   ├── auth.py             # Register/login/stage switch (6)
│   │   │   ├── vocab.py            # Word banks, flashcards, SM-2, quiz (7)
│   │   │   ├── grammar.py          # Knowledge tree, AI analysis (3)
│   │   │   ├── speak.py            # Materials, pronunciation eval (3)
│   │   │   └── stats.py            # Learning statistics overview (1)
│   │   ├── chains/grammar_chain.py # DeepSeek grammar chain
│   │   ├── models/                 # 7 SQLAlchemy models
│   │   ├── schemas/                # Pydantic request/response
│   │   ├── services/
│   │   │   ├── sm2.py              # SM-2 spaced repetition
│   │   │   └── iflytek.py          # iFlytek WebSocket evaluation
│   │   └── core/                   # config / database / security
│   ├── alembic/                    # DB migrations
│   ├── tests/                      # pytest (6 tests)
│   ├── seed_data.py                # 50 words + 20 grammar + 13 sentences
│   ├── requirements.txt            # Pinned dependencies
│   └── pyproject.toml
│
├── frontend/                       # Flutter App
│   └── lib/
│       ├── main.dart               # Entry + checkAuth on startup
│       ├── core/                   # router / providers / api_client / theme
│       └── features/
│           ├── auth/               # Login / Register
│           ├── vocab/              # Flashcards + quiz mode
│           ├── grammar/            # Knowledge tree + AI dialog
│           ├── speak/              # Materials + per-sentence practice
│           └── profile/            # Real-time stats + stage switch
│
├── docs/
│   ├── 英语宝典_PRD_终稿.md
│   └── 技术选型.md
│
├── docker-compose.yml              # PostgreSQL + Redis + MinIO
├── README.md / README_zh.md
└── .gitignore
```

## 🚀 Quick Start

### Prerequisites

- Python ≥3.11 · Flutter SDK ≥3.2 · Docker
- [DeepSeek API Key](https://platform.deepseek.com/)
- [iFlytek API Key](https://www.xfyun.cn/) (enable "Speech Evaluation" English service)

### 1. Start Infrastructure

```bash
docker compose up -d
# PostgreSQL :5433 | Redis :6380 | MinIO :9002
```

### 2. Configure

```bash
cp backend/.env.example backend/.env
# Fill in DEEPSEEK_API_KEY, IFLYTEK_*, etc.
```

### 3. Install + Migrate + Seed

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
```

## 📡 API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/register/phone` | — | Register with phone |
| `POST` | `/api/auth/login/phone` | — | Login with phone |
| `GET` | `/api/auth/me` | ✅ | Current user profile |
| `PUT` | `/api/auth/me/stage` | ✅ | Switch study stage |
| `GET` | `/api/vocab/banks` | — | List word banks |
| `GET` | `/api/vocab/flashcards` | ✅ | Today's flashcard tasks (+ `?force_new=true`) |
| `POST` | `/api/vocab/flashcards/review` | ✅ | Submit SM-2 review |
| `GET` | `/api/vocab/quiz` | ✅ | Generate quiz questions (en2cn/cn2en) |
| `POST` | `/api/vocab/quiz/submit` | ✅ | Submit quiz answers |
| `GET` | `/api/grammar/topics` | — | Grammar knowledge tree |
| `POST` | `/api/grammar/analyze` | ✅ | AI grammar analysis |
| `GET` | `/api/speak/materials` | — | List speaking materials |
| `GET` | `/api/speak/materials/{id}` | — | Material with sentences |
| `POST` | `/api/speak/evaluate` | ✅ | Submit audio for evaluation |
| `GET` | `/api/stats/overview` | ✅ | Learning statistics |

## 🧪 Testing

```bash
cd backend
python -m pytest tests/ -v
# 6 passed
```

## 🔧 Known Issues

| Issue | Status |
|---|---|
| iFlytek returns 401 | 🟡 Verify APPID & service in console |
| Real browser audio recording | 🟡 WAV placeholder; need MediaRecorder |
| Plugin SPM warnings | 🟢 Non-blocking |

## 📄 License

TBD
