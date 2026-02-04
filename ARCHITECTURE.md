# System Architecture - Agentic Honeypot

## Overview

The Agentic Honeypot is a multi-stage intelligent system that detects scams, engages scammers with a believable persona, and extracts actionable intelligence.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         INCOMING REQUEST                         │
│  POST /api/chat with sessionId, message, conversationHistory    │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                    ┌───────────▼──────────┐
                    │   API Key Validator   │
                    │  (Security Gateway)   │
                    └───────────┬──────────┘
                                │
                    ┌───────────▼──────────┐
                    │   Session Manager     │
                    │  - Get/Create Session │
                    │  - Store Messages     │
                    │  - Track State        │
                    └───────────┬──────────┘
                                │
                ┌───────────────▼────────────────┐
                │      Scam Detected?            │
                │  (Check session.scam_detected) │
                └───┬─────────────────────┬──────┘
                    │ NO                  │ YES
        ┌───────────▼─────────┐   ┌──────▼────────────────┐
        │   Scam Detector      │   │  Agent Already        │
        │   - Call LLM         │   │  Engaged?             │
        │   - Analyze Intent   │   └──────┬────────────────┘
        │   - Return Score     │          │
        └───────────┬──────────┘  ┌───────▼─────────────┐
                    │             │   Agent Engine       │
        ┌───────────▼──────────┐  │   - Generate Reply   │
        │  Confidence > 0.7?   │  │   - Stay In Persona  │
        └───┬──────────────┬───┘  │   - Extract Intel    │
            │ NO           │ YES  └─────────┬────────────┘
    ┌───────▼──────┐  ┌───▼──────────────┐        │
    │  Neutral      │  │ Mark Scam        │        │
    │  Response     │  │ Detected         │        │
    │               │  │ Engage Agent     │        │
    └───────┬───────┘  └──────┬───────────┘        │
            │                 │                    │
            │         ┌───────▼──────────────┐     │
            │         │  Intelligence        │◄────┘
            │         │  Extractor           │
            │         │  - Regex Patterns    │
            │         │  - Extract UPI, etc. │
            │         └──────┬───────────────┘
            │                │
            │        ┌───────▼──────────────┐
            │        │  Should Conclude?     │
            │        │  - 8+ messages        │
            │        │  - High-value intel   │
            │        │  - OR 15+ messages    │
            │        └───┬──────────────┬────┘
            │            │ NO           │ YES
            │    ┌───────▼──────┐  ┌───▼─────────────────┐
            │    │  Continue     │  │  Final Response +   │
            │    │  Engagement   │  │  GUVI Callback      │
            │    └───────┬───────┘  └─────────────────────┘
            │            │
        ┌───▼────────────▼──────┐
        │   Return JSON Reply    │
        │   { status, reply }    │
        └────────────────────────┘
