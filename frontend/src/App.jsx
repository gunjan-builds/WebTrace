import React, { useState } from 'react';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  return (
    <div className="w-full h-screen bg-[#090e1a] text-slate-100 font-sans overflow-hidden">
      {!isAuthenticated ? (
        <Login onLogin={() => setIsAuthenticated(true)} />
      ) : (
        <Dashboard />
      )}
    </div>
  );
}