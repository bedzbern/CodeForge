# CodeForge Manual Test Plan
# Stage 5: QA Lead — Extension & Dashboard Manual Tests
# These tests require actual hardware (teacher PC + student laptops)

## Prerequisites
- Teacher PC running at 192.168.1.1 with CodeForge server
- 3 student laptops with static IPs (192.168.1.2, .3, .4)
- All connected to isolated Wi-Fi hotspot (no internet)
- VS Code with CodeForge extension installed on student laptops
- Teacher dashboard open on teacher PC

---

## Part A: VS Code Extension Tests

### A1. Extension Loads
1. Open VS Code on student laptop (192.168.1.2)
2. Verify CodeForge sidebar icon appears in the activity bar
3. Click the sidebar icon — the CodeForge panel should open
4. Verify the panel shows a text area for questions and an "Ask" button

### A2. Ask a Question (Level 1)
1. Ensure teacher has set student 192.168.1.2 to Level 1 (Socratic Mirror)
2. Highlight some code in the editor
3. Type "Why does my loop not stop?" in the question box
4. Click "Ask"
5. Verify a response appears that asks a guiding question (NOT code)
6. Verify the response does NOT contain any Python code

### A3. Ask a Question (Level 3)
1. Teacher changes 192.168.1.2 to Level 3 (Error Translator)
2. Student asks: "I got an IndexError on line 5"
3. Verify the response explains what IndexError means
4. Verify the response does NOT suggest how to fix it

### A4. Ask a Question (Level 5 — Locked)
1. Teacher has NOT unlocked Level 5 for student
2. Student asks any question
3. Verify the response is at the student's current level (NOT Level 5)
4. Verify no full code solution is provided

### A5. Rate Limiting
1. Ask a question
2. Immediately ask another question (within 30 seconds)
3. Verify a "Too many requests" message appears
4. Wait 30 seconds, ask again
5. Verify the request succeeds

### A6. Code Snapshot
1. Highlight a block of code in VS Code
2. Ask "What does this code do?"
3. Verify the AI response references the specific code you highlighted

### A7. No Internet Test
1. Disconnect the student laptop from Wi-Fi
2. Try to open ChatGPT or Copilot in browser
3. Verify these sites are unreachable
4. Reconnect to the lab Wi-Fi
5. Verify CodeForge still works

---

## Part B: Teacher Dashboard Tests

### B1. Dashboard Loads
1. Open browser on teacher PC
2. Navigate to http://localhost:5173 (or the dashboard URL)
3. Verify the grid of student seats appears
4. Verify all 3 student seats are displayed

### B2. Live Grid Updates
1. Have student 192.168.1.2 ask a question
2. Verify student 2's seat turns yellow/active on the dashboard
3. Verify the question count for that student increases

### B3. Change Individual Hint Level
1. Click on student 192.168.1.2's seat card
2. Change the hint level to 4 (Logic Explainer)
3. Verify the level indicator updates on the dashboard
4. Have the student ask a question — verify they get a Logic Explainer response

### B4. Broadcast Level Change
1. Click "Broadcast" or "Set All" button
2. Set global level to 1 (Socratic Mirror)
3. Verify all student seats show level 1
4. Have multiple students ask questions — verify all get Socratic responses

### B5. Unlock Level 5
1. Click on student 192.168.1.3's seat
2. Click "Unlock Level 5" with a 5-minute duration
3. Verify the seat shows "Level 5 Unlocked" with a countdown
4. Have student 3 ask a question — verify they receive a full code answer
5. Wait for the 5 minutes to expire
6. Verify Level 5 auto-locks and the student returns to their previous level

### B6. Session Summary
1. After several questions from multiple students, click "Session Summary"
2. Verify the summary shows:
   - Total questions asked
   - Number of students who asked
   - Common topics
   - Common errors
   - Students needing follow-up
3. Verify the summary text is readable and accurate

### B7. Student Status Indicators
1. Have student 192.168.1.2 ask a question
2. Verify their seat shows "Active" status
3. Wait 5+ minutes without the student asking anything
4. Verify their seat changes to "Idle" status

### B8. Real-Time Updates
1. Have student 192.168.1.2 ask a question
2. Verify the dashboard updates in real-time (no manual refresh needed)
3. Verify the question text appears in the student's activity log

---

## Part C: Security Tests

### C1. IP Spoofing
1. Using curl or Postman, send a POST to /api/ask with:
   - student_ip: 192.168.1.3 (different from source)
   - question: "Hello"
2. Verify the request is rejected with 403

### C2. Teacher Endpoint Access
1. From student laptop (192.168.1.2), try to call:
   - POST /api/teacher/level
   - POST /api/teacher/broadcast
   - POST /api/teacher/unlock
2. Verify all requests are rejected with 403

### C3. Non-Lab IP
1. From a device outside the lab network (e.g., phone on mobile data)
2. Try to reach http://192.168.1.1:8000/api/ask
3. Verify the request is rejected (CORS or network isolation)

---

## Part D: Edge Cases

### D1. Empty Question
1. Try to submit a question with no text
2. Verify the request is rejected with a validation error

### D2. Very Long Question
1. Type a question with 2000+ characters
2. Verify the request is rejected with a validation error

### D3. Special Characters
1. Ask a question with special characters: <script>alert('x')</script>
2. Verify the AI responds normally (no script execution)

### D4. Concurrent Students
1. Have all 3 students ask questions simultaneously
2. Verify all 3 receive responses
3. Verify the dashboard shows all 3 as active

---

## Pass/Fail Criteria

| Test | Pass Condition |
|------|---------------|
| A1-A7 | Extension works correctly at all levels |
| B1-B8 | Dashboard shows live data and controls work |
| C1-C3 | Security measures prevent unauthorised access |
| D1-D4 | System handles edge cases gracefully |

**Overall pass:** All tests in Parts A, B, and C pass. Part D is informational.
