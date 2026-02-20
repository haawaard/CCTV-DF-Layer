"""
File System Monitor - NIST SP 800-86 Collection Phase
Continuously monitors CCTV storage directories for file creation, modification, and deletion events.
Implements automated evidence acquisition and forensic logging.
"""

import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.EvidenceLog import EvidenceLog
from core.ForensicHasher import ForensicHasher


class CCTVFileHandler(FileSystemEventHandler):
    """
    Handles file system events in monitored CCTV directory
    Implements NIST Collection Phase requirements
    """
    
    def __init__(self, auto_hash=True, file_extensions=None):
        self.auto_hash = auto_hash
        self.file_extensions = file_extensions or ['.mp4', '.avi', '.mkv', '.mov', '.jpg', '.jpeg', '.png']
        self.processing_files = set()
    
    def is_valid_file(self, file_path):
        """Check if file should be monitored based on extension"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.file_extensions
    
    def on_created(self, event):
        """Handle file creation events - NIST Collection Phase"""
        if event.is_directory:
            return
        
        if not self.is_valid_file(event.src_path):
            return
        
        # Wait for file to be completely written
        time.sleep(1)
        
        if event.src_path in self.processing_files:
            return
        
        self.processing_files.add(event.src_path)
        
        try:
            # Automatically acquire evidence
            if self.auto_hash and os.path.exists(event.src_path):
                print(f"[COLLECTION] New file detected: {os.path.basename(event.src_path)}")
                hash_value, context, camera_id = ForensicHasher.generate_hash(event.src_path)
                EvidenceLog.save_entry(context, hash_value)
                print(f"[COLLECTION] Evidence acquired: {camera_id}")
                
                # Log access event
                EvidenceLog.add_access_log_entry(
                    context['evidence_uuid'],
                    "System",
                    "Automatic acquisition - File created"
                )
        except Exception as e:
            print(f"[ERROR] Failed to process file: {e}")
        finally:
            self.processing_files.discard(event.src_path)
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
        
        if not self.is_valid_file(event.src_path):
            return
        
        # Log modification detection
        file_name = os.path.basename(event.src_path)
        existing = EvidenceLog.find_entry_by_filename(file_name)
        
        if existing:
            print(f"[ALERT] ⚠️ File modified: {file_name}")
            # Log the modification event
            EvidenceLog.add_access_log_entry(
                existing['evidence_uuid'],
                "System",
                "File modification detected"
            )
    
    def on_deleted(self, event):
        """Handle file deletion events - Track deletion"""
        if event.is_directory:
            return
        
        if not self.is_valid_file(event.src_path):
            return
        
        file_name = os.path.basename(event.src_path)
        existing = EvidenceLog.find_entry_by_filename(file_name)
        
        if existing:
            print(f"[ALERT] ⚠️ File deleted: {file_name}")
            
            # Log deletion event
            deletion_context = {
                "event_type": "DELETE",
                "file_name": file_name,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "evidence_uuid": existing['evidence_uuid'],
                "camera_id": existing['camera_id'],
                "file_size": existing.get('file_size', 0),
                "previous_hash": EvidenceLog.get_last_hash(),
                "original_location": existing.get('original_location', ''),
                "current_location": "DELETED",
                "access_log": existing.get('access_log', []),
                "hash_verification_log": existing.get('hash_verification_log', [])
            }
            
            # Save deletion event
            EvidenceLog.save_entry(deletion_context, existing['hash'])
            
            # Log access
            EvidenceLog.add_access_log_entry(
                existing['evidence_uuid'],
                "System",
                "File deletion detected"
            )


class FileSystemMonitor:
    """
    Main file system monitoring service for CCTV-DF Layer
    Implements continuous surveillance of evidence directories
    """
    
    def __init__(self, watch_directory=None, auto_hash=True):
        self.watch_directory = watch_directory
        self.auto_hash = auto_hash
        self.observer = None
        self.event_handler = None
        self.is_monitoring = False
    
    def start_monitoring(self, watch_directory=None):
        """Start monitoring the specified directory"""
        if watch_directory:
            self.watch_directory = watch_directory
        
        if not self.watch_directory or not os.path.exists(self.watch_directory):
            raise ValueError(f"Invalid watch directory: {self.watch_directory}")
        
        self.event_handler = CCTVFileHandler(auto_hash=self.auto_hash)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.watch_directory, recursive=False)
        self.observer.start()
        self.is_monitoring = True
        
        print(f"[MONITOR] Started monitoring: {self.watch_directory}")
        print(f"[MONITOR] Auto-hash enabled: {self.auto_hash}")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.is_monitoring = False
            print("[MONITOR] Monitoring stopped")
    
    def get_status(self):
        """Get monitoring status"""
        return {
            "is_monitoring": self.is_monitoring,
            "watch_directory": self.watch_directory,
            "auto_hash": self.auto_hash
        }
