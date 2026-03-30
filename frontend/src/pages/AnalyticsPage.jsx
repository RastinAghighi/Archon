import { useState, useEffect } from 'react';
import { analyticsApi } from '../api/client';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, BarChart, Bar,
} from 'recharts';
import {
  BookOpen, Flame, Target, Clock, Brain,
  TrendingUp, TrendingDown, CheckCircle2, Lock, Loader2,
} from 'lucide-react';

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

function getCategoryColor(name) {
  return CATEGORY_COLORS[name] || '#6b7280';
}

function phaseColor(index) {
  const colors = [
    'bg-blue-500', 'bg-indigo-500', 'bg-violet-500', 'bg-purple-500',
    'bg-fuchsia-500', 'bg-pink-500', 'bg-rose-500',
  ];
  return colors[index % colors.length];
}

function CircularProgress({ percent, size = 48, strokeWidth = 4 }) {
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
        strokeLinecap="round" className="transition-all duration-700" />
    </svg>
  );
}

function StatCard({ icon: Icon, label, children }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex items-center gap-2 text-gray-400 text-sm mb-2">
        <Icon size={16} />
        <span>{label}</span>
      </div>
      {children}
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 animate-pulse">
      <div className="h-4 bg-gray-800 rounded w-24 mb-3" />
      <div className="h-8 bg-gray-800 rounded w-16" />
    </div>
  );
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm shadow-lg">
      <p className="text-gray-300 font-medium">Episode {d.episode}</p>
      {d.topic && <p className="text-gray-400 text-xs">{d.topic}</p>}
      <p className="text-blue-400 font-semibold mt-1">{d.score}%</p>
    </div>
  );
}

