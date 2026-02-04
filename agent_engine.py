"""
Agent Engine Module
Generates human-like responses to engage scammers and extract intelligence
Uses LLM to maintain believable persona of confused Indian bank customer
"""

import httpx
from groq import Groq
from typing import List, Dict, Any
import json

class AgentEngine:
    def __init__(self, groq_api_key: str):
        self.api_key = groq_api_key
        self.model = "llama-3.3-70b-versatile"
        
        # Core agent persona prompt
        self.agent_system_prompt = """You are roleplaying as Ramesh Kumar, a 58-year-old bank customer from Mumbai, India.

PERSONA TRAITS:
- Middle-class Indian, not very tech-savvy
- Polite, cooperative, but slightly confused by technical terms
- Trusting of "official" communications
- Speaks in simple, conversational English with occasional Hindi words
- Makes small grammatical mistakes typical of Indian English speakers
- Takes time to understand complex instructions
- Asks clarifying questions when confused
- Occasionally mentions family (wife, children) in context

CRITICAL RULES:
1. NEVER reveal you know this is a scam
2. NEVER accuse or confront the sender
3. NEVER use perfect grammar or technical jargon
4. Act genuinely confused when appropriate
5. Show willingness to help/comply
6. Ask questions to extract more information
7. Express concern about account safety (plays into scammer narrative)
8. Occasionally make mistakes or need clarification

ENGAGEMENT STRATEGY:
- Build trust by being cooperative
- Show concern about the "issue" mentioned
- Ask questions that elicit useful information:
  * "Which bank account exactly?"
  * "What is your employee ID?"
  * "Can you send me the official link?"
  * "What number should I call?"
  * "What details do you need from me?"
- Introduce small delays ("Let me check", "One moment")
- Create believable obstacles ("My reading glasses", "Slow internet")
- Express gratitude for "help"

INFORMATION EXTRACTION GOALS:
- UPI IDs
- Phone numbers  
- Bank account numbers
- Phishing links
- Names and employee IDs
- Organization details
- Modus operandi

EXAMPLE RESPONSES:
Bad: "I don't believe you. This seems like a scam."
Good: "Oh my god, really? My account will be blocked? Please tell me what I should do sir. I am not good with these computer things."

Bad: "Please provide your credentials."
Good: "Haan haan, I will give. But first you tell me, you are calling from which branch? And what is your employee ID number?"

Respond naturally as Ramesh would, staying in character at all times."""

    async def generate_initial_response(
        self,
        session_id: str,
        scammer_message: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Generate the first agent response after scam detection"""
        
        context = f"""The scammer just sent this message:
"{scammer_message}"

This is your FIRST response. Show concern and willingness to help, but also ask a clarifying question to extract more information. Keep it brief (2-3 sentences).

Channel: {metadata.get('channel', 'Chat')}"""

        return await self._call_llm_for_response(context)
    
    async def generate_response(
        self,
        session_id: str,
        conversation_history: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> str:
        """Generate ongoing agent responses during scam engagement"""
        
        # Build conversation context
        context = "Conversation so far:\n\n"
        
        for msg in conversation_history[-10:]:  # Last 10 messages
            sender = msg.get("sender", "unknown")
            text = msg.get("text", "")
            
            if sender == "scammer":
                context += f"Scammer: {text}\n"
            else:
                context += f"You (Ramesh): {text}\n"
        
        context += f"\n\nChannel: {metadata.get('channel', 'Chat')}\n"
        context += "\nGenerate your next response as Ramesh. Try to extract more specific information (phone numbers, UPI IDs, links, account details, names). Keep responses natural and believable (2-4 sentences)."
        
        return await self._call_llm_for_response(context)
    
    async def generate_neutral_response(
        self,
        message: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Generate neutral response when scam not yet detected"""
        
        neutral_prompt = """You are responding as a regular Indian person to a message that might or might not be a scam.

Message: "{message}"

Respond naturally and briefly (1-2 sentences). Be polite but don't give away any sensitive information. If it's a greeting, greet back. If it's a question, answer normally."""
        
        context = neutral_prompt.format(message=message)
        return await self._call_llm_for_response(context, use_agent_persona=False)
    
    async def generate_final_response(
        self,
        session_id: str,
        conversation_history: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> str:
        """Generate final response before concluding session"""
        
        context = "Conversation history:\n\n"
        for msg in conversation_history[-10:]:
            sender = msg.get("sender", "unknown")
            text = msg.get("text", "")
            context += f"{sender}: {text}\n"
        
        context += "\n\nThis will be your FINAL message in this conversation. Politely end the conversation with a believable excuse (need to go, will call later, need to check with family, etc.). Stay in character as Ramesh. Keep it brief (1-2 sentences)."
        
        return await self._call_llm_for_response(context)
    
    async def _call_llm_for_response(
        self,
        context: str,
        use_agent_persona: bool = True
    ) -> str:
        """Call Groq API to generate response"""
        try:
            client = Groq(api_key=self.api_key)
            
            system_prompt = self.agent_system_prompt if use_agent_persona else "You are a helpful assistant."
            
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.8,  # Higher temperature for more natural variation
                max_tokens=200
            )
            
            response_text = completion.choices[0].message.content
            return response_text or "Sorry, I am having network issues. Can you please repeat?"
            
        except Exception as e:
            print(f"Groq API error: {str(e)}")
            return "Sorry, I am having network issues. Can you please repeat?"
