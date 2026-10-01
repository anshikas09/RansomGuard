from app.incidents.risk_engine import calculate_risk_score

def test_risk_score_low():
    score, severity, action = calculate_risk_score(ml_probability=0.10, event_frequency=1.0)
    assert score < 30.0
    assert severity == "LOW"
    assert action == "MONITOR"

def test_risk_score_high_entropy_and_suspicious_proc():
    score, severity, action = calculate_risk_score(
        ml_probability=0.75,
        entropy_change=2.5,
        process_signals="suspicious"
    )
    assert score >= 80.0
    assert severity in ["HIGH", "CRITICAL"]

def test_risk_score_critical_containment():
    score, severity, action = calculate_risk_score(
        ml_probability=0.95,
        event_frequency=25.0,
        entropy_change=3.0,
        ext_changes=5,
        process_signals=1
    )
    assert score >= 90.0
    assert severity == "CRITICAL"
    assert action == "CONTAIN"
