import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Cpu, Activity, Lock, CheckCircle2, ArrowRight, Zap, Play } from 'lucide-react';

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#0A0E17] text-gray-100 flex flex-col">
      {/* Header */}
      <header className="h-20 border-b border-gray-800 px-8 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Shield className="h-9 w-9 text-blue-500" />
          <span className="font-bold text-2xl tracking-wider">
            RANSOM<span className="text-blue-500">GUARD</span>
          </span>
        </div>
        <div className="flex items-center space-x-4">
          <Link to="/login" className="text-gray-300 hover:text-white font-medium text-sm px-4 py-2">
            Log In
          </Link>
          <Link
            to="/signup"
            className="bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm px-5 py-2.5 rounded-lg shadow-lg transition"
          >
            Get Started
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="flex-1 max-w-6xl mx-auto px-6 py-20 text-center flex flex-col items-center justify-center">
        <div className="inline-flex items-center space-x-2 bg-blue-950/80 border border-blue-800 text-blue-400 text-xs px-3.5 py-1.5 rounded-full mb-8 font-mono">
          <Zap className="h-3.5 w-3.5 text-blue-400" />
          <span>Behavioral AI/ML Ransomware Auto-Containment Platform</span>
        </div>

        <h1 className="text-5xl md:text-6xl font-extrabold text-white tracking-tight leading-tight max-w-4xl">
          Detect Ransomware Behavior in Real-Time with <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">LSTM Neural Networks</span>
        </h1>

        <p className="mt-6 text-lg text-gray-400 max-w-2xl leading-relaxed">
          RansomGuard monitors host filesystem telemetry, analyzes Shannon entropy spikes and sequence patterns with ONNX Runtime edge inference, and automatically contains critical threats in under 10 seconds.
        </p>

        <div className="mt-10 flex flex-wrap gap-4 justify-center">
          <Link
            to="/signup"
            className="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-8 py-3.5 rounded-xl shadow-xl flex items-center space-x-2 text-base transition"
          >
            <span>Launch SOC Platform</span>
            <ArrowRight className="h-5 w-5" />
          </Link>
          <Link
            to="/onboarding"
            className="bg-gray-900 hover:bg-gray-800 text-gray-200 font-semibold px-8 py-3.5 rounded-xl border border-gray-700 flex items-center space-x-2 text-base transition"
          >
            <Play className="h-5 w-5 text-emerald-400" />
            <span>Interactive Demo Workflow</span>
          </Link>
        </div>

        {/* Feature Grid */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 text-left w-full">
          <div className="bg-gray-900/60 border border-gray-800 p-6 rounded-2xl">
            <Cpu className="h-8 w-8 text-blue-400 mb-4" />
            <h3 className="text-lg font-bold text-white mb-2">Behavioral LSTM AI</h3>
            <p className="text-sm text-gray-400 leading-relaxed">
              Analyzes 10-event rolling sequences across 8 behavioral features: Shannon entropy change, modification frequency, extension alterations, and process signals.
            </p>
          </div>

          <div className="bg-gray-900/60 border border-gray-800 p-6 rounded-2xl">
            <Lock className="h-8 w-8 text-emerald-400 mb-4" />
            <h3 className="text-lg font-bold text-white mb-2">Automated Containment</h3>
            <p className="text-sm text-gray-400 leading-relaxed">
              Safely terminates malicious process execution, isolates network interfaces, and quarantines encrypted files with process whitelist verification.
            </p>
          </div>

          <div className="bg-gray-900/60 border border-gray-800 p-6 rounded-2xl">
            <Activity className="h-8 w-8 text-amber-400 mb-4" />
            <h3 className="text-lg font-bold text-white mb-2">Safe Simulation Lab</h3>
            <p className="text-sm text-gray-400 leading-relaxed">
              Demonstrate detection workflows safely in a controlled lab directory. Zero real malware required—ideal for university examination showcase.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-6 text-center text-xs text-gray-500 font-mono">
        RansomGuard Defensive Cybersecurity Platform &copy; 2026. Built for college evaluation.
      </footer>
    </div>
  );
};

export default LandingPage;
