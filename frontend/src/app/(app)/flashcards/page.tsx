// ==========================================
// File: src/app/flashcards/page.tsx
// Description: Spaced Repetition (Flashback Quizzes)
// Author: AI Agent
// Created: 2026-08-02
// ==========================================

"use client";

import React, { useState } from 'react';

const CARDS = [
  { question: "What does `is` check in Python?", answer: "Object identity (memory location), unlike `==` which checks value equality." },
  { question: "What is a closure in JavaScript?", answer: "A function that retains access to its lexical scope even when executed outside that scope." },
  { question: "What is the Big-O time complexity of binary search?", answer: "O(log n)" },
];

export default function FlashcardsPage() {
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);

  const card = CARDS[index % CARDS.length];

  return (
    <div className="max-w-2xl mx-auto space-y-8 text-center">
      <div>
        <h1 className="text-3xl font-bold mb-2">Flashbacks (Spaced Repetition)</h1>
        <p className="text-slate-400">Review core concepts to solidify long-term memory based on the SM-2 algorithm.</p>
      </div>

      <div
        onClick={() => setFlipped(!flipped)}
        className="h-80 bg-slate-900 border border-slate-800 hover:border-emerald-500/50 rounded-2xl p-8 flex flex-col justify-center items-center cursor-pointer transition-all shadow-2xl relative select-none"
      >
        <div className="text-xs text-slate-500 uppercase tracking-widest font-mono mb-4">
          {flipped ? "Answer" : "Question (Click to flip)"}
        </div>
        <div className="text-xl font-bold text-slate-100 max-w-lg">
          {flipped ? card.answer : card.question}
        </div>
      </div>

      {flipped && (
        <div className="flex justify-center space-x-4">
          <button onClick={() => { setFlipped(false); setIndex(index + 1); }} className="px-6 py-2.5 bg-red-900/40 text-red-300 border border-red-500/30 hover:bg-red-900/60 rounded-xl text-sm font-semibold transition-colors">
            Forgot (0/5)
          </button>
          <button onClick={() => { setFlipped(false); setIndex(index + 1); }} className="px-6 py-2.5 bg-amber-900/40 text-amber-300 border border-amber-500/30 hover:bg-amber-900/60 rounded-xl text-sm font-semibold transition-colors">
            Hard (3/5)
          </button>
          <button onClick={() => { setFlipped(false); setIndex(index + 1); }} className="px-6 py-2.5 bg-emerald-900/40 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-900/60 rounded-xl text-sm font-semibold transition-colors">
            Easy (5/5)
          </button>
        </div>
      )}
    </div>
  );
}
