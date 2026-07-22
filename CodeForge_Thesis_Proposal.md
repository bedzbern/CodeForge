# CodeForge: A Teacher-Controlled AI Assistant That Bridges the Gap Between Silent Students and Busy Teachers

**Thesis Proposal**  
*Prepared by [Your Name]*  
*Date: [Insert Date]*  
*Development Approach: AI-Assisted (Human + AI Coding Agent)*

---

## 1. The Twin Problems We Must Solve

### Problem A: The AI Over-Reliance Crisis
Students in computer laboratories have begun outsourcing their thinking to unrestricted AI tools (ChatGPT, Copilot).  
They paste answers without understanding. Their problem-solving skills atrophy.  
Banning AI completely is a short-term fix that leaves graduates unprepared for an AI-saturated workforce.

### Problem B: The Invisible Struggles of the Silent Student
In every lab, shy students never raise their hands. They fear judgment.  
Teachers can only help those who speak up. The silent ones fall behind, unseen.  
Our classrooms reward loudness and punish shyness. That is unfair.

**CodeForge solves both problems together.**

---

## 2. Our Solution: More Than a Guardrail, a Bridge

CodeForge is a school-hosted, teacher-controlled AI assistant that lives entirely inside the lab network.  
It is the **only AI tool available** to students during lab sessions.  
It replaces unrestricted public AI with a scaffolded mentor that:

- Gives hints, not answers, under the teacher's strict control.
- Provides a private, judgment-free way for students to ask for help.
- Gives the teacher a real-time dashboard that *sees* invisible struggles — connecting the quiet student with the busy teacher.

**Core Rule:**  
*The AI never gives full code unless the teacher explicitly unlocks it. But it always listens. And the teacher always sees.*

---

## 3. How It Works (Panel-Friendly Explanation)

### 3.1 Digital Seat Numbers
Every lab PC has a permanent local IP address (like a seat number).  
Computer 1 = `192.168.1.2`, Computer 2 = `192.168.1.3` … up to 50.  
The system knows exactly which student is asking, without logins.

### 3.2 A Private Hand Raise
When Maria types a question into the CodeForge panel inside her coding editor, only she sees the answer. No classmate knows.  
But on the teacher's dashboard, Maria's seat softly turns yellow.  
The teacher sees: *“Maria has asked three questions about for-loops in 10 minutes.”*  
The teacher walks over and says, *“I noticed you're working on loops. Want to talk it through?”*  
That conversation would never have happened otherwise.

### 3.3 The Whole-Class Pulse
At the end of the session, the dashboard delivers an AI-generated summary:  
*“Today, 18 out of 50 students struggled with array indexing. 12 had difficulty with function parameters. The most common error was ‘IndexError’.”*  
The teacher now knows exactly what to reteach — not from a hunch, but from real, silent data.

### 3.4 The Five Levels of AI Help (Training Wheels)

| Level | Name | Behaviour |
|-------|------|-----------|
| 1 | Socratic Mirror | Only asks guiding questions. |
| 2 | Hint Giver | Gives conceptual nudges. |
| 3 | Error Translator | Explains error messages, no fixes. |
| 4 | Logic Explainer | Plain-English solution, no code. |
| 5 | Full Answer | Writes code. **Locked. Only the teacher can unlock.** |

The teacher sets a global level, or per-student exceptions.

---

## 4. System Architecture (Technical Overview)
┌──────────────────────────────────────────────────────────┐
│ SCHOOL COMPUTER LAB                                      │
│ (Students only have access to the local AI server)       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ ┌──────────────┐ ┌─────────────────────────────────────┐ │
│ │ TEACHER PC   │ │         STUDENT PCs (1–50)          │ │
│ │ (192.168.1.1)│ │        (192.168.1.2 – .51)          │ │
│ │              │ │                                     │ │
│ │ ┌─────────┐  │ │ ┌─────────────────────────────────┐ │ │
│ │ │Dashboard│  │ │ │ VS Code +                       │ │ │
│ │ │(Web UI) │  │ │ │ CodeForge Extension             │ │ │
│ │ │         │  │ │ │ (Student Mode)                  │ │ │
│ │ │•Grid    │  │ │ └──────────┬──────────────────────┘ │ │
│ │ │•Rules   │  │ │            │                        │ │
│ │ │•Summary │  │ │            │ HTTP/WS                │ │
│ │ └────┬────┘  │ │            ▼                        │ │
│ └──────┼───────┘ │ ┌─────────────────────────────────┐ │ │
│        │         │ │ LOCAL AI SERVER                 │ │ │
│        └──── REST API ───┼─┤ • FastAPI               │ │ │
│                  │ │ • Rule Engine                   │ │ │
│                  │ │ • LLM (Ollama/API)              │ │ │
│                  │ │ • Analytics Engine              │ │ │
│                  │ └─────────────────────────────────┘ │ │
│                  └─────────────────────────────────────┘ │
│                                                          │
│ (The lab environment ensures that no external AI         │
│ websites are reachable. CodeForge is the sole AI.)       │
└──────────────────────────────────────────────────────────┘

### 4.1 Key Components
1. **Student Extension** – VS Code plugin. Sends highlighted code + question to the local server. No autocomplete.
2. **Local AI Server** – Processes requests through an LLM, respecting the rule engine.
3. **Rule Engine & Analytics** – Enforces hint levels per IP, logs all queries, generates end-of-session summaries.
4. **Teacher Dashboard** – Real-time web interface: live status grid, per-student rule adjustment, session summary.

