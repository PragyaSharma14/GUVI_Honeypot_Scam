"""
Scam Detector Module
Uses LLM (Groq) to classify scam intent
"""

from groq import Groq
from typing import List, Dict, Any, Tuple
import json

class ScamDetector:
    def __init__(self, groq_api_key: str):
        self.api_key = groq_api_key
        # Using Llama 3.3 70b model as specified by Groq
        self.model = "llama-3.3-70b-versatile"
        
        # Scam detection system prompt
        self.system_prompt = """You are an expert scam detection AI system specializing in Indian scam patterns.

Analyze the given message and conversation history to determine if it's a scam attempt.

COMMON INDIAN SCAM PATTERNS:
- Fake KYC update requests (banking, telecom, government)
- Prize/lottery winning notifications
- Fake delivery/courier messages
- Urgent account blocking threats
- OTP/PIN requests
- Tax refund scams
- Job offer scams requiring payment
- Investment/trading scams promising high returns
- Loan approval scams requiring advance fees
- Digital arrest scams (impersonating police/CBI)
- Aadhaar/PAN update scams
- Insurance maturity scams

SCAM INDICATORS:
1. Urgency ("immediately", "within 24 hours", "account will be blocked")
2. Requests for sensitive info (OTP, PIN, CVV, password, Aadhaar number)
3. Unsolicited offers (prizes, loans, jobs)
4. Threats (legal action, account suspension, arrest)
5. Suspicious links or APK downloads
6. Impersonation of banks, government, courier services
7. Requests for payment/transfer
8. Grammatical errors, poor language
9. Unknown sender claiming to be from known organization

Respond ONLY with a JSON object:
{
  "is_scam": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation",
  "scam_type": "KYC|Prize|Delivery|Threat|Financial|Other|None"
}"""

    async def detect_scam(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> Tuple[bool, float]:
        """
        Detect if a message is a scam attempt
        Returns: (is_scam: bool, confidence: float)
        """
        try:
            # Prepare context from conversation history
            context = self._build_context(message, conversation_history, metadata)
            
            # Call LLM for classification
            result = await self._call_llm(context)
            
            # Parse response
            is_scam = result.get("is_scam", False)
            confidence = result.get("confidence", 0.0)
            
            return is_scam, confidence
            
        except Exception as e:
            print(f"Error in scam detection: {str(e)}")
            # Conservative fallback - assume not scam on error
            return False, 0.0
    
    def _build_context(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> str:
        """Build context string for LLM"""
        context = f"Channel: {metadata.get('channel', 'Unknown')}\n"
        context += f"Language: {metadata.get('language', 'English')}\n"
        context += f"Locale: {metadata.get('locale', 'IN')}\n\n"
        
        if conversation_history:
            context += "Previous messages:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                sender = msg.get("sender", "unknown")
                text = msg.get("text", "")
                context += f"{sender}: {text}\n"
            context += "\n"
        
        context += f"Current message to analyze:\n{message}"
        
        return context
    
    async def _call_llm(self, context: str) -> Dict[str, Any]:
        """Call Groq API with Llama 3.1"""
        try:
            client = Groq(api_key=self.api_key)
            
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            content = completion.choices[0].message.content
            
            # Parse JSON response
            # Handle potential markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # If the content starts with text before JSON, try to find the JSON object
            # Look for JSON object in the content (even if preceded by reasoning)
            # Find the first JSON object in the content
            import re
            json_start = content.find('{')
            if json_start != -1:
                # Extract the JSON object
                brace_count = 0
                for i, char in enumerate(content[json_start:], json_start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            content = content[json_start:i+1]
                            break
            
            # If no JSON object was found, return default values
            if not content.strip().startswith('{'):
                return {"is_scam": False, "confidence": 0.0, "reasoning": "Could not parse response", "scam_type": "None"}
            
            result = json.loads(content)
            return result

        except Exception as e:
            print(f"Groq API error: {str(e)}")
            return {"is_scam": False, "confidence": 0.0}

    def _parse_semi_structured_response(self, content: str) -> dict:
        """Parse semi-structured response from the model when JSON format is not provided"""
        print("Parsing semi-structured response...")
        print(f"Content: {content}")
        
        # Initialize default values
        result = {
            "is_scam": False,
            "confidence": 0.0,
            "reasoning": "Could not parse response",
            "scam_type": "None"
        }
                
        # First, look for explicit is_scam values
        is_scam_patterns = [
            r'[Ii]s[_\s-]?[Ss]cam\s*[:=]\s*(true|false|yes|no)',
            r'[Cc]onclusion:.?\s*[Ii]s[_\s-]?[Ss]cam\s*[:=]\s*(true|false|yes|no)',
            r'^\s*-\s*[Ii]s[_\s-]?[Ss]cam\s*[:=]\s*(true|false|yes|no)',
            r'(?:^|\n)\s*-?\s*[Ii]s[_\s-]?[Ss]cam\s*[:=]\s*(true|false|yes|no)',
        ]
                
        for pattern in is_scam_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                is_scam_value = match.group(1).lower()
                result["is_scam"] = is_scam_value in ['true', 'yes']
                break
                
        # If no explicit is_scam found, infer from the content
        if not result["is_scam"]:
            # Look for positive indicators in the analysis
            positive_indicators = [
                r'matches the.*pattern',
                r'fits the.*pattern',
                r'this is.*scam',
                r'appears to be.*scam',
                r'indicates.*scam',
                r'is a.*scam',
                r'clear.*scam',
                r'likely.*scam',
                r'probable.*scam'
            ]
                    
            for indicator in positive_indicators:
                if re.search(indicator, content, re.IGNORECASE):
                    result["is_scam"] = True
                    break
                
        # Extract confidence if present
        confidence_patterns = [
            r'[Cc]onfidence\s*[:=]\s*([0-9]+\.?[0-9]*|low|medium|high)',
            r'[Cc]onfidence:?\s*([0-9]+\.?[0-9]*|low|medium|high)',
        ]
                
        for pattern in confidence_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                conf_val = match.group(1).lower()
                if conf_val.replace('.', '').isdigit():
                    try:
                        result["confidence"] = min(float(conf_val), 1.0)  # Cap at 1.0
                    except ValueError:
                        pass
                elif conf_val == 'low':
                    result["confidence"] = 0.3
                elif conf_val == 'medium':
                    result["confidence"] = 0.6
                elif conf_val == 'high':
                    result["confidence"] = 0.9
                break
                
        # Extract reasoning
        # Look for reasoning in various formats
        reasoning_patterns = [
            r'[Rr]easoning\s*[:=]\s*"([^"]+)"',
            r"[Rr]easoning\s*[:=]\s*'([^']+)",
            r'[Rr]easoning\s*[:=]\s*([^-\n]+?)(?=\n-|$|\n\d+\\.|[Cc]onclusion)',
            r'[Aa]nalysis:\s*([^-\n]+?)(?=\n-|$|\n\d+\\.|[Cc]onclusion)',
            r'[Aa]nalysis:(.+?)(?=\n\d+\\.|[Cc]onclusion|$)',
        ]
                
        for pattern in reasoning_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                result["reasoning"] = match.group(1).strip().strip('-').strip()
                break
                
        # If reasoning wasn't found, extract the analysis section
        if result["reasoning"] == "Could not parse response":
            # Look for analysis paragraphs
            analysis_match = re.search(r'Analysis:(.+?)(?=\n\d+\\.|[Cc]onclusion|$)', content, re.IGNORECASE | re.DOTALL)
            if analysis_match:
                result["reasoning"] = analysis_match.group(1).strip()
                
        # Extract scam type
        scam_type_patterns = [
            r'[Ss]cam[_\s]?[Tt]ype\s*[:=]\s*"?([A-Z\|]+)"?',
            r'-\s*[Ss]cam[_\s]?[Tt]ype:\s*([A-Z\|]+)',
            r'[Cc]onclusion:.?\s*[Ss]cam[_\s]?[Tt]ype\s*[:=]\s*"?([A-Z\|]+)"?',
        ]
                
        for pattern in scam_type_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                result["scam_type"] = match.group(1)
                break
                
        # If scam type is still None and we detected a scam, try to infer from the content
        if result["scam_type"] == "None" and result["is_scam"]:
            if 'urgent account blocking' in content.lower() or 'blocked' in content.lower():
                result["scam_type"] = "Threat"
            elif 'kyc' in content.lower() or 'verification' in content.lower():
                result["scam_type"] = "KYC"
            elif 'prize' in content.lower() or 'won' in content.lower():
                result["scam_type"] = "Prize"
            elif 'delivery' in content.lower() or 'courier' in content.lower():
                result["scam_type"] = "Delivery"
            else:
                result["scam_type"] = "Financial"
                
        # Adjust confidence based on scam indicators
        if result["is_scam"] and result["confidence"] == 0.0:
            result["confidence"] = 0.8  # High confidence if scam is detected
        elif not result["is_scam"] and result["confidence"] == 0.0:
            result["confidence"] = 0.2  # Default low confidence if not a scam
        
        print(f"Parsed result: {result}")
        return result