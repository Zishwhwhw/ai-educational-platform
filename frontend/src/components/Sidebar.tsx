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
    { name: 'Catalog', href: '/catalog', icon: '📚' },
    { name: 'Leaderboard', href: '/leaderboard', icon: '🏆' },
    { name: 'Store', href: '/store', icon: '💎' },
    { name: 'Achievements', href: '/achievements', icon: '🎯' },
    { name: 'Clans', href: '/clans', icon: '🛡️' },
    { name: 'Flashcards', href: '/flashcards', icon: '🧠' },
    { name: 'Messages', href: '/messages', icon: '💬' },
    { name: 'Profile', href: '/profile', icon: '👤' },
  ];

  return (
    <aside className="w-64 bg-surface border-r border-border p-4 hidden md:flex flex-col h-screen sticky top-0">
      <div className="flex items-center space-x-3 mb-8 px-2">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent text-base font-bold text-accent-fg">
          OC
        </div>
        <div className="text-xl font-extrabold text-text">
          OverCoding
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
                  ? 'bg-accent/10 text-accent border border-accent/30'
                  : 'text-text-2 hover:text-text hover:bg-raised'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="pt-4 border-t border-border mt-auto">
        <div className="bg-bg/60 border border-border rounded-xl p-3.5 flex items-center justify-between">
          <div className="text-xs">
            <div className="text-text-2">Subscription Tier</div>
            <div className="font-bold text-warning flex items-center space-x-1">
              <span>★</span>
              <span>Pro Member</span>
            </div>
          </div>
          <span className="text-xs px-2 py-1 bg-warning/10 text-warning border border-warning/20 rounded-md font-mono">
            ×2 XP
          </span>
        </div>
      </div>
    </aside>
  );
}
