# CodeForge – Development Session Log

> **Purpose:**  
> This file is the single source of truth for the CodeForge project's development state.  
> The AI coding agent (and you, the developer) must read this entire file at the start of every session to understand what has been done and what to work on next.  
> At the end of each session, update this file with a summary of accomplishments and the next tasks.

---

## Project Overview
- **Goal:** Build a teacher-controlled, IP‑based AI coding assistant for school computer labs.
- **Core Components:**
  1. VS Code Student Extension (TypeScript)
  2. AI Server + Rule Engine + Analytics (Python, FastAPI)
  3. Teacher Dashboard (React or vanilla JS)
  4. Network setup (demo with static IPs on an isolated hotspot)
- **Tech Stack:** (see main proposal Section 5)
- **AI Backend Abstraction:** `AIProvider` interface with `OllamaProvider` and `GroqProvider`.

---

## Current Overall Status
- [x] Project repository initialized
- [x] Architecture document completed (`docs/architecture.md`)
- [x] AI Server full scaffold (FastAPI running)
- [x] Database models implemented (5 tables)
- [x] Rule engine core logic implemented
- [x] AI Provider abstraction implemented (Groq + Ollama)
- [x] Rate limiter implemented
- [x] Analytics / session summary implemented
- [x] All 7 REST API endpoints implemented
- [x] Socket.IO events implemented
- [x] All 6 AI prompt files created
- [ ] Student extension basic UI and HTTP communication
- [ ] Teacher dashboard basic grid and live updates
- [ ] End‑to‑end integration tested (3 PCs)
- [ ] Session summary feature verified live

*Last updated: 2026-07-22*

---

## Session History

### Session 1 – 2026-07-22 (Chief Architect)
**What we did:**
- Created complete architecture document: `docs/architecture.md`
- Defined all 7 REST API endpoints with request/response schemas
- Defined 6 WebSocket events for real-time dashboard updates
- Designed 5-table SQLite schema (students, rules, queries, sessions, audit_log)
- Designed AI prompt structure (5 levels + base system prompt)
- Mapped out full file structure for server, extension, and dashboard
- Documented security and privacy measures (IP validation, rate limiting, Level 5 guard)

**Decisions made:**
- Architecture follows the thesis proposal exactly (FastAPI + React + SQLite + Socket.IO)
- AI Provider abstraction: `AIProvider` ABC with `GroqProvider` and `OllamaProvider`
- Students identified by IP only — no PII stored
- Rate limiting: 1 question per 30 seconds per IP
- Level 5 locked by default; teacher must unlock with optional time limit

**Files created/changed:**
- `docs/architecture.md` (complete architecture document)

---

### Session 2 – 2026-07-22 (Senior Developer)
**What we did:**
- Implemented the complete AI server backend:
  - `server/database.py` — SQLAlchemy engine, session factory, `init_db()`, `get_db()` dependency
  - `server/models.py` — 5 SQLAlchemy models: Student, Rule, Query, Session, AuditLog
  - `server/rule_engine.py` — get_or_create_rule, get_effective_level, set_hint_level, broadcast_level, unlock_level_5
  - `server/providers/base.py` — AIProvider abstract class (generate, health_check)
  - `server/providers/groq_provider.py` — Async Groq cloud API via httpx
  - `server/providers/ollama_provider.py` — Async local Ollama API via httpx
  - `server/prompts/` — 6 prompt files (base_system, level1-5)
  - `server/routers/student.py` — POST /api/ask (rate limit, rule engine, AI generation, query logging)
  - `server/routers/teacher.py` — GET /api/status, POST /teacher/level, /teacher/broadcast, /teacher/unlock, GET /api/summary, GET /api/health
  - `server/rate_limiter.py` — Per-IP rate limiter (30s default)
  - `server/websocket_events.py` — Socket.IO: connect/disconnect, request_full_status, teacher_level_change, teacher_broadcast, emit helpers
  - `server/analytics.py` — compute_session_stats, generate_summary_text, create_session_summary
  - `server/main.py` — FastAPI app with CORS, lifespan, provider init, router registration, Socket.IO ASGI wrapping
  - `server/requirements.txt` — FastAPI, uvicorn, SQLAlchemy, pydantic, httpx, python-socketio
  - `.gitignore` — __pycache__, .env, data/, node_modules/

