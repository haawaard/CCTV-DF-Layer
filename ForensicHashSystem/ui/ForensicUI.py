import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core.ForensicHasher import ForensicHasher
from core.EvidenceLog import EvidenceLog
from core.ForensicVerifier import ForensicVerifier
from core.EvidenceLogViewer import EvidenceLogViewer
import os

from PIL import Image, ImageTk
import cv2


class ForensicUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CCTV Digital Forensics Layer")

        # Windows
        window_width = 920
        window_height = 720

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)

        # Style setup
        style = ttk.Style()
        style.theme_use("clam")

        self.BG_COLOR = "#f4f6f8"
        self.PRIMARY = "#1A80C4"
        self.SUCCESS = "#2FA244"
        self.DANGER = "#C73E4F"
        self.TEXT_LIGHT = "#ffffff"

        self.root.configure(bg=self.BG_COLOR)

        style.configure("Main.TFrame", background=self.BG_COLOR)
        style.configure("TLabelframe", background=self.BG_COLOR)
        style.configure("TLabelframe.Label", background=self.BG_COLOR)

        style.configure(
            "Primary.TButton",
            background=self.PRIMARY,
            foreground=self.TEXT_LIGHT,
            padding=8,
            font=("Segoe UI", 10, "bold")
        )
        style.map("Primary.TButton", background=[("active", "#1A80C4")])

        style.configure(
            "Success.TButton",
            background=self.SUCCESS,
            foreground=self.TEXT_LIGHT,
            padding=8,
            font=("Segoe UI", 10, "bold")
        )
        style.map("Success.TButton", background=[("active", "#2FA244")])

        style.configure(
            "Danger.TButton",
            background=self.DANGER,
            foreground=self.TEXT_LIGHT,
            padding=8,
            font=("Segoe UI", 10, "bold")
        )
        style.map("Danger.TButton", background=[("active", "#C73E4F")])

        self.file_path = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready.")
        self.preview_image = None

        self.build_ui()

    # UI

    def build_ui(self):

        ttk.Label(
            self.root,
            text="CCTV Digital Forensics Layer",
            font=("Segoe UI", 15, "bold"),
            background=self.BG_COLOR
        ).pack(pady=12)

        main = ttk.Frame(self.root, padding=15, style="Main.TFrame")
        main.pack(fill="both", expand=True)

        # Evidence Details
        details_frame = ttk.LabelFrame(
            main,
            text="Evidence Details",
            padding=12
        )
        details_frame.pack(fill="both", expand=True, pady=6)

        file_row = ttk.Frame(details_frame, style="Main.TFrame")
        file_row.pack(fill="x", pady=(0, 10))

        ttk.Label(file_row, text="Evidence File:").pack(side="left")

        ttk.Entry(
            file_row,
            textvariable=self.file_path,
            state="readonly"
        ).pack(side="left", fill="x", expand=True, padx=8)

        ttk.Button(
            file_row,
            text="Browse",
            style="Primary.TButton",
            command=self.select_file
        ).pack(side="right")

        # Preview and Metadata
        content_row = ttk.Frame(details_frame, style="Main.TFrame")
        content_row.pack(fill="both", expand=True)

        # CCTV Preview
        preview_container = ttk.LabelFrame(
            content_row,
            text="CCTV Preview",
            padding=10
        )
        preview_container.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.preview_label = ttk.Label(
            preview_container,
            text="No preview available",
            anchor="center"
        )
        self.preview_label.pack(expand=True)

        # Metadata
        meta_container = ttk.LabelFrame(
            content_row,
            text="Metadata",
            padding=10
        )
        meta_container.pack(side="right", fill="y")

        ttk.Label(meta_container, text="Camera ID:").pack(anchor="w")
        self.camera_entry = ttk.Entry(meta_container, width=25)
        self.camera_entry.pack(pady=6)

        # Action Buttons
        action_frame = ttk.Frame(main, style="Main.TFrame")
        action_frame.pack(pady=12)

        ttk.Button(
            action_frame,
            text="Acquire Evidence",
            width=22,
            style="Primary.TButton",
            command=self.generate_hash
        ).grid(row=0, column=0, padx=8)

        ttk.Button(
            action_frame,
            text="Verify Integrity",
            width=22,
            style="Success.TButton",
            command=self.verify_file
        ).grid(row=0, column=1, padx=8)

        ttk.Button(
            action_frame,
            text="View Evidence Log",
            width=22,
            style="Danger.TButton",
            command=lambda: EvidenceLogViewer(self.root)
        ).grid(row=1, column=0, columnspan=2, pady=6)

        # Result
        self.result_label = ttk.Label(
            main,
            text="",
            wraplength=600,
            font=("Segoe UI", 10, "bold"),
            background=self.BG_COLOR
        )
        self.result_label.pack(pady=6)

        # Status Bar
        ttk.Label(
            self.root,
            textvariable=self.status_text,
            relief="sunken",
            anchor="w",
            padding=6
        ).pack(side="bottom", fill="x")

    # Functions

    def select_file(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Media Files", "*.jpg *.jpeg *.png *.mp4 *.avi"),
                ("All Files", "*.*")
            ]
        )

        if path:
            self.file_path.set(path)
            self.status_text.set(f"Selected: {os.path.basename(path)}")
            self.load_preview(path)

    def load_preview(self, path):
        try:
            ext = os.path.splitext(path)[1].lower()

            if ext in [".jpg", ".jpeg", ".png"]:
                image = Image.open(path)

            elif ext in [".mp4", ".avi"]:
                cap = cv2.VideoCapture(path)
                success, frame = cap.read()
                cap.release()

                if not success:
                    raise RuntimeError("Cannot read video")

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)

            else:
                self.preview_label.config(text="Unsupported format")
                return

            image.thumbnail((360, 200))
            self.preview_image = ImageTk.PhotoImage(image)
            self.preview_label.config(image=self.preview_image, text="")

        except Exception:
            self.preview_label.config(text="Preview unavailable")

    def generate_hash(self):
        if not self.file_path.get():
            messagebox.showerror("Missing File", "Please select an evidence file.")
            return

        camera_id = self.camera_entry.get().strip()
        if not camera_id:
            messagebox.showerror("Missing Camera ID", "Camera ID is required.")
            return

        hash_value, context = ForensicHasher.generate_hash(
            self.file_path.get(),
            camera_id
        )
        EvidenceLog.save_entry(context, hash_value)

        self.result_label.config(
            text="✔ Evidence acquired and securely logged.",
            foreground="green"
        )
        self.status_text.set("Evidence acquisition successful.")

    def verify_file(self):
        if not self.file_path.get():
            messagebox.showerror("Missing File", "Please select an evidence file.")
            return

        is_valid, message = ForensicVerifier.verify(
            self.file_path.get(),
            self.camera_entry.get().strip()
        )

        if is_valid:
            self.result_label.config(text=f"✔ {message}", foreground="green")
            self.status_text.set("Verification successful.")
        else:
            self.result_label.config(text=f"✖ {message}", foreground="red")
            self.status_text.set("Verification failed.")


if __name__ == "__main__":
    root = tk.Tk()
    ForensicUI(root)
    root.mainloop()
