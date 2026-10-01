import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import ChatbotDrawer from '../components/ChatbotDrawer';
import {
  ShieldAlert,
  CheckCircle,
  FileText,
  Activity,
  Cpu,
  ArrowLeft,
  Lock,
  MessageSquare,
  Save,
  Terminal
} from 'lucide-react';
import api from '../services/api';

interface Incident {
  id: number;
  endpoint_id: number;
  timestamp: string;
  threat_score: number;
  confidence: string;
  severity: string;
  suspected_process: string;
  affected_files: string[];
  behavior_timeline: Array<{ timestamp: string; event: string; severity: string }>;
  model_explanation: string;
  detection_signals: Array<{ signal?: string; value?: any; process?: string; file?: string }>;
  containment_status: string;
  response_actions: Array<{ action: string; status: string }>;
  analyst_notes: string;
  status: string;
}

const IncidentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [incident, setIncident] = useState<Incident | null>(null);
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const fetchIncident = async () => {
    try {
      const res = await api.get(`/incidents/${id}`);
      setIncident(res.data);
      setNotes(res.data.analyst_notes || '');
    } catch (err) {
      console.error('Failed to load incident details:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncident();
  }, [id]);

  const handleSaveNotes = async () => {
    if (!incident) return;
    setSaving(true);
    try {
      await api.patch(`/incidents/${incident.id}`, { analyst_notes: notes });
      await fetchIncident();
    } catch (err) {
      console.error('Failed to save analyst notes:', err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0E17] text-gray-100 flex items-center justify-center">
        <div className="text-blue-400 font-mono text-sm animate-pulse">Loading RansomGuard Incident Case File...</div>
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="min-h-screen bg-[#0A0E17] text-gray-100 p-8 text-center space-y-4">
        <h2 className="text-xl font-bold text-red-400">Incident Record Not Found</h2>
        <Link to="/dashboard" className="text-blue-400 underline text-sm">
          Return to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0A0E17] text-gray-100 flex flex-col">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 space-y-6 overflow-y-auto">
          {/* Top Back Link */}
          <div>
            <Link to="/dashboard" className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1">
              <ArrowLeft className="h-3.5 w-3.5" />
              <span>Back to Incident Dashboard</span>
            </Link>
          </div>

          {/* Incident Overview Card */}
          <div className="bg-gray-900/90 border border-gray-800 p-6 rounded-2xl space-y-4 shadow-xl">
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-gray-800 pb-4">
              <div>
                <div className="flex items-center space-x-3">
                  <span className="font-mono text-lg font-bold text-blue-400">
                    RANSOMWARE INCIDENT #INC-2026-{String(incident.id).padStart(4, '0')}
                  </span>
                  <span className="px-2.5 py-0.5 rounded text-xs font-mono font-bold uppercase bg-red-950 text-red-400 border border-red-800">
                    {incident.severity}
                  </span>
                </div>
                <p className="text-xs text-gray-400 mt-1">
                  Detected at: <span className="font-mono text-gray-300">{new Date(incident.timestamp).toLocaleString()}</span>
                </p>
              </div>

              <div className="flex items-center space-x-4 bg-gray-950 p-3 rounded-xl border border-gray-800">
                <div>
                  <div className="text-[10px] uppercase text-gray-500 font-mono">Threat Score</div>
                  <div className="text-2xl font-extrabold text-red-400 font-mono">{incident.threat_score.toFixed(1)}%</div>
                </div>
                <div className="border-l border-gray-800 pl-4">
                  <div className="text-[10px] uppercase text-gray-500 font-mono">Confidence</div>
                  <div className="text-sm font-bold text-gray-200 uppercase">{incident.confidence || 'HIGH'}</div>
                </div>
              </div>
            </div>

            {/* AI Reasoning Summary */}
            <div className="bg-blue-950/40 border border-blue-900/60 p-4 rounded-xl space-y-2">
              <div className="flex items-center space-x-2 text-blue-400 font-bold text-xs">
                <Cpu className="h-4 w-4" />
                <span>AI Model Behavioral Explanation</span>
              </div>
              <p className="text-xs text-gray-300 leading-relaxed font-mono">
                {incident.model_explanation ||
                  'The LSTM model observed a sequence of file-system events whose combined behavioral pattern resembles ransomware activity.'}
              </p>
            </div>
          </div>

          {/* Grid Layout: Detection Signals + Affected Files */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Detection Signals */}
            <div className="bg-gray-900/80 border border-gray-800 p-5 rounded-2xl space-y-3">
              <h3 className="font-bold text-sm text-white flex items-center space-x-2">
                <Activity className="h-4 w-4 text-amber-400" />
                <span>Extracted Attack Signals</span>
              </h3>

              <div className="space-y-2 text-xs">
                <div className="p-3 bg-gray-950 border border-gray-800 rounded-lg flex items-center justify-between">
                  <span className="text-gray-400">Suspected Process:</span>
                  <span className="font-mono text-amber-300 font-bold">{incident.suspected_process || 'Unknown'}</span>
                </div>

                {incident.detection_signals && incident.detection_signals.length > 0 ? (
                  incident.detection_signals.map((sig, i) => (
                    <div key={i} className="p-2.5 bg-gray-950 border border-gray-800 rounded-lg text-gray-300 flex items-center space-x-2 font-mono">
                      <span className="text-red-400 font-bold">✓</span>
                      <span>{sig.signal || sig.file || sig.process || JSON.stringify(sig)}</span>
                    </div>
                  ))
                ) : (
                  <div className="p-2.5 bg-gray-950 border border-gray-800 rounded-lg text-gray-500 italic">
                    No additional attack signals recorded for this incident.
                  </div>
                )}
              </div>
            </div>

            {/* Affected Files */}
            <div className="bg-gray-900/80 border border-gray-800 p-5 rounded-2xl space-y-3">
              <h3 className="font-bold text-sm text-white flex items-center space-x-2">
                <FileText className="h-4 w-4 text-blue-400" />
                <span>Affected Target Files</span>
              </h3>

              <div className="bg-gray-950 border border-gray-800 rounded-xl p-3 h-48 overflow-y-auto space-y-1.5 font-mono text-xs text-gray-300">
                {incident.affected_files && incident.affected_files.length > 0 ? (
                  incident.affected_files.map((file, idx) => (
                    <div key={idx} className="truncate text-red-300 hover:text-red-200">
                      {file}
                    </div>
                  ))
                ) : (
                  <div className="text-gray-500 italic">Target lab files encrypted in workspace directory</div>
                )}
              </div>
            </div>
          </div>

          {/* Analyst Case Notes & Audit History */}
          <div className="bg-gray-900/80 border border-gray-800 p-5 rounded-2xl space-y-3">
            <h3 className="font-bold text-sm text-white flex items-center space-x-2">
              <MessageSquare className="h-4 w-4 text-emerald-400" />
              <span>SOC Analyst Case Investigation Notes</span>
            </h3>

            <textarea
              rows={4}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Record investigation findings, root cause analysis, and containment justification..."
              className="w-full bg-gray-950 border border-gray-700 rounded-xl p-3 text-xs text-gray-200 focus:outline-none focus:border-blue-500 font-mono"
            />

            <div className="flex justify-end">
              <button
                onClick={handleSaveNotes}
                disabled={saving}
                className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-1.5 shadow-lg transition disabled:opacity-50"
              >
                <Save className="h-3.5 w-3.5" />
                <span>{saving ? 'Saving Notes...' : 'Save Case File Notes'}</span>
              </button>
            </div>
          </div>
        </main>
      </div>

      <ChatbotDrawer pageContext={`Incident Investigation Case #INC-${incident.id}`} />
    </div>
  );
};

export default IncidentDetailPage;
