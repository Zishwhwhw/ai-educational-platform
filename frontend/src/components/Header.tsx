// ==========================================
// File: src/components/Header.tsx
// Description: Header with user stats (Coins, Pts, Streak) and controls
// Author: AI Agent
// Created: 2026-08-02
// ==========================================

"use client";

import React, { useState } from 'react';
import Link from 'next/link';

import ThemeToggle from '@/components/ThemeToggle';

export default function Header() {
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 flex h-16 items-center justify-between border-b border-border bg-surface px-6">
      <div className="flex min-w-0 items-center gap-3">
        {/* Приветствие прячется, когда места нет: обрезка до «Wel...» бесполезна.
            Настоящая причина тесноты — панель ИИ на 320px, которая по дизайн-
            документу должна жить только на экране урока. Переносится в F3. */}
        <h1 className="hidden text-lg font-bold text-text xl:block">Welcome back, Student</h1>
        <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-accent/10 text-success border border-accent/20">
          Regular (Lvl 2)
        </span>
      </div>

      <div className="flex items-center space-x-5">
        {/* Streak */}
        <div className="flex items-center space-x-1.5 bg-raised border border-border px-3 py-1.5 rounded-lg text-xs font-bold text-warning">
          <span className="text-base animate-pulse">🔥</span>
          <span>5 Days Streak</span>
        </div>

        {/* Coins */}
        <div className="flex items-center space-x-1.5 bg-raised border border-border px-3 py-1.5 rounded-lg text-xs font-bold text-warning">
          <span>💎</span>
          <span>150 Coins</span>
        </div>

        {/* Points */}
        <div className="flex items-center space-x-1.5 bg-raised border border-border px-3 py-1.5 rounded-lg text-xs font-bold text-success">
          <span>🏆</span>
          <span>450 Pts</span>
        </div>

        <ThemeToggle />

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setNotificationsOpen(!notificationsOpen)}
            className="w-9 h-9 rounded-lg bg-raised border border-border flex items-center justify-center text-text-2 hover:text-text transition-colors relative"
          >
            🔔
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-success"></span>
          </button>

          {notificationsOpen && (
            <div className="absolute right-0 mt-2 w-72 bg-surface border border-border rounded-xl shadow-2xl p-4 text-xs z-50 space-y-3">
              <div className="font-bold text-sm text-text flex justify-between">
                <span>Notifications</span>
                <span className="text-success font-normal cursor-pointer">Mark read</span>
              </div>
              <div className="space-y-2">
                <div className="bg-raised p-2.5 rounded-lg text-text-2">
                  🎉 Achievement unlocked: <span className="text-success font-semibold">First Steps</span>!
                </div>
                <div className="bg-raised p-2.5 rounded-lg text-text-2">
                  ⚡ Clan rating updated: Your clan is rank #3!
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Profile Avatar */}
        <Link href="/profile" className="w-9 h-9 rounded-xl bg-accent flex items-center justify-center font-bold text-text shadow-md hover:scale-105 transition-transform">
          S
        </Link>
      </div>
    </header>
  );
}
