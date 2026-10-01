# Machine Learning Guide

The ML component of RansomGuard utilizes a deep learning approach combined with fallback heuristics to detect zero-day ransomware behavior based on file system telemetry.

## ML Pipeline Overview

1.  **Data Collection & Simulation:** Telemetry data is gathered from agents or the Simulation Lab.
2.  **Feature Extraction:** Raw file events are converted into 8 core features.
3.  **Inference (ONNX):** The lightweight LSTM model evaluates a time-series window of these features.
4.  **Risk Scoring:** The model's probability output is combined with heuristic rules.
5.  **Action:** If the score crosses defined thresholds, alerts or containment actions are triggered.

## Dataset Generation

Since real ransomware is dangerous, we use a custom **Simulation Lab** to generate synthetic behaviors. The lab simulates:
- Rapid file encryption (high entropy, rapid modification).
- File extension changes (e.g., appending `.locked`).
- Deletion of original files.
- Normal background system noise.

## Feature Engineering

We extract exactly 8 numerical features per time step (file event):

1.  **`entropy`**: Shannon entropy of the file (0-8). Encrypted files are close to 8.
2.  **`entropy_change`**: Difference in entropy before and after modification.
3.  **`mod_rate`**: Number of file modifications per second by the process.
4.  **`file_size`**: Size of the file in bytes (normalized).
5.  **`ext_changed`**: Boolean flag (1/0) if the extension was modified.
6.  **`is_suspicious_process`**: Flag if the parent process is unknown or lacks a valid signature.
7.  **`file_path_length`**: Length of the absolute file path.
8.  **`is_common_extension`**: Flag if the file is a commonly targeted type (e.g., `.docx`, `.jpg`).

## LSTM Model Architecture

Because ransomware operates over time (encrypting file by file), a Long Short-Term Memory (LSTM) network is used to capture temporal patterns.

- **Input Size:** 8 (Features)
- **Hidden Size:** 64
- **Layers:** 2 (Stacked LSTM)
- **Dropout:** 0.3
- **Output:** 1 (Sigmoid activation for probability 0.0 to 1.0)

## Training Process

1.  **Loss Function:** Binary Cross Entropy (BCEWithLogitsLoss).
2.  **Optimizer:** Adam with a learning rate of 0.001.
3.  **Regularization:** Early stopping based on validation loss to prevent overfitting.
4.  **Export:** The best performing PyTorch model (`.pt`) is exported to ONNX format (`.onnx`) for high-performance, dependency-light inference in production.

## Evaluation Metrics

The pipeline automatically calculates and logs:
- **Accuracy:** Overall correctness.
- **Precision:** Avoiding false positives (critical for auto-containment).
- **Recall:** Catching true positives (critical for security).
- **F1-Score:** Harmonic mean.
- **Confusion Matrix:** True Positives, False Positives, True Negatives, False Negatives.

## ONNX Runtime Inference

In production, RansomGuard does not require full PyTorch. It uses `onnxruntime` to load the exported model. This reduces memory footprint and increases inference speed, making it suitable for high-throughput cloud environments.

## Baseline Comparison

During development, the LSTM is compared against traditional ML models:
- **Logistic Regression:** Simple, fast, but fails on complex temporal patterns.
- **Random Forest:** Good feature importance, but lacks sequence memory.
LSTM consistently outperforms baselines on F1-score due to its ability to remember the sequence of rapid file modifications.

## Risk Scoring Engine

The final Threat Score is a weighted combination:
`Final Score = (ML Probability * 0.7) + (Heuristic Score * 0.3)`

**Heuristic Signals include:**
- Sudden spike in CPU usage.
- Known bad file extensions (e.g., `.wannacry`).
- Deletion of shadow copies.

## Heuristic Fallback

If the ML model is unloading, updating, or fails to execute, the system automatically falls back to a pure heuristic ruleset to ensure zero downtime protection.
