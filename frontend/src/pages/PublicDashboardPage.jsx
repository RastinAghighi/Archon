import { useState, useEffect } from 'react';
import { analyticsApi } from '../api/client';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Loader2 } from 'lucide-react';

const TOTAL_EPISODES = 165;

const CATEGORY_COLORS = {
  'Linear Algebra': '#3b82f6',
  'Calculus': '#8b5cf6',
  'Probability': '#f59e0b',
  'Statistics': '#10b981',
  'Optimization': '#ef4444',
  'Information Theory': '#ec4899',
  'Machine Learning': '#6366f1',
  'Deep Learning': '#14b8a6',
  'Signal Processing': '#f97316',
  'Numerical Methods': '#a855f7',
};

function CircularProgress({ percent, size = 160, strokeWidth = 10 }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percent / 100) * circumference;
  return (
    <svg width={size} height={size} className="transform -rotate-90">
      <circle cx={size / 2} cy={size / 2} r={radius}
        stroke="#1f2937" strokeWidth={strokeWidth} fill="none" />
      <circle cx={size / 2} cy={size / 2} r={radius}
        stroke="#3b82f6" strokeWidth={strokeWidth} fill="none"
        strokeDasharray={circumference} strokeDashoffset={offset}
        strokeLinecap="round" className="transition-all duration-1000" />
    </svg>
  );
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm shadow-lg">
      <p className="text-gray-300 font-medium">Episode {d.episode}</p>
      <p className="text-blue-400 font-semibold mt-1">{d.score}%</p>
    </div>
  );
}

export default function PublicDashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await analyticsApi.getPublic();
        setData(res.data);
      } catch (err) {
        console.error('Public dashboard fetch error:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const completedCount = data?.episodes_completed ?? 0;
  const completionPct = (completedCount / TOTAL_EPISODES) * 100;
  const streak = data?.current_streak ?? 0;
  const avgScore = data?.overall_score ?? data?.avg_score ?? 0;
  const categories = data?.categories ?? [];
  const phases = data?.phases ?? [];
  const scores = Array.isArray(data?.score_history) ? data.score_history
    : data?.score_history?.scores ?? data?.score_history?.history ?? [];
  const lastUpdated = data?.last_updated
    ? new Date(data.last_updated).toLocaleDateString('en-US', {
        year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit',
      })
    : new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <Loader2 size={48} className="animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="pt-16 pb-12 text-center">
        <h1 className="text-5xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 via-violet-400 to-fuchsia-400 bg-clip-text text-transparent">
          ARCHON
        </h1>
        <p className="text-gray-400 text-lg mt-3">AI/ML Learning Journey</p>
        <p className="text-gray-600 text-sm mt-2">Last updated: {lastUpdated}</p>
      </header>

      <div className="max-w-5xl mx-auto px-6 pb-16">
        {/* Hero Stats */}
        <div className="flex flex-col md:flex-row items-center justify-center gap-12 mb-16">
          {/* Circular Progress */}
          <div className="relative flex flex-col items-center">
            <CircularProgress percent={completionPct} size={180} strokeWidth={12} />
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-4xl font-bold tabular-nums">{completedCount}</span>
              <span className="text-gray-400 text-sm">/{TOTAL_EPISODES} Episodes</span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-8 text-center">
            <div>
              <p className="text-5xl font-bold tabular-nums">
                {streak} <span className="text-3xl">🔥</span>
              </p>
              <p className="text-gray-400 text-sm mt-2">Day Streak</p>
            </div>
            <div>
              <p className={`text-5xl font-bold tabular-nums ${
                avgScore >= 80 ? 'text-green-400' : avgScore >= 60 ? 'text-yellow-400' : 'text-red-400'
              }`}>
                {avgScore}%
              </p>
              <p className="text-gray-400 text-sm mt-2">Average Score</p>
            </div>
          </div>
        </div>

        {/* Category Breakdown */}
        {categories.length > 0 && (
          <div className="bg-gray-900/60 border border-gray-800 rounded-2xl p-8 mb-10">
            <h2 className="text-xl font-semibold mb-6 text-center">Category Breakdown</h2>
            <div className="space-y-4 max-w-2xl mx-auto">
              {categories.map((cat) => {
                const name = cat.name ?? cat.category ?? 'Unknown';
                const confidence = Math.round((cat.confidence ?? cat.avg_confidence ?? 0) * 100);
                const color = CATEGORY_COLORS[name] || '#6b7280';
                return (
                  <div key={name}>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-sm font-medium text-gray-300">{name}</span>
                      <span className="text-sm tabular-nums text-gray-400">{confidence}%</span>
                    </div>
                    <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{ width: `${confidence}%`, backgroundColor: color }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Score Trend */}
        {scores.length > 0 && (
          <div className="bg-gray-900/60 border border-gray-800 rounded-2xl p-8 mb-10">
            <h2 className="text-xl font-semibold mb-6 text-center">Score Trend</h2>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={scores} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="episode" stroke="#6b7280" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                <YAxis domain={[0, 100]} stroke="#6b7280" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone" dataKey="score" stroke="#3b82f6" strokeWidth={2}
                  dot={{ fill: '#3b82f6', r: 3 }} activeDot={{ r: 6, fill: '#60a5fa' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Phase Timeline */}
        {phases.length > 0 && (
          <div className="bg-gray-900/60 border border-gray-800 rounded-2xl p-8 mb-10">
            <h2 className="text-xl font-semibold mb-8 text-center">Phase Timeline</h2>
            <div className="flex items-center justify-between relative max-w-3xl mx-auto">
              {/* Connecting line */}
              <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-700" />

              {phases.map((phase, i) => {
                const pct = phase.completion ?? phase.percent ?? 0;
                const isCurrent = phase.current || phase.is_current;
                const isComplete = pct >= 100;
                return (
                  <div key={phase.name ?? i} className="relative flex flex-col items-center z-10" style={{ flex: 1 }}>
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-all ${
                        isComplete
                          ? 'bg-blue-500 border-blue-500 text-white'
                          : isCurrent
                          ? 'bg-blue-500/20 border-blue-500 text-blue-400 animate-pulse'
                          : 'bg-gray-800 border-gray-600 text-gray-500'
                      }`}
                    >
                      {isComplete ? '✓' : i + 1}
                    </div>
                    <p className={`text-xs mt-2 text-center max-w-[80px] leading-tight ${
                      isCurrent ? 'text-blue-400 font-medium' : isComplete ? 'text-gray-300' : 'text-gray-500'
                    }`}>
                      {phase.name}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="text-center pt-8 pb-4 border-t border-gray-800">
          <p className="text-gray-500 text-sm">
            Built with Claude AI, Python, React, and ☕
          </p>
          <p className="text-gray-600 text-xs mt-2">
            Powered by Archon — github.com/RastinAghighi/Archon
          </p>
        </footer>
      </div>
    </div>
  );
}