---

## 5. Technology Stack (Zero‑Cost, Open‑Source)

| Component               | Language     | Frameworks / Libraries                         | External Service                   |
|-------------------------|--------------|------------------------------------------------|------------------------------------|
| Student Extension       | TypeScript   | VS Code Ext API, axios, socket.io-client       | –                                  |
| AI Server + Rule Engine | Python 3.10+ | FastAPI, uvicorn, SQLAlchemy, python-socketio  | Groq API (free) or Ollama (local)  |
| Teacher Dashboard       | JavaScript   | React (Vite) or vanilla JS, socket.io-client   | –                                  |
| Real-Time Communication | –            | Socket.IO (server + client)                    | –                                  |
| Database                | –            | SQLite3                                        | –                                  |
| Network Setup (Demo)    | –            | Static IPs on isolated Wi‑Fi hotspot           | –                                  |
| AI Summarization        | –            | Same LLM provider                              | –                                  |
| Version Control         | –            | Git + GitHub (public repo)                     | –                                  |

**AI Backend Abstraction:**  
A common `AIProvider` interface allows swapping between:
- `OllamaProvider` (fully local, slower but offline)
- `GroqProvider` (free cloud API, fast)

---

## 6. Development Methodology: Building CodeForge with AI Assistance

As a game developer, I bring strong design thinking but am still learning advanced full‑stack coding.  
To build a robust thesis prototype, I will employ an **AI‑assisted development workflow** using modern AI coding agents (e.g., OpenCode, Cursor, or similar).

### 6.1 Why This Approach Is Justified
- **Speed & Accuracy:** AI agents can scaffold boilerplate, suggest architectures, and debug errors rapidly.
- **Learning Opportunity:** I will review, understand, and modify every line generated. This is a guided learning experience, not blind copy‑pasting.
- **Meta‑Relevance:** The thesis itself becomes a case study in human‑AI collaboration — building a tool to teach responsible AI use, while being built with AI responsibly.

### 6.2 How It Works in Practice
1. **Session‑Log System:** A dedicated `DEVELOPMENT_SESSION_LOG.md` file is maintained. At the start of every coding session, the AI agent reads this file to understand the current state.
2. **Architecture First:** I define the architecture, data flow, and prompts. The agent generates code modules accordingly.
3. **Incremental & Testable:** Each component is built in small, testable increments.
4. **Human Review:** No code is merged without my understanding and manual testing.
5. **Full Transparency:** The thesis will explain this methodology, emphasizing that the intellectual design and pedagogical innovation are entirely my own.

---

## 7. Implementation Plan

### 7.1 Prototype (Thesis Demo) – $0 Budget
- **Hardware:** 1 teacher PC + 3–5 student laptops, connected via an isolated Wi‑Fi hotspot (no internet, fully controlled network). Static IPs assigned manually.
- **AI Backend:** Groq Cloud free tier (fast, no GPU needed) for the live demo. A local Ollama instance will also be shown to prove the offline concept.
- **Software Scope:** Student extension, AI server with rule engine, teacher dashboard with live grid and summary.

### 7.2 Full‑Scale Deployment (Future)
Requires a GPU server ($6,000–$10,000). The prototype architecture scales directly.

### 7.3 Development Timeline (8–12 weeks)
- Weeks 1–2: Finalize architecture, set up development environment, configure AI agent session tracking.
- Weeks 3–6: Build AI server + rule engine + student extension (with AI assistance).
- Weeks 7–10: Build teacher dashboard, integrate real‑time updates.
- Weeks 11–12: Testing, evaluation, thesis writing.

---

## 8. Honest Limitations
1. **Hardware Cost:** Full‑scale local AI requires a GPU server. The thesis uses a free cloud proxy to prove the concept.
2. **AI Quality on CPU:** A truly offline local model is slower. We document both paths.
3. **Student Circumvention:** A student with a mobile phone could theoretically access external AI. CodeForge creates a *preferred*, supportive alternative that makes external tools less tempting.
4. **Content Safety:** Local models can occasionally give incorrect advice. Future work includes output filtering.

---

## 9. Evaluation
A controlled experiment with volunteer students:
- Compare CodeForge vs. unrestricted AI usage.
- Measure: code comprehension scores, frequency of help‑seeking, teacher's ability to spot struggling students.
- Collect qualitative feedback from students and teacher.

**Success Criteria:**
- AI obeys teacher‑set hint levels per seat.
- Shy students report feeling safer asking for help.
- Teacher identifies silent struggles and adjusts teaching using the session summary.

---

## 10. Closing Vision (For the Panel)

*“Panelists, imagine Maria. She never raises her hand. She’s lost, and no one knows. With CodeForge, she types a quiet question to a private AI. No classmate sees. But a small yellow light appears on the teacher’s screen. That light is an invitation — for the teacher to walk over and say, ‘I noticed you’re working on loops. Let’s figure it out together.’ That human connection never happened before. It happened because technology chose to be humble. To guide. To connect. We are not building a smarter AI. We are building a more human classroom.”*

---

## 11. Conclusion
CodeForge directly answers the twin crises of AI dependency and invisible student struggles.  
It reshapes AI into a tool that respects teacher authority, encourages genuine thinking, and gives every student a private, fear‑free way to reach out.  
This thesis will deliver a working prototype, a scalable architecture, and a proven model for how AI can bring students and teachers closer — not further apart.