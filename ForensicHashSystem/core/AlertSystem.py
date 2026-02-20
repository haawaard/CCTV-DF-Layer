"""
Alert System - Tamper Detection and Anomaly Monitoring
Implements real-time alerting for integrity violations and suspicious activities
"""

import time
from enum import Enum


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertType(Enum):
    """Types of forensic alerts"""
    INTEGRITY_FAILURE = "Integrity Verification Failed"
    FILE_MODIFIED = "File Modified"
    FILE_DELETED = "File Deleted"
    HASH_CHAIN_BROKEN = "Hash Chain Broken"
    UNAUTHORIZED_ACCESS = "Unauthorized Access"
    SYSTEM_ERROR = "System Error"


class Alert:
    """Individual alert object"""
    
    def __init__(self, alert_type, severity, message, evidence_uuid=None, details=None):
        self.alert_type = alert_type
        self.severity = severity
        self.message = message
        self.evidence_uuid = evidence_uuid
        self.details = details or {}
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.acknowledged = False
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "type": self.alert_type.value if isinstance(self.alert_type, AlertType) else str(self.alert_type),
            "severity": self.severity.value if isinstance(self.severity, AlertSeverity) else str(self.severity),
            "message": self.message,
            "evidence_uuid": self.evidence_uuid,
            "details": self.details,
            "acknowledged": self.acknowledged
        }


class AlertSystem:
    """
    Central alert management system for CCTV-DF Layer
    Provides real-time alert generation and tracking
    """
    
    _instance = None
    _alerts = []
    _max_alerts = 1000
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AlertSystem, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def create_alert(cls, alert_type, severity, message, evidence_uuid=None, details=None):
        """Create and store a new alert"""
        alert = Alert(alert_type, severity, message, evidence_uuid, details)
        cls._alerts.insert(0, alert)  # Add to beginning
        
        # Limit alert history
        if len(cls._alerts) > cls._max_alerts:
            cls._alerts = cls._alerts[:cls._max_alerts]
        
        # Print to console for monitoring
        severity_symbol = "🔴" if severity == AlertSeverity.CRITICAL else "⚠️" if severity == AlertSeverity.WARNING else "ℹ️"
        print(f"[ALERT] {severity_symbol} {alert.timestamp} - {alert.message}")
        
        return alert
    
    @classmethod
    def get_alerts(cls, limit=None, unacknowledged_only=False):
        """Get alerts with optional filtering"""
        alerts = cls._alerts
        
        if unacknowledged_only:
            alerts = [a for a in alerts if not a.acknowledged]
        
        if limit:
            alerts = alerts[:limit]
        
        return alerts
    
    @classmethod
    def get_alert_count(cls, severity=None, unacknowledged_only=False):
        """Get count of alerts"""
        alerts = cls._alerts
        
        if unacknowledged_only:
            alerts = [a for a in alerts if not a.acknowledged]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return len(alerts)
    
    @classmethod
    def acknowledge_alert(cls, index):
        """Mark an alert as acknowledged"""
        if 0 <= index < len(cls._alerts):
            cls._alerts[index].acknowledged = True
    
    @classmethod
    def clear_alerts(cls):
        """Clear all alerts"""
        cls._alerts = []
    
    @classmethod
    def get_statistics(cls):
        """Get alert statistics"""
        return {
            "total": len(cls._alerts),
            "critical": cls.get_alert_count(AlertSeverity.CRITICAL),
            "warning": cls.get_alert_count(AlertSeverity.WARNING),
            "info": cls.get_alert_count(AlertSeverity.INFO),
            "unacknowledged": cls.get_alert_count(unacknowledged_only=True)
        }
