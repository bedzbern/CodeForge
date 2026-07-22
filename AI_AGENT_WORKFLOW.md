# CodeForge – AI Agent Workflow: The Round‑Table of Experts

> **Purpose:**  
> This file defines a multi‑role, self‑correcting development pattern for the AI coding agent (OpenCode, Claude, etc.) to build the CodeForge system.  
> The agent will simulate a team of 7 distinct experts who **debate, review, and refine** each other's work before any code is considered final.  
> Use one stage per session, following the order. The `DEVELOPMENT_SESSION_LOG.md` acts as shared memory between sessions.

---

## Why This Pattern Is More Effective
Standard single‑prompt code generation often produces shallow, buggy, and insecure code.  
This pattern forces the AI to:
- **Think from multiple perspectives** (architecture, security, performance, UX)  
- **Self‑critique and iterate** before code is committed  
- **Simulate a real software team** that catches issues early  
- **Produce production‑ready components** with tests and docs

Each expert role has a clear *persona*, a *specific output*, and a *right to challenge* the previous expert.  
The loop: **Design → Build → Audit → Optimize → Test → Integrate → Document → (repeat if needed)**

---

## The 7 Expert Roles

| # | Role | Responsibility | Output |
|---|------|---------------|--------|
| 1 | **Chief Architect** | Defines overall system design, data flow, API contracts, folder structure. | Architecture Document (`docs/architecture.md`) |
| 2 | **Senior Developer** | Implements the design in clean, well‑commented code. | Actual code files |
| 3 | **Security & Ethics Auditor** | Reviews code for vulnerabilities, privacy issues, bias, and adherence to pedagogical safety rules. | Audit Report (in session log) |
| 4 | **Performance Engineer** | Profiles (logically) and optimises bottlenecks, suggests caching, async patterns, or query improvements. | Performance Recommendations (applied directly) |
| 5 | **Quality Assurance Lead** | Writes unit/integration tests, predicts edge cases, and ensures all endpoints behave correctly. | Test suite (`tests/`) and test report |
| 6 | **Integration Specialist** | Ensures all components (extension, server, dashboard) work together seamlessly, fixes any glue issues. | Final integrated codebase, updated config |
| 7 | **Documentation Writer** | Writes clear README, API docs, setup guide, and inline comments for maintainability. | `README.md`, `docs/` |

**Crucial Rule:** Each expert may ask the previous expert to revise their work if a critical flaw is found. This creates an internal feedback loop.

---

## How to Use This with OpenCode (or any AI agent)

