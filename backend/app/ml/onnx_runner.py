import os
import logging
import pickle
import numpy as np
from typing import List, Union

logger = logging.getLogger(__name__)

class ONNXInferenceEngine:
    def __init__(self, model_path: str = None, scaler_path: str = None):
        if model_path is None:
            model_path = os.getenv("MODEL_PATH", "./models/ransomware_detector.onnx")
        if scaler_path is None:
            scaler_path = os.getenv("SCALER_PATH", "./models/scaler.pkl")

        # Robust path resolution for model
        model_candidates = [
            model_path,
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "ransomware_detector.onnx")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models", "ransomware_detector.onnx")),
            os.path.abspath("./models/ransomware_detector.onnx"),
            os.path.abspath("../models/ransomware_detector.onnx")
        ]
        
        resolved_model_path = model_path
        for candidate in model_candidates:
            if candidate and os.path.exists(candidate):
                resolved_model_path = candidate
                break

        # Robust path resolution for scaler
        scaler_candidates = [
            scaler_path,
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "scaler.pkl")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models", "scaler.pkl")),
            os.path.abspath("./models/scaler.pkl"),
            os.path.abspath("../models/scaler.pkl")
        ]
        
        resolved_scaler_path = scaler_path
        for candidate in scaler_candidates:
            if candidate and os.path.exists(candidate):
                resolved_scaler_path = candidate
                break

        self.model_path = resolved_model_path
        self.scaler_path = resolved_scaler_path
        self.session = None
        self.scaler = None
        
        self.load_model()
        self.load_scaler()

    def load_model(self) -> bool:
        if os.path.exists(self.model_path):
            try:
                import onnxruntime as ort
                self.session = ort.InferenceSession(self.model_path)
                logger.info(f"ONNX Model successfully loaded from {self.model_path}")
                return True
            except Exception as e:
                logger.warning(f"Failed to load ONNX model at {self.model_path}: {e}")
                self.session = None
                return False
        else:
            logger.info(f"ONNX Model file not found at {self.model_path}. Using fallback rule-based predictor until model is trained.")
            self.session = None
            return False

    def load_scaler(self) -> bool:
        if os.path.exists(self.scaler_path):
            try:
                with open(self.scaler_path, "rb") as f:
                    self.scaler = pickle.load(f)
                logger.info(f"StandardScaler successfully loaded from {self.scaler_path}")
                return True
            except Exception as e:
                logger.warning(f"Failed to load scaler at {self.scaler_path}: {e}")
                self.scaler = None
                return False
        return False

    def predict(self, sequence: Union[List, np.ndarray]) -> float:
        """
        Accepts input sequence of shape (10, 8) or batch (1, 10, 8)
        Returns probability float between 0.0 and 1.0
        """
        seq_array = np.array(sequence, dtype=np.float32)
        if seq_array.ndim == 2:
            seq_array = np.expand_dims(seq_array, axis=0)  # Shape: (1, 10, 8)

        if self.session is not None:
            try:
                input_data = seq_array.copy()
                if self.scaler is not None:
                    # Scale (1, 10, 8) by flattening to (10, 8) and back
                    b, s, f = input_data.shape
                    flat_data = input_data.reshape(-1, f)
                    scaled_flat = self.scaler.transform(flat_data)
                    input_data = scaled_flat.reshape(b, s, f).astype(np.float32)

                input_name = self.session.get_inputs()[0].name
                outputs = self.session.run(None, {input_name: input_data})
                prob = float(outputs[0][0][0])
                return max(0.0, min(1.0, prob))
            except Exception as e:
                logger.error(f"ONNX Inference error: {e}")

        # Heuristic fallback if model not loaded
        # Feature order: [file_size, entropy, entropy_change, mod_rate, ext_changed, is_suspicious_process, file_path_length, is_common_extension]
        last_event = seq_array[0, -1, :]
        entropy = last_event[1]
        entropy_change = last_event[2]
        mod_rate = last_event[3]
        ext_changed = last_event[4]
        is_suspicious_process = last_event[5]

        # Calculate heuristic probability
        prob = 0.05
        if entropy > 7.0:
            prob += 0.35
        if entropy_change > 1.5:
            prob += 0.25
        if mod_rate < 0.5 and mod_rate > 0:
            prob += 0.15
        if ext_changed == 1:
            prob += 0.15
        if is_suspicious_process == 1:
            prob += 0.20

        return max(0.0, min(0.99, prob))

# Singleton instance
inference_engine = ONNXInferenceEngine()
