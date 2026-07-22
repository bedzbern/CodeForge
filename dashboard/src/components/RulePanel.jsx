import { useState } from "react";
import { changeLevel, broadcastLevel, unlockLevel } from "../api";

const LEVEL_NAMES = {
  1: "Socratic Mirror",
  2: "Hint Giver",
  3: "Error Translator",
  4: "Logic Explainer",
  5: "Full Answer",
};

export default function RulePanel({ student, onClose, onRefresh }) {
  const [selectedLevel, setSelectedLevel] = useState(student.current_hint_level);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleChangeLevel = async () => {
    setLoading(true);
    setMessage("");
    try {
      const res = await changeLevel(student.ip, selectedLevel);
      setMessage(res.success ? `Level changed to ${selectedLevel}` : "Failed");
      if (res.success) onRefresh();
    } catch (e) {
      setMessage("Error: " + e.message);
    }
    setLoading(false);
  };

  const handleBroadcast = async (level) => {
    setLoading(true);
    setMessage("");
    try {
      const res = await broadcastLevel(level);
      setMessage(
        res.success
          ? `Broadcast: all students set to level ${level}`
          : "Failed"
      );
      if (res.success) onRefresh();
    } catch (e) {
      setMessage("Error: " + e.message);
    }
    setLoading(false);
  };

  const handleUnlock = async (minutes) => {
    setLoading(true);
    setMessage("");
    try {
      const res = await unlockLevel(student.ip, minutes, "Teacher unlock");
      setMessage(
        res.success
          ? `Level 5 unlocked for ${minutes} minutes`
          : "Failed"
      );
    } catch (e) {
      setMessage("Error: " + e.message);
    }
    setLoading(false);
  };

  return (
    <div className="rule-panel">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3>
          Seat {student.seat_number} — {student.ip}
          <span style={{ fontWeight: 400, fontSize: 14, marginLeft: 12, color: "var(--text-secondary)" }}>
            Current: Level {student.current_hint_level} ({LEVEL_NAMES[student.current_hint_level]})
          </span>
        </h3>
        <button onClick={onClose} style={{ background: "transparent", border: "none", color: "var(--text-secondary)", cursor: "pointer", fontSize: 18 }}>
          &times;
        </button>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 12 }}>
        <span>Set level:</span>
        <select
          value={selectedLevel}
          onChange={(e) => setSelectedLevel(Number(e.target.value))}
        >
          {[1, 2, 3, 4, 5].map((l) => (
            <option key={l} value={l}>
              Level {l} — {LEVEL_NAMES[l]}
            </option>
          ))}
        </select>
        <button onClick={handleChangeLevel} disabled={loading}>
          Apply
        </button>
      </div>

      <div className="quick-actions">
        <button className="broadcast" onClick={() => handleBroadcast(1)}>
          Broadcast Level 1
        </button>
        <button className="broadcast" onClick={() => handleBroadcast(2)}>
          Broadcast Level 2
        </button>
        <button className="broadcast" onClick={() => handleBroadcast(3)}>
          Broadcast Level 3
        </button>
        <button onClick={() => handleUnlock(5)}>
          Unlock L5 (5 min)
        </button>
        <button onClick={() => handleUnlock(10)}>
          Unlock L5 (10 min)
        </button>
        <button onClick={() => handleUnlock(30)}>
          Unlock L5 (30 min)
        </button>
      </div>

      {message && (
        <div style={{ marginTop: 12, fontSize: 13, color: message.startsWith("Error") ? "var(--level-5)" : "#22c55e" }}>
          {message}
        </div>
      )}
    </div>
  );
}
