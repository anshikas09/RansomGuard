import numpy as np
import os
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import onnxruntime as ort

def evaluate_model():
    X_test_path = "./models/X_test.npy"
    y_test_path = "./models/y_test.npy"
    onnx_path = "./models/ransomware_detector.onnx"

    if not os.path.exists(X_test_path) or not os.path.exists(y_test_path) or not os.path.exists(onnx_path):
        print("Model or evaluation dataset missing. Please run train.py first.")
        return

    X_test = np.load(X_test_path)
    y_test = np.load(y_test_path)

    session = ort.InferenceSession(onnx_path)
    input_name = session.get_inputs()[0].name

    y_probs = []
    for i in range(len(X_test)):
        sample = np.expand_dims(X_test[i], axis=0).astype(np.float32)
        out = session.run(None, {input_name: sample})
        y_probs.append(out[0][0][0])

    y_probs = np.array(y_probs)
    y_preds = (y_probs >= 0.5).astype(int)

    acc = accuracy_score(y_test, y_preds)
    prec = precision_score(y_test, y_preds, zero_division=0)
    rec = recall_score(y_test, y_preds, zero_division=0)
    f1 = f1_score(y_test, y_preds, zero_division=0)
    auc = roc_auc_score(y_test, y_probs)
    cm = confusion_matrix(y_test, y_preds)

    print("=== RansomGuard LSTM Model Evaluation Metrics ===")
    print(f"Accuracy:  {acc * 100:.2f}%")
    print(f"Precision: {prec * 100:.2f}%")
    print(f"Recall:    {rec * 100:.2f}%")
    print(f"F1 Score:  {f1 * 100:.2f}%")
    print(f"ROC-AUC:   {auc:.4f}")
    print("Confusion Matrix (TN, FP, FN, TP):")
    print(cm)

if __name__ == "__main__":
    evaluate_model()
