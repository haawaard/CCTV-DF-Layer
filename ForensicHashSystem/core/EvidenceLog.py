import json
import os
import uuid
import time

class EvidenceLog:
    LOG_FILE = "evidence_log.json"
    CAMERA_COUNTER_FILE = "camera_counter.json"

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
    
    @classmethod
    def generate_camera_id(cls):
        """Generate auto-incremented camera ID in format CAM-XXXX"""
        if not os.path.exists(cls.CAMERA_COUNTER_FILE):
            counter = 1000
        else:
            with open(cls.CAMERA_COUNTER_FILE, "r") as f:
                counter = json.load(f).get("counter", 1000)
        
        counter += 1
        with open(cls.CAMERA_COUNTER_FILE, "w") as f:
            json.dump({"counter": counter}, f)
        
        return f"CAM-{counter:04d}"
    
    @classmethod
    def generate_evidence_uuid(cls):
        """Generate unique evidence UUID"""
        return str(uuid.uuid4())
    
    @classmethod
    def find_entry_by_uuid(cls, evidence_uuid):
        """Find entry by evidence UUID"""
        log = cls.load_log()
        for entry in log:
            if entry.get("evidence_uuid") == evidence_uuid:
                return entry
        return None
    
    @classmethod
    def add_access_log_entry(cls, evidence_uuid, user, action):
        """Add an access log entry for an evidence item"""
        log = cls.load_log()
        for entry in log:
            if entry.get("evidence_uuid") == evidence_uuid:
                if "access_log" not in entry:
                    entry["access_log"] = []
                entry["access_log"].append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "user": user,
                    "action": action
                })
                break
        
        with open(cls.LOG_FILE, "w") as f:
            json.dump(log, f, indent=4)
    
    @classmethod
    def add_verification_log_entry(cls, evidence_uuid, result, message):
        """Add a hash verification log entry"""
        log = cls.load_log()
        for entry in log:
            if entry.get("evidence_uuid") == evidence_uuid:
                if "hash_verification_log" not in entry:
                    entry["hash_verification_log"] = []
                entry["hash_verification_log"].append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "result": result,
                    "message": message
                })
                break
        
        with open(cls.LOG_FILE, "w") as f:
            json.dump(log, f, indent=4)
    
    @classmethod
    def update_storage_location(cls, evidence_uuid, new_location):
        """Update current storage location"""
        log = cls.load_log()
        for entry in log:
            if entry.get("evidence_uuid") == evidence_uuid:
                entry["current_location"] = new_location
                break
        
        with open(cls.LOG_FILE, "w") as f:
            json.dump(log, f, indent=4)
