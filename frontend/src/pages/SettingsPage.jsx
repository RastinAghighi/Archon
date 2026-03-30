import { useState, useEffect } from 'react';
import { pipelineApi } from '../api/client';
import {
  Cpu, FileText, FolderOpen, DollarSign, Info, Loader2, ExternalLink,
} from 'lucide-react';

function SectionCard({ icon: Icon, title, children }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-4">
        <Icon size={18} className="text-blue-400" />
        <h2 className="text-lg font-semibold">{title}</h2>
      </div>
      {children}
    </div>
  );
}

function ConfigRow({ label, value, mono = false }) {
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-gray-800 last:border-0">
      <span className="text-sm text-gray-400">{label}</span>
      <span className={`text-sm text-gray-200 ${mono ? 'font-mono' : 'font-medium'}`}>
        {value}
      </span>
    </div>
  );
}

const DEFAULT_MODELS = [
  { module: 'Document Writer', model: 'claude-opus-4-20250514' },
  { module: 'Curriculum Planner', model: 'claude-haiku-4-5-20251001' },
  { module: 'Source Ranker', model: 'claude-sonnet-4-20250514' },
  { module: 'Assessment Generator', model: 'claude-haiku-4-5-20251001' },
  { module: 'Show Notes', model: 'claude-sonnet-4-20250514' },
];

const DEFAULT_EPISODE_CONFIG = {
  target_words: 6000,
  target_pages: 15,
  study_time: 60,
};

const DEFAULT_PATHS = {
  pdfs: 'output/pdfs/',
  markdown: 'output/markdown/',
  assessments: 'output/assessments/',
  show_notes: 'output/show_notes/',
};

export default function SettingsPage() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchConfig() {
      try {
        const res = await pipelineApi.getConfig();
        setConfig(res.data);
      } catch (err) {
        console.error('Settings fetch error:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchConfig();
  }, []);

  const models = config?.models ?? DEFAULT_MODELS;
  const episodeConfig = config?.episode ?? DEFAULT_EPISODE_CONFIG;
  const paths = config?.paths ?? DEFAULT_PATHS;
  const episodesThisMonth = config?.usage?.episodes_this_month ?? 0;
  const costPerEpisode = config?.usage?.cost_per_episode ?? 0.69;
  const estimatedMonthlyCost = episodesThisMonth * costPerEpisode;

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 text-gray-100 p-6 lg:p-8">
        <h1 className="text-2xl font-bold mb-8">Settings</h1>
        <div className="flex items-center justify-center py-20">
          <Loader2 size={32} className="animate-spin text-gray-500" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-gray-400 text-sm mt-1">Configuration and system information</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Model Configuration */}
        <SectionCard icon={Cpu} title="Model Configuration">
          <div className="divide-y divide-gray-800">
            {(Array.isArray(models) ? models : DEFAULT_MODELS).map(({ module, model }) => (
              <div key={module} className="flex items-center justify-between py-3 first:pt-0 last:pb-0">
                <span className="text-sm text-gray-400">{module}</span>
                <span className="text-xs font-mono bg-gray-800 px-2.5 py-1 rounded-md text-gray-300">
                  {model}
                </span>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-600 mt-4">
            Models are configured in settings.yaml. Editing via UI coming soon.
          </p>
        </SectionCard>

        {/* Episode Configuration */}
        <SectionCard icon={FileText} title="Episode Configuration">
          <ConfigRow label="Target Words" value={`${episodeConfig.target_words ?? 6000} words`} />
          <ConfigRow label="Target Pages" value={`${episodeConfig.target_pages ?? 15} pages`} />
          <ConfigRow label="Study Time" value={`${episodeConfig.study_time ?? 60} minutes`} />
          <p className="text-xs text-gray-600 mt-4">
            These values are used by the document writer for episode generation.
          </p>
        </SectionCard>

        {/* Output Paths */}
        <SectionCard icon={FolderOpen} title="Output Paths">
          <ConfigRow label="PDFs" value={paths.pdfs ?? 'output/pdfs/'} mono />
          <ConfigRow label="Markdown" value={paths.markdown ?? 'output/markdown/'} mono />
          <ConfigRow label="Assessments" value={paths.assessments ?? 'output/assessments/'} mono />
          <ConfigRow label="Show Notes" value={paths.show_notes ?? 'output/show_notes/'} mono />
        </SectionCard>

        {/* API Usage Estimate */}
        <SectionCard icon={DollarSign} title="API Usage Estimate">
          <ConfigRow label="Episodes This Month" value={episodesThisMonth} />
          <ConfigRow label="Est. Cost Per Episode" value={`~$${costPerEpisode.toFixed(2)}`} />
          <div className="mt-4 bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">Estimated Monthly Cost</span>
              <span className="text-lg font-bold text-blue-400 tabular-nums">
                ~${estimatedMonthlyCost.toFixed(2)}
              </span>
            </div>
          </div>
        </SectionCard>

        {/* About */}
        <div className="lg:col-span-2">
          <SectionCard icon={Info} title="About">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-1">
              <ConfigRow label="Version" value="0.1.0" />
              <ConfigRow label="Built by" value="Rastin Aghighi" />
              <ConfigRow label="Powered by" value="Claude API (Anthropic)" />
              <div className="flex items-center justify-between py-2.5 border-b border-gray-800">
                <span className="text-sm text-gray-400">GitHub</span>
                <a
                  href="https://github.com/RastinAghighi/Archon"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-1"
                >
                  RastinAghighi/Archon
                  <ExternalLink size={12} />
                </a>
              </div>
            </div>
          </SectionCard>
        </div>
      </div>
    </div>
  );
}
