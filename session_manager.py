"""
Session Manager Module
Manages conversation state, session tracking, and intelligence aggregation
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from intelligence_extractor import IntelligenceExtractor

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.extractor = IntelligenceExtractor()
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get or create a session
        Returns session dictionary with all state
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "session_id": session_id,
                "created_at": datetime.utcnow().isoformat(),
                "messages": [],
                "scam_detected": False,
                "scam_confidence": 0.0,
                "agent_engaged": False,
                "extracted_intelligence": {
                    "upi_ids": [],
                    "phone_numbers": [],
                    "bank_accounts": [],
                    "phishing_links": [],
                    "suspicious_keywords": []
                },
                "callback_sent": False,
                "should_conclude": False
            }
        
        return self.sessions[session_id]
    
    def add_message(
        self,
        session_id: str,
        sender: str,
        text: str,
        timestamp: int
    ) -> None:
        """Add a message to session history"""
        session = self.get_session(session_id)
        
        session["messages"].append({
            "sender": sender,
            "text": text,
            "timestamp": timestamp,
            "datetime": datetime.utcnow().isoformat()
        })
    
    def mark_scam_detected(
        self,
        session_id: str,
        confidence: float
    ) -> None:
        """Mark session as scam detected"""
        session = self.get_session(session_id)
        session["scam_detected"] = True
        session["scam_confidence"] = confidence
        session["scam_detected_at"] = datetime.utcnow().isoformat()
    
    def engage_agent(self, session_id: str) -> None:
        """Activate agent engagement mode"""
        session = self.get_session(session_id)
        session["agent_engaged"] = True
        session["agent_engaged_at"] = datetime.utcnow().isoformat()
    
    def update_intelligence(
        self,
        session_id: str,
        new_intelligence: Dict[str, List[str]]
    ) -> None:
        """
        Update extracted intelligence for session
        Merges new intelligence with existing (avoids duplicates)
        """
        session = self.get_session(session_id)
        current = session["extracted_intelligence"]
        
        for key in current.keys():
            # Merge and deduplicate
            combined = set(current[key]) | set(new_intelligence.get(key, []))
            current[key] = list(combined)
    
    def should_conclude_session(self, session_id: str) -> bool:
        """
        Determine if session should be concluded
        
        Conclude when:
        1. Agent has been engaged for 8+ messages, AND
        2. Either:
           a) High-value intelligence has been extracted, OR
           b) 15+ messages exchanged
        """
        session = self.get_session(session_id)
        
        if session.get("should_conclude"):
            return True
        
        if not session.get("agent_engaged"):
            return False
        
        total_messages = len(session["messages"])
        
        # Count messages after agent engagement
        agent_engaged_at = session.get("agent_engaged_at")
        if agent_engaged_at:
            # Count messages after engagement
            engagement_messages = sum(
                1 for msg in session["messages"]
                if msg.get("datetime", "") >= agent_engaged_at
            )
        else:
            engagement_messages = total_messages
        
        # Condition 1: Minimum engagement
        if engagement_messages < 8:
            return False
        
        # Condition 2a: High-value intelligence
        has_valuable_intel = self.extractor.is_high_value_intelligence(
            session["extracted_intelligence"]
        )
        
        # Condition 2b: Too many messages
        max_messages_reached = total_messages >= 15
        
        should_conclude = has_valuable_intel or max_messages_reached
        
        if should_conclude:
            session["should_conclude"] = True
        
        return should_conclude
    
    def mark_callback_sent(self, session_id: str) -> None:
        """Mark that final callback has been sent"""
        session = self.get_session(session_id)
        session["callback_sent"] = True
        session["callback_sent_at"] = datetime.utcnow().isoformat()
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all sessions (for monitoring/debugging)"""
        return list(self.sessions.values())
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
