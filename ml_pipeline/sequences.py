import json
import numpy as np
from typing import List, Dict, Tuple
from ml_pipeline.features import extract_features_from_event

def build_sequences_by_session(
    events_list: List[Dict],
    seq_length: int = 10
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    Groups events by session_id to build sequence samples of shape (N, 10, 8).
    Returns (X, y, session_ids)
    """
    session_map = {}
    for event in events_list:
        sid = event.get("session_id", "default_session")
        if sid not in session_map:
            session_map[sid] = []
        session_map[sid].append(event)

    X_sequences = []
    y_labels = []
    sids = []

    for sid, evts in session_map.items():
        if len(evts) < seq_length:
            continue

        for i in range(len(evts) - seq_length + 1):
            window = evts[i : i + seq_length]
            seq_feats = [extract_features_from_event(e) for e in window]
            
            # Label determined by the final event in sequence window
            label = window[-1].get("label", 0)

            X_sequences.append(seq_feats)
            y_labels.append(label)
            sids.append(sid)

    return np.array(X_sequences, dtype=np.float32), np.array(y_labels, dtype=np.float32), sids

def split_by_session(
    X: np.ndarray, y: np.ndarray, sids: List[str],
    train_ratio: float = 0.7, val_ratio: float = 0.2
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Splits sequences by distinct session_id to guarantee zero data leakage between train/val/test sets.
    """
    unique_sessions = list(set(sids))
    np.random.shuffle(unique_sessions)

    n_train = int(len(unique_sessions) * train_ratio)
    n_val = int(len(unique_sessions) * val_ratio)

    train_sids = set(unique_sessions[:n_train])
    val_sids = set(unique_sessions[n_train : n_train + n_val])
    test_sids = set(unique_sessions[n_train + n_val:])

    train_idx = [i for i, s in enumerate(sids) if s in train_sids]
    val_idx = [i for i, s in enumerate(sids) if s in val_sids]
    test_idx = [i for i, s in enumerate(sids) if s in test_sids]

    return (
        X[train_idx], y[train_idx],
        X[val_idx], y[val_idx],
        X[test_idx], y[test_idx]
    )
