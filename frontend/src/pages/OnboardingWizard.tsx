import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import ChatbotDrawer from '../components/ChatbotDrawer';
import { CheckCircle2, ArrowRight, ArrowLeft, Shield, Monitor, Activity, Cpu, FlaskConical, Lock, LayoutDashboard } from 'lucide-react';

const OnboardingWizard: React.FC = () => {
  const [step, setStep] = useState(1);
  const navigate = useNavigate();

  const steps = [
    { title: 'Account', desc: 'Verify SOC Role & Permissions', icon: Shield },
    { title: 'Endpoint', desc: 'Connect Endpoint Agent Host', icon: Monitor },
    { title: 'Telemetry', desc: 'Verify Watchdog File Events Stream', icon: Activity },
    { title: 'AI Model', desc: 'Inspect PyTorch LSTM & ONNX Pipeline', icon: Cpu },
    { title: 'Simulation', desc: 'Launch Safe Simulation Lab', icon: FlaskConical },
    { title: 'Detection', desc: 'Observe Real-Time Threat Score Escalation', icon: Activity },
    { title: 'Containment', desc: 'Review Automated Process Kill & Isolation', icon: Lock },
    { title: 'Dashboard', desc: 'Explore Complete SOC Command Center', icon: LayoutDashboard }
  ];

  return (
    <div className="min-h-screen bg-[#0A0E17] text-gray-100 flex flex-col">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 space-y-6 overflow-y-auto max-w-5xl mx-auto">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Guided College Demo Onboarding</h1>
            <p className="text-xs text-gray-400">8-Step Walkthrough to Demonstrate RansomGuard End-to-End Capabilities</p>
          </div>

          {/* Progress Indicator */}
          <div className="bg-gray-900/80 border border-gray-800 p-5 rounded-2xl">
            <div className="grid grid-cols-4 sm:grid-cols-8 gap-2">
              {steps.map((s, idx) => {
                const Icon = s.icon;
                const num = idx + 1;
                const isCurrent = step === num;
                const isPast = step > num;

                return (
                  <div
                    key={num}
                    onClick={() => setStep(num)}
                    className={`cursor-pointer p-2.5 rounded-xl border text-center transition flex flex-col items-center space-y-1 ${
                      isCurrent
                        ? 'bg-blue-950/80 border-blue-500 text-blue-400'
                        : isPast
                        ? 'bg-emerald-950/40 border-emerald-800 text-emerald-400'
                        : 'bg-gray-950 border-gray-800 text-gray-600'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span className="text-[10px] font-mono font-bold">{num}. {s.title}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Step Detail Cards */}
          <div className="bg-gray-900/80 border border-gray-800 p-8 rounded-2xl space-y-6 shadow-2xl">
            <div className="flex items-center space-x-3 border-b border-gray-800 pb-4">
              <div className="p-3 bg-blue-950 border border-blue-800 rounded-xl text-blue-400">
                {React.createElement(steps[step - 1].icon, { className: 'h-6 w-6' })}
              </div>
              <div>
                <span className="text-xs font-mono text-blue-400 font-bold uppercase">Step {step} of 8</span>
                <h2 className="text-xl font-bold text-white">{steps[step - 1].title}: {steps[step - 1].desc}</h2>
              </div>
            </div>

            <div className="space-y-4 text-xs text-gray-300 leading-relaxed font-mono">
              {step === 1 && (
                <div className="space-y-2">
                  <p>Welcome to RansomGuard! Your SOC Analyst account is authenticated with JWT token security and Role-Based Access Control (RBAC).</p>
                  <div className="bg-gray-950 p-3 rounded-lg border border-gray-800 text-emerald-400">
                    ✓ Authenticated role: Administrator / SOC Analyst
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="space-y-2">
                  <p>Connect an endpoint host agent by starting `python endpoint_agent/agent.py`. The agent auto-registers via HTTPS to localhost:8000.</p>
                  <div className="bg-gray-950 p-3 rounded-lg border border-gray-800 text-blue-300 font-mono">
                    Endpoint Registration API: POST /api/v1/endpoints/register
                  </div>
                </div>
              )}

              {step === 3 && (
                <div className="space-y-2">
                  <p>The agent uses Watchdog to monitor `./scratch/ransim_lab` for file events and computes 8 numerical features per operation.</p>
                </div>
              )}

              {step === 4 && (
                <div className="space-y-2">
                  <p>The backend and agent run ONNX edge inference on 10-event rolling sequence windows with probability calculation in &lt; 50ms.</p>
                </div>
              )}

              {step === 5 && (
                <div className="space-y-2">
                  <p>Open the Safe Simulation Lab to launch a controlled synthetic ransomware burst. Zero risk to arbitrary user or system files.</p>
                </div>
              )}

              {step === 6 && (
                <div className="space-y-2">
                  <p>Observe the AI threat score escalate from 15% to 98% as rapid high-entropy file modifications occur in real time.</p>
                </div>
              )}

              {step === 7 && (
                <div className="space-y-2">
                  <p>When threat score exceeds 90%, automated containment triggers: malicious process killed, host network isolated, incident case opened.</p>
                </div>
              )}

              {step === 8 && (
                <div className="space-y-2">
                  <p>Explore the SOC Dashboard to review live WebSocket charts, incident timelines, analyst case file notes, and audit logs.</p>
                </div>
              )}
            </div>

            {/* Navigation Buttons */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-800">
              <button
                onClick={() => setStep((s) => Math.max(1, s - 1))}
                disabled={step === 1}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg text-xs font-medium flex items-center space-x-1 disabled:opacity-50"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Previous Step</span>
              </button>

              {step < 8 ? (
                <button
                  onClick={() => setStep((s) => Math.min(8, s + 1))}
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-1 shadow-lg"
                >
                  <span>Next Step</span>
                  <ArrowRight className="h-4 w-4" />
                </button>
              ) : (
                <button
                  onClick={() => navigate('/dashboard')}
                  className="px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold flex items-center space-x-2 shadow-lg"
                >
                  <CheckCircle2 className="h-4 w-4" />
                  <span>Go to SOC Command Center</span>
                </button>
              )}
            </div>
          </div>
        </main>
      </div>

      <ChatbotDrawer pageContext="Guided 8-Step Onboarding Walkthrough" />
    </div>
  );
};

export default OnboardingWizard;
