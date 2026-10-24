export default function EvidencePanel({ screenshots = [] }) {
  return (
    <section style={{
      background: "#10213b",
      color: "white",
      padding: "24px",
      borderRadius: "12px",
      marginTop: "20px"
    }}>
      <h2>Test Evidence</h2>

      {screenshots.length === 0 ? (
        <p style={{ color: "#aabbd3" }}>
          Screenshots will appear here when a test runs.
        </p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginTop: "16px" }}>
          <p style={{ margin: 0, color: "#4ade80", fontSize: "14px" }}>
            {screenshots.length} screenshot(s) captured successfully.
          </p>
          {screenshots.map((src, index) => (
            <div 
              key={index} 
              style={{
                background: "#0b1629",
                padding: "12px",
                borderRadius: "8px",
                border: "1px solid rgba(255, 255, 255, 0.1)"
              }}
            >
              <p style={{ fontSize: "12px", color: "#94a3b8", marginBottom: "8px" }}>
                Step {index + 1} Execution Snapshot
              </p>
              <img 
                src={src} 
                alt={`Test Evidence ${index + 1}`} 
                style={{ 
                  width: "1005", 
                  width: "100%", 
                  borderRadius: "6px",
                  display: "block",
                  border: "1px solid rgba(255, 255, 255, 0.05)"
                }} 
              />
            </div>
          ))}
        </div>
      )}
    </section>
  );
}