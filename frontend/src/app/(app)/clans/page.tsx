// ==========================================
// File: src/app/clans/page.tsx
// Description: Clan/Group Ratings (up to 5 people per clan)
// Author: AI Agent
// Created: 2026-08-02
// ==========================================

"use client";

import React, { useState } from 'react';

export default function ClansPage() {
  const [clans] = useState([
    { id: 1, name: "CyberKnights", description: "Python & AI enthusiasts. Daily coding sessions!", members: 4, max_members: 5, total_points: 12450, rank: 1 },
    { id: 2, name: "FullStackWizards", description: "React, Node, Go, Rust lovers.", members: 5, max_members: 5, total_points: 9800, rank: 2 },
    { id: 3, name: "AlgoCrushers", description: "LeetCode & Competitive programming clan.", members: 3, max_members: 5, total_points: 7600, rank: 3 },
  ]);

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold mb-2">Clan Leaderboard</h1>
          <p className="text-slate-400">Team up in groups of up to 5 students and compete for group ratings.</p>
        </div>
        <button className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-sm font-semibold shadow-[0_0_15px_rgba(5,150,105,0.4)] transition-colors">
          + Create Clan
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {clans.map(clan => (
          <div key={clan.id} className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between hover:border-emerald-500/50 transition-colors">
            <div>
              <div className="flex justify-between items-start mb-3">
                <span className="text-2xl font-bold text-amber-400">#{clan.rank}</span>
                <span className="px-2.5 py-1 rounded bg-slate-800 text-slate-300 text-xs font-mono">
                  👥 {clan.members}/{clan.max_members} Members
                </span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{clan.name}</h3>
              <p className="text-slate-400 text-xs mb-4">{clan.description}</p>
            </div>

            <div className="pt-4 border-t border-slate-800 flex justify-between items-center">
              <span className="font-bold text-emerald-400 text-sm">🏆 {clan.total_points} Pts</span>
              <button className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold rounded-lg border border-slate-700 transition-colors">
                Join Clan
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
