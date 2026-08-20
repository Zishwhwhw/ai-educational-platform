// ==========================================
// File: src/components/AISidebar.tsx
// Description: Interactive AI Mentor sidebar component
// Author: AI Agent
// Created: 2026-08-02
// ==========================================

"use client";

import React, { useState } from 'react';

export default function AISidebar() {
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<{ role: 'user' | 'ai'; text: string }[]>([
    { role: 'ai', text: 'Ask me to generate a course or help you with your code!' }
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    const userMessage = prompt.trim();
    setMessages(prev => [...prev, { role: 'user', text: userMessage }]);
    setPrompt("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: userMessage })
      });
      
      const data = await response.json();
      setMessages(prev => [...prev, { role: 'ai', text: data.response }]);
    } catch (error) {
      console.error("Failed to fetch AI response:", error);
      setMessages(prev => [...prev, { role: 'ai', text: "Error: Could not reach the AI server. Is the FastAPI backend running?" }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <aside className="w-80 bg-surface border-l border-border p-4 hidden lg:flex flex-col h-screen">
      <div className="text-lg font-bold text-success mb-4 flex items-center">
        <span className="mr-2">✨</span> AI Mentor
      </div>
      
      <div className="flex-1 bg-bg rounded-lg border border-border p-4 overflow-y-auto mb-4 flex flex-col space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`p-3 rounded-lg text-sm max-w-[90%] ${msg.role === 'ai' ? 'bg-raised text-text self-start' : 'bg-accent text-text self-end'}`}>
            {msg.text}
          </div>
        ))}
        {isLoading && (
          <div className="p-3 rounded-lg text-sm max-w-[90%] bg-raised text-text-2 self-start flex space-x-1">
            <span className="animate-bounce">.</span>
            <span className="animate-bounce" style={{ animationDelay: '0.2s' }}>.</span>
            <span className="animate-bounce" style={{ animationDelay: '0.4s' }}>.</span>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="mt-auto">
        <input 
          type="text" 
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Prompt AI..." 
          disabled={isLoading}
          className="w-full bg-raised border border-border rounded-lg px-4 py-3 focus:outline-none focus:border-accent disabled:opacity-50" 
        />
      </form>
    </aside>
  );
}
