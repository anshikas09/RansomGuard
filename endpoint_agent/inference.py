import os
import numpy as np
import logging
from typing import List, Union

logger = logging.getLogger(__name__)

class LocalONNXInference:
    def __init__(self, model_path: str = "./models/ransomware_detector.onnx"):
        self.model_path = model_path
        self.session = None
        self.load()

    def load(self) -> bool:
        if os.path.exists(self.model_path):
            try:
                import onnxruntime as ort
                self.session = ort.InferenceSession(self.model_path)
                logger.info(f"Local ONNX Model loaded at {self.model_path}")
                return True
            except Exception as e:
                logger.warning(f"Could not load ONNX model: {e}")
                self.session = None
                return False
        self.session = None
        return False

    def predict_sequence(self, sequence: Union[List, np.ndarray]) -> float:
        seq_arr = np.array(sequence, dtype=np.float32)
        if seq_arr.ndim == 2:
            seq_arr = np.expand_dims(seq_arr, axis=0)

        if self.session is not None:
            try:
                input_name = self.session.get_inputs()[0].name
                out = self.session.run(None, {input_name: seq_arr})
                return float(out[0][0][0])
            except Exception as e:
                logger.error(f"Inference error: {e}")

        # Fallback local risk evaluation
        last_event = seq_arr[0, -1, :]
        entropy = last_event[1]
        entropy_change = last_event[2]
        ext_changed = last_event[4]
        is_suspicious_proc = last_event[5]

        score = 0.05
        if entropy > 7.0: score += 0.35
        if entropy_change > 1.5: score += 0.25
        if ext_changed == 1: score += 0.20
        if is_suspicious_proc == 1: score += 0.15

        return min(0.99, score)
