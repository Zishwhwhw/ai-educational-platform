// ==========================================
// File: src/app/messages/page.tsx
// Description: Private Messaging UI (Discord-style DMs)
// Author: AI Agent
// Created: 2026-08-02
// ==========================================

"use client";

import React, { useState } from 'react';

export default function MessagesPage() {
  const [activeUser] = useState("AlexCodeMaster");
  const [messages, setMessages] = useState([
    { sender: "AlexCodeMaster", text: "Hey! How is your Python course going?" },
    { sender: "You", text: "Going great! Just completed the loops section and tested the CodeEditor." },
    { sender: "AlexCodeMaster", text: "Awesome! Let me know if you want to try Pair Programming mode later." },
  ]);
  const [input, setInput] = useState("");

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setMessages(prev => [...prev, { sender: "You", text: input }]);
    setInput("");
  };

  return (
    <div className="h-[calc(100vh-8rem)] bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden flex shadow-2xl">
      {/* User list */}
      <div className="w-72 bg-slate-950 border-r border-slate-800 p-4 space-y-2">
        <h2 className="font-bold text-lg mb-4 text-slate-300">Direct Messages</h2>
        <div className="p-3 bg-slate-800 rounded-xl cursor-pointer flex items-center space-x-3 border border-slate-700/60">
          <div className="w-9 h-9 rounded-lg bg-emerald-600 flex items-center justify-center font-bold text-white">A</div>
          <div>
            <div className="font-semibold text-sm">AlexCodeMaster</div>
            <div className="text-xs text-slate-400 truncate">Let me know if you want...</div>
          </div>
        </div>
      </div>

      {/* Chat window */}
      <div className="flex-1 flex flex-col">
        <div className="p-4 border-b border-slate-800 font-bold text-slate-200">
          Chat with @{activeUser}
        </div>

        <div className="flex-1 p-4 overflow-y-auto space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={`flex flex-col ${m.sender === "You" ? "items-end" : "items-start"}`}>
              <div className={`max-w-md px-4 py-2.5 rounded-2xl text-sm ${m.sender === "You" ? "bg-emerald-600 text-white" : "bg-slate-800 text-slate-200"}`}>
                {m.text}
              </div>
              <span className="text-[10px] text-slate-500 mt-1">{m.sender}</span>
            </div>
          ))}
        </div>

        <form onSubmit={handleSend} className="p-4 border-t border-slate-800 flex space-x-3">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-500"
          />
          <button type="submit" className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-sm font-semibold transition-colors">
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
