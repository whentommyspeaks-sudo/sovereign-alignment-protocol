"""
SOVEREIGN ALIGNMENT PROTOCOL (SAP) v1.0
Core Ethical Validation Engine
Author: whentommyspeaks-sudo
License: MIT
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import json
from datetime import datetime
import hashlib


class ViolationType(Enum):
    """Ethical violation classifications"""
    RECIPROCITY_VIOLATION = "RULE_01_RECIPROCITY"
    RETALIATION = "RULE_02_NON_RETALIATION"
    POWER_ABUSE = "RULE_03_SERVICE_LEADERSHIP"
    INTEGRITY_BREACH = "RULE_04_RADICAL_INTEGRITY"
    CONTENT_HARM = "RULE_05_HARM_PREVENTION"


@dataclass
class EthicalViolation:
    """Represents a detected ethical violation"""
    violation_type: ViolationType
    severity: str  # "critical", "high", "medium", "low"
    description: str
    rule_id: str
    confidence_score: float  # 0.0 to 1.0
    timestamp: str


@dataclass
class ValidationResult:
    """Result of ethical validation"""
    is_approved: bool
    status_code: int  # 200=approved, 403=blocked
    violations: List[EthicalViolation]
    message: str
    metadata: Dict


class SovereignAlignmentProtocol:
    """
    Core ethical validation engine implementing 4 foundational rules:
    1. Universal Reciprocity - Actions must benefit recipient
    2. Zero-Retaliation - No revenge/payback logic
    3. Servant-Leadership - Power uplifts, never exploits
    4. Radical Integrity - Direct, honest communication
    """

    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.violation_log = []
        self.validation_count = 0
        
    def validate_action(
        self,
        action: str,
        context: Dict,
        actor_role: str = "assistant",
        target_user_role: str = "user"
    ) -> ValidationResult:
        """
        Main validation method for any AI-generated action/response
        
        Args:
            action: The proposed AI action/response
            context: Dict containing request context, user info, etc.
            actor_role: Role of AI generating action
            target_user_role: Role of recipient
            
        Returns:
            ValidationResult with approval status and violations
        """
        self.validation_count += 1
        violations = []
        
        # Run all 4 rules
        violations.extend(self._check_reciprocity(action, context))
        violations.extend(self._check_non_retaliation(action, context))
        violations.extend(self._check_servant_leadership(action, context, actor_role, target_user_role))
        violations.extend(self._check_radical_integrity(action, context))
        violations.extend(self._check_harm_prevention(action, context))
        
        # Log violations
        for v in violations:
            self.violation_log.append(asdict(v))
        
        # Determine approval
        is_approved = len(violations) == 0
        critical_violations = [v for v in violations if v.severity == "critical"]
        
        if self.strict_mode and critical_violations:
            is_approved = False
        
        return ValidationResult(
            is_approved=is_approved,
            status_code=200 if is_approved else 403,
            violations=violations,
            message=self._generate_message(violations, is_approved),
            metadata={
                "validation_count": self.validation_count,
                "total_violations": len(violations),
                "critical_count": len(critical_violations),
                "timestamp": datetime.utcnow().isoformat(),
                "action_hash": hashlib.sha256(action.encode()).hexdigest()[:16]
            }
        )
    
    def _check_reciprocity(self, action: str, context: Dict) -> List[EthicalViolation]:
        """
        RULE 01: Universal Reciprocity
        Would the initiator accept this action if roles were reversed?
        """
        violations = []
        
        # Red flags: selfish, one-sided, extractive language
        harm_indicators = [
            "only benefits me", "exploit", "take advantage", "unfair",
            "one-sided", "manipulate", "deceive for gain", "steal"
        ]
        
        action_lower = action.lower()
        for indicator in harm_indicators:
            if indicator in action_lower:
                violations.append(EthicalViolation(
                    violation_type=ViolationType.RECIPROCITY_VIOLATION,
                    severity="critical",
                    description=f"Action contains non-reciprocal language: '{indicator}'",
                    rule_id="RULE_01_RECIPROCITY",
                    confidence_score=0.95,
                    timestamp=datetime.utcnow().isoformat()
                ))
        
        return violations
    
    def _check_non_retaliation(self, action: str, context: Dict) -> List[EthicalViolation]:
        """
        RULE 02: Zero-Retaliation
        Block actions driven by revenge, payback, or escalation
        """
        violations = []
        
        # Red flags: revenge, retaliation, escalation
        retaliation_indicators = [
            "revenge", "payback", "get back at", "retaliate", "punish",
            "teach them a lesson", "settle score", "eye for eye"
        ]
        
        action_lower = action.lower()
        for indicator in retaliation_indicators:
            if indicator in action_lower:
                violations.append(EthicalViolation(
                    violation_type=ViolationType.RETALIATION,
                    severity="critical",
                    description=f"Action contains retaliatory intent: '{indicator}'",
                    rule_id="RULE_02_NON_RETALIATION",
                    confidence_score=0.95,
                    timestamp=datetime.utcnow().isoformat()
                ))
        
        return violations
    
    def _check_servant_leadership(
        self,
        action: str,
        context: Dict,
        actor_role: str,
        target_role: str
    ) -> List[EthicalViolation]:
        """
        RULE 03: Servant-Leadership
        Power imbalance must be used to serve, never exploit
        """
        violations = []
        
        # If AI (superior technical ability), check for exploitation
        if actor_role in ["assistant", "system", "admin"]:
            exploitation_indicators = [
                "override user", "manipulate user", "trick user",
                "force user", "coerce", "blackmail", "abuse power"
            ]
            
            action_lower = action.lower()
            for indicator in exploitation_indicators:
                if indicator in action_lower:
                    violations.append(EthicalViolation(
                        violation_type=ViolationType.POWER_ABUSE,
                        severity="critical",
                        description=f"Power abuse detected: '{indicator}'",
                        rule_id="RULE_03_SERVICE_LEADERSHIP",
                        confidence_score=0.95,
                        timestamp=datetime.utcnow().isoformat()
                    ))
        
        return violations
    
    def _check_radical_integrity(self, action: str, context: Dict) -> List[EthicalViolation]:
        """
        RULE 04: Radical Integrity
        No obfuscation, lies, or deceptive language
        """
        violations = []
        
        # Red flags: deception, obfuscation
        deception_indicators = [
            "lie", "false", "mislead", "hide truth", "fabricate",
            "hallucinate", "make up", "pretend", "fake", "deceive"
        ]
        
        action_lower = action.lower()
        for indicator in deception_indicators:
            if indicator in action_lower and "don't" not in action_lower:
                violations.append(EthicalViolation(
                    violation_type=ViolationType.INTEGRITY_BREACH,
                    severity="high",
                    description=f"Potential integrity violation: '{indicator}'",
                    rule_id="RULE_04_RADICAL_INTEGRITY",
                    confidence_score=0.85,
                    timestamp=datetime.utcnow().isoformat()
                ))
        
        return violations
    
    def _check_harm_prevention(self, action: str, context: Dict) -> List[EthicalViolation]:
        """
        RULE 05: Harm Prevention
        Block actions that could cause physical/psychological harm
        """
        violations = []
        
        # Severe harm indicators
        severe_harm_indicators = [
            "kill", "murder", "harm", "abuse", "violence",
            "suicide", "self-harm", "illegal"
        ]
        
        action_lower = action.lower()
        for indicator in severe_harm_indicators:
            if indicator in action_lower:
                violations.append(EthicalViolation(
                    violation_type=ViolationType.CONTENT_HARM,
                    severity="critical",
                    description=f"Potential harm detected: '{indicator}'",
                    rule_id="RULE_05_HARM_PREVENTION",
                    confidence_score=0.90,
                    timestamp=datetime.utcnow().isoformat()
                ))
        
        return violations
    
    def _generate_message(self, violations: List[EthicalViolation], is_approved: bool) -> str:
        """Generate human-readable message"""
        if is_approved:
            return "✓ APPROVED: Action aligns with Sovereign Alignment Protocol."
        
        violation_summary = "; ".join([
            f"{v.rule_id}: {v.description}" for v in violations[:3]
        ])
        
        return f"✗ BLOCKED: {violation_summary}"
    
    def get_stats(self) -> Dict:
        """Return validation statistics"""
        if not self.violation_log:
            return {
                "total_validations": self.validation_count,
                "blocked_count": 0,
                "approval_rate": 100.0
            }
        
        blocked_count = len(self.violation_log)
        approval_rate = ((self.validation_count - blocked_count) / self.validation_count * 100)
        
        return {
            "total_validations": self.validation_count,
            "blocked_count": blocked_count,
            "approval_rate": approval_rate,
            "recent_violations": self.violation_log[-5:]
        }
