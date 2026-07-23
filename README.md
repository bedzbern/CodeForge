# CodeForge

**A teacher-controlled AI coding assistant for school computer labs.**

CodeForge replaces unrestricted AI (ChatGPT, Copilot) with a scaffolded mentor that gives hints instead of answers — under the teacher's strict control. It gives shy students a private way to ask for help, and gives teachers a real-time dashboard that sees who is struggling.

---

## How It Works

```
Student PC (VS Code + Extension)         Teacher PC (Dashboard + Server)
┌────────────────────────────┐           ┌──────────────────────────────┐
│  "Why does my loop skip   │  POST     │  ┌──────────────────────────┐ │
│   the last element?"       │ ───────►  │  │  CodeForge Server        │ │
│                            │           │  │  FastAPI + SQLite + AI   │ │
│  ◄── "What does range()   │ ◄───────  │  │  Rule Engine (5 levels)  │ │
│      return for the last   │  Response │  └──────────────────────────┘ │
│      index?"               │           │  ┌──────────────────────────┐ │
└────────────────────────────┘           │  │  Live Dashboard          │ │
                                         │  │  50-seat grid, real-time │ │
    Isolated Lab Network                 │  │  level control, summary  │ │
    (no internet = no ChatGPT)           │  └──────────────────────────┘ │
                                         └──────────────────────────────┘
```

1. Student asks a question through the VS Code extension sidebar
2. Server validates the student's IP, checks rate limits, determines the hint level
3. AI generates a response constrained by the level (Socratic questions → full code)
4. Response is shown to the student; teacher dashboard updates in real-time via WebSocket
5. Teacher can adjust levels per-student or broadcast to the whole class
6. End-of-session summary shows common topics, errors, and students needing follow-up

### The Five Hint Levels

| Level | Name | What the AI Does |
|-------|------|-----------------|
| 1 | Socratic Mirror | Only asks guiding questions — never gives answers |
| 2 | Hint Giver | Gives conceptual nudges — no code or pseudocode |
| 3 | Error Translator | Explains error messages in plain English |
| 4 | Logic Explainer | Explains the solution logic step by step |
| 5 | Full Answer | Writes complete code — **locked by default, teacher must unlock** |

---

## Quick Start (Teacher PC)

### Prerequisites

