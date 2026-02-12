import tkinter as tk
from tkinter import ttk, messagebox
from core.EvidenceLog import EvidenceLog
import json
import os

class EvidenceLogViewer:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Evidence Log Viewer - Chain of Custody")
        self.window.geometry("1400x600")
        self.window.resizable(True, True)
        
        # Configure style for buttons
        style = ttk.Style()
        style.configure(
            "Danger.TButton",
            background="#C73E4F",
            foreground="#ffffff",
            padding=8,
            font=("Segoe UI", 10, "bold")
        )

        self.build_table()
        self.load_data()

    def build_table(self):
        # Top button frame
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        ttk.Button(
            button_frame,
            text="🗑️ Clear All Evidence Logs",
            command=self.clear_all_logs,
            style="Danger.TButton"
        ).pack(side="right")
        
        # Main container with scrollbars
        container = ttk.Frame(self.window)
        container.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = (
            "evidence_uuid",
            "file_name",
            "camera_id",
            "event_type",
            "timestamp",
            "file_size",
            "hash",
            "original_location",
            "current_location",
            "access_log",
            "verification_log"
        )

        self.tree = ttk.Treeview(
            container,
            columns=columns,
            show="headings"
        )

        # Configure column headings and widths
        self.tree.heading("evidence_uuid", text="Evidence UUID")
        self.tree.heading("file_name", text="File Name")
        self.tree.heading("camera_id", text="Camera ID")
        self.tree.heading("event_type", text="Event")
        self.tree.heading("timestamp", text="Timestamp")
        self.tree.heading("file_size", text="Size (bytes)")
        self.tree.heading("hash", text="SHA-256 Hash")
        self.tree.heading("original_location", text="Original Location")
        self.tree.heading("current_location", text="Current Location")
        self.tree.heading("access_log", text="Access Log")
        self.tree.heading("verification_log", text="Hash Verification Log")

        self.tree.column("evidence_uuid", width=120)
        self.tree.column("file_name", width=160)
        self.tree.column("camera_id", width=90)
        self.tree.column("event_type", width=70)
        self.tree.column("timestamp", width=140)
        self.tree.column("file_size", width=90, anchor="e")
        self.tree.column("hash", width=220)
        self.tree.column("original_location", width=200)
        self.tree.column("current_location", width=200)
        self.tree.column("access_log", width=120)
        self.tree.column("verification_log", width=140)

        # Add both vertical and horizontal scrollbars
        vsb = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout for scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Add double-click event to view details
        self.tree.bind("<Double-1>", self.show_details)
        
        # Add info label
        info_label = ttk.Label(
            self.window,
            text="Double-click on any row to view detailed access and verification logs",
            font=("Segoe UI", 9, "italic")
        )
        info_label.pack(pady=(0, 5))

    def load_data(self):
        log_entries = EvidenceLog.load_log()

        for entry in log_entries:
            # Format access log count
            access_log = entry.get("access_log", [])
            access_log_text = f"{len(access_log)} entries" if access_log else "None"
            
            # Format verification log count
            verification_log = entry.get("hash_verification_log", [])
            verification_log_text = f"{len(verification_log)} checks" if verification_log else "None"
            
            self.tree.insert(
                "",
                "end",
                values=(
                    entry.get("evidence_uuid", "N/A")[:8] + "...",  # Truncated UUID
                    entry.get("file_name", "N/A"),
                    entry.get("camera_id", "N/A"),
                    entry.get("event_type", "N/A"),
                    entry.get("timestamp", "N/A"),
                    entry.get("file_size", "N/A"),
                    entry.get("hash", "N/A")[:20] + "...",  # Truncated hash
                    self.truncate_path(entry.get("original_location", "N/A")),
                    self.truncate_path(entry.get("current_location", "N/A")),
                    access_log_text,
                    verification_log_text
                ),
                tags=(entry.get("evidence_uuid"),)  # Store UUID in tags for reference
            )
    
    def truncate_path(self, path, max_length=30):
        """Truncate long file paths for display"""
        if len(path) <= max_length:
            return path
        return "..." + path[-(max_length-3):]
    
    def show_details(self, event):
        """Show detailed information for selected entry"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        tags = item.get("tags", [])
        
        if not tags:
            return
        
        evidence_uuid = tags[0]
        entry = EvidenceLog.find_entry_by_uuid(evidence_uuid)
        
        if not entry:
            messagebox.showerror("Error", "Entry not found")
            return
        
        # Create detail window
        detail_window = tk.Toplevel(self.window)
        detail_window.title(f"Evidence Details - {entry.get('file_name')}")
        detail_window.geometry("800x600")
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(detail_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap="word", font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Format and display entry details
        details = f"""EVIDENCE CHAIN OF CUSTODY DETAILS
{'='*80}

Evidence UUID: {entry.get('evidence_uuid', 'N/A')}
File Name: {entry.get('file_name', 'N/A')}
Camera ID: {entry.get('camera_id', 'N/A')}
Event Type: {entry.get('event_type', 'N/A')}
Timestamp: {entry.get('timestamp', 'N/A')}
File Size: {entry.get('file_size', 'N/A')} bytes

LOCATION INFORMATION:
{'-'*80}
Original Location: {entry.get('original_location', 'N/A')}
Current Location: {entry.get('current_location', 'N/A')}

HASH INFORMATION:
{'-'*80}
SHA-256 Hash: {entry.get('hash', 'N/A')}
Previous Hash: {entry.get('previous_hash', 'N/A')}

ACCESS LOG:
{'-'*80}
"""
        
        access_log = entry.get('access_log', [])
        if access_log:
            for idx, log in enumerate(access_log, 1):
                details += f"  {idx}. [{log.get('timestamp')}] {log.get('user')} - {log.get('action')}\n"
        else:
            details += "  No access log entries\n"
        
        details += f"\nHASH VERIFICATION LOG:\n{'-'*80}\n"
        
        verification_log = entry.get('hash_verification_log', [])
        if verification_log:
            for idx, log in enumerate(verification_log, 1):
                result_symbol = "✓" if log.get('result') == "PASSED" else "✗"
                details += f"  {idx}. [{log.get('timestamp')}] {result_symbol} {log.get('result')} - {log.get('message')}\n"
        else:
            details += "  No verification log entries\n"
        
        text_widget.insert("1.0", details)
        text_widget.configure(state="disabled")
    
    def clear_all_logs(self):
        """Clear all evidence logs and reset the system"""
        result = messagebox.askyesno(
            "Confirm Clear All",
            "⚠️ WARNING: This will permanently delete ALL evidence logs and reset the camera counter.\n\n"
            "This action cannot be undone!\n\n"
            "Are you sure you want to proceed?",
            icon="warning"
        )
        
        if not result:
            return
        
        # Double confirmation for safety
        result2 = messagebox.askyesno(
            "Final Confirmation",
            "This is your last chance to cancel.\n\n"
            "Delete ALL evidence logs?",
            icon="warning"
        )
        
        if not result2:
            return
        
        try:
            # Delete evidence log file
            if os.path.exists(EvidenceLog.LOG_FILE):
                os.remove(EvidenceLog.LOG_FILE)
            
            # Delete camera counter file
            if os.path.exists(EvidenceLog.CAMERA_COUNTER_FILE):
                os.remove(EvidenceLog.CAMERA_COUNTER_FILE)
            
            # Clear the tree view
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            messagebox.showinfo(
                "Success",
                "All evidence logs have been cleared and the system has been reset."
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to clear logs: {str(e)}"
            )
