export default function StudentGrid({ students, selectedStudent, onSelect }) {
  const allSeats = Array.from({ length: 50 }, (_, i) => {
    const seatNum = i + 1;
    const student = students.find((s) => s.seat_number === seatNum);
    return { seatNum, student };
  });

  return (
    <div className="student-grid">
      {allSeats.map(({ seatNum, student }) => (
        <div
          key={seatNum}
          className={`student-card ${selectedStudent?.seat_number === seatNum ? "selected" : ""}`}
          onClick={() => student && onSelect(student)}
          title={student ? `${student.ip} — Level ${student.current_hint_level}` : `Seat ${seatNum} (unregistered)`}
        >
          <div className="seat-number">{seatNum}</div>
          {student ? (
            <>
              <div className="seat-ip">{student.ip}</div>
              <div className={`level-badge level-${student.current_hint_level}`}>
                L{student.current_hint_level}
              </div>
              <div className="card-meta">
                <span>{student.total_queries_today || 0} Q</span>
                <span className={`activity-dot ${student.status === "active" ? "active" : "idle"}`} />
              </div>
            </>
          ) : (
            <div className="seat-ip" style={{ opacity: 0.4 }}>
              No student
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
