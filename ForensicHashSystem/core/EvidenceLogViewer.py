import tkinter as tk
from tkinter import ttk
from core.EvidenceLog import EvidenceLog

class EvidenceLogViewer:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Evidence Log Viewer")
        self.window.geometry("900x420")
        self.window.resizable(True, True)

        self.build_table()
        self.load_data()

    def build_table(self):
        columns = (
            "file_name",
            "camera_id",
            "event_type",
            "timestamp",
            "file_size",
            "hash"
        )

        self.tree = ttk.Treeview(
            self.window,
            columns=columns,
            show="headings"
        )

        self.tree.heading("file_name", text="File Name")
        self.tree.heading("camera_id", text="Camera ID")
        self.tree.heading("event_type", text="Event")
        self.tree.heading("timestamp", text="Timestamp")
        self.tree.heading("file_size", text="Size (bytes)")
        self.tree.heading("hash", text="SHA-256 Hash")

        self.tree.column("file_name", width=160)
        self.tree.column("camera_id", width=90)
        self.tree.column("event_type", width=80)
        self.tree.column("timestamp", width=140)
        self.tree.column("file_size", width=90, anchor="e")
        self.tree.column("hash", width=260)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(
            self.window,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def load_data(self):
        log_entries = EvidenceLog.load_log()

        for entry in log_entries:
            self.tree.insert(
                "",
                "end",
                values=(
                    entry.get("file_name"),
                    entry.get("camera_id"),
                    entry.get("event_type"),
                    entry.get("timestamp"),
                    entry.get("file_size"),
                    entry.get("hash")[:24] + "..."  # truncate for readability
                )
            )