- **Python 3.10+** ([download](https://www.python.org/downloads/))
- **Node.js 18+** ([download](https://nodejs.org/)) — only for the dashboard
- **Groq API key** — free at [console.groq.com](https://console.groq.com) (or use Ollama for offline)

### 1. Clone and install

```bash
git clone https://github.com/bedzbern/CodeForge.git
cd CodeForge

# Install Python dependencies
pip install -r server/requirements.txt

# Install dashboard dependencies (optional)
cd dashboard && npm install && cd ..
```

### 2. Configure

```bash
# Windows
set GROQ_API_KEY=gsk_your_key_here
set AI_PROVIDER=groq

# Linux/Mac
export GROQ_API_KEY=gsk_your_key_here
export AI_PROVIDER=groq
```

Or copy `.env.example` to `.env` and fill in your values.

### 3. Start the server

```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh
./start.sh
```

The server starts on `http://192.168.1.1:8000`. API docs at `http://192.168.1.1:8000/docs`.

### 4. Start the dashboard (optional)

```bash
# Windows
start-dashboard.bat

# Linux/Mac
cd dashboard && npm run dev
```

Dashboard opens at `http://localhost:5173`.

> **Local testing:** For testing on a single machine, set `TEACHER_IP=127.0.0.1` before starting the server. The dashboard will connect to `localhost` automatically via the Vite dev proxy.

---

## Demo Setup (3 Students)

### Network

Create an isolated Wi-Fi hotspot on the teacher PC (no internet required):

1. **Windows:** Settings → Network → Mobile Hotspot → Turn on
2. Set SSID and password
3. Static IP on teacher PC: `192.168.1.1` / subnet `255.255.255.0`

### Student PCs

On each student laptop connected to the hotspot:

1. Set static IP: `192.168.1.X` (X = 2, 3, 4, ...)
   - Windows: Settings → Network → Wi-Fi → Properties → IPv4 → Manual
   - IP: `192.168.1.X`, Subnet: `255.255.255.0`, Gateway: `192.168.1.1`
2. Install VS Code
3. Install the CodeForge extension (see below)

### Register students in the database

Students must be registered before they can ask questions:

```bash
python -c "
from server.database import init_db, SessionLocal
from server.models import Student, Rule
init_db()
db = SessionLocal()
for i, ip in enumerate(['192.168.1.2', '192.168.1.3', '192.168.1.4'], 1):
    db.add(Student(seat_number=i, ip_address=ip, label=f'Student {i}'))
    db.add(Rule(student_ip=ip, hint_level=2))
db.commit()
print('Students registered!')
"
```

### Install the extension

```bash
cd extension
npm install
npm run compile
```

Then in VS Code: Extensions → ... → Install from VSIX → select `codeforge-student-0.1.0.vsix`.

Or press `F5` in the `extension/` folder to launch the Extension Development Host.

### Walkthrough

1. **Student asks:** Open sidebar → type question → click "Ask CodeForge" → see response
2. **Teacher monitors:** Dashboard shows green/gray dots for active/idle students
3. **Teacher adjusts:** Click a student card → change level → student's next question gets different AI behaviour
4. **Teacher broadcasts:** Set all students to Level 1 during an exam, or Level 5 during a review
5. **End of session:** Click "Session Summary" tab → see common topics, errors, AI summary

---

## Running Tests

```bash
pip install pytest httpx
pytest tests/ -v
```

59 tests covering: API endpoints, rule engine, rate limiter, analytics, teacher auth, AI providers.

---

## Project Structure

```
CodeForge/
├── server/                    # Python FastAPI backend
│   ├── main.py                # App entry point, CORS, lifespan
│   ├── models.py              # 5 SQLAlchemy models
│   ├── database.py            # SQLite engine, session factory
│   ├── rule_engine.py         # Hint level enforcement + caching
│   ├── rate_limiter.py        # Per-IP 30s rate limit
│   ├── analytics.py           # Session summary generation
│   ├── prompt_cache.py        # Startup prompt loader
│   ├── providers/             # AI backends
│   │   ├── base.py            # Abstract AIProvider
│   │   ├── groq_provider.py   # Groq cloud (free, fast)
│   │   └── ollama_provider.py # Ollama local (offline)
│   ├── prompts/               # 6 prompt files (base + 5 levels)
│   ├── routers/
│   │   ├── student.py         # POST /api/ask
│   │   └── teacher.py         # /api/status, /teacher/*, /api/summary
│   ├── websocket_events.py    # Socket.IO real-time events
│   └── requirements.txt
│
├── extension/                 # VS Code extension (TypeScript)
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── extension.ts       # Entry point
│       ├── sidebarProvider.ts # Sidebar webview UI
│       ├── apiClient.ts       # HTTP client (zero deps)
│       └── getStudentIp.ts    # Auto-detect lab IP
│
├── dashboard/                 # Teacher Dashboard (React + Vite)
│   ├── package.json
│   ├── vite.config.ts         # API proxy config
│   └── src/
│       ├── App.jsx            # Main app with tabs
│       ├── api.js             # Fetch-based API client
│       ├── hooks/useSocket.js # Socket.IO hook
│       └── components/
│           ├── StudentGrid.jsx # 50-seat grid view
│           ├── StudentCard.jsx # Individual seat card
│           ├── RulePanel.jsx   # Level/broadcast/unlock controls
│           └── SummaryView.jsx # Session analytics
│
├── tests/                     # 59 pytest tests
├── docs/
│   ├── architecture.md        # System architecture
│   └── user_guide.md          # Teacher's guide
├── data/                      # SQLite database (gitignored)
├── start.bat                  # Windows server launcher
├── start.sh                   # Linux/Mac server launcher
└── start-dashboard.bat        # Dashboard launcher
```

---

## API Reference

All endpoints are prefixed with `/api`. Full interactive docs at `/docs` (Swagger UI).

### `POST /api/ask` — Ask a question

```json
// Request
{
  "student_ip": "192.168.1.2",
  "question": "Why does this return None?",
  "code_snapshot": "def add(a, b):\n    return a + b",
  "file_name": "math_utils.py",
  "line_number": 1
}

// Response (Level 1)
{
  "level": 1,
  "level_name": "Socratic Mirror",
  "response": "What does the return keyword do in Python?",
  "ip": "192.168.1.2",
  "timestamp": "2026-07-22T17:52:00Z"
}
```

### `GET /api/status` — Teacher: get all students

```json
{
  "students": [
    {
      "ip": "192.168.1.2",
      "seat_number": 1,
      "current_hint_level": 2,
      "total_queries_today": 5,
      "last_query_time": "2026-07-22T17:45:00Z",
      "status": "active"
    }
  ],
  "session_id": "sess_20260722_1",
  "total_active": 15,
  "total_idle": 35
}
```

### `POST /api/teacher/level` — Change one student's level

```json
// Request
{ "student_ip": "192.168.1.2", "new_level": 4 }

// Response
{ "success": true, "student_ip": "192.168.1.2", "new_level": 4 }
```

### `POST /api/teacher/broadcast` — Set all students to same level

```json
// Request
{ "new_level": 2 }

// Response
{ "success": true, "affected_students": 50, "new_level": 2 }
```

### `POST /api/teacher/unlock` — Temporarily unlock Level 5

```json
// Request
{ "student_ip": "192.168.1.2", "duration_minutes": 5, "reason": "Demonstrated understanding" }

// Response
{ "success": true, "unlocked_until": "2026-07-22T17:57:00Z" }
```

### `GET /api/summary` — End-of-session analytics

```
GET /api/summary?session_id=sess_20260722_1
```

### `GET /api/health` — Server health check

```json
{
  "status": "healthy",
  "ai_provider": "GroqProvider",
  "ai_online": "configured",
  "database": "connected",
  "uptime_seconds": 3420
}
```

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_PROVIDER` | `groq` | AI backend: `groq` (cloud) or `ollama` (local) |
| `GROQ_API_KEY` | — | Groq API key (free at console.groq.com) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `TEACHER_IP` | `192.168.1.1` | IP of the teacher PC (for auth) |
| `VITE_SERVER_URL` | `http://192.168.1.1:8000` | Server URL for dashboard dev proxy |

---

## Troubleshooting

### Server won't start

- **"ModuleNotFoundError: No module named 'server'"** — Run from the project root directory
- **"Port 8000 already in use"** — Another process is using the port: `netstat -ano | findstr :8000`
- **"GROQ_API_KEY not set"** — Set the environment variable before starting

### Students can't connect

- **403 Forbidden** — Student IP is not registered. Add them to the `students` table
- **Connection refused** — Check that the student and teacher are on the same network
- **429 Too Many Requests** — Rate limit: wait 30 seconds between questions

### Dashboard shows no data

- **"Disconnected"** — Server is not running, or Socket.IO is blocked. Check `http://192.168.1.1:8000/api/health`
- **Empty grid** — No students registered. Run the registration script above. Students only appear after they ask at least one question.
- **Connected but 0 students** — The dashboard fetches data on page load. Make sure `TEACHER_IP` is set to your machine's IP (e.g., `127.0.0.1` for local testing, `192.168.1.1` for lab). A hard refresh (Ctrl+Shift+R) may be needed after server restarts.
- **Seats show but never "active"** — Students are marked active only within 5 minutes of their last query. Send a test question to wake a seat up.

### AI responses are slow

- **Groq (cloud):** Usually 1-3 seconds. Check internet connection on teacher PC
- **Ollama (local):** 5-30 seconds without GPU. Expected on CPU-only machines

---

## Security

- **No student PII** — Students identified only by IP address
- **IP spoofing prevention** — Server validates real HTTP source IP
- **Rate limiting** — 1 question per 30 seconds per IP
- **Level 5 guard** — Full answers locked by default; teacher must unlock
- **Prompt injection defense** — Student input wrapped in XML delimiters
- **Isolated network** — No internet access means no external AI tools
- **CORS locked** — Only lab network IPs are allowed

---

## License

Educational use. Built as a thesis project.
