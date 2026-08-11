// ==========================================
// File: src/app/store/page.tsx
// Description: Gamification Store UI
// Author: AI Agent
// Created: 2026-08-02
// ==========================================

"use client";

import React, { useEffect, useState } from 'react';

interface StoreItem {
  id: number;
  name: string;
  description: string;
  price_coins: number;
  item_type: string;
}

export default function StorePage() {
  const [items, setItems] = useState<StoreItem[]>([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/store/items")
      .then(res => res.json())
      .then(data => setItems(data))
      .catch(err => console.error(err));
  }, []);

  const handlePurchase = async (itemId: number) => {
    try {
      const res = await fetch("http://localhost:8000/store/purchase", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: 1, item_id: itemId }) // Mock user_id 1
      });
      const data = await res.json();
      setMessage(data.message || data.detail);
      setTimeout(() => setMessage(""), 3000);
    } catch (err) {
      setMessage("Failed to purchase item.");
    }
  };

  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-3xl font-bold mb-2">Platform Store</h1>
        <p className="text-slate-400 mb-8">Spend your hard-earned coins on cosmetics, themes, and avatars.</p>
        
        {message && (
          <div className="bg-emerald-900/50 border border-emerald-500 text-emerald-300 px-4 py-3 rounded-lg mb-6">
            {message}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map(item => (
            <div key={item.id} className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden hover:border-amber-500/50 transition-colors">
              <div className="h-32 bg-slate-800 flex items-center justify-center">
                <span className="text-4xl">
                  {item.item_type === 'theme' ? '🎨' : item.item_type === 'avatar' ? '👤' : '🎖️'}
                </span>
              </div>
              <div className="p-5 flex flex-col items-center text-center">
                <h3 className="font-bold text-lg mb-1">{item.name}</h3>
                <p className="text-slate-400 text-sm mb-4 h-10">{item.description}</p>
                <button 
                  onClick={() => handlePurchase(item.id)}
                  className="w-full flex items-center justify-center space-x-2 bg-slate-800 hover:bg-slate-700 text-white py-2 rounded-lg transition-colors border border-slate-700"
                >
                  <span>Buy for</span>
                  <span className="text-amber-400 font-bold">{item.price_coins} 💎</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