```

---

## Component Details

### 1. Main Application (`main.py`)

**Responsibilities:**
- FastAPI application setup
- Route handling (`/api/chat`, `/api/sessions/{id}`)
- API key validation
- Orchestrate component calls
- Trigger GUVI callback

**Key Functions:**
- `chat_endpoint()` - Main conversation handler
- `send_final_callback()` - Async callback to GUVI
- `validate_api_key()` - Security middleware

**Data Flow:**
```
Request → Validate → Session → Detect/Engage → Extract → Respond
```

---

### 2. Scam Detector (`scam_detector.py`)

**Purpose:** Classify messages as scam or legitimate using LLM

**Technology:**
- OpenRouter API (DeepSeek-R1)
- Temperature: 0.3 (deterministic)
- Max tokens: 500

**Input:**
- Message text
- Conversation history (last 5 messages)
- Metadata (channel, language, locale)

**Output:**
```json
{
  "is_scam": bool,
  "confidence": float (0.0-1.0),
  "reasoning": string,
  "scam_type": string
}
```

**Scam Types:**
- KYC (fake verification)
- Prize (lottery/winnings)
- Delivery (fake courier)
- Threat (account blocking, arrest)
- Financial (loans, investments)
- Other

**Detection Indicators:**
1. Urgency keywords
2. Sensitive data requests (OTP, PIN, CVV)
3. Unsolicited offers
4. Threats
5. Suspicious links
6. Impersonation
7. Payment requests
8. Poor grammar

---

### 3. Agent Engine (`agent_engine.py`)

**Purpose:** Generate human-like responses as "Ramesh Kumar"

**Persona:**
- Name: Ramesh Kumar
- Age: 58 years
- Location: Mumbai, India
- Profile: Middle-class, not tech-savvy, trusting

**Behavior Traits:**
- Polite and cooperative
- Slightly confused by tech terms
- Uses simple English + Hindi words
- Makes grammatical mistakes
- Takes time to understand
- Asks clarifying questions
- Shows concern about account safety

**Response Types:**

1. **Initial Response** (After scam detection)
   - Show concern
   - Willingness to help
   - Ask clarifying question
   - Length: 2-3 sentences

2. **Ongoing Responses** (During engagement)
   - Continue conversation
   - Extract specific information
   - Maintain character
   - Length: 2-4 sentences

3. **Neutral Response** (Before scam detected)
   - Generic, polite response
   - No sensitive info
   - Length: 1-2 sentences

4. **Final Response** (Session conclusion)
   - Polite exit
   - Believable excuse ("need to go", "check with family")
   - Length: 1-2 sentences

**LLM Configuration:**
- Model: DeepSeek-R1
- Temperature: 0.8 (natural variation)
- Max tokens: 200

**Example Responses:**

❌ **Bad:**
> "I don't believe you. This is a scam."

✅ **Good:**
> "Oh my god really sir? My account will be blocked? Please tell me what to do. I am not good with computer things."

---

### 4. Intelligence Extractor (`intelligence_extractor.py`)

**Purpose:** Extract actionable intelligence using regex patterns

**Extraction Targets:**

1. **UPI IDs**
   - Pattern: `[\w\.-]+@[\w-]+`
   - Validates against known UPI handles: `@paytm`, `@ybl`, `@okaxis`, etc.
   - Example: `scammer@paytm`

2. **Phone Numbers**
   - Pattern: `(?:\+91|91|0)?[6-9]\d{9}`
   - Indian mobile numbers (10 digits, 6-9 prefix)
   - Cleans prefixes (+91, 91, 0)
   - Example: `9876543210`

3. **Bank Accounts**
   - Pattern: `\d{9,18}`
   - 9-18 digit sequences
   - Excludes phone numbers
   - Minimum 11 digits for bank accounts
   - Example: `12345678901234`

4. **Phishing Links**
   - Pattern: `https?://[^\s]+|www\.[^\s]+|bit\.ly/[^\s]+`
   - Full URLs, shortened links
   - Example: `http://fake-bank.com/kyc`

5. **Suspicious Keywords**
   - Pre-defined list of 50+ keywords
   - Categories: banking, urgency, threats, offers, technical
   - Examples: `kyc`, `otp`, `urgent`, `blocked`, `verify`

**Intelligence Aggregation:**
- Deduplicates across conversation
- Tracks cumulative intelligence per session
- Returns as sets (converted to lists for JSON)

**High-Value Intelligence Criteria:**
- At least 1 UPI ID OR
- At least 1 phone number AND 1 link OR
- At least 1 bank account

---

### 5. Session Manager (`session_manager.py`)

**Purpose:** Manage conversation state and session lifecycle

**Session Structure:**
```python
{
  "session_id": str,
  "created_at": ISO timestamp,
  "messages": [
    {
      "sender": "scammer|user",
      "text": str,
      "timestamp": int,
      "datetime": ISO timestamp
    }
  ],
  "scam_detected": bool,
  "scam_confidence": float,
  "scam_detected_at": ISO timestamp,
  "agent_engaged": bool,
  "agent_engaged_at": ISO timestamp,
  "extracted_intelligence": {
    "upi_ids": [],
    "phone_numbers": [],
    "bank_accounts": [],
    "phishing_links": [],
    "suspicious_keywords": []
  },
  "callback_sent": bool,
  "callback_sent_at": ISO timestamp,
  "should_conclude": bool
}
```

