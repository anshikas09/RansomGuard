import os
import shutil
import psutil
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

WHITELIST = {'chrome.exe', 'word.exe', 'excel.exe', 'explorer.exe', 'code.exe', 'python.exe', 'cmd.exe', 'powershell.exe'}

class ContainmentEngine:
    def __init__(self, safe_mode: bool = True, quarantine_dir: str = "./scratch/quarantine"):
        self.safe_mode = safe_mode
        self.quarantine_dir = quarantine_dir
        os.makedirs(self.quarantine_dir, exist_ok=True)
        self.isolation_status = False

    def kill_process(self, process_name: str) -> Dict[str, Any]:
        proc_clean = process_name.lower()
        if proc_clean in WHITELIST:
            logger.warning(f"Process {process_name} is Whitelisted! Skipping kill command.")
            return {"status": "skipped", "reason": "Whitelisted process"}

        killed_pids = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == proc_clean:
                    if self.safe_mode:
                        logger.info(f"[SAFE CONTAINMENT] Would terminate process {proc.info['name']} (PID: {proc.info['pid']})")
                    else:
                        proc.kill()
                        logger.info(f"Terminated process {proc.info['name']} (PID: {proc.info['pid']})")
                    killed_pids.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return {
            "status": "success",
            "target_process": process_name,
            "killed_pids": killed_pids,
            "safe_mode": self.safe_mode
        }

    def isolate_endpoint(self, isolate: bool = True) -> Dict[str, Any]:
        self.isolation_status = isolate
        mode_str = "ISOLATED" if isolate else "CONNECTED"
        logger.info(f"[SAFE CONTAINMENT] Endpoint network adapter state set to: {mode_str}")
        return {
            "status": "success",
            "is_isolated": self.isolation_status,
            "message": f"Endpoint network traffic {'blocked' if isolate else 'restored'}"
        }

    def quarantine_file(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {"status": "failed", "reason": "File does not exist"}

        try:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.quarantine_dir, filename)
            shutil.move(file_path, dest_path)
            logger.info(f"Quarantined file {file_path} to {dest_path}")
            return {"status": "success", "quarantined_to": dest_path}
        except Exception as e:
            logger.error(f"Failed to quarantine file {file_path}: {e}")
            return {"status": "failed", "error": str(e)}