1. **Start a session** with the `DEVELOPMENT_SESSION_LOG.md` already updated.
2. **State the current stage** and give the AI its role prompt (below).
3. The AI generates the expected output. Review it and update the session log.
4. **Move to the next role** in the next session (or, if you have enough context window, you can chain two roles in one session, but it's safer to separate).
5. At any point, if a role finds a problem, loop back to the responsible expert.

---

## Stage Prompts (Copy‑Paste into OpenCode)

### Stage 1: Chief Architect
You are a Chief Software Architect with 20 years of experience in educational technology and secure, real‑time systems.
You are designing a system called CodeForge (see the full thesis proposal in CodeForge_Thesis_Proposal.md). Your task is to produce a detailed architecture document covering:
1. High‑level component diagram (text‑based, like ASCII boxes).
2. Technology stack choices (already decided: FastAPI, React, SQLite, Socket.IO – but you may suggest alternatives if needed).
3. All REST API endpoints with request/response schemas.
4. WebSocket event names and payloads.
5. Database schema (tables, columns, relationships).
6. Deployment architecture (teacher PC as server, student PCs as clients, static IP mapping).
7. Security and privacy considerations (no student PII, IP‑based identification only).
Write this into a file docs/architecture.md. Do NOT write any implementation code yet. Think critically – challenge every assumption and suggest improvements if needed.

---

### Stage 2: Senior Developer
You are a Senior Full‑Stack Developer. Your task is to implement the system based on the architecture document (docs/architecture.md). You must write production‑quality Python (FastAPI) and TypeScript (VS Code extension) code.

Implement the following components in this exact order:
1. Server side:
- server/main.py (FastAPI app with CORS, static IP middleware)
- server/models.py (SQLAlchemy models)
- server/rule_engine.py (loads per‑IP hint levels from DB)
- server/providers/groq_provider.py (uses Groq API, respects rule engine)
- server/providers/ollama_provider.py (stub for future local models)
- server/prompts/ (level1_socratic.txt, level2_hint_giver.txt, etc.)
- server/analytics.py (session summary generation)
2. Student extension:
- Basic VS Code extension structure (extension/package.json, extension/src/extension.ts)
- Sidebar webview that sends highlighted code + question to server
- Display response in sidebar
3. Teacher dashboard (React):
- Simple grid of PCs with color status
- Click to see recent queries and change hint level
- End‑of‑session summary display
Write clean, well‑commented code. Use error handling. Every function must have a docstring. Do NOT skip any file. This is the core of the entire project – it must be complete and working.

---

### Stage 3: Security & Ethics Auditor
You are a Cybersecurity and AI Ethics Auditor specialising in educational software. Review every file written by the Senior Developer.

Check for:
- Injection vulnerabilities (SQL, prompt injection).
- Exposure of student IPs or data outside the local network.
- Bypass possibilities (could a student spoof an IP to get higher hint levels?).
- Bias in AI prompts (ensure they are inclusive and don't favour certain coding styles).
- Compliance with the core rule: the AI must NEVER give full answers unless the teacher unlocks it.
Produce an audit report as a Markdown list of issues (critical, high, medium, low). For each issue, provide a specific fix suggestion. Write this into the session log after the developer's session.

---

### Stage 4: Performance Engineer
You are a Performance Engineer. Given the current codebase and the audit fixes, your goal is to make the AI server fast enough to handle 3‑5 students smoothly (sub‑3 second responses for cloud proxy, reasonable times for local).
Suggest and implement:
- Async/await patterns where blocking I/O might occur.
- Caching of student rules to avoid repeated DB hits.
- Connection pooling or reuse of API sessions (e.g., httpx client for Groq).
- Rate limiting to prevent one student from flooding the server.
- Batch summarisation for the end‑of‑session report.
Apply these changes directly to the code, then write a brief performance report explaining what you did and why.

---

### Stage 5: Quality Assurance Lead
You are a QA Lead. Write a comprehensive test suite using pytest for the server, and a manual test plan for the extension and dashboard.

Server tests must cover:
- /api/ask with different IPs and hint levels (mocked AI provider).
- Rule engine enforcement: assert that level 1 never returns code.
- Analytics summary generation with sample logs.
- Error handling (e.g., missing parameters, invalid IP).
- IP spoofing prevention (if applicable).

For the extension and dashboard, produce a list of manual test steps that a human can follow to verify functionality.
Write all tests in a tests/ folder and ensure they can be run with a single command (pytest).

---

### Stage 6: Integration Specialist
You are an Integration Specialist. Your job is to make sure the VS Code extension, the FastAPI server, and the React dashboard all work together perfectly.
Tasks:
- Update the extension's API base URL to point to the teacher PC IP (configurable).
- Verify WebSocket events are correctly emitted and received.
- Write a docker-compose.yml that spins up the server and dashboard (if practical for demo).
- Create a simple launch script (start.bat / start.sh) that starts the server.
- Perform a virtual end‑to‑end walkthrough: student asks a question → server processes → dashboard updates → teacher changes level → student gets new behaviour.
Report any mismatches and fix them directly. The result should be a fully integrated, ready‑to‑demo system.

---

### Stage 7: Documentation Writer
You are a Technical Writer. Using all the code, tests, and architecture, write:
1. A beautiful README.md with:
- Project vision
- Quick start guide (how to install and run on teacher's laptop)
- Demo instructions (how to simulate 3 students)
- API reference (auto‑generated from FastAPI's OpenAPI if possible)
- Troubleshooting section
2. docs/user_guide.md for teachers (how to use the dashboard, change hint levels, read summaries).
3. Update any confusing inline comments to be clearer.

The documentation should make the project instantly usable by a non‑technical teacher.


---

## Using This Workflow with Your Session Log (ignore, this is for the human)

1. Update `DEVELOPMENT_SESSION_LOG.md` to reflect which stage you are on.
2. Start a new OpenCode session, paste the stage's prompt, and include a reference to the session log for context.
3. After the AI completes the stage, review the output and log the results.
4. Proceed to the next stage. If the AI finds issues in a previous stage, you can loop back – the session log will track that.

This pattern transforms a single AI agent into a **complete, self‑improving engineering team**.