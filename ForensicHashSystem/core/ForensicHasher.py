import hashlib
import json
import time
import os
from core.EvidenceLog import EvidenceLog

class ForensicHasher:

    @staticmethod
    def generate_hash(file_path, camera_id):
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        file_name = os.path.basename(file_path)

        existing_entry = EvidenceLog.find_entry(file_name, camera_id)
        event_type = "CREATE" if existing_entry is None else "MODIFY"

        previous_hash = EvidenceLog.get_last_hash()

        context = {
            "file_name": file_name,
            "file_size": len(file_bytes),
            "camera_id": camera_id,
            "event_type": event_type,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "previous_hash": previous_hash
        }

        combined_data = file_bytes + json.dumps(context, sort_keys=True).encode()
        hash_value = hashlib.sha256(combined_data).hexdigest()

        return hash_value, context
