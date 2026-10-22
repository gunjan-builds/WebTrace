
export default function LiveLogs({ logs = [] }) {
  return (
    <section style={{
      background: "#10213b",
      color: "white",
      padding: "24px",
      borderRadius: "12px",
      marginTop: "20px"
    }}>
      <h2>Live Logs</h2>

      <p style={{ color: "#aabbd3" }}>
        Recent activity from your test run.
      </p>

      {logs.length === 0 ? (
        <p style={{ color: "#94a3b8" }}>
          No activity yet. Start a test to see logs.
        </p>
      ) : (
        logs.map((log, index) => (
          <div key={index} style={{
            background: "#172c49",
            padding: "12px",
            marginTop: "8px",
            borderRadius: "8px"
          }}>
            <span style={{ color: "#60a5fa" }}>
              [{log.time || "Now"}]
            </span>
            {" "}
            {log.message || String(log)}
          </div>
        ))
      )}
    </section>
  );
}
