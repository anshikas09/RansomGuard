import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import Dashboard from './pages/Dashboard';
import EndpointsPage from './pages/EndpointsPage';
import IncidentDetailPage from './pages/IncidentDetailPage';
import ModelCenter from './pages/ModelCenter';
import SimulationLab from './pages/SimulationLab';
import SystemHealth from './pages/SystemHealth';
import OnboardingWizard from './pages/OnboardingWizard';
import NotFound from './pages/NotFound';

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0E17] text-blue-400 font-mono text-sm flex items-center justify-center">
        Authenticating RansomGuard Session...
      </div>
    );
  }
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/endpoints"
            element={
              <PrivateRoute>
                <EndpointsPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/incidents/:id"
            element={
              <PrivateRoute>
                <IncidentDetailPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/model-center"
            element={
              <PrivateRoute>
                <ModelCenter />
              </PrivateRoute>
            }
          />
          <Route
            path="/simulation-lab"
            element={
              <PrivateRoute>
                <SimulationLab />
              </PrivateRoute>
            }
          />
          <Route
            path="/system-health"
            element={
              <PrivateRoute>
                <SystemHealth />
              </PrivateRoute>
            }
          />
          <Route
            path="/onboarding"
            element={
              <PrivateRoute>
                <OnboardingWizard />
              </PrivateRoute>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
