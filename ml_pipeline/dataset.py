import json
import os
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict

class SyntheticDatasetGenerator:
    def __init__(self, output_dir: str = "./data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.common_extensions = ['docx', 'xlsx', 'pdf', 'jpg', 'png', 'txt', 'py', 'js', 'json', 'csv']
        self.benign_processes = [
            'word.exe', 'excel.exe', 'chrome.exe', 'firefox.exe', 
            'code.exe', 'explorer.exe', 'notepad.exe', 'outlook.exe'
        ]
        self.simulation_processes = [
            'ransim_burst.exe', 'ransim_entropy.exe', 'ransim_extension.exe'
        ]

    def calculate_entropy(self, is_encrypted: bool = False) -> float:
        if is_encrypted:
            return random.uniform(7.4, 7.99)
        return random.uniform(2.5, 5.5)

    def generate_benign_event(self, session_id: str, timestamp: datetime) -> Dict:
        operation = random.choice(['create', 'modify', 'delete', 'rename'])
        ext = random.choice(self.common_extensions)
        file_name = f"document_{random.randint(1000, 9999)}.{ext}"
        file_path = f"C:/Users/TestUser/Documents/{file_name}"
        
        file_size = random.randint(1024, 5242880)
        entropy = self.calculate_entropy(is_encrypted=False)
        process_name = random.choice(self.benign_processes)
        
        return {
            "session_id": session_id,
            "timestamp": timestamp.isoformat(),
            "file_path": file_path,
            "operation": operation,
            "process_name": process_name,
            "file_size": float(file_size),
            "entropy": float(entropy),
            "entropy_change": 0.0,
            "mod_rate": float(random.uniform(1.5, 30.0)),
            "ext_changed": 0,
            "is_suspicious_process": 0,
            "file_path_length": len(file_path),
            "is_common_extension": 1,
            "label": 0
        }

    def generate_malicious_event(self, session_id: str, timestamp: datetime, attack_type: str = "burst") -> Dict:
        operation = 'modify'
        ext = random.choice(['docx', 'xlsx', 'pdf', 'txt'])
        file_name = f"critical_data_{random.randint(1000, 9999)}.{ext}"
        file_path = f"C:/Users/TestUser/Documents/{file_name}"
        
        file_size = random.randint(2048, 1048576)
        entropy = self.calculate_entropy(is_encrypted=True)
        process_name = random.choice(self.simulation_processes)
        
        mod_rate = random.uniform(0.01, 0.3)
        ext_changed = 0
        is_common_ext = 1

        if attack_type == "extension_change":
            file_path = file_path.replace(f".{ext}", ".encrypted")
            ext_changed = 1
            is_common_ext = 0
        elif attack_type == "entropy_spike":
            entropy = random.uniform(7.85, 7.99)

        return {
            "session_id": session_id,
            "timestamp": timestamp.isoformat(),
            "file_path": file_path,
            "operation": operation,
            "process_name": process_name,
            "file_size": float(file_size),
            "entropy": float(entropy),
            "entropy_change": 0.0,
            "mod_rate": float(mod_rate),
            "ext_changed": ext_changed,
            "is_suspicious_process": 1,
            "file_path_length": len(file_path),
            "is_common_extension": is_common_ext,
            "label": 1
        }

    def generate_session(self, session_id: str, is_malicious: bool = False, 
                        num_events: int = 50, attack_type: str = "burst") -> List[Dict]:
        events = []
        base_time = datetime.utcnow()
        
        for i in range(num_events):
            if is_malicious:
                if i < int(num_events * 0.3):
                    event = self.generate_benign_event(session_id, base_time)
                else:
                    event = self.generate_malicious_event(session_id, base_time, attack_type)
            else:
                event = self.generate_benign_event(session_id, base_time)
            
            events.append(event)
            base_time += timedelta(seconds=event["mod_rate"])
        
        for i in range(1, len(events)):
            events[i]["entropy_change"] = round(events[i]["entropy"] - events[i-1]["entropy"], 4)
            if events[i]["label"] == 1 and attack_type == "extension_change":
                events[i]["ext_changed"] = 1

        return events

    def generate_dataset(self, num_benign_sessions: int = 100, 
                        num_malicious_sessions: int = 50,
                        events_per_session: int = 50) -> None:
        all_events = []
        
        print(f"Generating {num_benign_sessions} benign sessions...")
        for i in range(num_benign_sessions):
            session_id = f"benign_session_{i:04d}"
            events = self.generate_session(session_id, is_malicious=False, num_events=events_per_session)
            all_events.extend(events)
        
        attack_types = ["burst", "entropy_spike", "extension_change", "combined"]
        print(f"Generating {num_malicious_sessions} malicious sessions...")
        for i in range(num_malicious_sessions):
            session_id = f"malicious_session_{i:04d}"
            attack_type = random.choice(attack_types)
            events = self.generate_session(session_id, is_malicious=True, 
                                         num_events=events_per_session, attack_type=attack_type)
            all_events.extend(events)

        benign_events = [e for e in all_events if e["label"] == 0]
        malicious_events = [e for e in all_events if e["label"] == 1]
        
        with open(os.path.join(self.output_dir, "benign_events.jsonl"), 'w') as f:
            for event in benign_events:
                f.write(json.dumps(event) + "\n")
        
        with open(os.path.join(self.output_dir, "malicious_events.jsonl"), 'w') as f:
            for event in malicious_events:
                f.write(json.dumps(event) + "\n")
        
        with open(os.path.join(self.output_dir, "all_events.jsonl"), 'w') as f:
            for event in all_events:
                f.write(json.dumps(event) + "\n")
        
        print(f"Dataset generated successfully at {self.output_dir}:")
        print(f"  Benign events: {len(benign_events)}")
        print(f"  Malicious events: {len(malicious_events)}")
        print(f"  Total events: {len(all_events)}")

if __name__ == "__main__":
    generator = SyntheticDatasetGenerator()
    generator.generate_dataset(num_benign_sessions=100, num_malicious_sessions=50)
