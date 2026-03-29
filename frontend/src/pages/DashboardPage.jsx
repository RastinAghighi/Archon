import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyticsApi, episodesApi, pipelineApi } from '../api/client';
import {
  BookOpen,
  Flame,
  Target,
  Brain,
  ChevronRight,
  Loader2,
  Play,
  Sparkles,
} from 'lucide-react';

function StatCard({ icon: Icon, label, children }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
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
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 animate-pulse">
      <div className="h-4 bg-gray-800 rounded w-24 mb-3" />
      <div className="h-8 bg-gray-800 rounded w-16" />
    </div>
  );
}

function ProgressBar({ percent, color = 'bg-blue-500', className = '' }) {
  return (
    <div className={`h-2 bg-gray-800 rounded-full overflow-hidden ${className}`}>
      <div
        className={`h-full rounded-full transition-all duration-500 ${color}`}
        style={{ width: `${Math.min(100, Math.max(0, percent))}%` }}
      />
    </div>
  );
}

function scoreColor(score) {
  if (score >= 80) return 'text-green-400';
  if (score >= 60) return 'text-yellow-400';
  return 'text-red-400';
}

function scoreBadgeColor(score) {
  if (score >= 80) return 'bg-green-500/20 text-green-400';
  if (score >= 60) return 'bg-yellow-500/20 text-yellow-400';
  return 'bg-red-500/20 text-red-400';
}

