import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';

function DashboardPage() {
  return <h1 className="text-2xl font-bold">Dashboard</h1>;
}

function EpisodesPage() {
  return <h1 className="text-2xl font-bold">Episodes</h1>;
}

function AssessmentsPage() {
  return <h1 className="text-2xl font-bold">Assessments</h1>;
}

function SourcesPage() {
  return <h1 className="text-2xl font-bold">Sources</h1>;
}

function AnalyticsPage() {
  return <h1 className="text-2xl font-bold">Analytics</h1>;
}

function PipelinePage() {
  return <h1 className="text-2xl font-bold">Pipeline</h1>;
}

function PublicDashboardPage() {
  return <h1 className="text-2xl font-bold">Public Dashboard</h1>;
}

function SettingsPage() {
  return <h1 className="text-2xl font-bold">Settings</h1>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/episodes" element={<EpisodesPage />} />
          <Route path="/assessments" element={<AssessmentsPage />} />
          <Route path="/sources" element={<SourcesPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/pipeline" element={<PipelinePage />} />
          <Route path="/public" element={<PublicDashboardPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
