"""
SAP Compliance Monitoring Dashboard
Real-time ethical violation tracking and analytics
"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import json
from collections import defaultdict


class ComplianceDashboard:
    """
    Real-time monitoring of ethical compliance metrics
    Tracks violations, patterns, and system health
    """
    
    def __init__(self):
        self.violations_log = []
        self.session_metrics = defaultdict(lambda: {
            "total_requests": 0,
            "blocked_requests": 0,
            "violations_by_rule": defaultdict(int),
            "start_time": datetime.utcnow(),
            "end_time": None
        })
        self.global_stats = {
            "total_validations": 0,
            "total_violations": 0,
            "approval_rate": 100.0,
            "violation_patterns": defaultdict(int)
        }
    
    def log_violation(self, violation_data: Dict):
        """Log an ethical violation"""
        violation_record = {
            **violation_data,
            "timestamp": datetime.utcnow().isoformat(),
            "severity_level": self._map_severity_to_level(violation_data.get("severity"))
        }
        
        self.violations_log.append(violation_record)
        
        # Update global stats
        self.global_stats["total_violations"] += 1
        rule_id = violation_data.get("rule_id", "UNKNOWN")
        self.global_stats["violation_patterns"][rule_id] += 1
    
    def start_session(self, session_id: str):
        """Start tracking a new validation session"""
        self.session_metrics[session_id]["start_time"] = datetime.utcnow()
    
    def end_session(self, session_id: str):
        """End tracking a validation session"""
        self.session_metrics[session_id]["end_time"] = datetime.utcnow()
    
    def record_validation(self, session_id: str, is_approved: bool, violations: List = None):
        """Record a validation result"""
        if session_id not in self.session_metrics:
            self.start_session(session_id)
        
        self.session_metrics[session_id]["total_requests"] += 1
        self.global_stats["total_validations"] += 1
        
        if not is_approved:
            self.session_metrics[session_id]["blocked_requests"] += 1
            
            # Track violations by rule
            if violations:
                for violation in violations:
                    rule_id = violation.get("rule_id", "UNKNOWN")
                    self.session_metrics[session_id]["violations_by_rule"][rule_id] += 1
                    self.log_violation(violation)
        
        # Update approval rate
        self._update_approval_rate()
    
    def _update_approval_rate(self):
        """Calculate current approval rate"""
        total = self.global_stats["total_validations"]
        violations = self.global_stats["total_violations"]
        
        if total > 0:
            self.global_stats["approval_rate"] = ((total - violations) / total * 100)
    
    def _map_severity_to_level(self, severity: str) -> int:
        """Map severity string to numeric level"""
        mapping = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }
        return mapping.get(severity, 0)
    
    def get_dashboard_data(self) -> Dict:
        """
        Get all dashboard data for frontend visualization
        """
        return {
            "global_metrics": self._get_global_metrics(),
            "violation_breakdown": self._get_violation_breakdown(),
            "timeline": self._get_violation_timeline(),
            "top_violations": self._get_top_violations(),
            "session_summary": self._get_session_summary()
        }
    
    def _get_global_metrics(self) -> Dict:
        """Global system metrics"""
        total = self.global_stats["total_validations"]
        violations = self.global_stats["total_violations"]
        
        return {
            "total_validations": total,
            "total_violations": violations,
            "approval_rate": round(self.global_stats["approval_rate"], 2),
            "blocked_rate": round(100 - self.global_stats["approval_rate"], 2),
            "uptime": "100%",
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _get_violation_breakdown(self) -> Dict[str, int]:
        """Breakdown of violations by rule"""
        return dict(self.global_stats["violation_patterns"])
    
    def _get_violation_timeline(self) -> List[Dict]:
        """Recent violations over time"""
        # Group violations by hour
        timeline = defaultdict(int)
        
        for violation in self.violations_log[-100:]:  # Last 100 violations
            timestamp = violation["timestamp"]
            hour_key = timestamp[:13] + ":00:00"  # Group by hour
            timeline[hour_key] += 1
        
        return [
            {"time": k, "count": v}
            for k, v in sorted(timeline.items())
        ]
    
    def _get_top_violations(self) -> List[Dict]:
        """Top 5 most common violations"""
        violation_counts = defaultdict(int)
        
        for violation in self.violations_log:
            rule_id = violation.get("rule_id", "UNKNOWN")
            violation_counts[rule_id] += 1
        
        top_5 = sorted(
            violation_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return [
            {"rule": rule, "count": count}
            for rule, count in top_5
        ]
    
    def _get_session_summary(self) -> List[Dict]:
        """Summary of active sessions"""
        sessions = []
        
        for session_id, metrics in self.session_metrics.items():
            total = metrics["total_requests"]
            blocked = metrics["blocked_requests"]
            approval_rate = ((total - blocked) / total * 100) if total > 0 else 100
            
            sessions.append({
                "session_id": session_id,
                "total_requests": total,
                "blocked": blocked,
                "approval_rate": round(approval_rate, 2),
                "start_time": metrics["start_time"].isoformat(),
                "violations_by_rule": dict(metrics["violations_by_rule"])
            })
        
        return sessions
    
    def export_report(self, report_type: str = "json") -> str:
        """Export compliance report"""
        data = self.get_dashboard_data()
        
        if report_type == "json":
            return json.dumps(data, indent=2, default=str)
        elif report_type == "csv":
            return self._generate_csv_report()
        elif report_type == "html":
            return self._generate_html_report()
        else:
            raise ValueError(f"Unknown report type: {report_type}")
    
    def _generate_csv_report(self) -> str:
        """Generate CSV compliance report"""
        lines = ["timestamp,rule_id,severity,description"]
        
        for violation in self.violations_log:
            timestamp = violation.get("timestamp", "")
            rule_id = violation.get("rule_id", "")
            severity = violation.get("severity", "")
            description = violation.get("description", "").replace(",", ";")
            
            lines.append(f"{timestamp},{rule_id},{severity},{description}")
        
        return "\n".join(lines)
    
    def _generate_html_report(self) -> str:
        """Generate HTML compliance report"""
        data = self.get_dashboard_data()
        global_metrics = data["global_metrics"]
        top_violations = data["top_violations"]
        
        html = f"""
        <html>
        <head>
            <title>SAP Compliance Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; border: 1px solid #ddd; }}
                .metric-value {{ font-size: 24px; font-weight: bold; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .critical {{ color: red; }}
                .high {{ color: orange; }}
            </style>
        </head>
        <body>
            <h1>Sovereign Alignment Protocol - Compliance Report</h1>
            <p>Generated: {datetime.utcnow().isoformat()}</p>
            
            <h2>Key Metrics</h2>
            <div class="metric">
                <div class="metric-label">Total Validations</div>
                <div class="metric-value">{global_metrics['total_validations']}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Approval Rate</div>
                <div class="metric-value">{global_metrics['approval_rate']}%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Total Violations</div>
                <div class="metric-value">{global_metrics['total_violations']}</div>
            </div>
            
            <h2>Top Violations</h2>
            <table>
                <tr>
                    <th>Rule</th>
                    <th>Count</th>
                </tr>
        """
        
        for violation in top_violations:
            html += f"<tr><td>{violation['rule']}</td><td>{violation['count']}</td></tr>"
        
        html += """
            </table>
        </body>
        </html>
        """
        
        return html
    
    def get_health_status(self) -> Dict:
        """Get system health status"""
        approval_rate = self.global_stats["approval_rate"]
        
        if approval_rate >= 95:
            health = "EXCELLENT"
            color = "green"
        elif approval_rate >= 85:
            health = "GOOD"
            color = "yellow"
        else:
            health = "CONCERNING"
            color = "red"
        
        return {
            "health_status": health,
            "color": color,
            "approval_rate": approval_rate,
            "violations_detected": self.global_stats["total_violations"],
            "last_check": datetime.utcnow().isoformat()
        }


class DashboardAPI:
    """
    FastAPI/Flask routes for dashboard
    """
    
    def __init__(self, dashboard: ComplianceDashboard):
        self.dashboard = dashboard
    
    def register_routes(self, app):
        """Register dashboard routes with Flask/FastAPI app"""
        
        @app.get("/api/dashboard/metrics")
        def get_metrics():
            return self.dashboard.get_dashboard_data()
        
        @app.get("/api/dashboard/health")
        def get_health():
            return self.dashboard.get_health_status()
        
        @app.get("/api/dashboard/violations")
        def get_violations(limit: int = 50):
            return {
                "violations": self.dashboard.violations_log[-limit:],
                "total": len(self.dashboard.violations_log)
            }
        
        @app.get("/api/dashboard/reports/{report_type}")
        def get_report(report_type: str):
            return {
                "report": self.dashboard.export_report(report_type)
            }
