// ==========================================
// File: src/components/Sidebar.tsx
// Description: Main navigation sidebar with active link highlighting
// Author: AI Agent
// Created: 2026-08-02
// ==========================================

"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { name: 'Dashboard', href: '/', icon: '📊' },
    { name: 'Library', href: '/library', icon: '📚' },
    { name: 'Leaderboard', href: '/leaderboard', icon: '🏆' },
    { name: 'Store', href: '/store', icon: '💎' },
    { name: 'Achievements', href: '/achievements', icon: '🎯' },
    { name: 'Clans', href: '/clans', icon: '🛡️' },
    { name: 'Flashcards', href: '/flashcards', icon: '🧠' },
    { name: 'Messages', href: '/messages', icon: '💬' },
    { name: 'Profile', href: '/profile', icon: '👤' },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 p-4 hidden md:flex flex-col h-screen sticky top-0">
      <div className="flex items-center space-x-3 mb-8 px-2">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-xl font-bold text-slate-950 shadow-[0_0_20px_rgba(52,211,153,0.4)]">
          AI
        </div>
        <div className="text-xl font-extrabold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
          AI-Code
        </div>
      </div>

      <nav className="flex-1 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all font-medium text-sm ${
                isActive
                  ? 'bg-gradient-to-r from-emerald-500/20 to-teal-500/10 text-emerald-400 border border-emerald-500/30 shadow-[0_0_15px_rgba(52,211,153,0.15)]'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="pt-4 border-t border-slate-800/80 mt-auto">
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5 flex items-center justify-between">
          <div className="text-xs">
            <div className="text-slate-400">Subscription Tier</div>
            <div className="font-bold text-amber-400 flex items-center space-x-1">
              <span>★</span>
              <span>Pro Member</span>
            </div>
          </div>
          <span className="text-xs px-2 py-1 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-md font-mono">
            ×2 XP
          </span>
        </div>
      </div>
    </aside>
  );
}
