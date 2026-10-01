from typing import Tuple, Dict, Any, Union

def calculate_risk_score(
    ml_probability: float,
    event_frequency: float = 0.0,
    entropy_change: float = 0.0,
    ext_changes: int = 0,
    process_signals: Any = 0,
    endpoint_context: Dict[str, Any] = None,
    thresholds: Dict[str, float] = None,
    return_details: bool = False
) -> Union[Tuple[float, str, str], Tuple[float, str, str, float]]:
    """
    Modular Risk Engine combining ML prediction with real-time heuristic signals.
    - ml_probability: raw output from ONNX LSTM sequence model [0.0 - 1.0]
    - behavioral_score: heuristic score from burst rate, entropy delta, extension changes, suspicious process [0.0 - 100.0]
    - risk_score: final composite threat score [0.0 - 100.0]
    Returns: (risk_score, severity, recommended_action) or with behavioral_score if return_details=True
    """
    if thresholds is None:
        thresholds = {'alert': 80.0, 'containment': 90.0}

    # 1. Base ML Score derived from LSTM model (0.0 to 100.0)
    ml_score = round(ml_probability * 100.0, 2)

    # 2. Behavioral Heuristic Score (0.0 to 100.0)
    behavioral_score = 0.0
    if event_frequency > 10.0:  # High frequency burst (>10 files/sec)
        behavioral_score += 15.0
    if entropy_change > 2.0:  # Rapid synthetic encryption entropy spike
        behavioral_score += 35.0
    if ext_changes > 0:  # Extension alterations (.encrypted)
        behavioral_score += 25.0
    if str(process_signals).lower() in ["suspicious", "1", "true"]:
        behavioral_score += 25.0

    behavioral_score = min(behavioral_score, 100.0)

    # 3. Final Composite Threat Score
    # Combines ML probability with behavioral adjustments
    base_score = ml_score
    if event_frequency > 10.0:
        base_score += 10.0
    if entropy_change > 2.0:
        base_score += 15.0
    if ext_changes > 3:
        base_score += 10.0
    if str(process_signals).lower() in ["suspicious", "1", "true"]:
        base_score += 20.0

    risk_score = round(min(base_score, 100.0), 2)

    # 4. Map to standardized severity bands
    if risk_score < 30.0:
        severity = "LOW"
    elif risk_score < 60.0:
        severity = "MEDIUM"
    elif risk_score < 80.0:
        severity = "HIGH"
    else:
        severity = "CRITICAL"

    # 5. Determine action recommendation based on thresholds
    if risk_score >= thresholds.get('containment', 90.0):
        recommended_action = "CONTAIN"
    elif risk_score >= thresholds.get('alert', 80.0):
        recommended_action = "ALERT"
    else:
        recommended_action = "MONITOR"

    if return_details:
        return risk_score, severity, recommended_action, round(behavioral_score, 1)

    return risk_score, severity, recommended_action
