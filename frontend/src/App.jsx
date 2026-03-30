import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import DashboardPage from './pages/DashboardPage';
import EpisodesPage from './pages/EpisodesPage';
import AssessmentsPage from './pages/AssessmentsPage';
import SourcesPage from './pages/SourcesPage';
import AnalyticsPage from './pages/AnalyticsPage';
import PipelinePage from './pages/PipelinePage';
import PublicDashboardPage from './pages/PublicDashboardPage';
import SettingsPage from './pages/SettingsPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/public" element={<PublicDashboardPage />} />
        <Route element={<Layout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/episodes" element={<EpisodesPage />} />
          <Route path="/assessments" element={<AssessmentsPage />} />
          <Route path="/assessments/:episodeNum" element={<AssessmentsPage />} />
          <Route path="/sources" element={<SourcesPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/pipeline" element={<PipelinePage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
