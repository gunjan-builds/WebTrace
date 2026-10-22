
import { useState } from "react";
import TestForm from "../components/TestForm";
import AgentProgress from "../components/AgentProgress";
import TestJourney from "../components/TestJourney";
import LiveLogs from "../components/LiveLogs";
import TestResults from "../components/TestResults";
import EvidencePanel from "../components/EvidencePanel";

export default function Dashboard() {
  const [agents, setAgents] = useState([]);

  function handleStart(data) {
    alert("Website URL: " + data.url);

    setAgents([
      { name: "Explorer Agent", status: "Running" },
      { name: "Tester Agent", status: "Waiting" },
      { name: "Visual Auditor", status: "Waiting" },
      { name: "Reporter Agent", status: "Waiting" },
    ]);
  }

  return (
    <main className="dashboard">
      <header className="welcome">
        <p className="eyebrow">YOUR TESTING WORKSPACE</p>
        <h1>WebTrace Dashboard</h1>
        <p>
          Test websites in plain English and monitor your
          AI agents from one workspace.
        </p>
      </header>

      <div className="status-strip">
        <span className="status-indicator"></span>
        <span>Workspace ready</span>
        <span className="pill neutral">
          Demo mode
        </span>
      </div>

      <div className="dashboard-grid">
        <div className="left-column">
          <TestForm
            onStart={handleStart}
            loading={false}
          />

          <TestJourney currentStep={0} />

          <LiveLogs
            logs={[
              {
                time: "10:00:01",
                message: "Test workspace initialized.",
              },
              {
                time: "10:00:02",
                message: "Explorer Agent is ready.",
              },
              {
                time: "10:00:03",
                message: "Waiting for a test request.",
              },
            ]}
          />
        </div>

        <div className="middle-column">
          <AgentProgress agentsData={agents} />

          <TestResults
            results={{
              total: 10,
              passed: 8,
              failed: 2,
              bugs: 2,
            }}
          />
        </div>

        <div className="right-column">
          <EvidencePanel screenshots={[]} />
        </div>
      </div>
    </main>
  );
}
