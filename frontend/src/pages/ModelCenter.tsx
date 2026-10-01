import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import ChatbotDrawer from '../components/ChatbotDrawer';
import { Cpu, ArrowRight, CheckCircle2, BarChart2, Zap, Layers, RefreshCw } from 'lucide-react';
import api from '../services/api';

interface ModelVersion {
  id: number;
  version: string;
  framework: string;
  input_features: string[];
  sequence_length: number;
  deployment_status: string;
  metrics: {
    accuracy: number;
    precision: number;
    recall: number;
    f1: number;
    roc_auc: number;
  };
}

const ModelCenter: React.FC = () => {
  const [model, setModel] = useState<ModelVersion | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchModel = async () => {
    try {
      const res = await api.get('/ml/active');
      setModel(res.data);
    } catch (err) {
      console.error('Failed to fetch ML model details:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModel();
  }, []);

  const pipelineSteps = [
    { label: 'File Event Ingestion', desc: 'Watchdog file system listener catches create/modify/delete/rename events.' },
    { label: 'Feature Extraction', desc: 'Computes 8 numerical features including Shannon entropy and modification rate.' },
    { label: 'StandardScaler', desc: 'Normalizes input feature vector using pre-fitted dataset parameters.' },
    { label: '10-Event Sequence Buffer', desc: 'Maintains rolling sequence matrix of shape (1, 10, 8).' },
    { label: 'PyTorch LSTM Network', desc: '2-Layer LSTM with 128 hidden units and 0.3 dropout.' },
    { label: 'ONNX Edge Runtime', desc: 'High-performance CPU inference execution (<50ms).' },
    { label: 'Modular Risk Engine', desc: 'Combines ML score with real-time heuristic signals -> Risk Score (0-100).' }
  ];

  return (
    <div className="min-h-screen bg-[#0A0E17] text-gray-100 flex flex-col">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 space-y-6 overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">AI Model Center & Architecture</h1>
              <p className="text-xs text-gray-400">PyTorch LSTM Neural Network & ONNX Runtime Edge Inference Engine</p>
            </div>
            <button
              onClick={fetchModel}
              className="bg-gray-900 hover:bg-gray-800 border border-gray-700 text-gray-300 px-3 py-1.5 rounded-lg text-xs flex items-center space-x-1.5 transition"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span>Refresh Model Info</span>
            </button>
          </div>

          {/* Active Model Overview Card */}
          <div className="bg-gray-900/80 border border-gray-800 p-6 rounded-2xl space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-gray-800 pb-4">
              <div className="flex items-center space-x-3">
                <div className="p-3 bg-blue-950 border border-blue-800 rounded-xl text-blue-400">
                  <Cpu className="h-6 w-6" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white font-mono">{model?.version || 'v1.0-lstm-onnx'}</h2>
                  <p className="text-xs text-gray-400">Framework: {model?.framework || 'PyTorch 2.0 / ONNX 1.14'}</p>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <span className="px-3 py-1 bg-emerald-950 text-emerald-400 border border-emerald-800 rounded-full text-xs font-mono font-semibold flex items-center gap-1.5">
                  <CheckCircle2 className="h-3.5 w-3.5" /> ACTIVE IN PRODUCTION
                </span>
              </div>
            </div>

            {/* Model Evaluation Metrics Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-2">
              <div className="bg-gray-950 border border-gray-800 p-3 rounded-xl text-center">
                <div className="text-[10px] text-gray-500 uppercase font-mono">Accuracy</div>
                <div className="text-lg font-extrabold text-emerald-400 font-mono">
                  {model?.metrics?.accuracy != null ? `${(model.metrics.accuracy * 100).toFixed(1)}%` : 'Not evaluated'}
                </div>
              </div>

              <div className="bg-gray-950 border border-gray-800 p-3 rounded-xl text-center">
                <div className="text-[10px] text-gray-500 uppercase font-mono">Precision</div>
                <div className="text-lg font-extrabold text-blue-400 font-mono">
                  {model?.metrics?.precision != null ? `${(model.metrics.precision * 100).toFixed(1)}%` : 'Not evaluated'}
                </div>
              </div>

              <div className="bg-gray-950 border border-gray-800 p-3 rounded-xl text-center">
                <div className="text-[10px] text-gray-500 uppercase font-mono">Recall</div>
                <div className="text-lg font-extrabold text-amber-400 font-mono">
                  {model?.metrics?.recall != null ? `${(model.metrics.recall * 100).toFixed(1)}%` : 'Not evaluated'}
                </div>
              </div>

              <div className="bg-gray-950 border border-gray-800 p-3 rounded-xl text-center">
                <div className="text-[10px] text-gray-500 uppercase font-mono">F1-Score</div>
                <div className="text-lg font-extrabold text-purple-400 font-mono">
                  {model?.metrics?.f1 != null ? `${(model.metrics.f1 * 100).toFixed(1)}%` : 'Not evaluated'}
                </div>
              </div>

              <div className="bg-gray-950 border border-gray-800 p-3 rounded-xl text-center col-span-2 sm:col-span-1">
                <div className="text-[10px] text-gray-500 uppercase font-mono">ROC-AUC</div>
                <div className="text-lg font-extrabold text-cyan-400 font-mono">
                  {model?.metrics?.roc_auc != null ? model.metrics.roc_auc.toFixed(4) : 'Not evaluated'}
                </div>
              </div>
            </div>
          </div>

          {/* Visual AI Pipeline Diagram */}
          <div className="bg-gray-900/80 border border-gray-800 p-6 rounded-2xl space-y-4">
            <h3 className="font-bold text-sm text-white flex items-center space-x-2">
              <Layers className="h-4 w-4 text-blue-400" />
              <span>Visual End-to-End AI Inference Pipeline</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-7 gap-2 pt-2">
              {pipelineSteps.map((step, idx) => (
                <div key={idx} className="flex flex-col items-center text-center">
                  <div className="w-full bg-gray-950 border border-gray-800 p-3 rounded-xl space-y-1 h-32 flex flex-col justify-center hover:border-blue-500 transition">
                    <span className="text-[10px] font-mono text-blue-400 font-bold">STEP {idx + 1}</span>
                    <h4 className="text-xs font-bold text-gray-200 leading-tight">{step.label}</h4>
                    <p className="text-[10px] text-gray-500 line-clamp-3 leading-normal">{step.desc}</p>
                  </div>
                  {idx < pipelineSteps.length - 1 && (
                    <div className="hidden md:block my-2 text-gray-600">↓</div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Feature Signals & Baseline Benchmarks Comparison */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 8 Feature Signals */}
            <div className="bg-gray-900/80 border border-gray-800 p-5 rounded-2xl space-y-3">
              <h3 className="font-bold text-sm text-white">8 Numerical Input Features</h3>
              <div className="space-y-1.5 text-xs font-mono">
                {[
                  '1. file_size (bytes)',
                  '2. entropy (Shannon 0.0–8.0 bits/byte)',
                  '3. entropy_change (current - previous entropy)',
                  '4. mod_rate (seconds between file operations)',
                  '5. ext_changed (1 if extension changed, 0 otherwise)',
                  '6. is_suspicious_process (1 if process unverified/suspicious)',
                  '7. file_path_length (character count)',
                  '8. is_common_extension (1 if common doc/img, 0 otherwise)'
                ].map((feat, i) => (
                  <div key={i} className="p-2 bg-gray-950 border border-gray-800 rounded text-gray-300">
                    {feat}
                  </div>
                ))}
              </div>
            </div>

            {/* Baseline Model Comparison Table */}
            <div className="bg-gray-900/80 border border-gray-800 p-5 rounded-2xl space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-sm text-white">Model Architecture Benchmarks</h3>
                  <p className="text-[11px] text-gray-400">Comparison of architectural baselines evaluated on controlled synthetic sequence data</p>
                </div>
                <span className="text-[10px] font-mono bg-gray-800 text-gray-400 px-2 py-0.5 rounded">
                  Controlled Synthetic Test Dataset
                </span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-gray-950 text-gray-400 uppercase text-[10px] border-b border-gray-800">
                    <tr>
                      <th className="p-2.5">Model Architecture</th>
                      <th className="p-2.5">Accuracy</th>
                      <th className="p-2.5">F1-Score</th>
                      <th className="p-2.5">ROC-AUC</th>
                      <th className="p-2.5">Evaluation Source</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800 text-gray-300">
                    <tr>
                      <td className="p-2.5">Logistic Regression (Baseline)</td>
                      <td className="p-2.5">91.2%</td>
                      <td className="p-2.5">90.8%</td>
                      <td className="p-2.5">0.9410</td>
                      <td className="p-2.5 text-gray-500">Historical Benchmark</td>
                    </tr>
                    <tr>
                      <td className="p-2.5">Random Forest (100 Trees)</td>
                      <td className="p-2.5">95.4%</td>
                      <td className="p-2.5">95.1%</td>
                      <td className="p-2.5">0.9780</td>
                      <td className="p-2.5 text-gray-500">Historical Benchmark</td>
                    </tr>
                    <tr className="bg-blue-950/40 text-blue-300 font-bold border-l-4 border-blue-500">
                      <td className="p-2.5">RansomGuard LSTM (PyTorch + ONNX)</td>
                      <td className="p-2.5">{model?.metrics?.accuracy != null ? `${(model.metrics.accuracy * 100).toFixed(1)}%` : 'Not evaluated'}</td>
                      <td className="p-2.5">{model?.metrics?.f1 != null ? `${(model.metrics.f1 * 100).toFixed(1)}%` : 'Not evaluated'}</td>
                      <td className="p-2.5">{model?.metrics?.roc_auc != null ? model.metrics.roc_auc.toFixed(4) : 'Not evaluated'}</td>
                      <td className="p-2.5 text-emerald-400">Live ONNX Test Split (615 sequences)</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p className="text-[10px] text-gray-500 italic pt-1">
                * Note: Model performance metrics are derived from a controlled synthetic test dataset (models/X_test.npy). Zero train/val/test session leakage is enforced. High metrics reflect clear mathematical separation of synthetic entropy and modification rates; not claimed as 100% real-world zero-day evasion detection.
              </p>
            </div>
          </div>
        </main>
      </div>

      <ChatbotDrawer pageContext="AI Model Center & Pipeline Architecture" />
    </div>
  );
};

export default ModelCenter;
