
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
        <p>{screenshots.length} screenshot(s) captured.</p>
      )}
    </section>
  );
}
