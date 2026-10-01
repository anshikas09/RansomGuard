import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Shield, LogOut, User as UserIcon, Activity } from 'lucide-react';
import { Link } from 'react-router-dom';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="h-16 border-b border-gray-800 bg-[#0A0E17] px-6 flex items-center justify-between sticky top-0 z-40">
      <div className="flex items-center space-x-3">
        <Link to="/dashboard" className="flex items-center space-x-2 text-blue-500 hover:text-blue-400">
          <Shield className="h-8 w-8 text-blue-500 animate-pulse" />
          <span className="font-bold text-xl tracking-wider text-white">
            RANSOM<span className="text-blue-500">GUARD</span>
          </span>
        </Link>
        <span className="px-2 py-0.5 text-xs font-mono bg-blue-950 text-blue-400 border border-blue-800 rounded-full">
          SOC EDR v1.0
        </span>
      </div>

      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-2 bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5 text-xs">
          <Activity className="h-4 w-4 text-emerald-400" />
          <span className="text-gray-400">System Status:</span>
          <span className="text-emerald-400 font-semibold">PROTECTED</span>
        </div>

        {user && (
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 border-r border-gray-800 pr-4">
              <div className="w-8 h-8 rounded-full bg-blue-900 border border-blue-700 flex items-center justify-center text-blue-200 font-semibold text-sm">
                {user.full_name.charAt(0)}
              </div>
              <div className="text-left hidden md:block">
                <p className="text-xs font-medium text-gray-200">{user.full_name}</p>
                <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 bg-gray-800 text-gray-400 rounded font-mono">
                  {user.role}
                </span>
              </div>
            </div>

            <button
              onClick={logout}
              className="text-gray-400 hover:text-red-400 transition-colors p-1.5 rounded-lg hover:bg-gray-900"
              title="Logout"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
