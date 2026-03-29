import { Link, useLocation, Outlet } from 'react-router-dom';
import { BookOpen, BarChart3, Database, Settings, Play, Home, GraduationCap, Globe } from 'lucide-react';
import { clsx } from 'clsx';

const navItems = [
  { label: 'Dashboard', icon: Home, path: '/' },
  { label: 'Episodes', icon: BookOpen, path: '/episodes' },
  { label: 'Assessments', icon: GraduationCap, path: '/assessments' },
  { label: 'Sources', icon: Database, path: '/sources' },
  { label: 'Analytics', icon: BarChart3, path: '/analytics' },
  { label: 'Pipeline', icon: Play, path: '/pipeline' },
  { label: 'Public View', icon: Globe, path: '/public' },
  { label: 'Settings', icon: Settings, path: '/settings' },
];

const pageNames = {
  '/': 'Dashboard',
  '/episodes': 'Episodes',
  '/assessments': 'Assessments',
  '/sources': 'Sources',
  '/analytics': 'Analytics',
  '/pipeline': 'Pipeline',
  '/public': 'Public View',
  '/settings': 'Settings',
};

export default function Layout({ currentEpisode = 5, totalEpisodes = 165, streak = 0 }) {
  const location = useLocation();
  const currentPage = pageNames[location.pathname] || 'Archon';
  const progress = (currentEpisode / totalEpisodes) * 100;

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
      {/* Sidebar */}
      <aside className="w-60 flex-shrink-0 bg-gray-900 border-r border-gray-800 flex flex-col">
        {/* Logo */}
        <div className="px-5 py-6">
          <h1 className="text-xl font-bold tracking-widest bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            ARCHON
          </h1>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 space-y-0.5">
          {navItems.map(({ label, icon: Icon, path }) => {
            const isActive = location.pathname === path ||
              (path !== '/' && location.pathname.startsWith(path));

            return (
              <Link
                key={path}
                to={path}
                className={clsx(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-gray-800 text-white'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                )}
              >
                <Icon size={18} className={isActive ? 'text-blue-400' : undefined} />
                {label}
              </Link>
            );
          })}
        </nav>

        {/* Bottom stats */}
        <div className="px-5 py-4 border-t border-gray-800 space-y-3">
          <div>
            <div className="flex justify-between text-xs text-gray-400 mb-1.5">
              <span>Episode {currentEpisode}/{totalEpisodes}</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
          {streak > 0 && (
            <p className="text-xs text-gray-400">
              <span className="text-orange-400">&#x1F525;</span> {streak} day streak
            </p>
          )}
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="h-12 flex-shrink-0 border-b border-gray-800 flex items-center px-6">
          <h2 className="text-sm font-medium text-gray-300">{currentPage}</h2>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