**Key Operations:**

1. **Session Creation**
   - Auto-creates on first message
   - Initializes empty state

2. **Message Tracking**
   - Appends to conversation history
   - Timestamps each message

3. **State Transitions**
   - Not Detected → Scam Detected
   - Scam Detected → Agent Engaged
   - Agent Engaged → Should Conclude
   - Should Conclude → Callback Sent

4. **Conclusion Logic**
   - Minimum 8 messages after engagement
   - AND (High-value intelligence OR 15+ total messages)

**Storage:**
- In-memory dictionary (per-process)
- No database required
- Resets on server restart

---

## Data Flow Diagrams

### Flow 1: First Message (Scam Detection)

```
User/Scammer Message
        │
        ▼
┌───────────────────┐
│  Session Manager  │
│  - Create Session │
│  - Store Message  │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Scam Detector    │
│  - Call LLM       │
│  - Get Confidence │
└────────┬──────────┘
         │
    ┌────▼────┐
    │ Scam?   │
    └─┬────┬──┘
  YES │    │ NO
      │    │
      │    └──► Neutral Response
      │
      ▼
┌───────────────────┐
│ Mark Scam         │
│ Engage Agent      │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Agent Engine      │
│ Generate Initial  │
│ Response          │
└────────┬──────────┘
         │
         ▼
    Return Reply
```

### Flow 2: Ongoing Engagement

```
Scammer Reply
      │
      ▼
┌───────────────────┐
│ Add to Session    │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Agent Engine      │
│ Generate Response │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Intel Extractor   │
│ Extract from Msg  │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Update Session    │
│ Intelligence      │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Should Conclude?  │
└─┬──────────────┬──┘
  │ YES          │ NO
  │              │
  │              └──► Continue Engagement
  │
  ▼
┌───────────────────┐
│ Final Response    │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ GUVI Callback     │
│ (Async)           │
└───────────────────┘
```

---

## API Specifications

### Request Format

**Endpoint:** `POST /api/chat`

**Headers:**
```
x-api-key: string (required)
Content-Type: application/json
```

**Body:**
```json
{
  "sessionId": "string",
  "message": {
    "sender": "scammer | user",
    "text": "string",
    "timestamp": number
  },
  "conversationHistory": [
    {
      "sender": "string",
      "text": "string",
      "timestamp": number
    }
  ],
  "metadata": {
    "channel": "SMS | WhatsApp | Email | Chat",
    "language": "English",
    "locale": "IN"
  }
}
```

### Response Format

**Success:**
```json
{
  "status": "success",
  "reply": "string"
}
```

**Error (403):**
```json
{
  "detail": "Invalid API Key"
}
```

**Error (500):**
```json
{
  "detail": "Internal server error"
}
```

### GUVI Callback Format

**Endpoint:** `POST https://hackathon.guvi.in/api/updateHoneyPotFinalResult`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "sessionId": "string",
  "scamDetected": true,
  "totalMessagesExchanged": number,
  "extractedIntelligence": {
    "bankAccounts": ["string"],
    "upiIds": ["string"],
    "phishingLinks": ["string"],
    "phoneNumbers": ["string"],
    "suspiciousKeywords": ["string"]
  },
  "agentNotes": "string"
}
```

---

## Security Considerations

### 1. API Key Authentication
- Required on all endpoints (except health check)
- Validated via middleware
- Stored in environment variable

### 2. Input Validation
- Pydantic models enforce schema
- Type checking on all fields
- Enum validation for sender type

### 3. Rate Limiting (Recommended)
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/chat")
@limiter.limit("10/minute")
async def chat_endpoint(...):
    ...
```

### 4. Timeout Protection
- HTTP client timeout: 30 seconds
- Prevents hanging requests

### 5. Error Handling
- Try-catch blocks on all LLM calls
- Graceful degradation
- No sensitive data in error messages

---

## Scalability Considerations

### Current Architecture (Free Tier)
- **Storage:** In-memory (resets on restart)
- **Concurrency:** Async/await for I/O operations
- **Limits:** Render free tier (512 MB RAM)

