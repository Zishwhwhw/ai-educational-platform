// ==========================================
// File: src/app/achievements/page.tsx
// Description: All Achievements Grid & Skill Tree
// Author: AI Agent
// Created: 2026-08-02
// ==========================================

"use client";

import React from 'react';

const ACHIEVEMENTS = [
  { name: "First Steps", description: "Complete your first lesson", icon: "👣", unlocked: true },
  { name: "Code Warrior", description: "Submit 10 correct solutions", icon: "⚔️", unlocked: true },
  { name: "Streak Master", description: "Maintain a 7-day streak", icon: "🔥", unlocked: false },
  { name: "Course Completer", description: "Complete an entire course", icon: "🎓", unlocked: false },
  { name: "Perfect Code", description: "Get a perfect score on a hard task", icon: "💎", unlocked: false },
  { name: "Social Butterfly", description: "Post 5 comments", icon: "🦋", unlocked: true },
  { name: "Clan Leader", description: "Create or lead a clan", icon: "👑", unlocked: false },
  { name: "Speed Demon", description: "Complete 5 tasks in one day", icon: "⚡", unlocked: false },
  { name: "Reviewer", description: "Complete 3 peer reviews", icon: "🔍", unlocked: false },
];

export default function AchievementsPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2">Achievements & Skill Tree</h1>
        <p className="text-slate-400">Unlock badges, earn extra XP multipliers, and show off on your profile.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {ACHIEVEMENTS.map((ach, idx) => (
          <div
            key={idx}
            className={`p-5 rounded-xl border flex items-center space-x-4 transition-all ${
              ach.unlocked
                ? 'bg-slate-900 border-emerald-500/40 shadow-[0_0_15px_rgba(52,211,153,0.1)]'
                : 'bg-slate-900/40 border-slate-800/80 opacity-50 grayscale'
            }`}
          >
            <div className="text-4xl p-3 bg-slate-950 rounded-xl border border-slate-800">{ach.icon}</div>
            <div>
              <div className="font-bold text-base flex items-center space-x-2">
                <span>{ach.name}</span>
                {ach.unlocked && <span className="text-emerald-400 text-xs">✓ Unlocked</span>}
              </div>
              <p className="text-xs text-slate-400 mt-1">{ach.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
