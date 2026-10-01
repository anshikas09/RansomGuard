# User Guide

Welcome to the RansomGuard User Guide. This document will help you navigate the system as a Security Analyst.

## Getting Started

1.  **Sign Up / Login:** Navigate to the main web portal. Create a new administrative account or login with existing credentials.
2.  **Onboarding Wizard:** Upon first login, you'll be greeted by an onboarding wizard explaining the core concepts (Dashboard, Endpoints, ML Center).

## Dashboard Overview

The SOC (Security Operations Center) Dashboard provides a real-time overview of your environment.
- **Top Metrics:** Total endpoints, active incidents, and global system health.
- **Activity Graph:** A timeline chart showing file events and anomalies detected over the last 24 hours.
- **Recent Incidents:** A feed of the latest alerts ranked by severity.

## Endpoint Management

Navigate to the **Endpoints** tab to see all connected machines running the RansomGuard agent.
- **Status:** View online/offline status and last heartbeat.
- **Manual Isolation:** If you suspect an endpoint is compromised, you can manually click the "Isolate" button to cut off its network access while keeping the management connection alive for investigation.

## Running a Ransomware Simulation

To test the system or train the ML model, use the **Simulation Lab**.
1. Navigate to the Simulation Lab tab.
2. Select a simulation profile (e.g., "Rapid Encryption", "Extension Modification").
3. Click **Start Simulation**.
4. Watch the Dashboard to see the events stream in and observe the ML model detecting the simulated threat in real-time.
5. Click **Stop Simulation** to clean up the dummy files.

## Viewing Incident Investigations

When an alert fires, an Incident is created.
1. Click on an Incident in the dashboard.
2. **Timeline:** View the sequence of file events that led to the alert.
3. **Evidence:** See the calculated anomaly scores and features (e.g., entropy spikes).
4. **Action:** Mark the incident as a True Positive (Keep Isolated) or False Positive (Release Endpoint).

## Model Center Walkthrough

The Model Center allows you to manage the AI brains of RansomGuard.
- **Active Model:** View the currently loaded ONNX model and its performance metrics.
- **Version History:** See previously trained models.
- **Retrain:** (Admin only) Trigger a background job to retrain the model on new data collected from the system.

## Copilot Chatbot Usage

Stuck on an investigation? Use the **RansomGuard Copilot** integrated into the bottom right of the UI.
- Ask questions like: *"What is the normal entropy for a PDF file?"*
- Ask for summaries: *"Summarize Incident #104"*
- The Copilot is context-aware and trained on cybersecurity principles.

## System Health Monitoring

The Settings -> Health page displays backend metrics:
- Database connectivity
- ML Engine latency
- Active WebSocket connections

## FAQ / Troubleshooting

**Q: Why is an endpoint showing as Offline?**
A: Ensure the RansomGuard Agent service is running on the client machine and has network access to the API server.

**Q: Can I export the incident reports?**
A: Yes, click the "Export PDF" button on any incident detail page.

**Q: The ML Model is producing False Positives. What should I do?**
A: Mark the incidents as False Positives. This data is fed back into the system. You can then navigate to the Model Center and initiate a retraining job.
