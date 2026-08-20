// ==========================================
// File: src/app/profile/page.tsx
// Description: User Profile (Discord-style) with stats and achievements
// Author: AI Agent
// Created: 2026-08-02
// ==========================================

"use client";

import React from 'react';

export default function ProfilePage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Profile Header Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
        <div className="h-40 bg-gradient-to-r from-emerald-900 via-teal-900 to-slate-900 relative">
          <div className="absolute -bottom-12 left-8">
            <div className="w-24 h-24 rounded-2xl bg-slate-900 border-4 border-slate-950 flex items-center justify-center text-3xl font-extrabold text-emerald-400 shadow-xl">
              S
            </div>
          </div>
        </div>

        <div className="pt-16 p-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold">Student Developer</h1>
            <p className="text-slate-400 text-sm">Full-Stack AI Engineering Apprentice</p>
            <div className="flex items-center space-x-3 mt-3">
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Regular (Lvl 2)
              </span>
              <span className="text-xs text-slate-400 font-mono">Member since Aug 2026</span>
            </div>
          </div>

          <div className="flex space-x-3">
            <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-sm font-semibold border border-slate-700 transition-colors">
              Edit Profile
            </button>
            <button className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-sm font-semibold shadow-[0_0_15px_rgba(5,150,105,0.4)] transition-colors">
              Sync GitHub
            </button>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 text-center">
          <div className="text-slate-400 text-xs uppercase tracking-wider font-semibold mb-1">Total Points</div>
          <div className="text-3xl font-extrabold text-emerald-400">450</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 text-center">
          <div className="text-slate-400 text-xs uppercase tracking-wider font-semibold mb-1">In-Game Coins</div>
          <div className="text-3xl font-extrabold text-amber-400">150</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 text-center">
          <div className="text-slate-400 text-xs uppercase tracking-wider font-semibold mb-1">Current Streak</div>
          <div className="text-3xl font-extrabold text-orange-400">5 🔥</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 text-center">
          <div className="text-slate-400 text-xs uppercase tracking-wider font-semibold mb-1">Completed Tasks</div>
          <div className="text-3xl font-extrabold text-blue-400">14</div>
        </div>
      </div>

      {/* Achievements Showcase */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
        <h2 className="text-xl font-bold">Unlocked Achievements</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl flex items-center space-x-3">
            <span className="text-3xl">👣</span>
            <div>
              <div className="font-bold text-sm">First Steps</div>
              <div className="text-xs text-slate-400">Completed 1st lesson</div>
            </div>
          </div>

          <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl flex items-center space-x-3">
            <span className="text-3xl">⚔️</span>
            <div>
              <div className="font-bold text-sm">Code Warrior</div>
              <div className="text-xs text-slate-400">Submitted 10 solutions</div>
            </div>
          </div>

          <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl flex items-center space-x-3">
            <span className="text-3xl">🔥</span>
            <div>
              <div className="font-bold text-sm">Streak Master</div>
              <div className="text-xs text-slate-400">Maintained 5-day streak</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
