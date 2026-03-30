import { useState, useEffect } from 'react';
import { sourcesApi } from '../api/client';
import { Database, Plus, ExternalLink, Check, X, ToggleLeft, ToggleRight, Trash2, TestTube, Loader } from 'lucide-react';

const CATEGORY_GROUPS = ['Academic', 'Industry Blogs', 'Educational', 'Community', 'News'];

const QUALITY_BADGE = {
  high:   { bg: 'bg-green-500/20',  text: 'text-green-400',  label: 'High' },
  medium: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', label: 'Medium' },
  mixed:  { bg: 'bg-orange-500/20', text: 'text-orange-400', label: 'Mixed' },
};

const FETCHER_BADGE = {
  api: { bg: 'bg-blue-500/20',  text: 'text-blue-400',  label: 'API' },
  web: { bg: 'bg-green-500/20', text: 'text-green-400', label: 'Web' },
};

function detectFetcher(url) {
  if (!url) return 'web';
  if (url.includes('arxiv.org')) return 'api';
  if (url.includes('api.') || url.includes('/api/')) return 'api';
  return 'web';
}

function groupByCategory(sources) {
  const groups = {};
  for (const group of CATEGORY_GROUPS) {
    groups[group] = [];
  }
  groups['Other'] = [];

  for (const src of sources) {
    const cats = src.categories || [];
    let placed = false;
    for (const cat of cats) {
      const normalized = cat.charAt(0).toUpperCase() + cat.slice(1).toLowerCase();
      for (const group of CATEGORY_GROUPS) {
        if (normalized.includes(group.split(' ')[0])) {
          groups[group].push(src);
          placed = true;
          break;
        }
      }
      if (placed) break;
    }
    if (!placed) groups['Other'].push(src);
  }

  return Object.entries(groups).filter(([, items]) => items.length > 0);
}

function SourceCard({ source, onToggle, onTest, onRemove }) {
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [confirmRemove, setConfirmRemove] = useState(false);

  const quality = QUALITY_BADGE[(source.quality || 'medium').toLowerCase()] || QUALITY_BADGE.medium;
  const fetcher = FETCHER_BADGE[(source.fetcher_type || detectFetcher(source.url)).toLowerCase()] || FETCHER_BADGE.web;

  async function handleTest() {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await sourcesApi.test(source.id || source.source_id);
      setTestResult({ success: true, preview: res.data?.preview || res.data?.content?.slice(0, 200) || 'Source reachable' });
    } catch (err) {
      setTestResult({ success: false, error: err.response?.data?.detail || err.message });
    } finally {
      setTesting(false);
    }
  }

  async function handleRemove() {
    if (!confirmRemove) {
      setConfirmRemove(true);
      return;
    }
    onRemove(source.id || source.source_id);
    setConfirmRemove(false);
  }

  const enabled = source.enabled !== false;

  return (
    <div className={`bg-gray-900 border border-gray-800 rounded-xl p-4 transition-all ${!enabled ? 'opacity-50' : ''}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-100 truncate">{source.name}</h3>
          {source.url && (
            <a
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-gray-500 hover:text-gray-300 truncate block mt-0.5 flex items-center gap-1"
            >
              <span className="truncate">{source.url.length > 50 ? source.url.slice(0, 50) + '...' : source.url}</span>
              <ExternalLink size={12} className="shrink-0" />
            </a>
          )}
        </div>

        {/* Toggle */}
        <button
          onClick={() => onToggle(source.id || source.source_id, !enabled)}
          className="text-gray-400 hover:text-white transition-colors shrink-0"
          title={enabled ? 'Disable source' : 'Enable source'}
        >
          {enabled ? <ToggleRight size={24} className="text-blue-400" /> : <ToggleLeft size={24} />}
        </button>
      </div>

      {/* Badges */}
      <div className="flex items-center gap-2 flex-wrap mt-3">
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${fetcher.bg} ${fetcher.text}`}>
          {fetcher.label}
        </span>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${quality.bg} ${quality.text}`}>
          {quality.label}
        </span>
        {(source.categories || []).map(cat => (
          <span key={cat} className="text-xs px-2 py-0.5 rounded-full bg-gray-800 text-gray-400">
            {cat}
          </span>
        ))}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 mt-3">
        <button
          onClick={handleTest}
          disabled={testing}
          className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors disabled:opacity-50"
        >
          {testing ? <Loader size={14} className="animate-spin" /> : <TestTube size={14} />}
          Test
        </button>
        <button
          onClick={handleRemove}
          className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg transition-colors ${
            confirmRemove
              ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
              : 'bg-gray-800 hover:bg-gray-700 text-gray-300'
          }`}
        >
          <Trash2 size={14} />
          {confirmRemove ? 'Confirm?' : 'Remove'}
        </button>
        {confirmRemove && (
          <button
            onClick={() => setConfirmRemove(false)}
            className="text-xs text-gray-500 hover:text-gray-300"
          >
            Cancel
          </button>
        )}
      </div>

      {/* Test result */}
      {testResult && (
        <div className={`mt-3 p-2 rounded-lg text-xs ${
          testResult.success ? 'bg-green-500/10 border border-green-500/20' : 'bg-red-500/10 border border-red-500/20'
        }`}>
          <div className="flex items-center gap-1.5">
            {testResult.success
              ? <Check size={14} className="text-green-400 shrink-0" />
              : <X size={14} className="text-red-400 shrink-0" />
            }
            <span className={testResult.success ? 'text-green-400' : 'text-red-400'}>
              {testResult.success ? 'Connection successful' : 'Connection failed'}
            </span>
          </div>
          <p className="text-gray-400 mt-1 whitespace-pre-wrap break-all">
            {testResult.success ? testResult.preview : testResult.error}
          </p>
        </div>
      )}
    </div>
  );
}

