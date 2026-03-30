import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { episodesApi } from '../api/client';
import { BookOpen, Download, GraduationCap, Search, Filter } from 'lucide-react';

const CATEGORY_COLORS = {
  linear_algebra: { bg: 'bg-blue-500/20', text: 'text-blue-400', hex: '#3b82f6' },
  calculus: { bg: 'bg-green-500/20', text: 'text-green-400', hex: '#22c55e' },
  probability: { bg: 'bg-purple-500/20', text: 'text-purple-400', hex: '#a855f7' },
  math_integration: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', hex: '#eab308' },
  classical_ml: { bg: 'bg-orange-500/20', text: 'text-orange-400', hex: '#f97316' },
  deep_learning: { bg: 'bg-red-500/20', text: 'text-red-400', hex: '#ef4444' },
  transformers: { bg: 'bg-cyan-500/20', text: 'text-cyan-400', hex: '#06b6d4' },
  generative: { bg: 'bg-pink-500/20', text: 'text-pink-400', hex: '#ec4899' },
  rl: { bg: 'bg-emerald-500/20', text: 'text-emerald-400', hex: '#10b981' },
  safety: { bg: 'bg-amber-500/20', text: 'text-amber-400', hex: '#f59e0b' },
};

const DEFAULT_CATEGORY = { bg: 'bg-gray-500/20', text: 'text-gray-400', hex: '#6b7280' };

const PAGE_SIZE = 20;

function getCategoryStyle(category) {
  return CATEGORY_COLORS[category] || DEFAULT_CATEGORY;
}

