import numpy as np
import os
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def run_baseline_comparison():
    X_test_path = "./models/X_test.npy"
    y_test_path = "./models/y_test.npy"

    if not os.path.exists(X_test_path) or not os.path.exists(y_test_path):
        print("Test data missing. Run train.py first.")
        return

    X_test = np.load(X_test_path)
    y_test = np.load(y_test_path)

    # Flatten (N, 10, 8) -> (N, 80) for classical ML baseline models
    N, seq_len, num_feats = X_test.shape
    X_test_flat = X_test.reshape(N, -1)

    # Logistic Regression
    lr = LogisticRegression(max_iter=1000)
    lr.fit(X_test_flat, y_test)
    lr_preds = lr.predict(X_test_flat)
    lr_probs = lr.predict_proba(X_test_flat)[:, 1]

    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_test_flat, y_test)
    rf_preds = rf.predict(X_test_flat)
    rf_probs = rf.predict_proba(X_test_flat)[:, 1]

    print("=== Baseline Model Benchmarks ===")
    print("1. Logistic Regression:")
    print(f"   Accuracy:  {accuracy_score(y_test, lr_preds)*100:.2f}%")
    print(f"   F1 Score:  {f1_score(y_test, lr_preds, zero_division=0)*100:.2f}%")
    print(f"   ROC-AUC:   {roc_auc_score(y_test, lr_probs):.4f}")

    print("\n2. Random Forest (100 Trees):")
    print(f"   Accuracy:  {accuracy_score(y_test, rf_preds)*100:.2f}%")
    print(f"   F1 Score:  {f1_score(y_test, rf_preds, zero_division=0)*100:.2f}%")
    print(f"   ROC-AUC:   {roc_auc_score(y_test, rf_probs):.4f}")

if __name__ == "__main__":
    run_baseline_comparison()
