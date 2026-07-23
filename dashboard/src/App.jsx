import { useState, useCallback } from "react";
import { useSocket } from "./hooks/useSocket";
import StudentGrid from "./components/StudentGrid";
import RulePanel from "./components/RulePanel";
import SummaryView from "./components/SummaryView";

export default function App() {
  const [tab, setTab] = useState("grid");
  const [selectedIp, setSelectedIp] = useState(null);
  const { students, lastEvent, isConnected, refreshStudents } = useSocket();

  const selectedStudent = students.find((s) => s.ip === selectedIp) || null;

  const handleSelect = useCallback((student) => {
    setSelectedIp((prev) => (prev === student.ip ? null : student.ip));
  }, []);

  return (
    <>
      <header className="header">
        <h1>CodeForge Teacher Dashboard</h1>
        <div className="header-status">
          <span className={`status-dot ${isConnected ? "" : "disconnected"}`} />
          {isConnected ? "Connected" : "Disconnected"}
          {lastEvent && (
            <span style={{ marginLeft: 12 }}>
              Last: {lastEvent.type.replace("_", " ")}
            </span>
          )}
        </div>
      </header>

      <div className="tabs">
        <div
          className={`tab ${tab === "grid" ? "active" : ""}`}
          onClick={() => setTab("grid")}
        >
          Grid View
        </div>
        <div
          className={`tab ${tab === "summary" ? "active" : ""}`}
          onClick={() => setTab("summary")}
        >
          Session Summary
        </div>
      </div>

      <main className="main">
        {tab === "grid" && (
          <>
            <div className="stats-bar">
              <div className="stat">
                <div className="stat-label">Students</div>
                <div className="stat-value">{students.length}</div>
              </div>
              <div className="stat">
                <div className="stat-label">Active</div>
                <div className="stat-value" style={{ color: "#22c55e" }}>
                  {students.filter((s) => s.status === "active").length}
                </div>
              </div>
              <div className="stat">
                <div className="stat-label">Idle</div>
                <div className="stat-value" style={{ color: "#6b7280" }}>
                  {students.filter((s) => s.status !== "active").length}
                </div>
              </div>
            </div>

            {selectedStudent && (
              <RulePanel
                student={selectedStudent}
                onClose={() => setSelectedIp(null)}
                onRefresh={refreshStudents}
              />
            )}

            <StudentGrid
              students={students}
              selectedStudent={selectedStudent}
              onSelect={handleSelect}
            />
          </>
        )}

        {tab === "summary" && <SummaryView />}
      </main>
    </>
  );
}