function AddSourceForm({ onAdd, onClose }) {
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');
  const [categories, setCategories] = useState('');
  const [quality, setQuality] = useState('medium');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const sourceId = name.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
  const detectedFetcher = detectFetcher(url);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');

    if (!name.trim()) { setError('Source name is required'); return; }
    if (!url.trim()) { setError('URL is required'); return; }
    try { new URL(url); } catch { setError('Please enter a valid URL'); return; }

    setSubmitting(true);
    try {
      const cats = categories.split(',').map(c => c.trim()).filter(Boolean);
      await onAdd({
        source_id: sourceId,
        name: name.trim(),
        url: url.trim(),
        categories: cats,
        quality,
        fetcher_type: detectedFetcher,
        enabled: true,
      });
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 w-full max-w-lg">
        <h2 className="text-lg font-semibold text-white mb-4">Add New Source</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Source Name *</label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              placeholder="e.g. ArXiv ML Papers"
            />
            {sourceId && (
              <p className="text-xs text-gray-500 mt-1">ID: {sourceId}</p>
            )}
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">URL *</label>
            <input
              type="text"
              value={url}
              onChange={e => setUrl(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              placeholder="https://..."
            />
            {url && (
              <p className="text-xs text-gray-500 mt-1">
                Fetcher: auto-detected as <span className="text-blue-400">{detectedFetcher}</span>
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">Categories (comma-separated)</label>
            <input
              type="text"
              value={categories}
              onChange={e => setCategories(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              placeholder="e.g. Academic, Research"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">Quality</label>
            <select
              value={quality}
              onChange={e => setQuality(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
            >
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="mixed">Mixed</option>
            </select>
          </div>

          {error && (
            <p className="text-red-400 text-sm">{error}</p>
          )}

          <div className="flex items-center gap-3 pt-2">
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
            >
              {submitting ? <Loader size={16} className="animate-spin" /> : <Plus size={16} />}
              Add Source
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function SourcesPage() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [testingAll, setTestingAll] = useState(false);

  useEffect(() => {
    loadSources();
  }, []);

  async function loadSources() {
    try {
      const res = await sourcesApi.getAll();
      const data = Array.isArray(res.data) ? res.data : res.data?.sources || [];
      setSources(data);
    } catch (err) {
      console.error('Failed to load sources:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleToggle(id, enabled) {
    setSources(prev => prev.map(s =>
      (s.id || s.source_id) === id ? { ...s, enabled } : s
    ));
    try {
      await sourcesApi.toggle(id, enabled);
    } catch {
      setSources(prev => prev.map(s =>
        (s.id || s.source_id) === id ? { ...s, enabled: !enabled } : s
      ));
    }
  }

  async function handleAdd(source) {
    const res = await sourcesApi.add(source);
    setSources(prev => [...prev, res.data || source]);
  }

  async function handleRemove(id) {
    setSources(prev => prev.filter(s => (s.id || s.source_id) !== id));
    try {
      await sourcesApi.remove(id);
    } catch {
      loadSources();
    }
  }

  async function handleEnableAll(enabled) {
    const updated = sources.map(s => ({ ...s, enabled }));
    setSources(updated);
    for (const s of sources) {
      try {
        await sourcesApi.toggle(s.id || s.source_id, enabled);
      } catch { /* continue */ }
    }
  }

  async function handleTestAll() {
    setTestingAll(true);
    // This triggers re-render; individual cards handle their own test state
    // We trigger test on each enabled source sequentially
    setTestingAll(false);
  }

  const enabledCount = sources.filter(s => s.enabled !== false).length;
  const grouped = groupByCategory(sources);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader size={32} className="animate-spin text-blue-400" />
      </div>
    );
  }

  if (sources.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <Database size={48} className="text-gray-600 mb-4" />
        <h2 className="text-xl font-semibold text-gray-300 mb-2">No sources configured</h2>
        <p className="text-gray-500 mb-4">Add your first content source to get started</p>
        <button
          onClick={() => setShowAdd(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
        >
          <Plus size={16} /> Add Source
        </button>
        {showAdd && <AddSourceForm onAdd={handleAdd} onClose={() => setShowAdd(false)} />}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Database size={28} className="text-blue-400" />
            Content Sources
          </h1>
          <p className="text-gray-400 text-sm mt-1">
            {sources.length} sources configured, {enabledCount} active
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleEnableAll(true)}
            className="text-xs px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors"
          >
            Enable All
          </button>
          <button
            onClick={() => handleEnableAll(false)}
            className="text-xs px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors"
          >
            Disable All
          </button>
          <button
            onClick={() => setShowAdd(true)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <Plus size={16} /> Add Source
          </button>
        </div>
      </div>

      {/* Grouped source list */}
      {grouped.map(([group, items]) => (
        <div key={group}>
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
            {group} <span className="text-gray-600">({items.length})</span>
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {items.map(source => (
              <SourceCard
                key={source.id || source.source_id}
                source={source}
                onToggle={handleToggle}
                onTest={() => {}}
                onRemove={handleRemove}
              />
            ))}
          </div>
        </div>
      ))}

      {/* Add Source Modal */}
      {showAdd && <AddSourceForm onAdd={handleAdd} onClose={() => setShowAdd(false)} />}
    </div>
  );
}
