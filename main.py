"""
Agentic Honey-Pot for Scam Detection & Intelligence Extraction
GUVI Hackathon Project
FastAPI REST API for scam detection and intelligence gathering
"""

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
from groq import Groq
import httpx
from datetime import datetime
import asyncio
from enum import Enum

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from scam_detector import ScamDetector
from agent_engine import AgentEngine
from intelligence_extractor import IntelligenceExtractor
from session_manager import SessionManager

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Honey-Pot API",
    description="Scam Detection & Intelligence Extraction System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
API_KEY = os.getenv("API_KEY", "your-secret-api-key-change-in-production")
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable must be set")

# Initialize components
scam_detector = ScamDetector(GROQ_API_KEY)
agent_engine = AgentEngine(GROQ_API_KEY)
intelligence_extractor = IntelligenceExtractor()
session_manager = SessionManager()

# Pydantic Models
class SenderType(str, Enum):
    SCAMMER = "scammer"
    USER = "user"

class Message(BaseModel):
    sender: SenderType
    text: str
    timestamp: int

class Metadata(BaseModel):
    channel: str = Field(..., description="SMS | WhatsApp | Email | Chat")
    language: str = "English"
    locale: str = "IN"

class IncomingRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Dict[str, Any]] = []
    metadata: Metadata

class APIResponse(BaseModel):
    status: str = "success"
    reply: str

class ExtractedIntelligence(BaseModel):
    bankAccounts: List[str] = []
    upiIds: List[str] = []
    phishingLinks: List[str] = []
    phoneNumbers: List[str] = []
    suspiciousKeywords: List[str] = []

class FinalCallback(BaseModel):
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str


# API Key validation
async def validate_api_key(api_key: str):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key


@app.get("/")
async def root(x_api_key: str = Header(None, alias="x-api-key")):
    """Health check endpoint - accepts optional API key for compatibility"""
    return {
        "service": "Agentic Honey-Pot API",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/api/chat", response_model=APIResponse)
async def chat_endpoint(
    request: IncomingRequest,
    x_api_key: str = Header(None, alias="x-api-key"),
    X_API_KEY: str = Header(None, alias="X-API-Key"),
    content_type: str = Header(None, alias="content-type")
):
    """
    Main chat endpoint for scam detection and agent engagement
    Validates API key, processes messages, and manages scam detection workflow
    Accepts both x-api-key and X-API-Key headers for compatibility
    """
    # Check for API key in either header
    api_key = x_api_key or X_API_KEY
    
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    # Validate API key
    await validate_api_key(api_key)
    
    try:
        session_id = request.sessionId
        incoming_message = request.message.text
        sender = request.message.sender
        conversation_history = request.conversationHistory
        
        # Get or create session
        session = session_manager.get_session(session_id)
        
        # Add incoming message to session
        session_manager.add_message(
            session_id,
            sender=sender.value,
            text=incoming_message,
            timestamp=request.message.timestamp
        )
        
        # If scam already confirmed and agent is engaged
        if session.get("scam_detected") and session.get("agent_engaged"):
            # Check if we should conclude the conversation
            if session_manager.should_conclude_session(session_id):
                # Generate final response
                reply = await agent_engine.generate_final_response(
                    session_id,
                    session["messages"],
                    request.metadata.dict()
                )
                
                # Trigger final callback asynchronously
                asyncio.create_task(
                    send_final_callback(session_id, session)
                )
                
                return APIResponse(status="success", reply=reply)
            
            # Continue agent engagement
            reply = await agent_engine.generate_response(
                session_id,
                session["messages"],
                request.metadata.dict()
            )
            
            # Extract intelligence from the conversation
            intelligence = intelligence_extractor.extract_from_message(incoming_message)
            session_manager.update_intelligence(session_id, intelligence)
            
            return APIResponse(status="success", reply=reply)
        
        # Scam detection phase
        if not session.get("scam_detected"):
            # Analyze message for scam indicators
            is_scam, confidence = await scam_detector.detect_scam(
                incoming_message,
                conversation_history,
                request.metadata.dict()
            )
            
            if is_scam and confidence > 0.7:
                # Mark scam as detected
                session_manager.mark_scam_detected(session_id, confidence)
                session_manager.engage_agent(session_id)
                
                # Generate initial agent response
                reply = await agent_engine.generate_initial_response(
                    session_id,
                    incoming_message,
                    request.metadata.dict()
                )
                
                return APIResponse(status="success", reply=reply)
            else:
                # Not a scam yet, respond neutrally
                reply = await agent_engine.generate_neutral_response(
                    incoming_message,
                    request.metadata.dict()
                )
                return APIResponse(status="success", reply=reply)
        
        # Fallback response
        return APIResponse(
            status="success",
            reply="I'm sorry, I didn't quite understand. Could you please clarify?"
        )
        
    except Exception as e:
        # Log error in production
        print(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def send_final_callback(session_id: str, session: Dict[str, Any]):
    """
    Send final callback to GUVI endpoint
    This is called ONCE per session after scam engagement is complete
    """
    try:
        # Prepare extracted intelligence
        intelligence = session.get("extracted_intelligence", {})
        extracted_intel = ExtractedIntelligence(
            bankAccounts=intelligence.get("bank_accounts", []),
            upiIds=intelligence.get("upi_ids", []),
            phishingLinks=intelligence.get("phishing_links", []),
            phoneNumbers=intelligence.get("phone_numbers", []),
            suspiciousKeywords=intelligence.get("suspicious_keywords", [])
        )
        
        # Generate agent notes
        agent_notes = f"Session concluded after {len(session['messages'])} messages. "
        agent_notes += f"Scam confidence: {session.get('scam_confidence', 0):.2f}. "
        agent_notes += f"Intelligence extracted: {len(intelligence.get('upi_ids', []))} UPI IDs, "
        agent_notes += f"{len(intelligence.get('phone_numbers', []))} phone numbers, "
        agent_notes += f"{len(intelligence.get('phishing_links', []))} links."
        
        # Prepare callback payload
        callback_payload = FinalCallback(
            sessionId=session_id,
            scamDetected=True,
            totalMessagesExchanged=len(session["messages"]),
            extractedIntelligence=extracted_intel,
            agentNotes=agent_notes
        )
        
        # Send callback
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                GUVI_CALLBACK_URL,
                json=callback_payload.dict(),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"✓ Final callback sent successfully for session {session_id}")
                session_manager.mark_callback_sent(session_id)
            else:
                print(f"✗ Callback failed for session {session_id}: {response.status_code}")
                
    except Exception as e:
        print(f"Error sending final callback for session {session_id}: {str(e)}")


@app.get("/api/sessions/{session_id}")
async def get_session(
    session_id: str,
    x_api_key: str = Header(None, alias="x-api-key"),
    X_API_KEY: str = Header(None, alias="X-API-Key")
):
    """Get session details (for debugging/monitoring) - accepts both header formats"""
    # Check for API key in either header
    api_key = x_api_key or X_API_KEY
    
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    await validate_api_key(api_key)
    
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
