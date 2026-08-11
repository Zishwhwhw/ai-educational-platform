// ==========================================
// File: src/app/layout.tsx
// Description: Main root layout for the platform
// Author: AI Agent
// Created: 2026-08-02
// ==========================================

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";
import AISidebar from "@/components/AISidebar";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI-Code | Educational Platform",
  description: "Gamified educational platform for programming with AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-slate-950 text-white min-h-screen flex`}>
        {/* Navigation Sidebar */}
        <Sidebar />

        {/* Main Content Area */}
        <main className="flex-1 flex flex-col min-w-0">
          <Header />
          <div className="p-6 flex-1 overflow-y-auto">
            {children}
          </div>
        </main>

        {/* AI Mentor Sidebar */}
        <AISidebar />
      </body>
    </html>
  );
}
