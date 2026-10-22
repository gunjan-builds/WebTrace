import React, { useState } from 'react';
import { 
  LayoutDashboard, PlusCircle, History, FileText, Settings, Bell 
} from 'lucide-react';
import TestForm from '../components/TestForm';
import AgentProgress from '../components/AgentProgress';
import TestResults from '../components/TestResults';
import LiveLogs from '../components/LiveLogs';
import EvidencePanel from '../components/EvidencePanel';
import { runTest } from '../services/api';

export default function Dashboard() {
  const [isRunning, setIsRunning] = useState(false);

  const handleStartTest = async (url, objective) => {
    setIsRunning(true);
    try {
      await runTest(url, objective);
    } catch (err) {
      console.log("Simulating frontend test run...");
    } finally {
      setTimeout(() => setIsRunning(false), 3000);
    }
  };

  return (
    <div className="flex h-screen bg-[#0A0E1A] text-slate-100 font-sans overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800/60 bg-[#0D1222] p-5 flex flex-col justify-between">
        <div className="space-y-8">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 text-white p-2 rounded-xl font-bold text-xl shadow-lg shadow-blue-500/20">W</div>
            <div>
              <h1 className="font-bold text-lg leading-tight tracking-wide">WebTrace</h1>
              <p className="text-xs text-slate-400">AI-Powered QA Engineer</p>
            </div>
          </div>

          <nav className="space-y-1.5">
            {[
              { label: 'Dashboard', icon: LayoutDashboard, active: true },
              { label: 'New Test', icon: PlusCircle },
              { label: 'Test History', icon: History },
              { label: 'Reports', icon: FileText },
              { label: 'Settings', icon: Settings }
            ].map((item, idx) => (
              <button 
                key={idx}
                className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  item.active 
                    ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 font-semibold' 
                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                }`}
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl relative overflow-hidden">
          <p className="text-xs font-semibold text-slate-300 mb-1">Smarter Testing.</p>
          <p className="text-xs text-slate-400">Fewer Bugs. Better Software.</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-y-auto">
        <header className="px-8 py-4 border-b border-slate-800/60 flex justify-between items-center bg-[#0D1222]/40 backdrop-blur-sm">
          <p className="text-xs text-slate-400">Smarter Testing. Higher Confidence.</p>
          <div className="flex items-center gap-4">
            <button className="p-2 rounded-xl border border-slate-800 hover:bg-slate-800 text-slate-400 transition-colors">
              <Bell className="w-4 h-4" />
            </button>
            <div className="flex items-center gap-3 pl-2 border-l border-slate-800">
              <div className="w-8 h-8 rounded-full bg-blue-600 text-white font-bold text-xs flex items-center justify-center">VB</div>
              <span className="text-xs font-medium text-slate-200">Gauri Deshmukh</span>
            </div>
          </div>
        </header>

        <div className="p-8 space-y-6">
          <div>
            <h2 className="text-2xl font-bold tracking-tight">Good morning, Gauri</h2>
            <p className="text-sm text-slate-400 mt-1">Let's make your web applications more reliable.</p>
          </div>

          <div className="grid grid-cols-12 gap-6">
            <div className="col-span-5"><TestForm onStartTest={handleStartTest} isRunning={isRunning} /></div>
            <div className="col-span-4"><AgentProgress /></div>
            <div className="col-span-3"><TestResults /></div>
          </div>

          <div className="grid grid-cols-12 gap-6">
            <div className="col-span-6"><LiveLogs /></div>
            <div className="col-span-6"><EvidencePanel /></div>
          </div>
        </div>
      </main>
    </div>
  );
}