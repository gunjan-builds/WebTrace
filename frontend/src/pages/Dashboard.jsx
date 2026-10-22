import React, { useState } from 'react';
import { 
  Bot, Play, CheckCircle2, AlertTriangle, Bug, Eye, FileText, LayoutDashboard, History, Settings, Activity, ShieldCheck, Clock, ExternalLink, RefreshCw, Layers
} from 'lucide-react';

export default function Dashboard() {
  const [url, setUrl] = useState('https://ecommerce-demo.webtrace.ai');
  const [objective, setObjective] = useState('Verify full checkout flow with discount coupon applied');
  const [isRunning, setIsRunning] = useState(false);
  const [activeLogFilter, setActiveLogFilter] = useState('all');

  const handleStartTest = (e) => {
    e.preventDefault();
    setIsRunning(true);
    setTimeout(() => setIsRunning(false), 4500);
  };

  const logs = [
    { type: 'info', time: '10:42:15', text: 'Initializing browser engine (Chromium v118)...' },
    { type: 'info', time: '10:42:18', text: 'Target URL opened. Constructing visual accessibility tree.' },
    { type: 'bug', time: '10:42:25', text: '[Bug Detected] Overlapping text in navbar checkout CTA button.' },
    { type: 'warning', time: '10:42:31', text: '[Visual Flaw] Contrast ratio on footer links below WCAG standard (2.8:1).' },
    { type: 'info', time: '10:42:40', text: 'Form submission completed. Session token captured.' }
  ];

  const filteredLogs = logs.filter(log => {
    if (activeLogFilter === 'all') return true;
    return log.type === activeLogFilter;
  });

  return (
    <div className="app-shell">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Bot size={22} color="#ffffff" />
          </div>
          <div>
            <h2>WebTrace</h2>
            <small>AI QA ENGINEER</small>
          </div>
        </div>

        <div className="sidebar-label">CORE PLATFORM</div>
        <nav>
          <button className="nav-link active">
            <LayoutDashboard size={16} />
            Dashboard
          </button>
          <button className="nav-link">
            <Activity size={16} />
            Live Runs
          </button>
          <button className="nav-link">
            <History size={16} />
            Test History
          </button>

          <div className="sidebar-label" style={{ marginTop: '20px' }}>ANALYSIS</div>
          <button className="nav-link">
            <Layers size={16} />
            Visual Audits
          </button>
          <button className="nav-link">
            <Settings size={16} />
            Settings
          </button>
        </nav>

        <div className="sidebar-note">
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
            <ShieldCheck size={14} color="#64e4c0" />
            <strong style={{ fontSize: '11px', color: '#e8f0fc' }}>Enterprise QA AI</strong>
          </div>
          <p>Autonomous VLM + Playwright runner active.</p>
        </div>
      </aside>

      {/* Main Container */}
      <div className="main-area">
        {/* Header */}
        <header className="topbar">
          <div>
            <span className="topbar-title">WebTrace Autonomous Control Center</span>
            <span className="topbar-subtitle">Active Engine: Chromium / Vision LLM Pipeline</span>
          </div>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <span className="connection-label">
              <span className="status-indicator"></span> System Ready
            </span>
            <span className="pill neutral">Gauri Deshmukh</span>
          </div>
        </header>

        {/* Dashboard Canvas */}
        <main className="dashboard">
          <div className="welcome">
            <span className="eyebrow">AUTONOMOUS TESTING SUITE</span>
            <h1>Good evening, Gauri 👋</h1>
            <p>Run end-to-end multi-agent web verification with automatic defect and visual regression logging.</p>
          </div>

          {/* Banner Status Strip */}
          <div className="status-strip">
            <div className="status-indicator" style={{ background: isRunning ? '#62a5ff' : '#46cdb3' }}></div>
            <span>Status: <strong>{isRunning ? 'Execution in Progress...' : 'Idle & Ready'}</strong></span>
            <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Clock size={13} /> Last Execution: 2 mins ago
            </span>
          </div>

          {/* Grid Layout */}
          <div className="dashboard-grid">
            
            {/* Left Column: Input Form + User Journey */}
            <div className="left-column">
              <div className="panel">
                <div className="panel-heading">
                  <Bot size={24} />
                  <div>
                    <h2>Trigger Agent Suite</h2>
                    <p>Enter target application URL and objective.</p>
                  </div>
                </div>

                <form className="test-form" onSubmit={handleStartTest}>
                  <label>Application Target URL</label>
                  <input 
                    type="url" 
                    value={url} 
                    onChange={(e) => setUrl(e.target.value)} 
                    placeholder="https://example.com" 
                    required 
                  />

                  <label>Test Objective / Goal</label>
                  <textarea 
                    rows={3} 
                    value={objective} 
                    onChange={(e) => setObjective(e.target.value)} 
                    placeholder="Describe user workflow..." 
                    required 
                  />

                  <button type="submit" className="primary-button" disabled={isRunning}>
                    {isRunning ? <RefreshCw size={14} className="spin-icon" /> : <Play size={14} />}
                    {isRunning ? 'Executing Multi-Agent Pipeline...' : 'Run Autonomous Test'}
                  </button>
                </form>
              </div>

              {/* User Journey Map */}
              <div className="panel">
                <div className="section-heading">
                  <h2>User Journey Map</h2>
                  <span className="pill neutral">5 Steps</span>
                </div>
                <div className="journey">
                  <div className="journey-step">
                    <div className="journey-node done">1</div>
                    <small>Navigate</small>
                  </div>
                  <div className="journey-step">
                    <div className="journey-node done">2</div>
                    <small>Search</small>
                  </div>
                  <div className="journey-step">
                    <div className="journey-node done">3</div>
                    <small>Add Cart</small>
                  </div>
                  <div className="journey-step">
                    <div className="journey-node done">4</div>
                    <small>Checkout</small>
                  </div>
                  <div className="journey-step">
                    <div className="journey-node">5</div>
                    <small>Verify</small>
                  </div>
                </div>
              </div>
            </div>

            {/* Middle Column: Active Agents + Filterable Live Logs */}
            <div className="middle-column">
              <div className="panel">
                <div className="section-heading">
                  <h2><Activity size={18} /> Multi-Agent Engine</h2>
                  <span className="status-label">{isRunning ? 'Running' : 'Ready'}</span>
                </div>

                <div className="agent-row">
                  <div className="agent-icon"><Bot size={18} /></div>
                  <div className="agent-info">
                    <strong>Explorer Agent</strong>
                    <small>Mapping page layout & DOM tree</small>
                    <div className="progress-track">
                      <div className="progress-fill completed" style={{ width: '100%' }}></div>
                    </div>
                  </div>
                </div>

                <div className="agent-row">
                  <div className="agent-icon"><Play size={18} /></div>
                  <div className="agent-info">
                    <strong>Playwright Tester Agent</strong>
                    <small>Executing mouse clicks & input actions</small>
                    <div className="progress-track">
                      <div className={`progress-fill ${isRunning ? '' : 'completed'}`} style={{ width: isRunning ? '65%' : '100%' }}></div>
                    </div>
                  </div>
                </div>

                <div className="agent-row">
                  <div className="agent-icon"><Eye size={18} /></div>
                  <div className="agent-info">
                    <strong>Visual Auditor Agent</strong>
                    <small>Analyzing UI alignment & pixel anomalies</small>
                    <div className="progress-track">
                      <div className="progress-fill" style={{ width: isRunning ? '35%' : '80%' }}></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Logs Stream with Filters */}
              <div className="panel">
                <div className="section-heading">
                  <h2><FileText size={18} /> Live Stream Logs</h2>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    <button 
                      onClick={() => setActiveLogFilter('all')} 
                      className={`pill ${activeLogFilter === 'all' ? '' : 'neutral'}`}
                      style={{ cursor: 'pointer', padding: '3px 8px' }}
                    >All</button>
                    <button 
                      onClick={() => setActiveLogFilter('bug')} 
                      className={`pill ${activeLogFilter === 'bug' ? '' : 'neutral'}`}
                      style={{ cursor: 'pointer', padding: '3px 8px', color: '#ff7b7b' }}
                    >Bugs</button>
                    <button 
                      onClick={() => setActiveLogFilter('warning')} 
                      className={`pill ${activeLogFilter === 'warning' ? '' : 'neutral'}`}
                      style={{ cursor: 'pointer', padding: '3px 8px', color: '#ffd166' }}
                    >Visual</button>
                  </div>
                </div>

                <div className="log-list">
                  {filteredLogs.map((log, index) => (
                    <div className="log-row" key={index}>
                      <div className="log-dot" style={{ 
                        background: log.type === 'bug' ? '#ff6b6b' : log.type === 'warning' ? '#ffd166' : '#46cdb3' 
                      }}></div>
                      <span className="log-time">{log.time}</span>
                      <span style={{ 
                        color: log.type === 'bug' ? '#ff9b9b' : log.type === 'warning' ? '#ffe08a' : '#c8d8ee' 
                      }}>
                        {log.text}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Column: Execution Metrics + Visual Evidence */}
            <div className="right-column">
              <div className="panel">
                <div className="section-heading">
                  <h2>Execution Summary</h2>
                  <span className="pill">92% Health</span>
                </div>
                <div className="result-stats">
                  <div>
                    <CheckCircle2 size={16} color="#64e4c0" />
                    <span>Passed</span>
                    <strong>4 / 5</strong>
                  </div>
                  <div>
                    <Bug size={16} color="#ff6b6b" />
                    <span>Bugs</span>
                    <strong style={{ color: '#ff6b6b' }}>1</strong>
                  </div>
                  <div>
                    <AlertTriangle size={16} color="#ffd166" />
                    <span>Visual Flaws</span>
                    <strong style={{ color: '#ffd166' }}>1</strong>
                  </div>
                </div>
              </div>

              {/* Visual Evidence Showcase */}
              <div className="panel">
                <div className="section-heading">
                  <h2><Eye size={18} /> Captured Evidence</h2>
                  <span className="eyebrow" style={{ cursor: 'pointer' }}>VIEW ALL</span>
                </div>

                <div className="evidence-grid">
                  <div className="empty-evidence" style={{ textAlign: 'left', padding: '16px', display: 'flex', gap: '12px', alignItems: 'center' }}>
                    <Bug size={24} color="#ff6b6b" />
                    <div>
                      <strong style={{ fontSize: '12px', color: '#e8f0fc' }}>CTA Button Overlap</strong>
                      <p style={{ margin: '2px 0 0', fontSize: '10px', color: '#9aafcd' }}>Element `.btn-checkout` overlapped by notification banner.</p>
                    </div>
                  </div>

                  <div className="empty-evidence" style={{ textAlign: 'left', padding: '16px', display: 'flex', gap: '12px', alignItems: 'center' }}>
                    <AlertTriangle size={24} color="#ffd166" />
                    <div>
                      <strong style={{ fontSize: '12px', color: '#e8f0fc' }}>Low Contrast Ratio</strong>
                      <p style={{ margin: '2px 0 0', fontSize: '10px', color: '#9aafcd' }}>Footer nav text fails WCAG AA standard requirement.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>

          {/* Bottom Table: Recent Executions History */}
          <div className="panel" style={{ marginTop: '20px' }}>
            <div className="section-heading">
              <h2>Recent Autonomous Runs</h2>
              <span className="pill neutral">4 Executions Today</span>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '12px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #203653', color: '#8fa7c7' }}>
                    <th style={{ padding: '10px 8px' }}>TARGET URL</th>
                    <th style={{ padding: '10px 8px' }}>OBJECTIVE</th>
                    <th style={{ padding: '10px 8px' }}>STATUS</th>
                    <th style={{ padding: '10px 8px' }}>BUGS</th>
                    <th style={{ padding: '10px 8px' }}>TIME</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style={{ borderBottom: '1px solid #162842' }}>
                    <td style={{ padding: '10px 8px', color: '#79afff' }}>https://ecommerce-demo.webtrace.ai</td>
                    <td style={{ padding: '10px 8px', color: '#b9cbe4' }}>Checkout flow test with coupon</td>
                    <td style={{ padding: '10px 8px' }}><span className="pill" style={{ fontSize: '9px', padding: '2px 6px' }}>PASSED</span></td>
                    <td style={{ padding: '10px 8px', color: '#ff6b6b' }}>1 Bug</td>
                    <td style={{ padding: '10px 8px', color: '#8fa7c7' }}>10:42 PM</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid #162842' }}>
                    <td style={{ padding: '10px 8px', color: '#79afff' }}>https://app.webtrace.ai/login</td>
                    <td style={{ padding: '10px 8px', color: '#b9cbe4' }}>OAuth & SSO authentication validation</td>
                    <td style={{ padding: '10px 8px' }}><span className="pill" style={{ fontSize: '9px', padding: '2px 6px' }}>PASSED</span></td>
                    <td style={{ padding: '10px 8px', color: '#64e4c0' }}>0 Bugs</td>
                    <td style={{ padding: '10px 8px', color: '#8fa7c7' }}>08:15 PM</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '10px 8px', color: '#79afff' }}>https://app.webtrace.ai/settings</td>
                    <td style={{ padding: '10px 8px', color: '#b9cbe4' }}>Profile update and avatar upload test</td>
                    <td style={{ padding: '10px 8px' }}><span className="pill" style={{ fontSize: '9px', padding: '2px 6px' }}>PASSED</span></td>
                    <td style={{ padding: '10px 8px', color: '#64e4c0' }}>0 Bugs</td>
                    <td style={{ padding: '10px 8px', color: '#8fa7c7' }}>05:30 PM</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

        </main>
      </div>
    </div>
  );
}