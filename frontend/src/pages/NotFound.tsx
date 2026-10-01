import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, ArrowLeft } from 'lucide-react';

const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#0A0E17] text-gray-100 flex flex-col items-center justify-center p-6 text-center space-y-4">
      <ShieldAlert className="h-16 w-16 text-amber-400 animate-bounce" />
      <h1 className="text-4xl font-extrabold text-white">404 - Security Zone Unmapped</h1>
      <p className="text-xs text-gray-400 max-w-sm">The requested SOC dashboard route does not exist or requires higher RBAC authorization.</p>
      <Link
        to="/dashboard"
        className="bg-blue-600 hover:bg-blue-500 text-white font-medium px-5 py-2.5 rounded-lg text-xs flex items-center space-x-2 transition shadow-lg mt-2"
      >
        <ArrowLeft className="h-4 w-4" />
        <span>Return to SOC Command Center</span>
      </Link>
    </div>
  );
};

export default NotFound;
