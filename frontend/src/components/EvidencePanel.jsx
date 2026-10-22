import React from 'react';

export default function EvidencePanel() {
  return (
    <div className="bg-[#0D1222] border border-slate-800/80 rounded-2xl p-6 shadow-xl flex flex-col justify-between h-full">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-semibold text-sm">Screenshots & Visual Evidence</h3>
        <button className="text-xs text-blue-400 hover:underline">View All</button>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {['Homepage', 'Product Page', 'Cart (Issue Detected)'].map((label, idx) => (
          <div key={idx} className="bg-[#13192B] border border-slate-800 rounded-xl p-2 group hover:border-blue-500/50 transition-colors">
            <div className="aspect-video bg-slate-800/80 rounded-lg mb-2 flex items-center justify-center relative overflow-hidden">
              <span className="text-[10px] text-slate-500">Screenshot {idx + 1}</span>
              {idx === 2 && (
                <div className="absolute top-1 right-1 bg-red-500 text-white text-[9px] px-1.5 rounded font-bold">
                  Bug
                </div>
              )}
            </div>
            <p className="text-[11px] font-medium text-slate-300 truncate">{label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}