function phaseColor(index) {
  const colors = [
    'bg-blue-500',
    'bg-indigo-500',
    'bg-violet-500',
    'bg-purple-500',
    'bg-fuchsia-500',
    'bg-pink-500',
    'bg-rose-500',
  ];
  return colors[index % colors.length];
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const [overview, setOverview] = useState(null);
  const [episodes, setEpisodes] = useState(null);
  const [pipelineStatus, setPipelineStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        const [overviewRes, episodesRes, statusRes] = await Promise.all([
          analyticsApi.getOverview(),
          episodesApi.getAll(),
          pipelineApi.getStatus(),
        ]);
        setOverview(overviewRes.data);
        const allEps = episodesRes.data;
        setEpisodes(Array.isArray(allEps) ? allEps.slice(-5).reverse() : []);
        setPipelineStatus(statusRes.data);
      } catch (err) {
        console.error('Dashboard fetch error:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  async function handleGenerate() {
    setGenerating(true);
    try {
      await pipelineApi.run();
      const [overviewRes, episodesRes] = await Promise.all([
        analyticsApi.getOverview(),
        episodesApi.getAll(),
      ]);
      setOverview(overviewRes.data);
      const allEps = episodesRes.data;
      setEpisodes(Array.isArray(allEps) ? allEps.slice(-5).reverse() : []);
    } catch (err) {
      console.error('Generate error:', err);
    } finally {
      setGenerating(false);
    }
  }

  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  const totalEpisodes = 165;
  const completedCount = overview?.episodes_completed ?? 0;
  const completionPct = (completedCount / totalEpisodes) * 100;
  const streak = overview?.current_streak ?? 0;
  const overallScore = overview?.overall_score ?? 0;
  const knowledgeCoverage = overview?.knowledge_coverage ?? 0;
  const nextTopic = overview?.next_topic ?? pipelineStatus?.next_topic ?? null;
  const phases = overview?.phases ?? [];

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6 lg:p-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold">Welcome back</h1>
          <p className="text-gray-400 text-sm mt-1">{today}</p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="inline-flex items-center gap-2 bg-blue-500 hover:bg-blue-600 disabled:opacity-60 disabled:cursor-not-allowed text-white font-medium px-5 py-2.5 rounded-lg transition-colors"
        >
          {generating ? (
            <Loader2 size={18} className="animate-spin" />
          ) : (
            <Play size={18} />
          )}
          {generating ? 'Generating...' : 'Generate Episode'}
        </button>
      </div>

      {/* Stats Cards */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[...Array(4)].map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard icon={BookOpen} label="Episodes Completed">
            <p className="text-3xl font-bold tabular-nums">
              {completedCount}<span className="text-lg text-gray-500">/{totalEpisodes}</span>
            </p>
            <ProgressBar percent={completionPct} className="mt-3" />
          </StatCard>

          <StatCard icon={Flame} label="Current Streak">
            <p className="text-3xl font-bold tabular-nums">
              {streak} <span className="text-lg">🔥</span>
            </p>
            <p className="text-sm text-gray-500 mt-1">consecutive days</p>
          </StatCard>

          <StatCard icon={Target} label="Overall Score">
            <p className={`text-3xl font-bold tabular-nums ${scoreColor(overallScore)}`}>
              {overallScore}%
            </p>
          </StatCard>

          <StatCard icon={Brain} label="Knowledge Coverage">
            <p className="text-3xl font-bold tabular-nums text-blue-400">
              {knowledgeCoverage}%
            </p>
          </StatCard>
        </div>
      )}

      {/* Two-column section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Recent Episodes */}
        <div className="lg:col-span-2 bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">Recent Episodes</h2>
          {loading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-14 bg-gray-800 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : episodes && episodes.length > 0 ? (
            <div className="space-y-2">
              {episodes.map((ep) => (
                <button
                  key={ep.episode_number ?? ep.num}
                  onClick={() => navigate(`/episodes/${ep.episode_number ?? ep.num}`)}
                  className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-gray-800 transition-colors text-left group"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-mono text-gray-500 w-10">
                      #{String(ep.episode_number ?? ep.num).padStart(3, '0')}
                    </span>
                    <div>
                      <p className="font-medium text-gray-200 group-hover:text-white transition-colors">
                        {ep.topic ?? ep.title ?? 'Untitled'}
                      </p>
                      {ep.date && (
                        <p className="text-xs text-gray-500">{ep.date}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {ep.score != null && (
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${scoreBadgeColor(ep.score)}`}>
                        {ep.score}%
                      </span>
                    )}
                    <ChevronRight size={16} className="text-gray-600 group-hover:text-gray-400 transition-colors" />
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No episodes yet. Generate your first one!</p>
          )}
        </div>

        {/* Next Up */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Sparkles size={18} className="text-blue-400" />
            Next Up
          </h2>
          {loading ? (
            <div className="space-y-3 animate-pulse">
              <div className="h-6 bg-gray-800 rounded w-3/4" />
              <div className="h-4 bg-gray-800 rounded w-1/2" />
              <div className="h-4 bg-gray-800 rounded w-1/3" />
            </div>
          ) : nextTopic ? (
            <div>
              <p className="text-lg font-medium text-gray-100 mb-3">
                {nextTopic.name ?? nextTopic.topic ?? 'Next Topic'}
              </p>
              <div className="flex flex-wrap gap-2 mb-4">
                {nextTopic.category && (
                  <span className="text-xs px-2 py-1 rounded-full bg-blue-500/20 text-blue-400 font-medium">
                    {nextTopic.category}
                  </span>
                )}
                {nextTopic.depth && (
                  <span className="text-xs px-2 py-1 rounded-full bg-purple-500/20 text-purple-400 font-medium">
                    Depth: {nextTopic.depth}
                  </span>
                )}
              </div>
              <button
                onClick={handleGenerate}
                disabled={generating}
                className="w-full flex items-center justify-center gap-2 bg-blue-500 hover:bg-blue-600 disabled:opacity-60 disabled:cursor-not-allowed text-white font-medium px-4 py-2 rounded-lg transition-colors text-sm"
              >
                {generating ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  <Play size={16} />
                )}
                Generate Now
              </button>
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No upcoming topic found.</p>
          )}
        </div>
      </div>

      {/* Phase Progress */}
      {!loading && phases.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">Phase Progress</h2>
          <div className="space-y-4">
            {phases.map((phase, i) => {
              const pct = phase.completion ?? phase.percent ?? 0;
              const isCurrent = phase.current || phase.is_current;
              return (
                <div
                  key={phase.name ?? i}
                  className={`p-3 rounded-lg ${isCurrent ? 'bg-gray-800 ring-1 ring-blue-500/50' : ''}`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className={`text-sm font-medium ${isCurrent ? 'text-blue-400' : 'text-gray-300'}`}>
                      Phase {i + 1}: {phase.name}
                    </span>
                    <span className="text-sm tabular-nums text-gray-400">{Math.round(pct)}%</span>
                  </div>
                  <ProgressBar percent={pct} color={phaseColor(i)} />
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
