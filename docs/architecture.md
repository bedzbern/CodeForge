# CodeForge Architecture Document

> **Version:** 1.0  
> **Date:** 2026-07-22  
> **Author:** Chief Architect (AI Agent)  
> **Status:** Approved — Ready for Implementation

---

## Table of Contents

1. [High-Level Component Diagram](#1-high-level-component-diagram)
2. [Technology Stack](#2-technology-stack)
3. [REST API Endpoints](#3-rest-api-endpoints)
4. [WebSocket Events](#4-websocket-events)
5. [Database Schema](#5-database-schema)
6. [Deployment Architecture](#6-deployment-architecture)
7. [Security & Privacy](#7-security--privacy)
8. [AI Prompt Design](#8-ai-prompt-design)
9. [File Structure](#9-file-structure)

---

## 1. High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SCHOOL COMPUTER LAB                         │
│                   (Isolated network, no external AI)                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐          ┌──────────────────────────────────┐ │
│  │   TEACHER PC     │          │       STUDENT PCs (1–50)         │ │
│  │  192.168.1.1     │          │      192.168.1.2 – 192.168.1.51 │ │
│  │                  │          │                                  │ │
│  │  ┌────────────┐  │          │  ┌────────────────────────────┐  │ │
│  │  │  Teacher   │  │          │  │  VS Code +                 │  │ │
│  │  │  Dashboard │  │          │  │  CodeForge Extension       │  │ │
│  │  │  (React)   │  │          │  │  (Student Mode)            │  │ │
│  │  │            │  │          │  └─────────────┬──────────────┘  │ │
│  │  │ • Live Grid│  │          │                │                  │ │
│  │  │ • Rules    │  │          │                │  HTTP POST       │ │
│  │  │ • Summary  │  │          │                │  /api/ask        │ │
│  │  └─────┬──────┘  │          │                │                  │ │
│  └────────┼─────────┘          │                │                  │ │
│           │                    └────────────────┼──────────────────┘ │
│           │                                    │                    │
│           │     ┌──────────────────────────────┘                    │
│           │     │                                                   │
│           │     ▼                                                   │
│  ┌────────┴─────────────────────────────────────────────────────┐  │
│  │                    LOCAL AI SERVER                            │  │
│  │                   192.168.1.1:8000                            │  │
│  │                                                               │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐  │  │
│  │  │   FastAPI    │  │ Rule Engine  │  │   AI Provider       │  │  │
│  │  │   Router     │──│              │──│                     │  │  │
│  │  │             │  │ • Load rules │  │ • GroqProvider      │  │  │
│  │  │  REST API   │  │ • Enforce    │  │ • OllamaProvider    │  │  │
│  │  │  + CORS     │  │   levels     │  │                     │  │  │
│  │  └──────┬──────┘  └──────────────┘  └─────────────────────┘  │  │
│  │         │                                                     │  │
│  │  ┌──────┴──────┐  ┌──────────────┐                           │  │
│  │  │   SQLite    │  │  Analytics   │                           │  │
│  │  │   Database  │  │  Engine      │                           │  │
│  │  │             │  │ • Summaries  │                           │  │
│  │  └─────────────┘  └──────────────┘                           │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              Socket.IO (Real-time layer)                       │  │
│  │   Server emits: student_query, level_change, summary_ready    │  │
│  │   Dashboard listens: live updates                             │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

| Component               | Language     | Frameworks / Libraries                         | Notes                                      |
|-------------------------|--------------|------------------------------------------------|--------------------------------------------|
| Student Extension       | TypeScript   | VS Code Extension API, Axios                   | Sends highlighted code + question to server |
| AI Server + Rule Engine | Python 3.10+ | FastAPI, uvicorn, SQLAlchemy, python-socketio  | Core backend                               |
| Teacher Dashboard       | JavaScript   | React (Vite)                                   | Real-time web UI                           |
| Real-Time Communication | —            | Socket.IO                                      | Server ↔ Dashboard push                    |
| Database                | —            | SQLite3                                        | File: `data/codeforge.db`                  |
| AI Backend (Cloud)      | —            | Groq API (free tier)                           | Primary for demo                           |
| AI Backend (Local)      | —            | Ollama (offline fallback)                      | Slower, no GPU → CPU-only                  |
| Version Control         | —            | Git + GitHub                                   | Public repository                          |

### AI Provider Abstraction

```python
class AIProvider(ABC):
    """Abstract base class for AI backends."""
    
    @abstractmethod
    async def generate(self, messages: list[dict], model: str | None = None) -> str:
        """Send messages and return the AI response text."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the provider is reachable."""
        ...
```

Two concrete implementations:
- `GroqProvider` — calls Groq cloud API via `httpx` (async, free, fast)
- `OllamaProvider` — calls local Ollama HTTP API (offline, slow on CPU)

---

## 3. REST API Endpoints

All endpoints are prefixed with `/api`.

### 3.1 `POST /api/ask` — Student asks a question

**Request:**
```json
{
  "student_ip": "192.168.1.2",
  "code_snapshot": "def add(a, b):\n    return a + b",
  "question": "Why does this return None when I call add(2, 3)?",
  "file_name": "math_utils.py",
  "line_number": 1
}
```

**Response (Level 1 — Socratic):**
```json
{
  "level": 1,
  "level_name": "Socratic Mirror",
  "response": "Interesting — what does the `return` keyword do in Python? What happens if a function doesn't have a `return` statement?",
  "ip": "192.168.1.2",
  "timestamp": "2026-07-22T17:52:00Z"
}
```

**Response (Level 5 — Full Answer, UNLOCKED by teacher):**
```json
{
  "level": 5,
  "level_name": "Full Answer",
  "response": "def add(a, b):\n    return a + b\n\nThe issue is likely indentation or the function body. Here's the corrected version...",
  "ip": "192.168.1.2",
  "timestamp": "2026-07-22T17:52:00Z"
}
```

**Error Responses:**
```json
// Missing student_ip
{ "error": "student_ip is required", "code": 400 }

// Student not registered (IP not in DB)
{ "error": "Unknown student IP", "code": 404 }

// Rate limit exceeded
{ "error": "Too many requests. Please wait 30 seconds.", "code": 429 }
```

---

### 3.2 `GET /api/status` — Teacher dashboard polls student status

**Response:**
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
    },
    {
      "ip": "192.168.1.3",
      "seat_number": 2,
      "current_hint_level": 1,
      "total_queries_today": 0,
      "last_query_time": null,
      "status": "idle"
    }
  ],
  "session_id": "sess_20260722_1",
  "total_active": 15,
  "total_idle": 35
}
```

---

### 3.3 `POST /api/teacher/level` — Teacher changes a student's hint level

**Request:**
```json
{
  "student_ip": "192.168.1.2",
  "new_level": 4,
  "session_id": "sess_20260722_1"
}
```

**Response:**
```json
{
  "success": true,
  "student_ip": "192.168.1.2",
  "new_level": 4,
  "message": "Hint level updated"
}
```

---

### 3.4 `POST /api/teacher/broadcast` — Teacher sets global hint level

**Request:**
```json
{
  "new_level": 2,
  "session_id": "sess_20260722_1"
}
```

**Response:**
```json
{
  "success": true,
  "affected_students": 50,
  "new_level": 2
}
```

---

### 3.5 `POST /api/teacher/unlock` — Teacher temporarily unlocks Level 5

**Request:**
```json
{
  "student_ip": "192.168.1.2",
  "duration_minutes": 5,
  "reason": "Student has demonstrated understanding"
}
```

**Response:**
```json
{
  "success": true,
  "student_ip": "192.168.1.2",
  "unlocked_until": "2026-07-22T17:57:00Z",
  "message": "Level 5 unlocked for 5 minutes"
}
```

---

### 3.6 `GET /api/summary` — End-of-session analytics

**Query params:** `?session_id=sess_20260722_1`

**Response:**
```json
{
  "session_id": "sess_20260722_1",
  "date": "2026-07-22",
  "total_questions": 87,
  "total_students_who Asked": 28,
  "common_topics": [
    { "topic": "for-loops", "count": 18 },
    { "topic": "array indexing", "count": 12 },
    { "topic": "function parameters", "count": 9 }
  ],
  "common_errors": [
    { "error": "IndexError", "count": 14 },
    { "error": "TypeError", "count": 8 }
  ],
  "ai_summary": "Today, 18 out of 50 students struggled with array indexing. 12 had difficulty with function parameters. The most common error was 'IndexError'. Consider reviewing zero-based indexing tomorrow.",
  "students_needing_followup": ["192.168.1.5", "192.168.1.12", "192.168.1.27"]
}
```

---

### 3.7 `GET /api/health` — Server health check

**Response:**
```json
{
  "status": "healthy",
  "ai_provider": "groq",
  "ai_online": true,
  "database": "connected",
  "uptime_seconds": 3420
}
```

---

## 4. WebSocket Events

Socket.IO connection from Teacher Dashboard to Server at `http://192.168.1.1:8000`

### Server → Client (Dashboard)

| Event Name         | Payload                                       | When                                    |
|--------------------|-----------------------------------------------|-----------------------------------------|
| `student_query`    | `{ ip, seat, question, level, timestamp }`    | Student submits a question via `/api/ask`|
| `level_changed`    | `{ ip, old_level, new_level, by }`            | Teacher changes a level                 |
| `student_active`   | `{ ip, seat, total_queries }`                 | Student connects / first query          |
| `student_idle`     | `{ ip, seat }`                                | No activity for > 5 minutes             |
| `summary_ready`    | `{ session_id, summary_url }`                 | End-of-session summary generated        |
| `server_status`    | `{ ai_online, db_status, uptime }`            | Periodic health heartbeat (every 30s)   |

### Client → Server (Dashboard)

| Event Name              | Payload                                     | Purpose                                |
|-------------------------|---------------------------------------------|----------------------------------------|
| `request_full_status`   | `{}`                                        | Dashboard requests current state       |
| `teacher_level_change`  | `{ student_ip, new_level, session_id }`     | Quick level change via WebSocket       |
| `teacher_broadcast`     | `{ new_level, session_id }`                 | Global level change                    |

---

## 5. Database Schema

SQLite file: `data/codeforge.db`

### Table: `students`

```sql
CREATE TABLE students (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    seat_number   INTEGER NOT NULL UNIQUE,          -- 1–50
    ip_address    TEXT NOT NULL UNIQUE,              -- '192.168.1.2'
    label         TEXT,                              -- Optional: 'Maria', 'Seat 1'
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_active   DATETIME
);
```

### Table: `rules`

```sql
CREATE TABLE rules (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    student_ip      TEXT NOT NULL UNIQUE,             -- FK → students.ip_address
    hint_level      INTEGER DEFAULT 2                 -- 1–5
                    CHECK (hint_level BETWEEN 1 AND 5),
    level_5_unlocked BOOLEAN DEFAULT FALSE,
    unlock_until    DATETIME,                         -- When Level 5 lock expires
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_ip) REFERENCES students(ip_address)
);
```

### Table: `queries`

```sql
CREATE TABLE queries (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    student_ip    TEXT NOT NULL,
    session_id    TEXT NOT NULL,                      -- e.g. 'sess_20260722_1'
    question      TEXT NOT NULL,
    code_snapshot TEXT,                               -- The highlighted code
    file_name     TEXT,
    line_number   INTEGER,
    hint_level    INTEGER NOT NULL,                   -- Level used for response
    ai_response   TEXT NOT NULL,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_ip) REFERENCES students(ip_address)
);
```

### Table: `sessions`

```sql
CREATE TABLE sessions (
    id            TEXT PRIMARY KEY,                   -- 'sess_20260722_1'
    date          DATE NOT NULL,
    started_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    ended_at      DATETIME,
    total_queries INTEGER DEFAULT 0,
    summary_text  TEXT                                -- AI-generated summary
);
```

### Table: `audit_log`

```sql
CREATE TABLE audit_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    action        TEXT NOT NULL,                      -- 'level_change', 'broadcast', 'unlock'
    actor         TEXT NOT NULL,                      -- 'teacher_dashboard', 'system'
    target_ip     TEXT,
    details       TEXT,                               -- JSON blob
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. Deployment Architecture

### Demo Setup (Thesis Prototype)

```
Teacher PC (192.168.1.1)
├── FastAPI server (port 8000)
├── SQLite database
├── Teacher Dashboard (React, served by FastAPI static files)
│
├── Isolated Wi-Fi Hotspot (no internet)
│   └── All students connect to this network
│
Student Laptops (192.168.1.2 – 192.168.1.6)
├── VS Code + CodeForge Extension
├── Static IP assigned manually in Wi-Fi settings
```

**Network isolation:** Students cannot access external AI (ChatGPT, Copilot) because the hotspot has no internet. CodeForge is the sole AI.

**Static IP assignment:** Manually configured on each student laptop:
- Windows: Network Settings → Wi-Fi → Properties → IPv4 → Manual
- Set IP: `192.168.1.X`, Subnet: `255.255.255.0`, Gateway: `192.168.1.1`

---

## 7. Security & Privacy

### 7.1 No Student PII
- Students are identified **only by IP address**. No names, emails, or passwords.
- Optional `label` field is for teacher's reference only (e.g., "Seat 1").
- All data stays on the local SQLite file on the teacher's PC.

### 7.2 IP Spoofing Prevention
- The server validates the **source IP of every HTTP request** against the known student list.
- If a request comes from an unknown IP, it is rejected with `403 Forbidden`.
- The demo network is isolated — external devices cannot reach the server.

### 7.3 Prompt Injection Defense
- Student-submitted code and questions are passed as **user content only** — never interpreted as system instructions.
- System prompts are loaded from trusted files on the server, never from user input.
- All AI responses pass through the rule engine before being returned.

### 7.4 Rate Limiting
- Per-IP limit: **1 question every 30 seconds**.
- Returns HTTP `429 Too Many Requests` with a helpful message.

### 7.5 Level 5 Guard
- Level 5 (Full Answer) is **locked by default** for all students.
- Teacher must explicitly unlock it via `POST /api/teacher/unlock` with an optional time limit.
- All Level 5 unlocks are logged in the audit trail.

### 7.6 CORS Policy
- In production/demo mode: CORS allows only `192.168.1.x` origins.
- For development: `http://localhost:5173` (Vite dev server) is allowed.

---

## 8. AI Prompt Design

### System Prompt Structure

Each hint level has a dedicated prompt file loaded at server startup:

```
server/prompts/
├── level1_socratic.txt
├── level2_hint_giver.txt
├── level3_error_translator.txt
├── level4_logic_explainer.txt
└── level5_full_answer.txt
```

### Base System Prompt (shared by all levels)

```
You are CodeForge, an educational AI assistant in a school computer lab.
You are helping a student learn to code.
Rules:
- Never mention that you are an AI language model.
- Never provide external links or references.
- Be encouraging and patient.
- Keep responses concise (under 200 words unless explaining complex logic).
- If the student asks something unrelated to coding, politely redirect them.
```

### Level-Specific Instructions

| Level | Key Instruction |
|-------|-----------------|
| 1 | "You may ONLY ask guiding questions. Never give answers, hints, or explanations. Guide the student to discover the answer themselves." |
| 2 | "You may give conceptual hints (e.g., 'Think about how loops work'), but never write code or pseudocode." |
| 3 | "Explain what error messages mean in plain English. Never suggest how to fix the error." |
| 4 | "Explain the solution logic in plain English, step by step. Do NOT write any code." |
| 5 | "Provide the complete, correct code solution with a brief explanation." |

---

## 9. File Structure

```
codeforge/
├── server/                         # Python FastAPI backend
│   ├── main.py                     # FastAPI app, CORS, startup
│   ├── models.py                   # SQLAlchemy models (5 tables)
│   ├── database.py                 # DB engine, session factory
│   ├── rule_engine.py              # Loads per-IP rules, enforces levels
│   ├── analytics.py                # Session summary generation
│   ├── rate_limiter.py             # Per-IP rate limiting middleware
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py                 # AIProvider abstract class
│   │   ├── groq_provider.py        # Groq cloud API
│   │   └── ollama_provider.py      # Local Ollama API
│   ├── prompts/
│   │   ├── base_system.txt         # Shared system prompt
│   │   ├── level1_socratic.txt
│   │   ├── level2_hint_giver.txt
│   │   ├── level3_error_translator.txt
│   │   ├── level4_logic_explainer.txt
│   │   └── level5_full_answer.txt
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── student.py              # POST /api/ask
│   │   └── teacher.py              # /api/teacher/*, /api/status, /api/summary
│   ├── websocket_events.py         # Socket.IO event handlers
│   └── requirements.txt
│
├── extension/                      # VS Code Extension (TypeScript)
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── extension.ts            # Extension entry point
│       ├── sidebarProvider.ts      # Sidebar webview (question UI)
│       └── apiClient.ts            # HTTP client to talk to server
│
├── dashboard/                      # Teacher Dashboard (React + Vite)
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── components/
│       │   ├── StudentGrid.jsx     # Live grid of 50 seats
│       │   ├── StudentCard.jsx     # Individual seat card
│       │   ├── RulePanel.jsx       # Level adjustment controls
│       │   └── SummaryView.jsx     # End-of-session summary
│       └── hooks/
│           └── useSocket.js        # Socket.IO connection hook
│
├── tests/
│   ├── test_api.py
│   ├── test_rule_engine.py
│   └── test_analytics.py
│
├── data/                           # Runtime data (gitignored)
│   └── codeforge.db
│
├── docs/
│   ├── architecture.md             # This file
│   └── user_guide.md               # Teacher's user guide
│
├── .gitignore
├── README.md
└── DEVELOPMENT_SESSION_LOG.md
```

---

## Appendix A: IP Address Mapping

| Seat # | IP Address   | Teacher Reference |
|--------|-------------|-------------------|
| —      | 192.168.1.1 | Teacher PC (server) |
| 1      | 192.168.1.2 | Student 1         |
| 2      | 192.168.1.3 | Student 2         |
| ...    | ...         | ...               |
| 50     | 192.168.1.51 | Student 50       |

---

## Appendix B: Session ID Format

```
sess_{YYYYMMDD}_{session_number}
```
Example: `sess_20260722_1` for the first session on July 22, 2026.

---

*This document is the single source of truth for all implementation decisions. All code must conform to this architecture.*
