import Image from "next/image";
import CodeEditor from "../components/CodeEditor";

export default function Home() {
  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-3xl font-bold mb-6">Continue Learning</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          {/* Course Card 1 */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden hover:border-emerald-500/50 transition-colors cursor-pointer group">
            <div className="h-32 bg-gradient-to-r from-emerald-900 to-teal-900 relative">
              <div className="absolute inset-0 bg-black/20 group-hover:bg-transparent transition-colors"></div>
              <div className="absolute bottom-4 left-4 text-white font-bold text-lg">Python Fundamentals</div>
            </div>
            <div className="p-4">
              <div className="flex justify-between text-sm text-slate-400 mb-2">
                <span>Progress</span>
                <span>65%</span>
              </div>
              <div className="w-full h-2 bg-slate-800 rounded-full relative">
                <div className="absolute top-0 left-0 h-full bg-emerald-500 rounded-full" style={{ width: '65%' }}></div>
                <div className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-emerald-400 rounded-full border-2 border-slate-900 shadow-[0_0_10px_rgba(52,211,153,0.5)]" style={{ left: 'calc(65% - 8px)' }}></div>
              </div>
            </div>
          </div>

          {/* Course Card 2 */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden hover:border-emerald-500/50 transition-colors cursor-pointer group">
            <div className="h-32 bg-gradient-to-r from-blue-900 to-indigo-900 relative">
              <div className="absolute inset-0 bg-black/20 group-hover:bg-transparent transition-colors"></div>
              <div className="absolute bottom-4 left-4 text-white font-bold text-lg">React to Mastery</div>
            </div>
            <div className="p-4">
              <div className="flex justify-between text-sm text-slate-400 mb-2">
                <span>Progress</span>
                <span>12%</span>
              </div>
              <div className="w-full h-2 bg-slate-800 rounded-full relative">
                <div className="absolute top-0 left-0 h-full bg-blue-500 rounded-full" style={{ width: '12%' }}></div>
                <div className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-blue-400 rounded-full border-2 border-slate-900 shadow-[0_0_10px_rgba(96,165,250,0.5)]" style={{ left: 'calc(12% - 8px)' }}></div>
              </div>
            </div>
          </div>

        </div>
      </section>

      <section className="mt-12">
        <h2 className="text-2xl font-bold mb-6">Interactive Coding Task</h2>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="col-span-1 lg:col-span-1 bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-bold text-emerald-400 mb-4">Task: Python Loops</h3>
            <p className="text-slate-300 text-sm mb-4">
              Write a Python function `sum_even(numbers)` that takes a list of integers and returns the sum of all even numbers in the list.
            </p>
            <div className="bg-slate-950 p-4 rounded text-sm font-mono text-slate-400 mb-6">
              Input: [1, 2, 3, 4, 5, 6]<br/>
              Output: 12
            </div>
            
            <h4 className="font-bold text-sm text-slate-400 mb-2">AI Hint System</h4>
            <div className="space-y-2">
              <div className="px-3 py-2 bg-slate-800 rounded text-sm text-slate-300 border border-slate-700">Attempt 1: No hints yet.</div>
            </div>
          </div>
          <div className="col-span-1 lg:col-span-2">
            <CodeEditor initialCode="def sum_even(numbers):\n    # Your code here\n    pass\n" language="python" />
          </div>
        </div>
      </section>
    </div>
  );
}
