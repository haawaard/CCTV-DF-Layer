import hashlib
import json
import os
from core.EvidenceLog import EvidenceLog

class ForensicVerifier:

    @staticmethod
    def verify(file_path, camera_id=None):
        file_name = os.path.basename(file_path)
        
        # Load all log entries
        log = EvidenceLog.load_log()
        
        # Try to find entry by camera_id, or search for file_name if camera_id not provided
        if camera_id:
            entry = EvidenceLog.find_entry(file_name, camera_id)
        else:
            # Search for the most recent entry with this file name
            entry = None
            for e in reversed(log):
                if e.get("file_name") == file_name:
                    entry = e
                    break

        if entry is None:
            return False, "No matching log entry found.", None

        # Find the original CREATE entry for comparison
        original_entry = None
        for e in log:
            if e.get("file_name") == file_name and e.get("event_type") == "CREATE":
                original_entry = e
                break

        file_size = os.path.getsize(file_path)

        # Calculate current file hash
        hash_data = f"{file_name}{file_size}".encode()
        current_hash = hashlib.sha256(hash_data).hexdigest()
        
        evidence_uuid = entry.get("evidence_uuid")
        event_type = entry.get("event_type")

        # Check against the most recent entry
        stored_hash = entry["hash"]
        
        if stored_hash == current_hash:
            # Hash matches the recorded entry
            if event_type == "MODIFY":
                # Check if it matches the original
                if original_entry and original_entry["hash"] != current_hash:
                    message = "⚠️ WARNING: File was MODIFIED from original. Current state matches last recorded modification, but differs from original evidence."
                    result = "PASSED_MODIFIED"
                else:
                    message = "Integrity verified. File matches recorded MODIFY event."
                    result = "PASSED"
            else:
                message = "✓ Integrity verified. File is ORIGINAL and unmodified."
                result = "PASSED"
            
            # Log successful verification
            if evidence_uuid:
                EvidenceLog.add_verification_log_entry(
                    evidence_uuid,
                    result,
                    message
                )
                EvidenceLog.add_access_log_entry(
                    evidence_uuid,
                    "System",
                    "Verification performed"
                )
            return True, message, evidence_uuid
        else:
            # Hash doesn't match - file was tampered with
            message = "❌ TAMPERING DETECTED: File hash does not match any recorded value. File may have been altered outside the evidence system."
            if evidence_uuid:
                EvidenceLog.add_verification_log_entry(
                    evidence_uuid,
                    "FAILED",
                    message
                )
                EvidenceLog.add_access_log_entry(
                    evidence_uuid,
                    "System",
                    "Failed verification attempt - tampering detected"
                )
            return False, message, evidence_uuid
