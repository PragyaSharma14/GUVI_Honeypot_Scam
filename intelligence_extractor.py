"""
Intelligence Extractor Module
Extracts scam intelligence using regex patterns for Indian context
"""

import re
from typing import Dict, List, Set

class IntelligenceExtractor:
    def __init__(self):
        # Regex patterns for Indian context
        
        # UPI ID pattern: user@bank or phonenumber@upi
        self.upi_pattern = re.compile(r'\b[\w\.-]+@[\w-]+\b')
        
        # Indian phone number: 10 digits, optional +91/0 prefix
        self.phone_pattern = re.compile(r'(?:\+91|91|0)?[6-9]\d{9}\b')
        
        # Bank account: 9-18 digits
        self.bank_account_pattern = re.compile(r'\b\d{9,18}\b')
        
        # URL pattern
        self.url_pattern = re.compile(
            r'https?://[^\s]+|www\.[^\s]+|bit\.ly/[^\s]+|tinyurl\.com/[^\s]+'
        )
        
        # Suspicious keywords
        self.suspicious_keywords = [
            'kyc', 'update', 'verify', 'account', 'blocked', 'suspended',
            'otp', 'cvv', 'pin', 'password', 'aadhaar', 'pan',
            'prize', 'lottery', 'won', 'congratulations',
            'urgent', 'immediately', 'expire', 'cancel',
            'refund', 'tax', 'cashback', 'reward',
            'click here', 'download', 'apk', 'install',
            'bank', 'axis', 'hdfc', 'sbi', 'icici', 'paytm', 'phonepe', 'googlepay',
            'police', 'arrest', 'court', 'legal action',
            'loan approved', 'credit card', 'offer',
            'delivery', 'courier', 'parcel', 'custom duty'
        ]
    
    def extract_from_message(self, message: str) -> Dict[str, List[str]]:
        """
        Extract intelligence from a single message
        Returns dict with lists of extracted entities
        """
        message_lower = message.lower()
        
        intelligence = {
            "upi_ids": [],
            "phone_numbers": [],
            "bank_accounts": [],
            "phishing_links": [],
            "suspicious_keywords": []
        }
        
        # Extract UPI IDs
        upi_matches = self.upi_pattern.findall(message)
        # Filter out common false positives
        upi_ids = [
            upi for upi in upi_matches
            if any(bank in upi.lower() for bank in ['paytm', 'phonepe', 'gpay', 'ybl', 'okaxis', 'okhdfcbank', 'oksbi', 'okicici'])
        ]
        intelligence["upi_ids"] = list(set(upi_ids))
        
        # Extract phone numbers
        phone_matches = self.phone_pattern.findall(message)
        # Clean phone numbers (remove +91, 91, 0 prefix)
        cleaned_phones = []
        for phone in phone_matches:
            clean = re.sub(r'^(\+91|91|0)', '', phone)
            if len(clean) == 10:
                cleaned_phones.append(clean)
        intelligence["phone_numbers"] = list(set(cleaned_phones))
        
        # Extract potential bank accounts (9-18 digits)
        # Exclude phone numbers already found
        account_matches = self.bank_account_pattern.findall(message)
        potential_accounts = [
            acc for acc in account_matches
            if acc not in cleaned_phones and len(acc) >= 11  # Bank accounts usually 11+ digits
        ]
        intelligence["bank_accounts"] = list(set(potential_accounts))
        
        # Extract URLs
        url_matches = self.url_pattern.findall(message)
        intelligence["phishing_links"] = list(set(url_matches))
        
        # Extract suspicious keywords
        found_keywords = [
            keyword for keyword in self.suspicious_keywords
            if keyword in message_lower
        ]
        intelligence["suspicious_keywords"] = list(set(found_keywords))
        
        return intelligence
    
    def extract_from_conversation(
        self,
        messages: List[Dict[str, str]]
    ) -> Dict[str, Set[str]]:
        """
        Extract all intelligence from conversation history
        Returns aggregated intelligence with Sets to avoid duplicates
        """
        aggregated = {
            "upi_ids": set(),
            "phone_numbers": set(),
            "bank_accounts": set(),
            "phishing_links": set(),
            "suspicious_keywords": set()
        }
        
        for msg in messages:
            text = msg.get("text", "")
            extracted = self.extract_from_message(text)
            
            for key in aggregated.keys():
                aggregated[key].update(extracted.get(key, []))
        
        # Convert sets back to lists
        return {
            key: list(values) for key, values in aggregated.items()
        }
    
    def is_high_value_intelligence(self, intelligence: Dict[str, List[str]]) -> bool:
        """
        Determine if extracted intelligence is valuable
        Used to decide when to conclude session
        """
        # High value if we have:
        # - At least 1 UPI ID OR
        # - At least 1 phone number AND 1 link OR
        # - At least 1 bank account
        
        has_upi = len(intelligence.get("upi_ids", [])) > 0
        has_phone = len(intelligence.get("phone_numbers", [])) > 0
        has_link = len(intelligence.get("phishing_links", [])) > 0
        has_bank = len(intelligence.get("bank_accounts", [])) > 0
        
        return has_upi or (has_phone and has_link) or has_bank