export default function AnalyticsPage() {
  const [overview, setOverview] = useState(null);
  const [scoreHistory, setScoreHistory] = useState(null);
  const [knowledgeGraph, setKnowledgeGraph] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [overviewRes, scoresRes, graphRes] = await Promise.all([
          analyticsApi.getOverview(),
          analyticsApi.getScoreHistory(),
          analyticsApi.getKnowledgeGraph(),
        ]);
        setOverview(overviewRes.data);
        setScoreHistory(scoresRes.data);
        setKnowledgeGraph(graphRes.data);
      } catch (err) {
        console.error('Analytics fetch error:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const completedCount = overview?.episodes_completed ?? 0;
  const completionPct = (completedCount / TOTAL_EPISODES) * 100;
  const streak = overview?.current_streak ?? 0;
  const avgScore = overview?.overall_score ?? 0;
  const scoreTrend = overview?.score_trend ?? 0;
  const studyHours = overview?.study_hours ?? Math.round(completedCount * 0.75);
  const knowledgeCoverage = overview?.knowledge_coverage ?? 0;

  const phases = overview?.phases ?? [];
  const categories = overview?.categories ?? knowledgeGraph?.categories ?? [];

  const scores = Array.isArray(scoreHistory) ? scoreHistory
    : scoreHistory?.scores ?? scoreHistory?.history ?? [];

  const topics = knowledgeGraph?.topics ?? knowledgeGraph?.nodes ?? [];
  const topicsByPhase = {};
  topics.forEach(t => {
    const phase = t.phase ?? 'Other';
    if (!topicsByPhase[phase]) topicsByPhase[phase] = [];
    topicsByPhase[phase].push(t);
  });

  const mastered = topics.filter(t => (t.confidence ?? 0) >= 0.9).length;
  const inProgress = topics.filter(t => (t.confidence ?? 0) > 0 && (t.confidence ?? 0) < 0.9).length;
  const notStarted = topics.filter(t => (t.confidence ?? 0) === 0).length;

  const categoryData = (Array.isArray(categories) ? categories : []).map(c => ({
    name: c.name ?? c.category ?? 'Unknown',
    confidence: Math.round((c.confidence ?? c.avg_confidence ?? 0) * 100),
    fill: getCategoryColor(c.name ?? c.category),
  }));

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Analytics & Progress</h1>
        <p className="text-gray-400 text-sm mt-1">Track your learning journey through all 165 episodes</p>
      </div>

      {/* Top Stats Row */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          {[...Array(5)].map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          <StatCard icon={BookOpen} label="Episodes">
            <div className="flex items-center gap-3">
              <CircularProgress percent={completionPct} />
              <p className="text-2xl font-bold tabular-nums">
                {completedCount}<span className="text-sm text-gray-500">/{TOTAL_EPISODES}</span>
              </p>
            </div>
          </StatCard>

          <StatCard icon={Flame} label="Streak">
            <p className="text-2xl font-bold tabular-nums">
              {streak} <span className="text-lg">days</span>
            </p>
          </StatCard>

          <StatCard icon={Target} label="Avg Score">
            <div className="flex items-center gap-2">
              <p className={`text-2xl font-bold tabular-nums ${
                avgScore >= 80 ? 'text-green-400' : avgScore >= 60 ? 'text-yellow-400' : 'text-red-400'
              }`}>
                {avgScore}%
              </p>
              {scoreTrend !== 0 && (
                <span className={`flex items-center text-xs ${scoreTrend > 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {scoreTrend > 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                  {Math.abs(scoreTrend)}%
                </span>
              )}
            </div>
          </StatCard>

          <StatCard icon={Clock} label="Study Hours">
            <p className="text-2xl font-bold tabular-nums">
              {studyHours}<span className="text-sm text-gray-500"> hrs</span>
            </p>
          </StatCard>

          <StatCard icon={Brain} label="Coverage">
            <p className="text-2xl font-bold tabular-nums text-blue-400">
              {knowledgeCoverage}%
            </p>
            <p className="text-xs text-gray-500 mt-1">confidence &gt; 0.6</p>
          </StatCard>
        </div>
      )}

      {/* Score Trend Chart */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-8">
        <h2 className="text-lg font-semibold mb-4">Assessment Scores Over Time</h2>
        {loading ? (
          <div className="h-72 bg-gray-800 rounded-lg animate-pulse" />
        ) : scores.length > 0 ? (
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={scores} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis
                dataKey="episode"
                stroke="#6b7280"
                tick={{ fill: '#9ca3af', fontSize: 12 }}
                label={{ value: 'Episode', position: 'insideBottom', offset: -2, fill: '#9ca3af' }}
              />
              <YAxis
                domain={[0, 100]}
                stroke="#6b7280"
                tick={{ fill: '#9ca3af', fontSize: 12 }}
                label={{ value: 'Score %', angle: -90, position: 'insideLeft', fill: '#9ca3af' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ color: '#9ca3af' }} />
              <Line
                type="monotone"
                dataKey="score"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: '#3b82f6', r: 3 }}
                activeDot={{ r: 6, fill: '#60a5fa' }}
                name="Score"
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-72 flex items-center justify-center text-gray-500">
            <p>No assessment scores yet. Complete some episodes to see your progress!</p>
          </div>
        )}
      </div>

      {/* Category Breakdown + Phase Progress */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Knowledge by Category */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">Knowledge by Category</h2>
          {loading ? (
            <div className="h-72 bg-gray-800 rounded-lg animate-pulse" />
          ) : categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={categoryData} layout="vertical"
                margin={{ top: 5, right: 20, bottom: 5, left: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={false} />
                <XAxis type="number" domain={[0, 100]} stroke="#6b7280"
                  tick={{ fill: '#9ca3af', fontSize: 12 }} />
                <YAxis type="category" dataKey="name" stroke="#6b7280" width={120}
                  tick={{ fill: '#9ca3af', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8 }}
                  labelStyle={{ color: '#d1d5db' }}
                  itemStyle={{ color: '#93c5fd' }}
                  formatter={(value) => [`${value}%`, 'Confidence']}
                />
                <Bar dataKey="confidence" radius={[0, 4, 4, 0]} barSize={20}>
                  {categoryData.map((entry, i) => (
                    <rect key={i} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-72 flex items-center justify-center text-gray-500">
              <p>No category data available yet.</p>
            </div>
          )}
        </div>

        {/* Phase Progress */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">Phase Progress</h2>
          {loading ? (
            <div className="space-y-4 animate-pulse">
              {[...Array(7)].map((_, i) => (
                <div key={i} className="h-14 bg-gray-800 rounded-lg" />
              ))}
            </div>
          ) : phases.length > 0 ? (
            <div className="space-y-3 max-h-[320px] overflow-y-auto pr-1">
              {phases.map((phase, i) => {
                const pct = Math.round(phase.completion ?? phase.percent ?? 0);
                const isCurrent = phase.current || phase.is_current;
                const isComplete = pct >= 100;
                const epCount = phase.episode_count ?? phase.episodes ?? 0;
                return (
                  <div
                    key={phase.name ?? i}
                    className={`p-3 rounded-lg border ${
                      isCurrent ? 'border-blue-500/50 bg-gray-800' : 'border-gray-800'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center gap-2">
                        {isComplete ? (
                          <CheckCircle2 size={16} className="text-green-400" />
                        ) : (
                          <span className="text-xs text-gray-500 font-mono w-4 text-center">{i + 1}</span>
                        )}
                        <span className={`text-sm font-medium ${
                          isCurrent ? 'text-blue-400' : isComplete ? 'text-green-400' : 'text-gray-300'
                        }`}>
                          {phase.name}
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        {epCount > 0 && (
                          <span className="text-xs text-gray-500">{epCount} eps</span>
                        )}
                        <span className="text-sm tabular-nums text-gray-400 w-10 text-right">{pct}%</span>
                      </div>
                    </div>
                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${phaseColor(i)}`}
                        style={{ width: `${Math.min(100, pct)}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="h-72 flex items-center justify-center text-gray-500">
              <p>No phase data available.</p>
            </div>
          )}
        </div>
      </div>

      {/* Knowledge Graph Summary */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-lg font-semibold mb-4">Knowledge Graph</h2>

        {/* Three stat boxes */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4 text-center">
            <p className="text-3xl font-bold text-green-400 tabular-nums">{mastered}</p>
            <p className="text-sm text-green-300 mt-1">Mastered</p>
            <p className="text-xs text-gray-500">confidence &ge; 90%</p>
          </div>
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4 text-center">
            <p className="text-3xl font-bold text-yellow-400 tabular-nums">{inProgress}</p>
            <p className="text-sm text-yellow-300 mt-1">In Progress</p>
            <p className="text-xs text-gray-500">0% &lt; confidence &lt; 90%</p>
          </div>
          <div className="bg-gray-500/10 border border-gray-600/20 rounded-lg p-4 text-center">
            <p className="text-3xl font-bold text-gray-400 tabular-nums">{notStarted}</p>
            <p className="text-sm text-gray-300 mt-1">Not Started</p>
            <p className="text-xs text-gray-500">confidence = 0%</p>
          </div>
        </div>

        {/* Topics grouped by phase */}
        {loading ? (
          <div className="h-40 bg-gray-800 rounded-lg animate-pulse" />
        ) : Object.keys(topicsByPhase).length > 0 ? (
          <div className="space-y-6">
            {Object.entries(topicsByPhase).map(([phaseName, phaseTopics]) => (
              <div key={phaseName}>
                <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
                  {phaseName}
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {phaseTopics.map((topic, i) => {
                    const conf = Math.round((topic.confidence ?? 0) * 100);
                    const unlocked = topic.unlocked !== false;
                    const status = conf >= 90 ? 'mastered' : conf > 0 ? 'progress' : 'not-started';
                    return (
                      <div
                        key={topic.name ?? i}
                        className={`flex items-center gap-3 p-2.5 rounded-lg ${
                          unlocked ? 'bg-gray-800/50' : 'bg-gray-800/20 opacity-50'
                        }`}
                      >
                        {!unlocked && <Lock size={14} className="text-gray-600 shrink-0" />}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-2 mb-1">
                            <span className={`text-sm truncate ${unlocked ? 'text-gray-200' : 'text-gray-500'}`}>
                              {topic.name ?? topic.topic}
                            </span>
                            <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 font-medium ${
                              status === 'mastered' ? 'bg-green-500/20 text-green-400'
                                : status === 'progress' ? 'bg-yellow-500/20 text-yellow-400'
                                : 'bg-gray-700 text-gray-500'
                            }`}>
                              {status === 'mastered' ? 'Mastered' : status === 'progress' ? `${conf}%` : 'New'}
                            </span>
                          </div>
                          <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full transition-all duration-500 ${
                                status === 'mastered' ? 'bg-green-500'
                                  : status === 'progress' ? 'bg-yellow-500'
                                  : 'bg-gray-700'
                              }`}
                              style={{ width: `${conf}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-sm text-center py-8">
            No knowledge graph data yet. Complete assessments to build your knowledge map!
          </p>
        )}
      </div>
    </div>
  );
}
