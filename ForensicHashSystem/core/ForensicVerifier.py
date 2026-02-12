import hashlib
import json
import os
from core.EvidenceLog import EvidenceLog

class ForensicVerifier:

    @staticmethod
    def verify(file_path, camera_id=None):
        file_name = os.path.basename(file_path)
        
        # Try to find entry by camera_id, or search for file_name if camera_id not provided
        if camera_id:
            entry = EvidenceLog.find_entry(file_name, camera_id)
        else:
            # Search for any entry with this file name
            log = EvidenceLog.load_log()
            entry = None
            for e in reversed(log):
                if e.get("file_name") == file_name:
                    entry = e
                    break

        if entry is None:
            return False, "No matching log entry found.", None

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        stored_hash = entry["hash"]
        context = entry.copy()
        context.pop("hash")

        combined_data = file_bytes + json.dumps(context, sort_keys=True).encode()
        recalculated_hash = hashlib.sha256(combined_data).hexdigest()
        
        evidence_uuid = entry.get("evidence_uuid")

        if stored_hash == recalculated_hash:
            # Log successful verification
            if evidence_uuid:
                EvidenceLog.add_verification_log_entry(
                    evidence_uuid,
                    "PASSED",
                    "Integrity verified. Hash matches recorded value."
                )
                EvidenceLog.add_access_log_entry(
                    evidence_uuid,
                    "System",
                    "Verification performed"
                )
            return True, "Integrity verified. Hash matches recorded value.", evidence_uuid
        else:
            # Log failed verification
            if evidence_uuid:
                EvidenceLog.add_verification_log_entry(
                    evidence_uuid,
                    "FAILED",
                    "Integrity check failed. Hash does not match recorded value."
                )
                EvidenceLog.add_access_log_entry(
                    evidence_uuid,
                    "System",
                    "Failed verification attempt"
                )
            return False, "Integrity check failed. Hash does not match recorded value.", evidence_uuid
