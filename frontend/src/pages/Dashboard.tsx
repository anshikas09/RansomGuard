import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import ChatbotDrawer from '../components/ChatbotDrawer';
import {
  ShieldAlert,
  Monitor,
  CheckCircle,
  AlertTriangle,
  Zap,
  Activity,
  ArrowUpRight,
  RefreshCw,
  Sliders,
  Trash2
} from 'lucide-react';
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';
import api from '../services/api';
import { wsService } from '../services/websocket';
import { Link } from 'react-router-dom';

interface Incident {
  id: number;
  endpoint_id: number;
  timestamp: string;
  threat_score: number;
  severity: string;
  suspected_process: string;
  status: string;
  containment_status: string;
}

interface Endpoint {
  id: number;
  hostname: string;
  status: string;
  current_risk: number;
  is_isolated?: boolean;
}

interface TelemetryEvent {
  id: number;
  endpoint_id: number;
  timestamp: string;
  process_name: string;
  risk_score: number;
  ransomware_probability: number;
  entropy: number;
  severity: string;
}

const Dashboard: React.FC = () => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [endpoints, setEndpoints] = useState<Endpoint[]>([]);
  const [telemetryEvents, setTelemetryEvents] = useState<TelemetryEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(true);
  const [resetting, setResetting] = useState(false);

  const fetchData = async () => {
    try {
      const [incRes, epRes, telemRes] = await Promise.all([
        api.get('/incidents/'),
        api.get('/endpoints/'),
        api.get('/telemetry/recent?limit=30')
      ]);
      setIncidents(incRes.data);
      setEndpoints(epRes.data);
      setTelemetryEvents(telemRes.data);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

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
      await fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to reset demo data.');
    } finally {
      setResetting(false);
    }
  };

  useEffect(() => {
    fetchData();
    wsService.connect();

    wsService.subscribe('TELEMETRY_BATCH_INGESTED', () => fetchData());
    wsService.subscribe('INCIDENT_UPDATED', () => fetchData());
    wsService.subscribe('SIMULATION_PROGRESS', () => fetchData());
    wsService.subscribe('DEMO_DATA_RESET', () => fetchData());

    return () => {
      wsService.unsubscribe('TELEMETRY_BATCH_INGESTED', () => {});
      wsService.unsubscribe('DEMO_DATA_RESET', () => {});
    };
  }, []);

  const totalEndpoints = endpoints.length;
  const isolatedEndpoints = endpoints.filter((e) => e.is_isolated).length;
  const onlineUnrestricted = endpoints.filter((e) => e.status === 'online' && !e.is_isolated).length;

  const totalHistoricalIncidents = incidents.length;
  const historicalCritical = incidents.filter((i) => i.severity === 'CRITICAL').length;

  // Active incidents are strictly uncontained, unresolved, and non-false-positive
  const activeOpenThreats = incidents.filter(
    (i) => i.status === 'new' || i.status === 'investigating' || i.status === 'active'
  ).length;

  const activeCriticalThreats = incidents.filter(
    (i) =>
      (i.status === 'new' || i.status === 'investigating' || i.status === 'active') &&
      i.severity === 'CRITICAL'
  ).length;

  // Contained incidents are those that have been mitigated/isolated
  const containedIncidents = incidents.filter(
    (i) => i.containment_status === 'completed' || i.status === 'contained'
  ).length;

  // Temporal sequence from real chronological telemetry events
  const timelineData = telemetryEvents.length > 0
    ? [...telemetryEvents]
        .reverse()
        .map((ev) => ({
          time: new Date(ev.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          risk: Number((ev.risk_score || 0).toFixed(1)),
          ml_prob: Number(((ev.ransomware_probability || 0) * 100).toFixed(1)),
          process: ev.process_name || 'System',
          threshold: 80.0
        }))
    : [];

  const severityPieData = [
    { name: 'Critical', value: incidents.filter((i) => i.severity === 'CRITICAL').length, color: '#EF4444' },
    { name: 'High', value: incidents.filter((i) => i.severity === 'HIGH').length, color: '#F59E0B' },
    { name: 'Medium', value: incidents.filter((i) => i.severity === 'MEDIUM').length, color: '#3B82F6' },
    { name: 'Low', value: incidents.filter((i) => i.severity === 'LOW').length, color: '#10B981' }
  ];

  return (
    <div className="min-h-screen bg-[#0A0E17] text-gray-100 flex flex-col">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 space-y-6 overflow-y-auto">
          {/* Header Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                <span>SOC Command Center</span>
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></span>
              </h1>
              <p className="text-xs text-gray-400">Real-Time Behavioral AI Ransomware Telemetry & Threat Monitor</p>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={fetchData}
                className="bg-gray-900 hover:bg-gray-800 border border-gray-700 text-gray-300 px-3 py-1.5 rounded-lg text-xs flex items-center space-x-1.5 transition"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                <span>Refresh Data</span>
              </button>
              <button
                onClick={handleResetDemoData}
                disabled={resetting}
                className="bg-red-950/60 hover:bg-red-900/80 border border-red-800 text-red-300 px-3 py-1.5 rounded-lg text-xs flex items-center space-x-1.5 transition"
                title="Clears test incidents, telemetry events, and containment actions while preserving endpoints and users."
              >
                <Trash2 className="h-3.5 w-3.5" />
                <span>{resetting ? 'Resetting...' : 'Reset Local Demo Data'}</span>
              </button>
              <Link
                to="/simulation-lab"
                className="bg-blue-600 hover:bg-blue-500 text-white font-medium px-4 py-1.5 rounded-lg text-xs flex items-center space-x-1.5 transition shadow-lg"
              >
                <Zap className="h-3.5 w-3.5" />
                <span>Launch Simulation</span>
              </Link>
            </div>
          </div>

          {/* Metric Stat Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gray-900/80 border border-gray-800 p-5 rounded-2xl space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400 font-semibold uppercase">Protected Endpoints</span>
                <Monitor className="h-5 w-5 text-blue-400" />
              </div>
              <div className="flex items-baseline space-x-2">
                <span className="text-3xl font-extrabold text-white">{totalEndpoints}</span>
                <span className="text-xs text-emerald-400 font-medium">({onlineUnrestricted} Online · {isolatedEndpoints} Isolated)</span>
              </div>
              <p className="text-[11px] text-gray-500">Real-time agent health from database</p>
            </div>

            <div className="bg-gray-900/80 border border-gray-800 p-5 rounded-2xl space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400 font-semibold uppercase">Active Incidents</span>
                <AlertTriangle className="h-5 w-5 text-amber-400" />
              </div>
              <div className="flex items-baseline space-x-2">
                <span className="text-3xl font-extrabold text-amber-400">{activeOpenThreats}</span>
                <span className="text-xs text-amber-300 font-medium">{activeCriticalThreats} Critical Active</span>
              </div>
              <p className="text-[11px] text-gray-500">Requires SOC Analyst Investigation</p>
            </div>

            <div className="bg-gray-900/80 border border-gray-800 p-5 rounded-2xl space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400 font-semibold uppercase">Contained Incidents</span>
                <CheckCircle className="h-5 w-5 text-emerald-400" />
              </div>
              <div className="flex items-baseline space-x-2">
                <span className="text-3xl font-extrabold text-emerald-400">{containedIncidents}</span>
                <span className="text-xs text-emerald-300 font-medium">Auto-Mitigated</span>
              </div>
              <p className="text-[11px] text-gray-500">Threats Isolated & Neutralized</p>
            </div>

            <div className="bg-gray-900/80 border border-gray-800 p-5 rounded-2xl space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400 font-semibold uppercase">Total Historical Incidents</span>
                <ShieldAlert className="h-5 w-5 text-red-400" />
              </div>
              <div className="flex items-baseline space-x-2">
                <span className="text-3xl font-extrabold text-white">{totalHistoricalIncidents}</span>
                <span className="text-xs text-red-400 font-medium">{historicalCritical} Critical Logged</span>
              </div>
              <p className="text-[11px] text-gray-500">All incidents logged in database</p>
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Line Chart: Threat Scores */}
            <div className="lg:col-span-2 bg-gray-900/80 border border-gray-800 p-5 rounded-2xl space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-sm text-white">Telemetry Threat Sequence & Risk Score Trend</h3>
                  <p className="text-xs text-gray-400">Chronological Telemetry Event Risk Score (%) vs. 80% Alert Threshold</p>
                </div>
                <span className="text-xs font-mono bg-blue-950 text-blue-400 border border-blue-800 px-2 py-0.5 rounded">
                  Live Telemetry Feed (Recent {timelineData.length})
                </span>
              </div>

              <div className="h-64">
                {timelineData.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-gray-500 text-xs italic">
                    <Activity className="h-8 w-8 text-gray-600 mb-2" />
                    <span>No telemetry threat sequence data available yet.</span>
                    <span className="text-[10px] text-gray-600 mt-1">Start a simulation in Simulation Lab to generate live telemetry.</span>
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={timelineData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                      <XAxis dataKey="time" stroke="#6B7280" fontSize={11} />
                      <YAxis domain={[0, 100]} stroke="#6B7280" fontSize={11} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '8px', fontSize: '12px' }}
                      />
                      <Line type="monotone" dataKey="risk" stroke="#EF4444" strokeWidth={2.5} dot={{ r: 3 }} name="Risk Score (%)" />
                      <Line type="monotone" dataKey="ml_prob" stroke="#3B82F6" strokeWidth={1.5} dot={{ r: 2 }} name="ML Probability (%)" />
                      <Line type="monotone" dataKey="threshold" stroke="#F59E0B" strokeDasharray="5 5" strokeWidth={1.5} name="Alert Threshold (80%)" />
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            {/* Pie Chart: Severity Distribution */}
            <div className="bg-gray-900/80 border border-gray-800 p-5 rounded-2xl space-y-4">
              <div>
                <h3 className="font-bold text-sm text-white">Historical Severity Breakdown</h3>
                <p className="text-xs text-gray-400">Distribution across all {totalHistoricalIncidents} logged incidents</p>
              </div>

              <div className="h-48 flex items-center justify-center">
                {totalHistoricalIncidents === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-gray-500 text-xs italic">
                    <Activity className="h-8 w-8 text-gray-600 mb-2" />
                    <span>No historical incidents recorded.</span>
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={severityPieData} cx="50%" cy="50%" innerRadius={50} outerRadius={70} paddingAngle={4} dataKey="value">
                        {severityPieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '8px', fontSize: '12px' }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs pt-2 border-t border-gray-800">
                {severityPieData.map((item, i) => (
                  <div key={i} className="flex items-center space-x-2">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }}></span>
                    <span className="text-gray-300 font-medium">{item.name}:</span>
                    <span className="text-gray-400">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recent Incident Feed Table */}
          <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-sm text-white">Detected Incidents & Threat Feed</h3>
                <p className="text-xs text-gray-400">Live SOC incident queue with automated containment triggers</p>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-gray-950 text-gray-400 font-mono text-[11px] uppercase border-b border-gray-800">
                  <tr>
                    <th className="p-3">Incident ID</th>
                    <th className="p-3">Timestamp</th>
                    <th className="p-3">Process</th>
                    <th className="p-3">Threat Score</th>
                    <th className="p-3">Severity</th>
                    <th className="p-3">Containment</th>
                    <th className="p-3">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/60 text-gray-200">
                  {incidents.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="p-6 text-center text-gray-500 italic">
                        No ransomware incidents detected yet. Start a safe simulation in the Simulation Lab!
                      </td>
                    </tr>
                  ) : (
                    incidents.slice(0, 5).map((inc) => (
                      <tr key={inc.id} className="hover:bg-gray-800/40 transition">
                        <td className="p-3 font-mono font-semibold text-blue-400">#INC-2026-{String(inc.id).padStart(4, '0')}</td>
                        <td className="p-3 text-gray-400 font-mono">{new Date(inc.timestamp).toLocaleString()}</td>
                        <td className="p-3 font-mono font-medium text-amber-300">{inc.suspected_process || 'Unknown'}</td>
                        <td className="p-3 font-bold text-white">{inc.threat_score.toFixed(1)}%</td>
                        <td className="p-3">
                          <span
                            className={`px-2 py-0.5 rounded font-semibold text-[10px] uppercase font-mono ${
                              inc.severity === 'CRITICAL'
                                ? 'bg-red-950 text-red-400 border border-red-800'
                                : inc.severity === 'HIGH'
                                ? 'bg-amber-950 text-amber-400 border border-amber-800'
                                : 'bg-blue-950 text-blue-400 border border-blue-800'
                            }`}
                          >
                            {inc.severity}
                          </span>
                        </td>
                        <td className="p-3 text-gray-300">
                          {inc.containment_status === 'completed' ? (
                            <span className="text-emerald-400 flex items-center gap-1 font-mono text-[11px]">
                              <CheckCircle className="h-3.5 w-3.5" /> CONTAINED
                            </span>
                          ) : (
                            <span className="text-amber-400 font-mono text-[11px]">MONITORING</span>
                          )}
                        </td>
                        <td className="p-3">
                          <Link
                            to={`/incidents/${inc.id}`}
                            className="text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-1"
                          >
                            <span>Investigate</span>
                            <ArrowUpRight className="h-3.5 w-3.5" />
                          </Link>
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

      <ChatbotDrawer pageContext="SOC Dashboard Overview" />
    </div>
  );
};

export default Dashboard;
