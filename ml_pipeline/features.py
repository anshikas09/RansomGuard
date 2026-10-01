import numpy as np
import pickle
import os
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Tuple

FEATURE_NAMES = [
    "file_size",
    "entropy",
    "entropy_change",
    "mod_rate",
    "ext_changed",
    "is_suspicious_process",
    "file_path_length",
    "is_common_extension"
]

def extract_features_from_event(event: Dict) -> List[float]:
    return [
        float(event.get("file_size", 0.0)),
        float(event.get("entropy", 0.0)),
        float(event.get("entropy_change", 0.0)),
        float(event.get("mod_rate", 0.0)),
        float(event.get("ext_changed", 0)),
        float(event.get("is_suspicious_process", 0)),
        float(event.get("file_path_length", 0)),
        float(event.get("is_common_extension", 1))
    ]

def fit_and_save_scaler(X_raw: np.ndarray, scaler_path: str = "./models/scaler.pkl") -> StandardScaler:
    os.makedirs(os.path.dirname(scaler_path), exist_ok=True)
    scaler = StandardScaler()

    # Reshape X from (N, 10, 8) to (N*10, 8) for fitting
    if X_raw.ndim == 3:
        N, seq_len, num_feats = X_raw.shape
        X_flat = X_raw.reshape(-1, num_feats)
        scaler.fit(X_flat)
    else:
        scaler.fit(X_raw)

    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)

    print(f"StandardScaler fit and saved to {scaler_path}")
    return scaler

def load_scaler(scaler_path: str = "./models/scaler.pkl") -> StandardScaler:
    if os.path.exists(scaler_path):
        with open(scaler_path, "rb") as f:
            return pickle.load(f)
    scaler = StandardScaler()
    return scaler
