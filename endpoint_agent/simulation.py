import os
import time
import random

class SafeRansomwareSimulator:
    def __init__(self, target_dir: str = "./scratch/ransim_lab"):
        self.target_dir = target_dir
        os.makedirs(self.target_dir, exist_ok=True)

    def run_simulation(self, duration_sec: int = 20, file_count: int = 25, rate_files_per_sec: float = 5.0):
        print(f"Starting Safe Ransomware Simulation in '{self.target_dir}'...")
        print(f"Parameters: {file_count} files, {rate_files_per_sec} ops/sec, duration {duration_sec}s")

        interval = 1.0 / max(0.5, rate_files_per_sec)

        # 1. Generate initial benign files
        created_files = []
        for i in range(file_count):
            fname = f"sample_doc_{i:03d}.docx"
            fpath = os.path.join(self.target_dir, fname)
            with open(fpath, "w") as f:
                f.write("Safe benign user document content.\n" * 20)
            created_files.append(fpath)

        time.sleep(1.0)

        # 2. Simulate rapid ransomware burst modifications and extension renaming
        print("Simulating ransomware burst encryption attack...")
        start_time = time.time()
        for i, fpath in enumerate(created_files):
            if time.time() - start_time > duration_sec:
                break

            if os.path.exists(fpath):
                # High-entropy synthetic encryption content
                high_entropy_data = bytes([random.randint(0, 255) for _ in range(4096)])
                enc_path = fpath.replace(".docx", ".encrypted")

                with open(enc_path, "wb") as f:
                    f.write(high_entropy_data)

                try:
                    os.remove(fpath)
                except Exception:
                    pass

                print(f"  [{i+1}/{file_count}] Encrypted & renamed: {os.path.basename(fpath)} -> {os.path.basename(enc_path)}")

            time.sleep(interval)

        print("Safe simulation lab execution completed.")

if __name__ == "__main__":
    sim = SafeRansomwareSimulator()
    sim.run_simulation()