### Production Improvements

1. **Add Database**
   ```python
   # PostgreSQL for session persistence
   from sqlalchemy import create_engine
   DATABASE_URL = os.getenv("DATABASE_URL")
   ```

2. **Add Redis Cache**
   ```python
   # Cache LLM responses
   import redis
   cache = redis.from_url(os.getenv("REDIS_URL"))
   ```

3. **Add Queue System**
   ```python
   # Celery for async callbacks
   from celery import Celery
   celery = Celery('honeypot', broker=os.getenv("REDIS_URL"))
   ```

4. **Horizontal Scaling**
   - Deploy multiple instances
   - Load balancer (Render handles this)
   - Share session state via Redis

---

## Monitoring & Observability

### Key Metrics to Track

1. **API Metrics**
   - Request rate
   - Response time
   - Error rate
   - 4xx/5xx status codes

2. **Scam Detection Metrics**
   - Detection rate
   - False positive rate
   - Average confidence score

3. **Engagement Metrics**
   - Messages per session
   - Session duration
   - Conclusion rate

4. **Intelligence Metrics**
   - UPI IDs extracted
   - Phone numbers extracted
   - Links extracted
   - High-value intel percentage

### Logging Strategy

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Log important events
logger.info(f"Scam detected for session {session_id}")
logger.warning(f"Callback failed for session {session_id}")
logger.error(f"LLM call failed: {error}")
```

---

## Testing Strategy

### 1. Unit Tests
```python
# test_intelligence_extractor.py
def test_upi_extraction():
    extractor = IntelligenceExtractor()
    text = "Send money to scammer@paytm"
    result = extractor.extract_from_message(text)
    assert "scammer@paytm" in result["upi_ids"]
```

### 2. Integration Tests
```python
# test_api.py
async def test_scam_detection():
    response = await client.post("/api/chat", json={...})
    assert response.status_code == 200
    assert "reply" in response.json()
```

### 3. Load Tests
```bash
# Using locust
locust -f locustfile.py --host=https://your-api.com
```

---

## Deployment Architecture (Render.com)

```
┌─────────────────────────────────────────┐
│         Render.com Platform             │
│  ┌───────────────────────────────────┐  │
│  │     Web Service Container         │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │    FastAPI Application      │  │  │
│  │  │    (uvicorn)                │  │  │
│  │  └─────────────┬───────────────┘  │  │
│  │                │                   │  │
│  │  ┌─────────────▼───────────────┐  │  │
│  │  │   Session Manager           │  │  │
│  │  │   (In-Memory Storage)       │  │  │
│  │  └─────────────┬───────────────┘  │  │
│  └────────────────┼───────────────────┘  │
│                   │                      │
│         ┌─────────▼──────────┐           │
│         │  Environment Vars   │           │
│         │  - OPENROUTER_KEY   │           │
│         │  - API_KEY          │           │
│         └─────────────────────┘           │
└─────────────────┬───────────────────────┘
                  │
      ┌───────────▼──────────┐
      │   HTTPS Load         │
      │   Balancer           │
      └───────────┬──────────┘
                  │
          Public Internet
```

---

## Future Enhancements

1. **Multi-Language Support**
   - Hindi, Tamil, Telugu translations
   - Language-specific personas

2. **Advanced Intelligence**
   - Named entity recognition
   - Sentiment analysis
   - Network graph of scammers

3. **Real-Time Dashboard**
   - Live session monitoring
   - Intelligence visualization
   - Scam pattern analytics

4. **ML-Based Detection**
   - Train custom scam classifier
   - Reduce dependency on LLM
   - Faster classification

5. **Integration APIs**
   - Webhook notifications
   - Export to SIEM systems
   - Slack/Discord alerts

---

## Conclusion

This architecture provides:
- ✅ Modular, maintainable code
- ✅ Scalable design patterns
- ✅ Security best practices
- ✅ Production-ready deployment
- ✅ Clear data flows
- ✅ Comprehensive documentation

Ready for GUVI Hackathon submission! 🚀
