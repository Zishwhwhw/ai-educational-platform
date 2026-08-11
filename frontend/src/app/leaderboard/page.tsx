// ==========================================
// File: src/app/leaderboard/page.tsx
// Description: Global Leaderboard with Top 5% tier highlights
// Author: AI Agent
// Created: 2026-08-02
// ==========================================

"use client";

import React, { useEffect, useState } from 'react';

interface LeaderboardUser {
  rank: number;
  user_id: number;
  username: str;
  points: number;
  level: str;
  avatar_url: str;
  tier?: str;
  discount?: number;
  is_shadowbanned?: boolean;
}

export default function LeaderboardPage() {
  const [users, setUsers] = useState<LeaderboardUser[]>([
    { rank: 1, user_id: 101, username: "AlexCodeMaster", points: 3450, level: "Middle Plus", avatar_url: "", tier: "Absolute Top", discount: 50 },
    { rank: 2, user_id: 102, username: "PyNinja99", points: 2890, level: "Middle", avatar_url: "", tier: "Discipline", discount: 25 },
    { rank: 3, user_id: 103, username: "DevSarah", points: 2410, level: "Middle", avatar_url: "", tier: "Progress", discount: 15 },
    { rank: 4, user_id: 1, username: "Student (You)", points: 450, level: "Regular", avatar_url: "", tier: undefined },
    { rank: 5, user_id: 105, username: "CheaterBot", points: 9999, level: "Senior", avatar_url: "", tier: undefined, is_shadowbanned: true },
  ]);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2">Global Leaderboard</h1>
        <p className="text-slate-400">Top 5% of students receive up to 50% discount on course sales and subscriptions!</p>
      </div>

      {/* Top Tiers Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-amber-900/40 to-yellow-900/20 border border-amber-500/30 rounded-xl p-5">
          <div className="text-2xl mb-1">👑</div>
          <div className="font-bold text-amber-300 text-lg">Top 2% Absolute Top</div>
          <div className="text-xs text-slate-400 mt-1">30–50% Subscription & Course Discount</div>
        </div>

        <div className="bg-gradient-to-br from-emerald-900/40 to-teal-900/20 border border-emerald-500/30 rounded-xl p-5">
          <div className="text-2xl mb-1">🔥</div>
          <div className="font-bold text-emerald-300 text-lg">Top 1.5% Discipline</div>
          <div className="text-xs text-slate-400 mt-1">Streak Leaders (15–25% Discount)</div>
        </div>

        <div className="bg-gradient-to-br from-blue-900/40 to-indigo-900/20 border border-blue-500/30 rounded-xl p-5">
          <div className="text-2xl mb-1">⚡</div>
          <div className="font-bold text-blue-300 text-lg">Top 1.5% Progress</div>
          <div className="text-xs text-slate-400 mt-1">Hard Task Champions (10–15% Discount)</div>
        </div>
      </div>

      {/* Leaderboard Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="px-6 py-4 border-b border-slate-800 font-semibold text-slate-400 text-xs flex justify-between uppercase tracking-wider">
          <div className="flex space-x-6">
            <span className="w-8">Rank</span>
            <span>Student</span>
          </div>
          <div className="flex space-x-8">
            <span className="w-24">Level</span>
            <span className="w-24 text-right">Points</span>
            <span className="w-28 text-right">Reward Tier</span>
          </div>
        </div>

        <div className="divide-y divide-slate-800/60">
          {users.map(u => (
            <div key={u.user_id} className={`px-6 py-4 flex items-center justify-between transition-colors ${u.user_id === 1 ? 'bg-emerald-500/10' : 'hover:bg-slate-800/40'}`}>
              <div className="flex items-center space-x-6">
                <span className={`w-8 font-bold text-lg ${u.rank === 1 ? 'text-amber-400' : u.rank === 2 ? 'text-slate-300' : u.rank === 3 ? 'text-amber-600' : 'text-slate-500'}`}>
                  #{u.rank}
                </span>
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-emerald-400">
                    {u.username[0]}
                  </div>
                  <div>
                    <div className="font-semibold text-sm flex items-center space-x-2">
                      <span>{u.username}</span>
                      {u.is_shadowbanned && (
                        <span className="px-2 py-0.5 rounded text-[10px] bg-red-500/20 text-red-400 border border-red-500/30">
                          Speedrunner (Shadowbanned)
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-8 text-sm">
                <span className="w-24 px-2 py-1 rounded bg-slate-800 text-center text-xs text-slate-300 border border-slate-700 font-mono">
                  {u.level}
                </span>
                <span className="w-24 text-right font-bold text-emerald-400">
                  {u.points} pts
                </span>
                <div className="w-28 text-right">
                  {u.tier ? (
                    <span className="px-2.5 py-1 rounded text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
                      -{u.discount}% Off
                    </span>
                  ) : (
                    <span className="text-slate-600 text-xs">—</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
