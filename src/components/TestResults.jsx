
export default function TestResults({ results = {} }) {
  const items = [
    { label: "Total Tests", value: results.total ?? 0 },
    { label: "Passed", value: results.passed ?? 0 },
    { label: "Failed", value: results.failed ?? 0 },
    { label: "Bugs Found", value: results.bugs ?? 0 },
  ];

  return (
    <section style={{
      background: "#10213b",
      color: "white",
      padding: "24px",
      borderRadius: "12px",
      marginTop: "20px"
    }}>
      <h2>Test Results</h2>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
        gap: "12px"
      }}>
        {items.map((item) => (
          <div key={item.label} style={{
            background: "#172c49",
            padding: "18px",
            borderRadius: "8px"
          }}>
            <p style={{ color: "#aabbd3" }}>{item.label}</p>
            <h2>{item.value}</h2>
          </div>
        ))}
      </div>
    </section>
  );
}
