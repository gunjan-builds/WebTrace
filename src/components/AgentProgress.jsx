
const agentList = [
  { name: "Explorer Agent", role: "Plans the test journey" },
  { name: "Tester Agent", role: "Performs browser actions" },
  { name: "Visual Auditor", role: "Checks UI and visual issues" },
  { name: "Reporter Agent", role: "Prepares the final report" },
];

export default function AgentProgress({ agentsData = [] }) {
  return (
    <section style={{
      background: "#10213b",
      color: "white",
      padding: "24px",
      borderRadius: "12px",
      marginTop: "20px"
    }}>
      <h2>AI Agent Progress</h2>

      {agentList.map((agent) => {
        const data = agentsData.find(
          (item) =>
            item.name?.toLowerCase() === agent.name.toLowerCase()
        );

        return (
          <div key={agent.name} style={{
            padding: "14px",
            marginTop: "10px",
            background: "#172c49",
            borderRadius: "8px"
          }}>
            <strong>{agent.name}</strong>
            <p style={{ color: "#aabbd3" }}>{agent.role}</p>
            <span>
              Status: {data?.status || "Waiting"}
            </span>
          </div>
        );
      })}
    </section>
  );
}
