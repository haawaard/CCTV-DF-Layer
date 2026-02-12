import hashlib
import json
import time
import os
from core.EvidenceLog import EvidenceLog

class ForensicHasher:

    @staticmethod
    def generate_hash(file_path, camera_id=None):
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        file_name = os.path.basename(file_path)
        
        # Auto-generate camera ID if not provided
        if not camera_id:
            camera_id = EvidenceLog.generate_camera_id()

        existing_entry = EvidenceLog.find_entry(file_name, camera_id)
        event_type = "CREATE" if existing_entry is None else "MODIFY"

        previous_hash = EvidenceLog.get_last_hash()
        
        # Generate evidence UUID for new entries
        evidence_uuid = existing_entry.get("evidence_uuid") if existing_entry else EvidenceLog.generate_evidence_uuid()
        
        # Chain of custody fields
        original_location = existing_entry.get("original_location", file_path) if existing_entry else file_path

        context = {
            "evidence_uuid": evidence_uuid,
            "file_name": file_name,
            "file_size": len(file_bytes),
            "camera_id": camera_id,
            "event_type": event_type,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "previous_hash": previous_hash,
            "original_location": original_location,
            "current_location": file_path,
            "access_log": existing_entry.get("access_log", []) if existing_entry else [],
            "hash_verification_log": existing_entry.get("hash_verification_log", []) if existing_entry else []
        }

        combined_data = file_bytes + json.dumps(context, sort_keys=True).encode()
        hash_value = hashlib.sha256(combined_data).hexdigest()

        return hash_value, context, camera_id
