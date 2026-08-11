// ==========================================
// File: src/components/Header.tsx
// Description: Header with user stats (Coins, Pts, Streak) and controls
// Author: AI Agent
// Created: 2026-08-02
// ==========================================

"use client";

import React, { useState } from 'react';
import Link from 'next/link';

export default function Header() {
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  return (
    <header className="h-16 border-b border-slate-800 flex items-center justify-between px-6 bg-slate-900/50 backdrop-blur-md sticky top-0 z-40">
      <div className="flex items-center space-x-3">
        <h1 className="text-lg font-bold text-slate-200">Welcome back, Student</h1>
        <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          Regular (Lvl 2)
        </span>
      </div>

      <div className="flex items-center space-x-5">
        {/* Streak */}
        <div className="flex items-center space-x-1.5 bg-slate-800/80 border border-slate-700/60 px-3 py-1.5 rounded-lg text-xs font-bold text-amber-400">
          <span className="text-base animate-pulse">🔥</span>
          <span>5 Days Streak</span>
        </div>

        {/* Coins */}
        <div className="flex items-center space-x-1.5 bg-slate-800/80 border border-slate-700/60 px-3 py-1.5 rounded-lg text-xs font-bold text-amber-300">
          <span>💎</span>
          <span>150 Coins</span>
        </div>

        {/* Points */}
        <div className="flex items-center space-x-1.5 bg-slate-800/80 border border-slate-700/60 px-3 py-1.5 rounded-lg text-xs font-bold text-emerald-400">
          <span>🏆</span>
          <span>450 Pts</span>
        </div>

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setNotificationsOpen(!notificationsOpen)}
            className="w-9 h-9 rounded-lg bg-slate-800 border border-slate-700/60 flex items-center justify-center text-slate-300 hover:text-white transition-colors relative"
          >
            🔔
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-emerald-400"></span>
          </button>

          {notificationsOpen && (
            <div className="absolute right-0 mt-2 w-72 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-4 text-xs z-50 space-y-3">
              <div className="font-bold text-sm text-slate-200 flex justify-between">
                <span>Notifications</span>
                <span className="text-emerald-400 font-normal cursor-pointer">Mark read</span>
              </div>
              <div className="space-y-2">
                <div className="bg-slate-800/60 p-2.5 rounded-lg text-slate-300">
                  🎉 Achievement unlocked: <span className="text-emerald-400 font-semibold">First Steps</span>!
                </div>
                <div className="bg-slate-800/60 p-2.5 rounded-lg text-slate-300">
                  ⚡ Clan rating updated: Your clan is rank #3!
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Profile Avatar */}
        <Link href="/profile" className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center font-bold text-white shadow-md hover:scale-105 transition-transform">
          S
        </Link>
      </div>
    </header>
  );
}
