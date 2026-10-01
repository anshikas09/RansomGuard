import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import ChatbotDrawer from '../components/ChatbotDrawer';
import { FlaskConical, Play, Square, AlertOctagon, CheckCircle2, ShieldAlert, Activity, RefreshCw, Trash2 } from 'lucide-react';
import api from '../services/api';
import { wsService } from '../services/websocket';

interface SimulationState {
  is_running: boolean;
  simulation_id?: string;
  simulation_type: string;
  target_hostname?: string;
  files_touched: number;
  files_modified: number;
  current_rate: number;
  entropy_change: number;
  ml_probability: number;
  behavioral_score: number;
  threat_score: number;
  detection_status: string;
  containment_status: string;
}

const SimulationLab: React.FC = () => {
  const [simType, setSimType] = useState('combined');
  const [fileCount, setFileCount] = useState(30);
  const [modRate, setModRate] = useState(10);
  const [intensity, setIntensity] = useState('medium');
  const [endpoints, setEndpoints] = useState<any[]>([]);
  const [selectedHost, setSelectedHost] = useState('');
  const [state, setState] = useState<SimulationState>({
    is_running: false,
    simulation_type: 'combined',
    files_touched: 0,
    files_modified: 0,
    current_rate: 0,
    entropy_change: 0,
    ml_probability: 0,
    behavioral_score: 0,
    threat_score: 0,
    detection_status: 'NORMAL',
    containment_status: 'MONITORING'
  });

  const fetchStatus = async () => {
    try {
      const [res, epRes] = await Promise.all([
        api.get('/simulation/status'),
        api.get('/endpoints/')
      ]);
      setState(res.data);
      setEndpoints(epRes.data);
      if (epRes.data.length > 0 && !selectedHost) {
        setSelectedHost(epRes.data[0].hostname);
      }
    } catch (e) {
      console.error('Failed to load simulation status/endpoints:', e);
    }
  };

  useEffect(() => {
    fetchStatus();
    wsService.connect();

    wsService.subscribe('SIMULATION_PROGRESS', (data: SimulationState) => {
      setState(data);
    });
    wsService.subscribe('SIMULATION_COMPLETED', (data: SimulationState) => {
      setState(data);
    });

    return () => {
      wsService.unsubscribe('SIMULATION_PROGRESS', () => {});
    };
  }, []);

  const handleStart = async () => {
    try {
      const res = await api.post('/simulation/start', {
        simulation_type: simType,
        number_of_files: fileCount,
        modification_rate: modRate,
        extension_changes: simType === 'combined' || simType === 'extension_change',
        intensity: intensity,
        duration_seconds: 30,
        target_hostname: selectedHost || undefined
      });
      setState(res.data);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to start simulation lab');
    }
  };

  const handleStop = async () => {
    try {
      const res = await api.post('/simulation/stop');
      setState(res.data);
    } catch (err) {
      console.error('Failed to stop simulation:', err);
    }
  };

  const [resetting, setResetting] = useState(false);

  const handleResetDemoData = async () => {
    const confirmed = window.confirm(
      'Are you sure you want to reset local demo data?\n\n' +
      'This will safely clear simulation telemetry, test incidents, and containment actions.\n' +
      'Registered endpoints, models, and users will NOT be deleted.'
    );
    if (!confirmed) return;

    setResetting(true);
    try {
      const res = await api.post('/demo/reset');
      alert(`Demo reset complete!\nCleared: ${res.data.cleared.incidents} incidents, ${res.data.cleared.telemetry_events} telemetry events.`);
      await fetchStatus();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to reset demo data.');
    } finally {
      setResetting(false);
    }
  };

  const getStatusBadgeColor = (status: string) => {
    if (status.includes('RANSOMWARE')) return 'bg-red-950 text-red-400 border-red-800 animate-pulse';
    if (status.includes('HIGH RISK')) return 'bg-amber-950 text-amber-400 border-amber-800';
    if (status.includes('SUSPICIOUS')) return 'bg-blue-950 text-blue-400 border-blue-800';
    return 'bg-emerald-950 text-emerald-400 border-emerald-800';
  };

  return (
    <div className="min-h-screen bg-[#0A0E17] text-gray-100 flex flex-col">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 space-y-6 overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                <FlaskConical className="h-6 w-6 text-blue-400" />
                <span>Safe Ransomware Simulation Lab</span>
              </h1>
              <p className="text-xs text-gray-400">
                Generate synthetic ransomware behavioral patterns safely in <code className="text-blue-400">./scratch/ransim_lab</code>
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={handleResetDemoData}
                disabled={resetting}
                className="bg-red-950/60 hover:bg-red-900/80 border border-red-800 text-red-300 px-3 py-1.5 rounded-lg text-xs flex items-center space-x-1.5 transition"
                title="Clears test incidents, telemetry events, and containment actions while preserving endpoints and users."
              >
                <Trash2 className="h-3.5 w-3.5" />
                <span>{resetting ? 'Resetting...' : 'Reset Local Demo Data'}</span>
              </button>
              <div className="px-3 py-1 bg-emerald-950 border border-emerald-800 text-emerald-400 text-xs rounded-full font-mono">
                SAFE LAB ENVIRONMENT
              </div>
            </div>
          </div>

          {/* Visual State Flow Progression */}
          <div className="bg-gray-900/80 border border-gray-800 p-5 rounded-2xl space-y-3">
            <h3 className="text-xs font-semibold text-gray-400 uppercase font-mono">Visual Detection & Containment State Flow</h3>
            <div className="grid grid-cols-5 gap-2 text-center text-xs font-mono">
              <div className={`p-3 rounded-xl border ${state.threat_score < 30 ? 'bg-emerald-950/80 text-emerald-300 border-emerald-700' : 'bg-gray-950 text-gray-600 border-gray-800'}`}>
                1. NORMAL
              </div>
              <div className={`p-3 rounded-xl border ${state.threat_score >= 30 && state.threat_score < 60 ? 'bg-blue-950/80 text-blue-300 border-blue-700' : 'bg-gray-950 text-gray-600 border-gray-800'}`}>
                2. SUSPICIOUS
              </div>
              <div className={`p-3 rounded-xl border ${state.threat_score >= 60 && state.threat_score < 80 ? 'bg-amber-950/80 text-amber-300 border-amber-700' : 'bg-gray-950 text-gray-600 border-gray-800'}`}>
                3. HIGH RISK
              </div>
              <div className={`p-3 rounded-xl border ${state.threat_score >= 80 ? 'bg-red-950/80 text-red-300 border-red-700 animate-pulse' : 'bg-gray-950 text-gray-600 border-gray-800'}`}>
                4. RANSOMWARE DETECTED
              </div>
              <div className={`p-3 rounded-xl border ${state.containment_status.includes('CONTAINED') ? 'bg-purple-950/80 text-purple-300 border-purple-700' : 'bg-gray-950 text-gray-600 border-gray-800'}`}>
                5. CONTAINED
              </div>
            </div>
          </div>

          {/* Real-time State & Controls Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Lab Configuration Form */}
            <div className="bg-gray-900/80 border border-gray-800 p-6 rounded-2xl space-y-4">
              <h3 className="font-bold text-sm text-white">Lab Parameters</h3>

              <div className="space-y-3 text-xs">
                <div>
                  <label className="block text-gray-400 mb-1">Target Endpoint Host</label>
                  <select
                    value={selectedHost}
                    onChange={(e) => setSelectedHost(e.target.value)}
                    disabled={state.is_running}
                    className="w-full bg-gray-950 border border-gray-700 rounded-lg p-2 text-gray-200 font-mono"
                  >
                    {endpoints.length === 0 ? (
                      <option value="">demo-soc-endpoint-vm01 (Default)</option>
                    ) : (
                      endpoints.map((ep) => (
                        <option key={ep.id} value={ep.hostname}>
                          {ep.hostname} ({ep.status}) {ep.is_isolated ? '[ISOLATED]' : ''}
                        </option>
                      ))
                    )}
                  </select>
                </div>

                <div>
                  <label className="block text-gray-400 mb-1">Simulation Pattern</label>
                  <select
                    value={simType}
                    onChange={(e) => setSimType(e.target.value)}
                    disabled={state.is_running}
                    className="w-full bg-gray-950 border border-gray-700 rounded-lg p-2 text-gray-200"
                  >
                    <option value="combined">Combined (Entropy + Rapid Mod + Ext Change)</option>
                    <option value="rapid_modification">Rapid File Modification Burst</option>
                    <option value="entropy_increase">High Shannon Entropy Spike</option>
                    <option value="extension_change">Extension Rename (.docx -&gt; .encrypted)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-gray-400 mb-1">Target File Count ({fileCount})</label>
                  <input
                    type="range"
                    min="10"
                    max="100"
                    value={fileCount}
                    onChange={(e) => setFileCount(Number(e.target.value))}
                    disabled={state.is_running}
                    className="w-full accent-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-gray-400 mb-1">Modification Rate ({modRate} files/sec)</label>
                  <input
                    type="range"
                    min="1"
                    max="30"
                    value={modRate}
                    onChange={(e) => setModRate(Number(e.target.value))}
                    disabled={state.is_running}
                    className="w-full accent-blue-500"
                  />
                </div>
              </div>

              <div className="pt-2 flex space-x-3">
                {state.is_running ? (
                  <button
                    onClick={handleStop}
                    className="flex-1 bg-red-600 hover:bg-red-500 text-white font-semibold py-2.5 rounded-lg text-xs flex items-center justify-center space-x-2 transition shadow-lg"
                  >
                    <Square className="h-4 w-4" />
                    <span>Stop Lab Simulation</span>
                  </button>
                ) : (
                  <button
                    onClick={handleStart}
                    className="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-semibold py-2.5 rounded-lg text-xs flex items-center justify-center space-x-2 transition shadow-lg"
                  >
                    <Play className="h-4 w-4" />
                    <span>Start Safe Simulation</span>
                  </button>
                )}
              </div>
            </div>

            {/* Real-time Display */}
            <div className="lg:col-span-2 bg-gray-900/80 border border-gray-800 p-6 rounded-2xl space-y-5">
              <div className="flex items-center justify-between border-b border-gray-800 pb-3">
                <div>
                  <h3 className="font-bold text-sm text-white">Live Telemetry & Threat Monitor</h3>
                  <p className="text-xs text-gray-400">Observer watching workspace directory `./scratch/ransim_lab`</p>
                </div>
                <span className={`px-3 py-1 rounded border text-xs font-mono font-bold ${getStatusBadgeColor(state.detection_status)}`}>
                  {state.detection_status}
                </span>
              </div>

              {/* Risk Engine Breakdown Gauges */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="bg-gray-950 p-3.5 rounded-xl border border-gray-800 space-y-1.5">
                  <div className="flex items-center justify-between text-[11px] font-mono">
                    <span className="text-gray-400">ML Model Probability:</span>
                    <span className="font-bold text-blue-400 font-mono">{(state.ml_probability || 0).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-900 h-2 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 transition-all duration-300" style={{ width: `${Math.min(100, state.ml_probability || 0)}%` }}></div>
                  </div>
                  <span className="text-[10px] text-gray-500 font-mono block">ONNX 2-Layer LSTM</span>
                </div>

                <div className="bg-gray-950 p-3.5 rounded-xl border border-gray-800 space-y-1.5">
                  <div className="flex items-center justify-between text-[11px] font-mono">
                    <span className="text-gray-400">Behavioral Score:</span>
                    <span className="font-bold text-amber-400 font-mono">{(state.behavioral_score || 0).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-900 h-2 rounded-full overflow-hidden">
                    <div className="h-full bg-amber-500 transition-all duration-300" style={{ width: `${Math.min(100, state.behavioral_score || 0)}%` }}></div>
                  </div>
                  <span className="text-[10px] text-gray-500 font-mono block">Heuristics (Rate/Entropy/Ext)</span>
                </div>

                <div className="bg-gray-950 p-3.5 rounded-xl border border-gray-800 space-y-1.5">
                  <div className="flex items-center justify-between text-[11px] font-mono">
                    <span className="text-gray-400">Final Risk Score:</span>
                    <span className={`font-bold font-mono ${state.threat_score >= 80 ? 'text-red-400' : state.threat_score >= 50 ? 'text-amber-400' : 'text-emerald-400'}`}>
                      {state.threat_score.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-900 h-2 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 ${
                        state.threat_score >= 80 ? 'bg-red-500' : state.threat_score >= 50 ? 'bg-amber-500' : 'bg-emerald-500'
                      }`}
                      style={{ width: `${Math.min(100, state.threat_score)}%` }}
                    ></div>
                  </div>
                  <span className="text-[10px] text-gray-500 font-mono block">Weighted Composite Score</span>
                </div>
              </div>

              {/* Real-Time Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
                <div className="bg-gray-950 border border-gray-800 p-3 rounded-xl">
                  <span className="text-gray-500 block">Files Touched</span>
                  <span className="text-lg font-bold text-white">{state.files_touched}</span>
                </div>
                <div className="bg-gray-950 border border-gray-800 p-3 rounded-xl">
                  <span className="text-gray-500 block">Files Modified</span>
                  <span className="text-lg font-bold text-amber-400">{state.files_modified}</span>
                </div>
                <div className="bg-gray-950 border border-gray-800 p-3 rounded-xl">
                  <span className="text-gray-500 block">Current Rate</span>
                  <span className="text-lg font-bold text-blue-400">{state.current_rate} ops/s</span>
                </div>
                <div className="bg-gray-950 border border-gray-800 p-3 rounded-xl">
                  <span className="text-gray-500 block">Entropy Spike</span>
                  <span className="text-lg font-bold text-purple-400">+{state.entropy_change}</span>
                </div>
              </div>

              {/* Containment Action Indicator */}
              <div className="p-3.5 bg-gray-950 border border-gray-800 rounded-xl text-xs space-y-1">
                <span className="text-gray-500 font-mono uppercase text-[10px]">Automated Containment State:</span>
                <p className="font-mono text-emerald-400 font-semibold">{state.containment_status}</p>
              </div>
            </div>
          </div>
        </main>
      </div>

      <ChatbotDrawer pageContext="Safe Ransomware Simulation Lab" />
    </div>
  );
};

export default SimulationLab;
