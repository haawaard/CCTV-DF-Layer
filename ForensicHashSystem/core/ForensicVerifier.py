import hashlib
import json
import os
from core.EvidenceLog import EvidenceLog

class ForensicVerifier:

    @staticmethod
    def verify(file_path, camera_id):
        file_name = os.path.basename(file_path)
        entry = EvidenceLog.find_entry(file_name, camera_id)

        if entry is None:
            return False, "No matching log entry found."

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        stored_hash = entry["hash"]
        context = entry.copy()
        context.pop("hash")

        combined_data = file_bytes + json.dumps(context, sort_keys=True).encode()
        recalculated_hash = hashlib.sha256(combined_data).hexdigest()

        if stored_hash == recalculated_hash:
            return True, "Integrity verified. No tampering detected."
        else:
            return False, "Integrity failed. Evidence may be tampered."
