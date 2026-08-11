// ==========================================
// File: src/app/library/page.tsx
// Description: Course library with search and language filters
// Author: AI Agent
// Created: 2026-08-02
// ==========================================

"use client";

import React, { useState } from 'react';

const COURSES = [
  { id: 1, title: "Python Fundamentals", language: "Python", difficulty: "Beginner", description: "Learn variables, loops, functions, and OOP in Python 3.12.", progress: 65, color: "from-emerald-900 to-teal-900", isPreinstalled: true },
  { id: 2, title: "React to Mastery", language: "JavaScript", difficulty: "Intermediate", description: "Hooks, Context, Next.js 14 App Router, and State Management.", progress: 12, color: "from-blue-900 to-indigo-900", isPreinstalled: true },
  { id: 3, title: "Data Structures & Algorithms", language: "Python", difficulty: "Advanced", description: "Trees, Graphs, Dynamic Programming, and Big-O notation.", progress: 0, color: "from-purple-900 to-pink-900", isPreinstalled: false },
  { id: 4, title: "Go Microservices", language: "Go", difficulty: "Advanced", description: "Build scalable gRPC & REST microservices with Go.", progress: 0, color: "from-cyan-900 to-blue-900", isPreinstalled: false },
  { id: 5, title: "SQL & Relational Databases", language: "SQL", difficulty: "Beginner", description: "Master SELECT, JOINs, GROUP BY, indexes, and ACID transactions.", progress: 40, color: "from-amber-900 to-orange-900", isPreinstalled: true },
  { id: 6, title: "Rust for Systems Programming", language: "Rust", difficulty: "Advanced", description: "Memory safety without garbage collection, borrow checker, and concurrency.", progress: 0, color: "from-red-900 to-orange-900", isPreinstalled: false },
];

export default function LibraryPage() {
  const [search, setSearch] = useState("");
  const [selectedLang, setSelectedLang] = useState("All");

  const filtered = COURSES.filter(c => {
    const matchesSearch = c.title.toLowerCase().includes(search.toLowerCase()) || c.description.toLowerCase().includes(search.toLowerCase());
    const matchesLang = selectedLang === "All" || c.language === selectedLang;
    return matchesSearch && matchesLang;
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2">Course Library</h1>
        <p className="text-slate-400">Explore pre-installed fundamentals and AI-generated courses.</p>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4 justify-between items-center">
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search courses..."
          className="w-full md:w-96 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-500"
        />

        <div className="flex space-x-2 overflow-x-auto w-full md:w-auto">
          {["All", "Python", "JavaScript", "SQL", "Go", "Rust"].map(lang => (
            <button
              key={lang}
              onClick={() => setSelectedLang(lang)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition-colors border ${
                selectedLang === lang
                  ? 'bg-emerald-600 text-white border-emerald-500 shadow-[0_0_10px_rgba(5,150,105,0.4)]'
                  : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-white'
              }`}
            >
              {lang}
            </button>
          ))}
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map(course => (
          <div key={course.id} className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden hover:border-emerald-500/50 transition-colors group cursor-pointer flex flex-col">
            <div className={`h-36 bg-gradient-to-r ${course.color} relative p-5 flex flex-col justify-between`}>
              <div className="flex justify-between items-start">
                <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-black/40 text-white backdrop-blur-md">
                  {course.language}
                </span>
                {course.isPreinstalled && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    Pre-installed
                  </span>
                )}
              </div>
              <h3 className="text-xl font-bold text-white group-hover:text-emerald-400 transition-colors">
                {course.title}
              </h3>
            </div>

            <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
              <p className="text-slate-400 text-sm">{course.description}</p>

              <div>
                <div className="flex justify-between text-xs text-slate-400 mb-1.5 font-medium">
                  <span>Progress</span>
                  <span className="text-emerald-400 font-bold">{course.progress}%</span>
                </div>
                <div className="w-full h-2 bg-slate-800 rounded-full relative overflow-visible">
                  <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${course.progress}%` }}></div>
                  {course.progress > 0 && (
                    <div
                      className="absolute top-1/2 -translate-y-1/2 w-3.5 h-3.5 bg-emerald-400 rounded-full border-2 border-slate-900 shadow-[0_0_8px_rgba(52,211,153,0.8)]"
                      style={{ left: `calc(${course.progress}% - 7px)` }}
                    ></div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
