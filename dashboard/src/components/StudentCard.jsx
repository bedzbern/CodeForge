export default function StudentCard({ student }) {
  return (
    <div className="student-card">
      <div className="seat-number">{student.seat_number}</div>
      <div className="seat-ip">{student.ip}</div>
      <div className={`level-badge level-${student.current_hint_level}`}>
        L{student.current_hint_level}
      </div>
      <div className="card-meta">
        <span>{student.total_queries_today || 0} Q</span>
        <span className={`activity-dot ${student.status === "active" ? "active" : "idle"}`} />
      </div>
    </div>
  );
}
