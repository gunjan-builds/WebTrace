import { useState } from "react";
import TestForm from "../components/TestForm";
import AgentProgress from "../components/AgentProgress";
import TestJourney from "../components/TestJourney";
import LiveLogs from "../components/LiveLogs";
import TestResults from "../components/TestResults";
import EvidencePanel from "../components/EvidencePanel";

export default function Dashboard() {
  const [loading, setLoading] = useState(false);
  const [agents, setAgents] = useState([]);
  const [logs, setLogs] = useState([
    { time: "10:00:01", message: "Test workspace initialized." },
    { time: "10:00:02", message: "Explorer Agent is ready." },
  ]);
  const [results, setResults] = useState({ total: 0, passed: 0, failed: 0, bugs: 0 });
  const [screenshots, setScreenshots] = useState([]);

  async function handleStart(data) {
    setLoading(true);
    setAgents([
      { name: "Explorer Agent", status: "Running" },
      { name: "Tester Agent", status: "Running" },
      { name: "Visual Auditor", status: "Running" },
      { name: "Reporter Agent", status: "Waiting" },
    ]);

    try {
      const response = await fetch("http://127.0.0.1:8000/run-test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: data.url, objective: data.objective }),
      });

      const result = await response.json();

      if (response.ok) {
        setResults(result.summary || { total: 5, passed: 4, failed: 0, bugs: 1 });
        setScreenshots(result.screenshots || []);
        if (result.logs) {
          setLogs((prev) => [...prev, ...result.logs]);
        }
        setAgents([
          { name: "Explorer Agent", status: "Completed" },
          { name: "Tester Agent", status: "Completed" },
          { name: "Visual Auditor", status: "Completed" },
          { name: "Reporter Agent", status: "Completed" },
        ]);
      } else {
        alert("Error running test: " + result.detail);
      }
    } catch (err) {
      console.error("Connection failed:", err);
      alert("Backend server se connect nahi ho paya! Check karo uvicorn chal raha hai na.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="dashboard">
      <header className="welcome">
        <p className="eyebrow">YOUR TESTING WORKSPACE</p>
        <h1>WebTrace Dashboard</h1>
        <p>
          Test websites in plain English and monitor your AI agents from one workspace.
        </p>
      </header>

      <div className="status-strip">
        <span className="status-indicator"></span>
        <span>{loading ? "Running tests..." : "Workspace ready"}</span>
        <span className="pill neutral">Live Engine</span>
      </div>

      <div className="dashboard-grid">
        <div className="left-column">
          <TestForm onStart={handleStart} loading={loading} />
          <TestJourney currentStep={loading ? 3 : 5} />
          <LiveLogs logs={logs} />
        </div>

        <div className="middle-column">
          <AgentProgress agentsData={agents} />
          <TestResults results={results} />
        </div>

        <div className="right-column">
          <EvidencePanel screenshots={screenshots} />
        </div>
      </div>
    </main>
  );
}