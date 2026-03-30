import { useState, useEffect } from 'react';
import { pipelineApi } from '../api/client';
import {
  Play, Loader2, CheckCircle2, XCircle, ChevronDown,
  Clock, Zap, AlertTriangle, Terminal,
} from 'lucide-react';

function StatusBadge({ status }) {
  if (status === 'running') {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-yellow-500/20 text-yellow-400 text-sm font-medium">
        <span className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse" />
        Running
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-sm font-medium">
      <span className="w-2 h-2 rounded-full bg-green-400" />
      Ready
    </span>
  );
}

export default function PipelinePage() {
  const [status, setStatus] = useState(null);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Advanced options
  const [topicOverride, setTopicOverride] = useState('');
  const [skipPdf, setSkipPdf] = useState(false);
  const [skipAssessment, setSkipAssessment] = useState(false);
  const [skipSources, setSkipSources] = useState(false);
  const [skipPush, setSkipPush] = useState(false);
  const [usePaperEngine, setUsePaperEngine] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        const [statusRes, configRes] = await Promise.all([
          pipelineApi.getStatus(),
          pipelineApi.getConfig().catch(() => ({ data: null })),
        ]);
        setStatus(statusRes.data);
        setConfig(configRes.data);
      } catch (err) {
        console.error('Pipeline fetch error:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  async function handleRun() {
    setRunning(true);
    setLogs([]);
    setResult(null);
    setError(null);

    const addLog = (msg) => setLogs(prev => [...prev, { time: new Date(), msg }]);

    addLog('Starting pipeline...');

    const params = {};
    if (topicOverride.trim()) params.topic_id = topicOverride.trim();
    if (skipPdf) params.skip_pdf = true;
    if (skipAssessment) params.skip_assessment = true;
    if (skipSources) params.skip_sources = true;
    if (skipPush) params.skip_push = true;
    if (usePaperEngine) params.use_paper_engine = true;

    addLog('Sending request to pipeline API...');

    try {
      const res = await pipelineApi.run(params);
      addLog('Pipeline completed successfully!');
      setResult(res.data);

      // Refresh status
      const statusRes = await pipelineApi.getStatus();
      setStatus(statusRes.data);
    } catch (err) {
      const msg = err.response?.data?.detail ?? err.message;
      addLog(`Error: ${msg}`);
      setError(msg);
    } finally {
      setRunning(false);
    }
  }

  const pipelineStatus = running ? 'running' : (status?.status ?? 'ready');
  const lastRun = status?.last_run
    ? new Date(status.last_run).toLocaleString()
    : 'Never';
  const lastEpisode = status?.last_episode ?? status?.latest_episode ?? '—';
  const recentRuns = status?.recent_runs ?? [];

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Pipeline</h1>
        <p className="text-gray-400 text-sm mt-1">Generate episodes and manage the content pipeline</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Status + Run */}
        <div className="lg:col-span-2 space-y-6">
          {/* Status Card */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Pipeline Status</h2>
              <StatusBadge status={pipelineStatus} />
            </div>
            {loading ? (
              <div className="space-y-3 animate-pulse">
                <div className="h-4 bg-gray-800 rounded w-48" />
                <div className="h-4 bg-gray-800 rounded w-36" />
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Last Run</p>
                  <p className="text-sm font-medium text-gray-300 mt-1">{lastRun}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Last Episode</p>
                  <p className="text-sm font-medium text-gray-300 mt-1">{lastEpisode}</p>
                </div>
              </div>
            )}
          </div>

          {/* Generate Section */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="text-lg font-semibold mb-4">Generate Next Episode</h2>

            <button
              onClick={handleRun}
              disabled={running}
              className="w-full flex items-center justify-center gap-2 bg-blue-500 hover:bg-blue-600 disabled:opacity-60 disabled:cursor-not-allowed text-white font-semibold px-6 py-3 rounded-xl transition-colors text-lg"
            >
              {running ? (
                <Loader2 size={22} className="animate-spin" />
              ) : (
                <Play size={22} />
              )}
              {running ? 'Generating...' : 'Generate Next Episode'}
            </button>

            {/* Advanced Options */}
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-300 transition-colors mt-4"
            >
              <ChevronDown size={16} className={`transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
              Advanced Options
            </button>

            {showAdvanced && (
              <div className="mt-4 p-4 bg-gray-800/50 rounded-lg border border-gray-700 space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Topic Override</label>
                  <input
                    type="text"
                    value={topicOverride}
                    onChange={(e) => setTopicOverride(e.target.value)}
                    placeholder="e.g. linear_algebra_eigenvalues"
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-600 focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { label: 'Skip PDF', value: skipPdf, set: setSkipPdf },
                    { label: 'Skip Assessment', value: skipAssessment, set: setSkipAssessment },
                    { label: 'Skip Sources', value: skipSources, set: setSkipSources },
                    { label: 'Skip Push', value: skipPush, set: setSkipPush },
                    { label: 'Use Paper Engine', value: usePaperEngine, set: setUsePaperEngine },
                  ].map(({ label, value, set }) => (
                    <label key={label} className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={value}
                        onChange={(e) => set(e.target.checked)}
                        className="rounded bg-gray-700 border-gray-600 text-blue-500 focus:ring-blue-500"
                      />
                      {label}
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Progress Log */}
            {logs.length > 0 && (
              <div className="mt-6 bg-gray-950 border border-gray-800 rounded-lg p-4 max-h-60 overflow-y-auto">
                <div className="flex items-center gap-2 mb-3">
                  <Terminal size={14} className="text-gray-500" />
                  <span className="text-xs text-gray-500 uppercase tracking-wider font-medium">Pipeline Log</span>
                </div>
                <div className="space-y-1 font-mono text-xs">
                  {logs.map((log, i) => (
                    <div key={i} className="flex gap-2">
                      <span className="text-gray-600 shrink-0">
                        {log.time.toLocaleTimeString()}
                      </span>
                      <span className={log.msg.startsWith('Error') ? 'text-red-400' : 'text-gray-300'}>
                        {log.msg}
                      </span>
                    </div>
                  ))}
                  {running && (
                    <div className="flex items-center gap-2 text-blue-400">
                      <Loader2 size={12} className="animate-spin" />
                      <span>Processing...</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Result */}
            {result && (
              <div className="mt-4 bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 size={18} className="text-green-400" />
                  <span className="font-medium text-green-400">Episode Generated</span>
                </div>
                <div className="text-sm text-gray-300 space-y-1">
                  {result.episode_number && <p>Episode: #{String(result.episode_number).padStart(3, '0')}</p>}
                  {result.topic && <p>Topic: {result.topic}</p>}
                  {result.pdf_path && <p>PDF: {result.pdf_path}</p>}
                </div>
              </div>
            )}

            {/* Error */}
            {error && !running && (
              <div className="mt-4 bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                <div className="flex items-center gap-2">
                  <XCircle size={18} className="text-red-400" />
                  <span className="font-medium text-red-400">Pipeline Error</span>
                </div>
                <p className="text-sm text-gray-400 mt-1">{error}</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Schedule + Recent Runs */}
        <div className="space-y-6">
          {/* Schedule */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <Clock size={18} className="text-blue-400" />
              <h2 className="text-lg font-semibold">Schedule</h2>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Frequency</span>
                <span className="text-sm font-medium text-gray-200">Nightly at 2:00 AM</span>
              </div>
              <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
                <div className="flex items-start gap-2">
                  <AlertTriangle size={14} className="text-blue-400 mt-0.5 shrink-0" />
                  <p className="text-xs text-blue-300">
                    Automated scheduling via Azure Functions coming in Week 6
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Runs */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <Zap size={18} className="text-yellow-400" />
              <h2 className="text-lg font-semibold">Recent Runs</h2>
            </div>
            {loading ? (
              <div className="space-y-3 animate-pulse">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="h-12 bg-gray-800 rounded-lg" />
                ))}
              </div>
            ) : recentRuns.length > 0 ? (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {recentRuns.slice(0, 10).map((run, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      {run.status === 'success' ? (
                        <CheckCircle2 size={16} className="text-green-400 shrink-0" />
                      ) : (
                        <XCircle size={16} className="text-red-400 shrink-0" />
                      )}
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-gray-200 truncate">
                          {run.topic ?? `Episode #${run.episode_number ?? '?'}`}
                        </p>
                        <p className="text-xs text-gray-500">
                          {run.timestamp ? new Date(run.timestamp).toLocaleString() : '—'}
                        </p>
                      </div>
                    </div>
                    {run.cost && (
                      <span className="text-xs text-gray-500 shrink-0 ml-2">
                        ${run.cost.toFixed(2)}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm text-center py-6">No pipeline runs recorded yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
