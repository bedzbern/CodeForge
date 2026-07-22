import { useState, useEffect } from "react";
import { fetchSummary } from "../api";

export default function SummaryView() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadSummary();
  }, []);

  const loadSummary = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await fetchSummary();
      setSummary(data);
    } catch (e) {
      setError("Failed to load summary. Is the server running?");
    }
    setLoading(false);
  };

  if (loading) return <div style={{ color: "var(--text-secondary)" }}>Loading summary...</div>;
  if (error) return <div style={{ color: "var(--level-5)" }}>{error}</div>;
  if (!summary) return <div>No summary data available.</div>;

  const maxTopic = Math.max(...(summary.common_topics || []).map((t) => t.count), 1);

  return (
    <div className="summary-view">
      <h2>Session Summary — {summary.date}</h2>

      <div className="stats-bar">
        <div className="stat">
          <div className="stat-label">Total Questions</div>
          <div className="stat-value">{summary.total_questions}</div>
        </div>
        <div className="stat">
          <div className="stat-label">Students Who Asked</div>
          <div className="stat-value">{summary["total_students_who Asked"] || 0}</div>
        </div>
      </div>

      {summary.common_topics && summary.common_topics.length > 0 && (
        <div className="summary-section">
          <h3>Common Topics</h3>
          <div className="bar-chart">
            {summary.common_topics.map((topic) => (
              <div className="bar-row" key={topic.topic}>
                <span className="bar-label">{topic.topic}</span>
                <div
                  className="bar"
                  style={{ width: `${(topic.count / maxTopic) * 200}px` }}
                />
                <span className="bar-count">{topic.count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {summary.common_errors && summary.common_errors.length > 0 && (
        <div className="summary-section">
          <h3>Common Errors</h3>
          <ul className="error-list">
            {summary.common_errors.map((err) => (
              <li key={err.error}>
                <span>{err.error}</span>
                <span style={{ color: "var(--text-secondary)" }}>{err.count}x</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {summary.ai_summary && (
        <div className="summary-section">
          <h3>AI Summary</h3>
          <p className="ai-summary">{summary.ai_summary}</p>
        </div>
      )}

      {summary.students_needing_followup && summary.students_needing_followup.length > 0 && (
        <div className="summary-section">
          <h3>Students Needing Follow-up</h3>
          <div className="followup-list">
            {summary.students_needing_followup.map((ip) => (
              <span className="followup-tag" key={ip}>{ip}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
