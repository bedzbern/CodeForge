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
- [ ] AI Server basic scaffold (FastAPI running)
- [ ] Database models implemented
- [ ] Rule engine core logic implemented
- [ ] AI Provider abstraction implemented
- [ ] Student extension basic UI and HTTP communication
- [ ] Teacher dashboard basic grid and live updates
- [ ] End‑to‑end integration tested (3 PCs)
- [ ] Session summary feature working

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

**Next session tasks:**
- **Stage 2: Senior Developer** — Implement server components:
  1. `server/database.py` — SQLAlchemy engine and session factory
  2. `server/models.py` — All 5 SQLAlchemy models
  3. `server/rule_engine.py` — Load per-IP rules, enforce hint levels
  4. `server/providers/base.py` — `AIProvider` abstract class
  5. `server/providers/groq_provider.py` — Groq API client
  6. `server/providers/ollama_provider.py` — Ollama API client (stub)
  7. `server/prompts/` — All 6 prompt files
  8. `server/main.py` — FastAPI app with CORS, startup, routes
  9. `server/routers/student.py` — POST /api/ask
  10. `server/routers/teacher.py` — Teacher endpoints
  11. `server/rate_limiter.py` — Per-IP rate limiting
  12. `server/websocket_events.py` — Socket.IO handlers
  13. `server/analytics.py` — Session summary generation

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
1. [ ] Implement `server/database.py` — SQLAlchemy engine and session factory
2. [ ] Implement `server/models.py` — All 5 SQLAlchemy models
3. [ ] Implement `server/rule_engine.py` — Load per-IP rules, enforce hint levels
4. [ ] Implement `server/providers/base.py` — `AIProvider` abstract class
5. [ ] Implement `server/providers/groq_provider.py` — Groq API client
6. [ ] Implement `server/providers/ollama_provider.py` — Ollama API client (stub)
7. [ ] Create `server/prompts/` — All 6 prompt files
8. [ ] Implement `server/main.py` — FastAPI app with CORS, startup, routes
9. [ ] Implement `server/routers/student.py` — POST /api/ask
10. [ ] Implement `server/routers/teacher.py` — Teacher endpoints
11. [ ] Implement `server/rate_limiter.py` — Per-IP rate limiting
12. [ ] Implement `server/websocket_events.py` — Socket.IO handlers
13. [ ] Implement `server/analytics.py` — Session summary generation
14. [ ] Scaffold VS Code extension with a sidebar webview
15. [ ] Set up Teacher Dashboard (React + Vite)
16. [ ] End-to-end integration testing

---

*This file is alive. It grows with the project. The AI agent relies on it to be an effective partner.*