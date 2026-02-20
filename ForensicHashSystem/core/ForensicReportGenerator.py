"""
Forensic Report Generator - NIST SP 800-86 Reporting Phase
Generates authenticated forensic reports in PDF and CSV formats
"""

import csv
import json
import time
from core.EvidenceLog import EvidenceLog


class ForensicReportGenerator:
    """
    Generates forensic reports for evidence documentation and legal proceedings
    Implements NIST Reporting Phase requirements
    """
    
    @staticmethod
    def generate_csv_report(output_path="forensic_report.csv"):
        """Generate CSV export of evidence log"""
        log_entries = EvidenceLog.load_log()
        
        if not log_entries:
            return False, "No evidence entries to export"
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                # Define CSV columns
                fieldnames = [
                    'Evidence UUID', 'File Name', 'Camera ID', 'Event Type',
                    'Timestamp', 'File Size (bytes)', 'SHA-256 Hash',
                    'Previous Hash', 'Original Location', 'Current Location',
                    'Access Log Count', 'Verification Log Count'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for entry in log_entries:
                    writer.writerow({
                        'Evidence UUID': entry.get('evidence_uuid', 'N/A'),
                        'File Name': entry.get('file_name', 'N/A'),
                        'Camera ID': entry.get('camera_id', 'N/A'),
                        'Event Type': entry.get('event_type', 'N/A'),
                        'Timestamp': entry.get('timestamp', 'N/A'),
                        'File Size (bytes)': entry.get('file_size', 'N/A'),
                        'SHA-256 Hash': entry.get('hash', 'N/A'),
                        'Previous Hash': entry.get('previous_hash', 'N/A')[:16] + '...' if entry.get('previous_hash') else 'None',
                        'Original Location': entry.get('original_location', 'N/A'),
                        'Current Location': entry.get('current_location', 'N/A'),
                        'Access Log Count': len(entry.get('access_log', [])),
                        'Verification Log Count': len(entry.get('hash_verification_log', []))
                    })
            
            return True, f"CSV report generated: {output_path}"
        
        except Exception as e:
            return False, f"Failed to generate CSV: {str(e)}"
    
    @staticmethod
    def generate_text_report(output_path="forensic_report.txt"):
        """Generate detailed text report"""
        log_entries = EvidenceLog.load_log()
        stats = EvidenceLog.get_chain_statistics()
        
        if not log_entries:
            return False, "No evidence entries to export"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # Header
                f.write("="*80 + "\n")
                f.write("CCTV DIGITAL FORENSICS (CCTV-DF) LAYER - FORENSIC REPORT\n")
                f.write("="*80 + "\n")
                f.write(f"Report Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Report Type: Evidence Chain Analysis\n")
                f.write(f"Framework: NIST SP 800-86\n\n")
                
                # Chain Statistics
                f.write("EVIDENCE CHAIN STATISTICS\n")
                f.write("-"*80 + "\n")
                f.write(f"Total Entries: {stats['total_entries']}\n")
                f.write(f"CREATE Events: {stats['create_events']}\n")
                f.write(f"MODIFY Events: {stats['modify_events']}\n")
                f.write(f"DELETE Events: {stats['delete_events']}\n")
                f.write(f"First Entry: {stats.get('first_entry', 'N/A')}\n")
                f.write(f"Last Entry: {stats.get('last_entry', 'N/A')}\n")
                f.write(f"Hash Chain Status: {'VALID' if stats['chain_valid'] else 'BROKEN'}\n")
                f.write(f"Chain Message: {stats['chain_message']}\n\n")
                
                # Evidence Entries
                f.write("EVIDENCE ENTRIES\n")
                f.write("="*80 + "\n\n")
                
                for idx, entry in enumerate(log_entries, 1):
                    f.write(f"Entry #{idx}\n")
                    f.write("-"*80 + "\n")
                    f.write(f"Evidence UUID: {entry.get('evidence_uuid', 'N/A')}\n")
                    f.write(f"File Name: {entry.get('file_name', 'N/A')}\n")
                    f.write(f"Camera ID: {entry.get('camera_id', 'N/A')}\n")
                    f.write(f"Event Type: {entry.get('event_type', 'N/A')}\n")
                    f.write(f"Timestamp: {entry.get('timestamp', 'N/A')}\n")
                    f.write(f"File Size: {entry.get('file_size', 'N/A')} bytes\n")
                    f.write(f"SHA-256 Hash: {entry.get('hash', 'N/A')}\n")
                    f.write(f"Previous Hash: {entry.get('previous_hash', 'None')}\n")
                    f.write(f"Original Location: {entry.get('original_location', 'N/A')}\n")
                    f.write(f"Current Location: {entry.get('current_location', 'N/A')}\n")
                    
                    # Access Log
                    access_log = entry.get('access_log', [])
                    f.write(f"\nAccess Log ({len(access_log)} entries):\n")
                    if access_log:
                        for log in access_log:
                            f.write(f"  - [{log.get('timestamp')}] {log.get('user')}: {log.get('action')}\n")
                    else:
                        f.write("  No access log entries\n")
                    
                    # Verification Log
                    verification_log = entry.get('hash_verification_log', [])
                    f.write(f"\nVerification Log ({len(verification_log)} checks):\n")
                    if verification_log:
                        for log in verification_log:
                            result = "✓" if log.get('result') == 'PASSED' else "✗"
                            f.write(f"  {result} [{log.get('timestamp')}] {log.get('result')}: {log.get('message')}\n")
                    else:
                        f.write("  No verification log entries\n")
                    
                    f.write("\n")
                
                # Footer
                f.write("="*80 + "\n")
                f.write("END OF REPORT\n")
                f.write("="*80 + "\n")
            
            return True, f"Text report generated: {output_path}"
        
        except Exception as e:
            return False, f"Failed to generate text report: {str(e)}"
    
    @staticmethod
    def generate_chain_verification_report(output_path="chain_verification.txt"):
        """Generate hash chain verification report"""
        valid, message, broken_links = EvidenceLog.verify_hash_chain()
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("HASH CHAIN VERIFICATION REPORT\n")
                f.write("="*80 + "\n")
                f.write(f"Verification Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Status: {'VALID' if valid else 'BROKEN'}\n")
                f.write(f"Message: {message}\n\n")
                
                if not valid and broken_links:
                    f.write("BROKEN CHAIN LINKS DETECTED\n")
                    f.write("-"*80 + "\n")
                    for link in broken_links:
                        f.write(f"Position: {link['position']}\n")
                        f.write(f"Evidence UUID: {link['evidence_uuid']}\n")
                        f.write(f"File Name: {link['file_name']}\n")
                        f.write(f"Timestamp: {link['timestamp']}\n\n")
                
                f.write("="*80 + "\n")
            
            return True, f"Chain verification report: {output_path}"
        
        except Exception as e:
            return False, f"Failed to generate verification report: {str(e)}"
