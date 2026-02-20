"""
Forensic Dashboard - NIST SP 800-86 Analysis Phase
Real-time monitoring, alerting, and forensic analysis interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.AlertSystem import AlertSystem, AlertSeverity
from core.EvidenceLog import EvidenceLog
from core.FileSystemMonitor import FileSystemMonitor
from core.ForensicReportGenerator import ForensicReportGenerator
from core.Config import Config


class ForensicDashboard:
    """
    Main forensic monitoring dashboard
    Implements NIST Analysis Phase with real-time monitoring and alerting
    """
    
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("CCTV-DF Layer - Forensic Dashboard")
        self.window.geometry("1200x700")
        self.window.resizable(True, True)
        
        # Initialize monitoring
        self.monitor = FileSystemMonitor()
        self.config = Config.load_config()
        
        # Configure styles
        self.setup_styles()
        
        # Build UI
        self.build_dashboard()
        
        # Start refresh loop
        self.refresh_data()
    
    def setup_styles(self):
        """Setup custom styles for dashboard"""
        style = ttk.Style()
        
        style.configure("Dashboard.TFrame", background="#f0f0f0")
        style.configure("Card.TFrame", background="white", relief="raised")
        style.configure("Title.TLabel", font=("Segoe UI", 12, "bold"), background="white")
        style.configure("Stat.TLabel", font=("Segoe UI", 24, "bold"), background="white")
        style.configure("Info.TLabel", font=("Segoe UI", 9), background="white")
    
    def build_dashboard(self):
        """Build the main dashboard interface"""
        # Header
        header = ttk.Frame(self.window, style="Dashboard.TFrame")
        header.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(
            header,
            text="🔒 CCTV Digital Forensics Layer - Monitoring Dashboard",
            font=("Segoe UI", 16, "bold"),
            background="#f0f0f0"
        ).pack(side="left")
        
        ttk.Label(
            header,
            text="NIST SP 800-86 Framework",
            font=("Segoe UI", 9, "italic"),
            background="#f0f0f0"
        ).pack(side="right")
        
        # Main container
        main_container = ttk.Frame(self.window, style="Dashboard.TFrame")
        main_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Top section - Statistics Cards
        stats_frame = ttk.Frame(main_container, style="Dashboard.TFrame")
        stats_frame.pack(fill="x", pady=(0, 10))
        
        # Statistics cards
        self.create_stat_card(stats_frame, "Total Evidence", "0", 0)
        self.create_stat_card(stats_frame, "Critical Alerts", "0", 1)
        self.create_stat_card(stats_frame, "Monitoring", "OFF", 2)
        self.create_stat_card(stats_frame, "Hash Chain", "UNKNOWN", 3)
        
        # Middle section - Split view
        content_frame = ttk.Frame(main_container, style="Dashboard.TFrame")
        content_frame.pack(fill="both", expand=True)
        
        # Left panel - Alerts
        left_panel = ttk.Frame(content_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.build_alerts_panel(left_panel)
        
        # Right panel - Controls and Status
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.build_control_panel(right_panel)
    
    def create_stat_card(self, parent, title, value, column):
        """Create a statistics card"""
        card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        card.grid(row=0, column=column, padx=5, sticky="nsew")
        parent.columnconfigure(column, weight=1)
        
        ttk.Label(card, text=title, style="Info.TLabel").pack()
        
        # Store reference to value label
        value_label = ttk.Label(card, text=value, style="Stat.TLabel")
        value_label.pack(pady=5)
        
        # Store reference based on title
        if title == "Total Evidence":
            self.total_evidence_label = value_label
        elif title == "Critical Alerts":
            self.critical_alerts_label = value_label
        elif title == "Monitoring":
            self.monitoring_status_label = value_label
        elif title == "Hash Chain":
            self.chain_status_label = value_label
    
    def build_alerts_panel(self, parent):
        """Build the alerts monitoring panel"""
        panel = ttk.LabelFrame(parent, text="🚨 Real-Time Alerts", padding=10)
        panel.pack(fill="both", expand=True)
        
        # Alert controls
        control_frame = ttk.Frame(panel)
        control_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(
            control_frame,
            text="Clear Alerts",
            command=self.clear_alerts
        ).pack(side="left", padx=5)
        
        ttk.Button(
            control_frame,
            text="Refresh",
            command=self.refresh_alerts
        ).pack(side="left")
        
        # Alert list with scrollbar
        list_frame = ttk.Frame(panel)
        list_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.alerts_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 9),
            height=15
        )
        self.alerts_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.alerts_listbox.yview)
    
    def build_control_panel(self, parent):
        """Build the control and status panel"""
        # Monitoring Control
        monitor_frame = ttk.LabelFrame(parent, text="📁 Directory Monitoring", padding=10)
        monitor_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(monitor_frame, text="Monitored Directory:").pack(anchor="w")
        
        dir_frame = ttk.Frame(monitor_frame)
        dir_frame.pack(fill="x", pady=5)
        
        self.dir_var = tk.StringVar(value=self.config.get('monitored_directory', 'Not set'))
        ttk.Entry(dir_frame, textvariable=self.dir_var, state="readonly").pack(side="left", fill="x", expand=True)
        
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).pack(side="right", padx=(5, 0))
        
        # Monitor control buttons
        button_frame = ttk.Frame(monitor_frame)
        button_frame.pack(fill="x", pady=5)
        
        self.start_monitor_btn = ttk.Button(
            button_frame,
            text="▶ Start Monitoring",
            command=self.start_monitoring
        )
        self.start_monitor_btn.pack(side="left", padx=2)
        
        self.stop_monitor_btn = ttk.Button(
            button_frame,
            text="⏹ Stop Monitoring",
            command=self.stop_monitoring,
            state="disabled"
        )
        self.stop_monitor_btn.pack(side="left", padx=2)
        
        # Chain Verification
        chain_frame = ttk.LabelFrame(parent, text="🔗 Hash Chain Verification", padding=10)
        chain_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(
            chain_frame,
            text="Verify Hash Chain",
            command=self.verify_chain,
            width=20
        ).pack(pady=5)
        
        self.chain_result_label = ttk.Label(chain_frame, text="Not verified", wraplength=250)
        self.chain_result_label.pack(pady=5)
        
        # Report Generation
        report_frame = ttk.LabelFrame(parent, text="📄 Forensic Reports (NIST Reporting Phase)", padding=10)
        report_frame.pack(fill="x")
        
        ttk.Button(
            report_frame,
            text="Generate CSV Report",
            command=lambda: self.generate_report("csv"),
            width=20
        ).pack(pady=2)
        
        ttk.Button(
            report_frame,
            text="Generate Text Report",
            command=lambda: self.generate_report("text"),
            width=20
        ).pack(pady=2)
        
        ttk.Button(
            report_frame,
            text="Chain Verification Report",
            command=lambda: self.generate_report("chain"),
            width=20
        ).pack(pady=2)
    
    def browse_directory(self):
        """Browse for directory to monitor"""
        directory = filedialog.askdirectory(title="Select CCTV Storage Directory")
        if directory:
            self.dir_var.set(directory)
            Config.set('monitored_directory', directory)
            messagebox.showinfo("Success", f"Directory set: {directory}")
    
    def start_monitoring(self):
        """Start directory monitoring"""
        directory = self.dir_var.get()
        if not directory or directory == "Not set":
            messagebox.showerror("Error", "Please select a directory first")
            return
        
        try:
            self.monitor.start_monitoring(directory)
            self.start_monitor_btn.config(state="disabled")
            self.stop_monitor_btn.config(state="normal")
            messagebox.showinfo("Monitoring Started", f"Now monitoring: {directory}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitoring: {str(e)}")
    
    def stop_monitoring(self):
        """Stop directory monitoring"""
        self.monitor.stop_monitoring()
        self.start_monitor_btn.config(state="normal")
        self.stop_monitor_btn.config(state="disabled")
        messagebox.showinfo("Monitoring Stopped", "Directory monitoring has been stopped")
    
    def verify_chain(self):
        """Verify hash chain integrity"""
        valid, message, broken_links = EvidenceLog.verify_hash_chain()
        
        if valid:
            self.chain_result_label.config(text=f"✓ {message}", foreground="green")
            messagebox.showinfo("Chain Valid", message)
        else:
            self.chain_result_label.config(text=f"✗ {message}", foreground="red")
            details = f"{message}\n\nBroken at {len(broken_links)} location(s)"
            messagebox.showwarning("Chain Broken", details)
    
    def generate_report(self, report_type):
        """Generate forensic report"""
        if report_type == "csv":
            success, message = ForensicReportGenerator.generate_csv_report()
        elif report_type == "text":
            success, message = ForensicReportGenerator.generate_text_report()
        elif report_type == "chain":
            success, message = ForensicReportGenerator.generate_chain_verification_report()
        else:
            success, message = False, "Unknown report type"
        
        if success:
            messagebox.showinfo("Report Generated", message)
        else:
            messagebox.showerror("Report Error", message)
    
    def refresh_alerts(self):
        """Refresh alerts display"""
        self.alerts_listbox.delete(0, tk.END)
        
        alerts = AlertSystem.get_alerts(limit=50)
        
        if not alerts:
            self.alerts_listbox.insert(tk.END, "No alerts")
            return
        
        for alert in alerts:
            severity_icon = "🔴" if alert.severity == AlertSeverity.CRITICAL else "⚠️" if alert.severity == AlertSeverity.WARNING else "ℹ️"
            alert_text = f"{severity_icon} [{alert.timestamp}] {alert.message}"
            self.alerts_listbox.insert(tk.END, alert_text)
    
    def clear_alerts(self):
        """Clear all alerts"""
        result = messagebox.askyesno("Clear Alerts", "Clear all alerts?")
        if result:
            AlertSystem.clear_alerts()
            self.refresh_alerts()
    
    def refresh_data(self):
        """Refresh dashboard data"""
        # Update statistics
        stats = EvidenceLog.get_chain_statistics()
        alert_stats = AlertSystem.get_statistics()
        
        self.total_evidence_label.config(text=str(stats['total_entries']))
        self.critical_alerts_label.config(text=str(alert_stats['critical']))
        
        # Monitoring status
        if self.monitor.is_monitoring:
            self.monitoring_status_label.config(text="ON", foreground="green")
        else:
            self.monitoring_status_label.config(text="OFF", foreground="red")
        
        # Chain status
        if stats['chain_valid']:
            self.chain_status_label.config(text="VALID", foreground="green")
        else:
            self.chain_status_label.config(text="BROKEN", foreground="red")
        
        # Refresh alerts
        self.refresh_alerts()
        
        # Schedule next refresh
        self.window.after(2000, self.refresh_data)