**Decisions made:**
- Provider selected via `AI_PROVIDER` env var (default: groq)
- CORS allows localhost:5173 (Vite dev) and 192.168.1.x (lab network)
- Session auto-created on first query of the day
- Health check endpoint returns provider type and uptime
- Socket.IO events use AsyncServer with ASGI wrapping

**Files created/changed:**
- `server/database.py`
- `server/models.py`
- `server/rule_engine.py`
- `server/providers/base.py`
- `server/providers/groq_provider.py`
- `server/providers/ollama_provider.py`
- `server/providers/__init__.py`
- `server/prompts/base_system.txt`
- `server/prompts/level1_socratic.txt`
- `server/prompts/level2_hint_giver.txt`
- `server/prompts/level3_error_translator.txt`
- `server/prompts/level4_logic_explainer.txt`
- `server/prompts/level5_full_answer.txt`
- `server/routers/__init__.py`
- `server/routers/student.py`
- `server/routers/teacher.py`
- `server/rate_limiter.py`
- `server/websocket_events.py`
- `server/analytics.py`
- `server/main.py`
- `server/requirements.txt`
- `.gitignore`
- `server/__init__.py`

**Next session tasks:**
- **Stage 3: Security & Ethics Auditor** — Review all server code for vulnerabilities
  - SQL injection risks
  - Prompt injection vectors
  - IP spoofing possibilities
  - Rate limiter bypasses
  - CORS misconfigurations
  - Level 5 guard enforcement
  - PII exposure risks
  - Audit report with severity ratings and fix suggestions

---

*[Add new sessions below using the template.]*

---

## Session Template

### Session X – [Date]
**What we did:**
- ...

**Decisions made:**
- ...

**Files created/changed:**
- ...

**Next session tasks:**
- ...

---

## Rules for the AI Coding Agent
1. **Read this entire file first** before suggesting any code.
2. **Follow the architecture** defined in the main proposal. Do not introduce new frameworks without discussion.
3. **Keep components modular:** server, extension, dashboard remain separate directories with clear interfaces.
4. **Write explanatory comments** in generated code — I need to understand every part.
5. **Prefer small, testable increments.** One feature at a time.
6. **When uncertain, ask.** I provide the pedagogical intent; you translate it into code.
7. **Update this session log at session end** (summary + next tasks), pending my approval.

---

## Current Task Queue (Prioritized)
1. [x] ~~Implement `server/database.py`~~
2. [x] ~~Implement `server/models.py`~~
3. [x] ~~Implement `server/rule_engine.py`~~
4. [x] ~~Implement `server/providers/base.py`~~
5. [x] ~~Implement `server/providers/groq_provider.py`~~
6. [x] ~~Implement `server/providers/ollama_provider.py`~~
7. [x] ~~Create `server/prompts/`~~
8. [x] ~~Implement `server/main.py`~~
9. [x] ~~Implement `server/routers/student.py`~~
10. [x] ~~Implement `server/routers/teacher.py`~~
11. [x] ~~Implement `server/rate_limiter.py`~~
12. [x] ~~Implement `server/websocket_events.py`~~
13. [x] ~~Implement `server/analytics.py`~~
14. [ ] **Stage 3: Security & Ethics Auditor** — Review server code for vulnerabilities
15. [ ] **Stage 4: Performance Engineer** — Async patterns, caching, connection pooling
16. [ ] **Stage 5: QA Lead** — pytest test suite for server
17. [ ] Scaffold VS Code extension with a sidebar webview
18. [ ] Set up Teacher Dashboard (React + Vite)
19. [ ] End-to-end integration testing

---

*This file is alive. It grows with the project. The AI agent relies on it to be an effective partner.*