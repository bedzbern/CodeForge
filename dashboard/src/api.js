const SERVER_URL =
  import.meta.env.VITE_SERVER_URL || "http://192.168.1.1:8000";

export async function fetchStatus() {
  const res = await fetch(`${SERVER_URL}/api/status`);
  if (!res.ok) throw new Error(`Status fetch failed: ${res.status}`);
  return res.json();
}

export async function fetchHealth() {
  const res = await fetch(`${SERVER_URL}/api/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

export async function changeLevel(studentIp, newLevel) {
  const res = await fetch(`${SERVER_URL}/api/teacher/level`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_ip: studentIp, new_level: newLevel }),
  });
  return res.json();
}

export async function broadcastLevel(newLevel) {
  const res = await fetch(`${SERVER_URL}/api/teacher/broadcast`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ new_level: newLevel }),
  });
  return res.json();
}

export async function unlockLevel(studentIp, durationMinutes, reason = "") {
  const res = await fetch(`${SERVER_URL}/api/teacher/unlock`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      student_ip: studentIp,
      duration_minutes: durationMinutes,
      reason,
    }),
  });
  return res.json();
}

export async function fetchSummary(sessionId) {
  const params = sessionId ? `?session_id=${sessionId}` : "";
  const res = await fetch(`${SERVER_URL}/api/summary${params}`);
  if (!res.ok) throw new Error(`Summary fetch failed: ${res.status}`);
  return res.json();
}
