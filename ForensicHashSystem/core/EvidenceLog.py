import json
import os

class EvidenceLog:
    LOG_FILE = "evidence_log.json"

    @classmethod
    def load_log(cls):
        if not os.path.exists(cls.LOG_FILE):
            return []
        with open(cls.LOG_FILE, "r") as f:
            return json.load(f)

    @classmethod
    def save_entry(cls, context, hash_value):
        log = cls.load_log()
        entry = {**context, "hash": hash_value}
        log.append(entry)

        with open(cls.LOG_FILE, "w") as f:
            json.dump(log, f, indent=4)

    @classmethod
    def get_last_hash(cls):
        log = cls.load_log()
        return log[-1]["hash"] if log else ""

    @classmethod
    def find_entry(cls, file_name, camera_id):
        log = cls.load_log()
        for entry in reversed(log):
            if entry["file_name"] == file_name and entry["camera_id"] == camera_id:
                return entry
        return None
