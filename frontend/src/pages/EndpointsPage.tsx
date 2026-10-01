import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import ChatbotDrawer from '../components/ChatbotDrawer';
import { Monitor, Shield, ShieldAlert, Cpu, HardDrive, Lock, Unlock, RefreshCw, AlertTriangle, Plus, Trash2 } from 'lucide-react';
import api from '../services/api';
import { wsService } from '../services/websocket';

interface Endpoint {
  id: number;
  hostname: string;
  os: string;
  ip_address: string;
  agent_version: string;
  status: string;
  last_heartbeat: string;
  cpu_usage: number;
  memory_usage: number;
  current_risk: number;
  is_isolated: boolean;
  telemetry_status: string;
}

const EndpointsPage: React.FC = () => {
  const [endpoints, setEndpoints] = useState<Endpoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEndpoint, setSelectedEndpoint] = useState<Endpoint | null>(null);
  const [modalAction, setModalAction] = useState<'isolate' | 'release' | null>(null);
  const [processing, setProcessing] = useState(false);

  // New endpoint registration modal state
  const [showAddModal, setShowAddModal] = useState(false);
  const [newHostname, setNewHostname] = useState('');
  const [newOS, setNewOS] = useState('Windows 11 Pro');
  const [newIP, setNewIP] = useState('');
  const [newAgentVersion, setNewAgentVersion] = useState('1.0.0');

  const fetchEndpoints = async () => {
    try {
      const res = await api.get('/endpoints/');
      setEndpoints(res.data);
    } catch (err) {
      console.error('Failed to fetch endpoints:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEndpoints();
    wsService.connect();

    wsService.subscribe('ENDPOINT_UPDATED', () => fetchEndpoints());
    wsService.subscribe('ENDPOINT_DELETED', () => fetchEndpoints());
    wsService.subscribe('CONTAINMENT_TRIGGERED', () => fetchEndpoints());

    return () => {
      wsService.unsubscribe('ENDPOINT_UPDATED', () => {});
    };
  }, []);

  const handleIsolationToggle = async () => {
    if (!selectedEndpoint || !modalAction) return;
    setProcessing(true);

    try {
      await api.post(`/endpoints/${selectedEndpoint.id}/isolate`, {
        action: modalAction,
        reason: 'Manual SOC Analyst Command'
      });
      await fetchEndpoints();
      setSelectedEndpoint(null);
      setModalAction(null);
    } catch (err) {
      console.error('Failed to update isolation status:', err);
    } finally {
      setProcessing(false);
    }
  };

  const handleRegisterEndpoint = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newHostname.trim()) return;
    setProcessing(true);

    try {
      await api.post('/endpoints/register', {
        hostname: newHostname.trim(),
        os: newOS.trim() || 'Unknown OS',
        ip_address: newIP.trim() || '192.168.1.150',
        agent_version: newAgentVersion.trim() || '1.0.0'
      });
      await fetchEndpoints();
      setShowAddModal(false);
      setNewHostname('');
      setNewIP('');
    } catch (err) {
      console.error('Failed to register endpoint:', err);
      alert('Failed to register endpoint');
    } finally {
      setProcessing(false);
    }
  };

  const handleDeleteEndpoint = async (ep: Endpoint) => {
    if (!window.confirm(`Are you sure you want to decommission endpoint '${ep.hostname}'?`)) return;

    try {
      await api.delete(`/endpoints/${ep.id}`);
      await fetchEndpoints();
    } catch (err) {
      console.error('Failed to delete endpoint:', err);
      alert('Failed to delete endpoint');
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0E17] text-gray-100 flex flex-col">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 space-y-6 overflow-y-auto">
          {/* Header */}
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">Endpoint Fleet Management</h1>
              <p className="text-xs text-gray-400">Monitor host telemetry, health heartbeats, and network isolation controls</p>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowAddModal(true)}
                className="bg-blue-600 hover:bg-blue-500 text-white px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition shadow-lg"
              >
                <Plus className="h-3.5 w-3.5" />
                <span>Register Endpoint</span>
              </button>
              <button
                onClick={fetchEndpoints}
                className="bg-gray-900 hover:bg-gray-800 border border-gray-700 text-gray-300 px-3 py-1.5 rounded-lg text-xs flex items-center space-x-1.5 transition"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                <span>Refresh Fleet</span>
              </button>
            </div>
          </div>

          {/* Endpoints Table */}
          <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-5 space-y-4">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-gray-950 text-gray-400 font-mono text-[11px] uppercase border-b border-gray-800">
                  <tr>
                    <th className="p-3">Hostname</th>
                    <th className="p-3">OS / Agent Version</th>
                    <th className="p-3">IP Address</th>
                    <th className="p-3">Agent Status</th>
                    <th className="p-3">CPU / Memory Telemetry</th>
                    <th className="p-3">Current Risk Score</th>
                    <th className="p-3">Network Isolation</th>
                    <th className="p-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/60 text-gray-200">
                  {endpoints.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="p-6 text-center text-gray-500 italic">
                        No registered endpoints found. Click "Register Endpoint" or run `python endpoint_agent/agent.py`.
                      </td>
                    </tr>
                  ) : (
                    endpoints.map((ep) => (
                      <tr key={ep.id} className="hover:bg-gray-800/40 transition">
                        <td className="p-3 font-semibold text-white flex items-center space-x-2">
                          <Monitor className="h-4 w-4 text-blue-400" />
                          <span>{ep.hostname}</span>
                        </td>
                        <td className="p-3 text-gray-400">
                          <div>{ep.os || 'Unknown OS'}</div>
                          <span className="text-[10px] font-mono text-gray-500">{ep.agent_version ? `v${ep.agent_version}` : 'N/A'}</span>
                        </td>
                        <td className="p-3 font-mono text-gray-300">{ep.ip_address || 'N/A'}</td>
                        <td className="p-3">
                          <span
                            className={`px-2 py-0.5 rounded font-mono text-[10px] uppercase font-semibold ${
                              ep.status === 'online'
                                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                                : 'bg-gray-800 text-gray-400'
                            }`}
                          >
                            {ep.status}
                          </span>
                        </td>
                        <td className="p-3">
                          {ep.cpu_usage != null && ep.cpu_usage > 0 ? (
                            <div className="flex items-center space-x-3 text-[11px] font-mono text-gray-300">
                              <span>CPU: {ep.cpu_usage.toFixed(1)}%</span>
                              <span>RAM: {ep.memory_usage ? `${ep.memory_usage.toFixed(0)}MB` : 'N/A'}</span>
                            </div>
                          ) : (
                            <span className="text-gray-500 italic text-[11px] font-mono">Telemetry unavailable</span>
                          )}
                        </td>
                        <td className="p-3">
                          <div className="flex items-center space-x-2">
                            <div className="w-16 bg-gray-800 h-2 rounded-full overflow-hidden">
                              <div
                                className={`h-full ${
                                  ep.current_risk > 80
                                    ? 'bg-red-500'
                                    : ep.current_risk > 50
                                    ? 'bg-amber-500'
                                    : 'bg-emerald-500'
                                }`}
                                style={{ width: `${Math.min(100, ep.current_risk)}%` }}
                              ></div>
                            </div>
                            <span className="font-mono font-bold text-xs">{ep.current_risk != null ? `${ep.current_risk.toFixed(1)}%` : '0.0%'}</span>
                          </div>
                        </td>
                        <td className="p-3">
                          {ep.is_isolated ? (
                            <span className="text-red-400 font-semibold font-mono text-[11px] flex items-center gap-1">
                              <Lock className="h-3.5 w-3.5" /> ISOLATED
                            </span>
                          ) : (
                            <span className="text-emerald-400 font-semibold font-mono text-[11px] flex items-center gap-1">
                              <Unlock className="h-3.5 w-3.5" /> CONNECTED
                            </span>
                          )}
                        </td>
                        <td className="p-3 text-right">
                          <div className="flex items-center justify-end space-x-2">
                            {ep.is_isolated ? (
                              <button
                                onClick={() => {
                                  setSelectedEndpoint(ep);
                                  setModalAction('release');
                                }}
                                className="px-2.5 py-1 bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 rounded text-[11px] transition font-medium"
                              >
                                Release
                              </button>
                            ) : (
                              <button
                                onClick={() => {
                                  setSelectedEndpoint(ep);
                                  setModalAction('isolate');
                                }}
                                className="px-2.5 py-1 bg-red-950 hover:bg-red-900 text-red-300 border border-red-800 rounded text-[11px] transition font-medium"
                              >
                                Isolate
                              </button>
                            )}
                            <button
                              onClick={() => handleDeleteEndpoint(ep)}
                              title="Decommission Endpoint"
                              className="p-1 bg-gray-800 hover:bg-red-950 text-gray-400 hover:text-red-400 rounded transition"
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </main>
      </div>

      {/* Register Endpoint Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-gray-900 border border-gray-800 p-6 rounded-2xl max-w-md w-full space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Plus className="h-5 w-5 text-blue-400" />
                <span>Register New Endpoint</span>
              </h3>
              <button onClick={() => setShowAddModal(false)} className="text-gray-400 hover:text-white text-xs">✕</button>
            </div>

            <form onSubmit={handleRegisterEndpoint} className="space-y-3 text-xs">
              <div>
                <label className="block text-gray-400 mb-1">Hostname *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. WS-SOC-TEST01"
                  value={newHostname}
                  onChange={(e) => setNewHostname(e.target.value)}
                  className="w-full bg-gray-950 border border-gray-700 rounded-lg p-2 text-gray-200 font-mono"
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-1">Operating System</label>
                <input
                  type="text"
                  placeholder="e.g. Windows 11 Enterprise"
                  value={newOS}
                  onChange={(e) => setNewOS(e.target.value)}
                  className="w-full bg-gray-950 border border-gray-700 rounded-lg p-2 text-gray-200"
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-1">IP Address</label>
                <input
                  type="text"
                  placeholder="e.g. 192.168.1.145"
                  value={newIP}
                  onChange={(e) => setNewIP(e.target.value)}
                  className="w-full bg-gray-950 border border-gray-700 rounded-lg p-2 text-gray-200 font-mono"
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-1">Agent Version</label>
                <input
                  type="text"
                  placeholder="1.0.0"
                  value={newAgentVersion}
                  onChange={(e) => setNewAgentVersion(e.target.value)}
                  className="w-full bg-gray-950 border border-gray-700 rounded-lg p-2 text-gray-200 font-mono"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={processing}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-lg transition"
                >
                  {processing ? 'Registering...' : 'Register Endpoint'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Confirmation Modal */}
      {selectedEndpoint && modalAction && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-gray-900 border border-gray-800 p-6 rounded-2xl max-w-md w-full space-y-4 shadow-2xl">
            <div className="flex items-center space-x-3 text-amber-400">
              <AlertTriangle className="h-6 w-6 shrink-0" />
              <h3 className="text-base font-bold text-white">
                Confirm Host Isolation Action
              </h3>
            </div>
            <p className="text-xs text-gray-300 leading-relaxed">
              Are you sure you want to <strong className="text-white uppercase">{modalAction}</strong> endpoint{' '}
              <span className="font-mono text-blue-400">{selectedEndpoint.hostname}</span>?
              {modalAction === 'isolate' && ' This will block all outbound non-management network traffic.'}
            </p>
            <div className="flex justify-end space-x-3 pt-2">
              <button
                onClick={() => {
                  setSelectedEndpoint(null);
                  setModalAction(null);
                }}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg text-xs font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleIsolationToggle}
                disabled={processing}
                className={`px-4 py-2 text-white rounded-lg text-xs font-semibold shadow-lg transition ${
                  modalAction === 'isolate' ? 'bg-red-600 hover:bg-red-500' : 'bg-emerald-600 hover:bg-emerald-500'
                }`}
              >
                {processing ? 'Executing...' : `Confirm ${modalAction.toUpperCase()}`}
              </button>
            </div>
          </div>
        </div>
      )}

      <ChatbotDrawer pageContext="Endpoint Fleet Management" />
    </div>
  );
};

export default EndpointsPage;
