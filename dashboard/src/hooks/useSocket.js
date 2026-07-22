import { useEffect, useState, useRef } from "react";
import { io } from "socket.io-client";

const SERVER_URL =
  import.meta.env.VITE_SERVER_URL || "http://192.168.1.1:8000";

export function useSocket() {
  const [students, setStudents] = useState([]);
  const [lastEvent, setLastEvent] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [serverStatus, setServerStatus] = useState(null);
  const socketRef = useRef(null);

  useEffect(() => {
    const socket = io(SERVER_URL, {
      transports: ["websocket", "polling"],
      reconnectionAttempts: 10,
      reconnectionDelay: 3000,
    });
    socketRef.current = socket;

    socket.on("connect", () => {
      setIsConnected(true);
      socket.emit("request_full_status");
    });

    socket.on("disconnect", () => setIsConnected(false));

    socket.on("student_query", (data) => {
      setLastEvent({ type: "student_query", data, time: Date.now() });
      setStudents((prev) =>
        prev.map((s) =>
          s.ip === data.ip
            ? { ...s, status: "active", total_queries_today: (s.total_queries_today || 0) + 1, last_query_time: data.timestamp }
            : s
        )
      );
    });

    socket.on("level_changed", (data) => {
      setLastEvent({ type: "level_changed", data, time: Date.now() });
      setStudents((prev) =>
        prev.map((s) =>
          s.ip === data.ip ? { ...s, current_hint_level: data.new_level } : s
        )
      );
    });

    socket.on("student_active", (data) => {
      setStudents((prev) =>
        prev.map((s) => (s.ip === data.ip ? { ...s, status: "active" } : s))
      );
    });

    socket.on("student_idle", (data) => {
      setStudents((prev) =>
        prev.map((s) => (s.ip === data.ip ? { ...s, status: "idle" } : s))
      );
    });

    socket.on("server_status", (data) => {
      setServerStatus(data);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const refreshStudents = async () => {
    try {
      const res = await fetch(`${SERVER_URL}/api/status`);
      if (res.ok) {
        const data = await res.json();
        setStudents(data.students || []);
      }
    } catch (e) {
      console.error("Failed to refresh status:", e);
    }
  };

  return { students, setStudents, lastEvent, isConnected, serverStatus, refreshStudents, socket: socketRef };
}
