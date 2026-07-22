# CodeForge — Teacher's Guide

Welcome to CodeForge! This guide explains how to use the Teacher Dashboard to monitor your students, control AI assistance levels, and get insights from each lab session.

---

## What Is CodeForge?

CodeForge is an AI coding assistant that runs entirely on your school's local network. Unlike ChatGPT or Copilot, CodeForge:

- **Gives hints, not answers** — by default, the AI asks guiding questions instead of writing code for students
- **Keeps you in control** — you decide how much help each student gets, from 1 (questions only) to 5 (full code)
- **Shows you everything** — a live dashboard tells you which students are asking questions and about what
- **Stays private** — no student data leaves the school network; no accounts or logins needed

Students use it through a panel inside their code editor (VS Code). You use it through a web dashboard in your browser.

---

## Getting Started

### First time setup (one-time)

1. **Start the server** on your teacher PC:
   - Double-click `start.bat` (Windows) or run `./start.sh` (Mac/Linux)
   - A terminal window opens — leave it running during class

2. **Open the dashboard** in your browser:
   - Double-click `start-dashboard.bat`
   - Or go to `http://localhost:5173`

3. **Register student computers** — see [Registering Students](#registering-students) below

### Starting a lab session

1. Turn on the Wi-Fi hotspot on your teacher PC
2. Have students connect to the hotspot and set their static IPs
3. Start the server (`start.bat` or `./start.sh`)
4. Open the dashboard in your browser
5. You should see student cards appear as they start asking questions

---

## The Dashboard

### Grid View

The main screen shows a grid of 50 seats. Each seat card displays:

- **Seat number** (1-50)
- **IP address** (e.g., 192.168.1.2)
- **Current hint level** (color-coded: green=1, blue=2, orange=3, purple=4, red=5)
- **Question count** today
- **Status dot** (green = active in last 5 minutes, gray = idle)

The stats bar at the top shows total students, active count, and idle count.

### Changing a Student's Level

1. **Click a student card** in the grid
2. The **Rule Panel** appears above the grid
3. Use the dropdown to select a new level (1-5)
4. Click **Apply**

The student's next question will use the new level immediately.

### Quick Level Actions

In the Rule Panel, you also have quick-action buttons:

- **Broadcast Level 1/2/3** — Sets ALL students to that level at once (great for exams or reviews)
- **Unlock L5 (5/10/30 min)** — Temporarily gives one student access to full code answers. The unlock expires automatically.

### Session Summary

Click the **Session Summary** tab to see analytics for the current session:

- **Total questions** asked
- **Students who asked** — how many students used the system
- **Common topics** — a bar chart of what students are asking about
- **Common errors** — which error types appear most often
- **AI Summary** — a plain-English paragraph summarizing the session
- **Students needing follow-up** — IPs of students who may need extra help

---

## The Five Hint Levels

| Level | Name | What the AI Does | When to Use |
|-------|------|-----------------|-------------|
| 1 | Socratic Mirror | Only asks questions — "What do you think `range()` returns here?" | When you want students to think through problems themselves |
| 2 | Hint Giver | Gives conceptual nudges — "Think about zero-based indexing" | Default level; gentle guidance without answers |
| 3 | Error Translator | Explains error messages in plain English — "IndexError means your list index is out of bounds" | When students are stuck on confusing error messages |
| 4 | Logic Explainer | Explains the solution step by step in words — no code | When students understand the problem but need a logic roadmap |
| 5 | Full Answer | Writes complete, correct code | **Locked by default.** Only use when a student has demonstrated understanding and needs to move on |

### Recommendation

- Start most students at **Level 2** (the default)
- Move struggling students to **Level 1** to force more thinking
- Move advanced students to **Level 3 or 4** to keep them progressing
- Use **Level 5** sparingly — only when a student is genuinely stuck and has tried

---

## Registering Students

Before students can use CodeForge, their computers must be registered. You only need to do this once per computer.

### Option A: Using the dashboard (future)

Coming soon — the dashboard will have a student management panel.

### Option B: Using the command line

Open a terminal on the teacher PC and run:

```bash
python -c "
from server.database import init_db, SessionLocal
from server.models import Student, Rule
init_db()
db = SessionLocal()

# Register 5 students (adjust IPs to match your lab)
students = [
    (1, '192.168.1.2', 'Student 1'),
    (2, '192.168.1.3', 'Student 2'),
    (3, '192.168.1.4', 'Student 3'),
    (4, '192.168.1.5', 'Student 4'),
    (5, '192.168.1.6', 'Student 5'),
]

for seat, ip, label in students:
    db.add(Student(seat_number=seat, ip_address=ip, label=label))
    db.add(Rule(student_ip=ip, hint_level=2))

db.commit()
print('Done! Registered', len(students), 'students.')
"
```

Adjust the IP addresses to match your lab's configuration.

### Option C: Using the API directly

```bash
# Add a student
curl -X POST http://192.168.1.1:8000/api/teacher/add_student \
  -H "Content-Type: application/json" \
  -d '{"seat_number": 1, "ip_address": "192.168.1.2", "label": "Student 1"}'
```

---

## Static IP Setup for Student PCs

Each student computer needs a static IP address on the `192.168.1.x` network.

### Windows

1. Open **Settings** → **Network & Internet** → **Wi-Fi**
2. Click the connected network → **Properties**
3. Scroll to **IP assignment** → click **Edit**
4. Select **Manual**
5. Enter:
   - IP address: `192.168.1.X` (where X is 2-51)
   - Subnet mask: `255.255.255.0`
   - Gateway: `192.168.1.1`
6. Save

### Mac

1. Open **System Preferences** → **Network**
2. Select Wi-Fi → **Advanced** → **TCP/IP** tab
3. Configure IPv4: **Manually**
4. Enter the IP, subnet mask (255.255.255.0), and router (192.168.1.1)
5. OK → Apply

---

## AI Provider Options

### Groq (Recommended for demos)

- Cloud-based, fast (1-3 second responses)
- Free tier available at [console.groq.com](https://console.groq.com)
- Requires internet connection on the teacher PC
- Set `AI_PROVIDER=groq` and `GROQ_API_KEY=your_key`

### Ollama (Offline / slow)

- Runs locally on the teacher PC — no internet needed
- Slower without a GPU (5-30 seconds per response)
- Good for testing or when internet is unavailable
- Install Ollama from [ollama.ai](https://ollama.ai), then: `ollama pull llama3`
- Set `AI_PROVIDER=ollama`

---

## Frequently Asked Questions

**Q: Can students see each other's questions?**
No. Each student sees only their own conversation in their VS Code sidebar.

**Q: Can students bypass the hint levels?**
No. The server enforces levels for every request. Even if a student modifies the extension, the server controls the AI's behaviour.

**Q: What if a student asks something unrelated to coding?**
The AI politely redirects them back to coding topics.

**Q: Can I see which students are NOT asking questions?**
Yes. On the dashboard grid, students who haven't asked anything show as idle (gray dot) with 0 questions. This helps you spot silent students.

**Q: What happens if the server crashes during class?**
Students will see a connection error. Just restart the server — no data is lost (it's saved to a SQLite file).

**Q: Does this work on macOS/Linux?**
Yes. The server runs on any OS with Python 3.10+. The dashboard runs on any OS with Node.js 18+. The VS Code extension works on all platforms.

**Q: How many students can use it at once?**
The system is designed for 3-50 concurrent students. With Groq (cloud), response times stay under 3 seconds.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Dashboard shows "Disconnected" | Make sure the server is running (`start.bat`). Check `http://192.168.1.1:8000/api/health` in a browser |
| Student gets "Unknown student IP" | Their computer isn't registered. Run the registration script above |
| Student gets "Too many requests" | They're asking too fast. Wait 30 seconds |
| AI responses are slow | If using Groq: check internet. If using Ollama: expected without GPU |
| Dashboard shows no students | No students have asked questions yet, or the database is empty |
| "Connection refused" from student | Student and teacher PCs are not on the same network |
