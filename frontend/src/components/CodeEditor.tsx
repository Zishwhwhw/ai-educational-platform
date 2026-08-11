// ==========================================
// File: src/components/CodeEditor.tsx
// Description: Monaco Editor component with WebSocket integration for Anti-Fraud & Execution
// Author: AI Agent
// Created: 2026-08-02
// ==========================================

"use client";

import React, { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';

interface CodeEditorProps {
  initialCode?: string;
  language?: string;
  roomId?: string;
}

export default function CodeEditor({ 
  initialCode = '# Write your Python code here\n', 
  language = 'python',
  roomId = 'default_room'
}: CodeEditorProps) {
  const [code, setCode] = useState(initialCode);
  const [statusMsg, setStatusMsg] = useState("");
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to WebSocket on mount
    const ws = new WebSocket(`ws://localhost:8000/ws/editor/${roomId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log(`Connected to room: ${roomId}`);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === "code_change") {
        // Someone else typed
        setCode(data.code);
      } else if (data.type === "execution_result") {
        // Run code result (or anti-fraud)
        if (data.status === "error") {
          setStatusMsg(`❌ ${data.message}`);
        } else {
          setStatusMsg(`✅ ${data.message} Points earned: +${data.points}`);
        }
      }
    };

    return () => {
      ws.close();
    };
  }, [roomId]);

  const handleEditorChange = (value: string | undefined) => {
    const newCode = value || "";
    setCode(newCode);
    
    // Broadcast change
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: "code_change",
        code: newCode
      }));
    }
  };

  const handleRunCode = () => {
    setStatusMsg("Running...");
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: "run_code",
        code: code
      }));
    } else {
      setStatusMsg("❌ Disconnected from server.");
    }
  };

  return (
    <div className="flex flex-col h-[500px] w-full rounded-xl overflow-hidden border border-slate-800 bg-slate-900 shadow-xl">
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-3 flex items-center justify-between">
        <div className="flex space-x-2">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <div className="w-3 h-3 rounded-full bg-amber-500"></div>
          <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
        </div>
        <div className="text-sm text-slate-400 font-mono">main.py</div>
        <div className="flex items-center space-x-4">
          <span className="text-sm font-semibold">{statusMsg}</span>
          <button 
            onClick={handleRunCode}
            className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs px-3 py-1 rounded shadow-[0_0_10px_rgba(5,150,105,0.4)] transition-all"
          >
            Run Code
          </button>
        </div>
      </div>
      <div className="flex-1 relative">
        <Editor
          height="100%"
          language={language}
          theme="vs-dark"
          value={code}
          onChange={handleEditorChange}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            padding: { top: 16 },
            roundedSelection: false,
            scrollBeyondLastLine: false,
            cursorBlinking: "smooth",
          }}
        />
      </div>
    </div>
  );
}
