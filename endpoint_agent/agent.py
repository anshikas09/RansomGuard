import os
import sys
import time
import json
import yaml
import requests
import threading
import logging
from queue import Queue, Empty
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from feature_extractor import FeatureExtractor
from inference import LocalONNXInference
from containment import ContainmentEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Agent] %(message)s")
logger = logging.getLogger("RansomGuardAgent")

class TelemetryEventHandler(FileSystemEventHandler):
    def __init__(self, event_queue: Queue, feature_extractor: FeatureExtractor):
        super().__init__()
        self.event_queue = event_queue
        self.extractor = feature_extractor

    def on_modified(self, event):
        if not event.is_directory:
            feat = self.extractor.extract("modify", event.src_path, "ransim_burst.exe")
            self.event_queue.put(feat)

    def on_created(self, event):
        if not event.is_directory:
            feat = self.extractor.extract("create", event.src_path, "ransim_burst.exe")
            self.event_queue.put(feat)

    def on_deleted(self, event):
        if not event.is_directory:
            feat = self.extractor.extract("delete", event.src_path, "ransim_burst.exe")
            self.event_queue.put(feat)

    def on_moved(self, event):
        if not event.is_directory:
            feat = self.extractor.extract("rename", event.dest_path, "ransim_extension.exe")
            self.event_queue.put(feat)

class RansomGuardAgent:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self.load_config(config_path)
        self.hostname = self.config["agent"]["hostname"]
        self.backend_url = self.config["backend"]["url"]
        self.telemetry_interval = self.config["backend"]["telemetry_interval"]
        self.heartbeat_interval = self.config["backend"]["heartbeat_interval"]
        self.target_dir = self.config["monitoring"]["target_directory"]

        os.makedirs(self.target_dir, exist_ok=True)

        self.extractor = FeatureExtractor()
        self.inference = LocalONNXInference()
        self.containment = ContainmentEngine(safe_mode=self.config["containment"]["enabled"])

        self.event_queue = Queue()
        self.is_running = True
        self.registered = False

    def load_config(self, path: str) -> dict:
        if os.path.exists(path):
            with open(path, "r") as f:
                return yaml.safe_load(f)
        return {
            "agent": {"hostname": "demo-endpoint-vm01", "version": "1.0.0", "os": "Windows 11 Security Lab"},
            "backend": {"url": "http://localhost:8000", "telemetry_interval": 5, "heartbeat_interval": 30},
            "monitoring": {"target_directory": "./scratch/ransim_lab"},
            "containment": {"enabled": True}
        }

    def register(self):
        try:
            url = f"{self.backend_url}/api/v1/endpoints/register"
            payload = {
                "hostname": self.hostname,
                "os": self.config["agent"]["os"],
                "ip_address": "127.0.0.1",
                "agent_version": self.config["agent"]["version"]
            }
            resp = requests.post(url, json=payload, timeout=5)
            if resp.status_code == 200:
                self.registered = True
                logger.info(f"Agent successfully registered to backend at {url}")
            else:
                logger.warning(f"Registration returned status {resp.status_code}")
        except Exception as e:
            logger.warning(f"Backend registration pending (backend offline or unreachable): {e}")

    def send_heartbeat_loop(self):
        while self.is_running:
            try:
                import psutil
                cpu_val = round(psutil.cpu_percent(interval=0.1), 1)
                mem_val = round(psutil.Process().memory_info().rss / (1024 * 1024), 1)
                url = f"{self.backend_url}/api/v1/endpoints/heartbeat"
                payload = {
                    "hostname": self.hostname,
                    "cpu_usage": cpu_val,
                    "memory_usage": mem_val,
                    "telemetry_count": self.event_queue.qsize(),
                    "status": "online"
                }
                requests.post(url, json=payload, timeout=5)
            except Exception:
                pass
            time.sleep(self.heartbeat_interval)

    def telemetry_flush_loop(self):
        while self.is_running:
            time.sleep(self.telemetry_interval)
            events_to_send = []
            while not self.event_queue.empty():
                try:
                    events_to_send.append(self.event_queue.get_nowait())
                except Empty:
                    break

            if not events_to_send:
                continue

            try:
                url = f"{self.backend_url}/api/v1/telemetry/"
                payload = {
                    "hostname": self.hostname,
                    "events": events_to_send
                }
                resp = requests.post(url, json=payload, timeout=5)
                if resp.status_code in (200, 201):
                    logger.info(f"Flushed {len(events_to_send)} file event telemetry records to backend.")
                else:
                    logger.warning(f"Failed to ingest telemetry: status {resp.status_code}")
            except Exception as e:
                logger.warning(f"Backend unreachable, queuing telemetry locally ({len(events_to_send)} events preserved): {e}")
                # Requeue events for retry
                for ev in events_to_send:
                    self.event_queue.put(ev)

    def start(self):
        logger.info(f"Starting RansomGuard Endpoint Agent monitoring directory '{self.target_dir}'...")
        self.register()

        # Start background threads
        hb_thread = threading.Thread(target=self.send_heartbeat_loop, daemon=True)
        tf_thread = threading.Thread(target=self.telemetry_flush_loop, daemon=True)
        hb_thread.start()
        tf_thread.start()

        event_handler = TelemetryEventHandler(self.event_queue, self.extractor)
        observer = Observer()
        observer.schedule(event_handler, self.target_dir, recursive=False)
        observer.start()

        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping agent...")
            self.is_running = False
            observer.stop()
        observer.join()

if __name__ == "__main__":
    agent = RansomGuardAgent()
    agent.start()
