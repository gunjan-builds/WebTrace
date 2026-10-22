
export default function TestForm({ onStart, loading }) {
  return (
    <section style={{
      background: "#10213b",
      color: "white",
      padding: "24px",
      borderRadius: "12px"
    }}>
      <h2>Start a Website Test</h2>

      <p>Enter a website URL to begin testing.</p>

      <button
        onClick={() => onStart({
          url: "https://example.com",
          objective: "Check whether the website loads correctly"
        })}
        disabled={loading}
      >
        {loading ? "Starting..." : "Start Test"}
      </button>
    </section>
  );
}
