import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Monitor,
  AlertTriangle,
  Cpu,
  FlaskConical,
  HeartPulse,
  Sparkles,
  BookOpen
} from 'lucide-react';

const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/dashboard', label: 'SOC Overview', icon: LayoutDashboard },
    { to: '/endpoints', label: 'Endpoints', icon: Monitor },
    { to: '/model-center', label: 'AI Model Center', icon: Cpu },
    { to: '/simulation-lab', label: 'Simulation Lab', icon: FlaskConical },
    { to: '/system-health', label: 'System Health', icon: HeartPulse },
    { to: '/onboarding', label: 'Guided Setup', icon: BookOpen },
  ];

  return (
    <aside className="w-64 bg-[#0A0E17] border-r border-gray-800 min-h-[calc(100vh-4rem)] p-4 flex flex-col justify-between">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[10px] font-semibold uppercase tracking-wider text-gray-500 font-mono">
          SOC NAVIGATION
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600/10 text-blue-400 border border-blue-500/30'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-gray-900/60'
                }`
              }
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>

      <div className="p-3 bg-gray-900/60 border border-gray-800 rounded-xl space-y-2 text-xs">
        <div className="flex items-center space-x-2 text-blue-400 font-semibold">
          <Sparkles className="h-4 w-4" />
          <span>College Evaluation Ready</span>
        </div>
        <p className="text-gray-400 text-[11px] leading-relaxed">
          Zero malware risk. Operates exclusively in designated lab workspace directory.
        </p>
      </div>
    </aside>
  );
};

export default Sidebar;
