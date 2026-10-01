import os
import math
import time
from typing import Dict, Any

COMMON_EXTENSIONS = {'docx', 'xlsx', 'pdf', 'jpg', 'jpeg', 'png', 'txt', 'py', 'js', 'json', 'csv', 'html'}
WHITELIST_PROCESSES = {'chrome.exe', 'word.exe', 'excel.exe', 'explorer.exe', 'code.exe', 'notepad.exe'}

class FeatureExtractor:
    def __init__(self):
        self.last_event_time = time.time()
        self.last_file_entropies = {}

    def calculate_shannon_entropy(self, file_path: str) -> float:
        """Calculate Shannon entropy (0 to 8 bits per byte)"""
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            return 3.5

        try:
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return 0.0

            # Read sample chunk up to 64KB for high performance
            read_bytes = min(file_size, 65536)
            with open(file_path, "rb") as f:
                data = f.read(read_bytes)

            if not data:
                return 0.0

            byte_counts = [0] * 256
            for b in data:
                byte_counts[b] += 1

            entropy = 0.0
            total = len(data)
            for count in byte_counts:
                if count > 0:
                    p = count / total
                    entropy -= p * math.log2(p)

            return round(entropy, 4)
        except Exception:
            return 4.0

    def extract(self, event_type: str, file_path: str, process_name: str = "unknown") -> Dict[str, Any]:
        now = time.time()
        mod_rate = max(0.01, now - self.last_event_time)
        self.last_event_time = now

        file_size = 0.0
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            try:
                file_size = float(os.path.getsize(file_path))
            except Exception:
                file_size = 1024.0

        current_entropy = self.calculate_shannon_entropy(file_path)
        previous_entropy = self.last_file_entropies.get(file_path, current_entropy)
        entropy_change = round(current_entropy - previous_entropy, 4)
        self.last_file_entropies[file_path] = current_entropy

        ext = file_path.split('.')[-1].lower() if '.' in file_path else ''
        ext_changed = 1 if ext in ['encrypted', 'locked', 'crypto', 'ransom'] else 0
        is_common_ext = 1 if ext in COMMON_EXTENSIONS else 0

        proc_clean = process_name.lower()
        is_suspicious_proc = 1 if (proc_clean not in WHITELIST_PROCESSES or 'ransim' in proc_clean) else 0

        return {
            "file_path": file_path,
            "operation": event_type,
            "file_size": file_size,
            "entropy": current_entropy,
            "entropy_change": entropy_change,
            "mod_rate": mod_rate,
            "ext_changed": ext_changed,
            "is_suspicious_process": is_suspicious_proc,
            "file_path_length": len(file_path),
            "is_common_extension": is_common_ext,
            "process_name": process_name
        }