function formatDate(dateStr) {
  if (!dateStr) return null;
  const d = new Date(dateStr);
  if (isNaN(d)) return dateStr;
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function scoreColor(score) {
  if (score >= 80) return 'text-green-400';
  if (score >= 60) return 'text-yellow-400';
  return 'text-red-400';
}

function EpisodeCard({ episode, onRead, onDownload, onQuiz }) {
  const cat = getCategoryStyle(episode.category);
  const epNum = episode.episode_number ?? episode.num;

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-blue-500/50 transition-colors relative flex flex-col">
      {/* Episode number badge */}
      <span className="absolute -top-2.5 -left-2.5 w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-xs font-bold text-white">
        {epNum}
      </span>

      {/* Topic title */}
      <h3 className="font-semibold text-gray-100 truncate mt-1 mb-2">
        {episode.topic ?? episode.title ?? 'Untitled'}
      </h3>

      {/* Category badge + Phase */}
      <div className="flex items-center gap-2 flex-wrap mb-3">
        {episode.category && (
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${cat.bg} ${cat.text}`}>
            {episode.category.replace(/_/g, ' ')}
          </span>
        )}
        {episode.phase != null && (
          <span className="text-xs text-gray-500">Phase {episode.phase}</span>
        )}
      </div>

      {/* Date */}
      {(episode.date || episode.generated_date) && (
        <p className="text-xs text-gray-500 mb-2">
          {formatDate(episode.date || episode.generated_date)}
        </p>
      )}

      {/* Assessment score */}
      <div className="mb-4">
        {episode.score != null ? (
          <span className={`text-sm font-medium ${scoreColor(episode.score)}`}>
            {episode.score}%
          </span>
        ) : (
          <span className="text-sm text-gray-600">Not assessed</span>
        )}
      </div>

      {/* Spacer to push buttons to bottom */}
      <div className="mt-auto flex items-center gap-2">
        <button
          onClick={() => onRead(episode)}
          className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white transition-colors"
        >
          <BookOpen size={14} />
          Read
        </button>
        <button
          onClick={() => onDownload(epNum)}
          className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white transition-colors"
        >
          <Download size={14} />
          PDF
        </button>
        <button
          onClick={() => onQuiz(epNum)}
          className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 hover:text-blue-300 transition-colors"
        >
          <GraduationCap size={14} />
          Quiz
        </button>
      </div>
    </div>
  );
}

function ReadModal({ episode, onClose }) {
  if (!episode) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4" onClick={onClose}>
      <div
        className="bg-gray-900 border border-gray-800 rounded-xl max-w-3xl w-full max-h-[80vh] overflow-y-auto p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-100">
            Episode {episode.episode_number ?? episode.num}: {episode.topic ?? episode.title ?? 'Untitled'}
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-300 text-xl leading-none">&times;</button>
        </div>
        <div className="prose prose-invert max-w-none text-sm text-gray-300 whitespace-pre-wrap">
          {episode.markdown || episode.content || 'No content available.'}
        </div>
      </div>
    </div>
  );
}

export default function EpisodesPage() {
  const navigate = useNavigate();
  const [episodes, setEpisodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  const [page, setPage] = useState(1);
  const [readingEpisode, setReadingEpisode] = useState(null);

  useEffect(() => {
    async function fetchEpisodes() {
      try {
        const res = await episodesApi.getAll();
        const data = Array.isArray(res.data) ? res.data : [];
        setEpisodes(data);
      } catch (err) {
        console.error('Failed to fetch episodes:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchEpisodes();
  }, []);

  const filtered = useMemo(() => {
    let result = [...episodes];

    // Search filter
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter((ep) => {
        const topic = (ep.topic ?? ep.title ?? '').toLowerCase();
        return topic.includes(q);
      });
    }

    // Sort
    if (sortBy === 'newest') {
      result.sort((a, b) => (b.episode_number ?? b.num ?? 0) - (a.episode_number ?? a.num ?? 0));
    } else if (sortBy === 'oldest') {
      result.sort((a, b) => (a.episode_number ?? a.num ?? 0) - (b.episode_number ?? b.num ?? 0));
    } else if (sortBy === 'phase') {
      result.sort((a, b) => (a.phase ?? 0) - (b.phase ?? 0));
    }

    return result;
  }, [episodes, searchQuery, sortBy]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  // Reset to page 1 when filters change
  useEffect(() => {
    setPage(1);
  }, [searchQuery, sortBy]);

  function handleRead(episode) {
    setReadingEpisode(episode);
  }

  function handleDownload(epNum) {
    const url = episodesApi.getPdfUrl(epNum);
    window.open(url, '_blank');
  }

  function handleQuiz(epNum) {
    navigate(`/assessments/${epNum}`);
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Episodes</h1>
        <p className="text-gray-400 text-sm mt-1">
          {loading ? 'Loading...' : `${episodes.length} episodes generated`}
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            placeholder="Search by topic..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-gray-900 border border-gray-800 rounded-lg pl-9 pr-4 py-2 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-500/50 transition-colors"
          />
        </div>
        <div className="relative">
          <Filter size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-gray-900 border border-gray-800 rounded-lg pl-9 pr-8 py-2 text-sm text-gray-200 appearance-none focus:outline-none focus:border-blue-500/50 transition-colors cursor-pointer"
          >
            <option value="newest">Newest first</option>
            <option value="oldest">Oldest first</option>
            <option value="phase">By phase</option>
          </select>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-gray-900 border border-gray-800 rounded-xl p-5 animate-pulse">
              <div className="h-5 bg-gray-800 rounded w-3/4 mb-3" />
              <div className="h-4 bg-gray-800 rounded w-1/2 mb-2" />
              <div className="h-3 bg-gray-800 rounded w-1/3 mb-4" />
              <div className="h-8 bg-gray-800 rounded w-full" />
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-gray-500">
          <BookOpen size={48} className="mb-4 text-gray-700" />
          <p className="text-lg font-medium text-gray-400">
            {episodes.length === 0
              ? 'No episodes yet. Generate your first episode from the Dashboard.'
              : 'No episodes match your search.'}
          </p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {paginated.map((ep) => (
              <EpisodeCard
                key={ep.episode_number ?? ep.num}
                episode={ep}
                onRead={handleRead}
                onDownload={handleDownload}
                onQuiz={handleQuiz}
              />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1.5 text-sm rounded-lg bg-gray-900 border border-gray-800 text-gray-400 hover:text-white hover:border-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                Previous
              </button>
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter((p) => p === 1 || p === totalPages || Math.abs(p - page) <= 1)
                .reduce((acc, p, idx, arr) => {
                  if (idx > 0 && p - arr[idx - 1] > 1) {
                    acc.push(<span key={`gap-${p}`} className="text-gray-600 px-1">...</span>);
                  }
                  acc.push(
                    <button
                      key={p}
                      onClick={() => setPage(p)}
                      className={`w-8 h-8 text-sm rounded-lg transition-colors ${
                        p === page
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white hover:border-gray-700'
                      }`}
                    >
                      {p}
                    </button>
                  );
                  return acc;
                }, [])}
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-1.5 text-sm rounded-lg bg-gray-900 border border-gray-800 text-gray-400 hover:text-white hover:border-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {/* Read Modal */}
      <ReadModal episode={readingEpisode} onClose={() => setReadingEpisode(null)} />
    </div>
  );
}
