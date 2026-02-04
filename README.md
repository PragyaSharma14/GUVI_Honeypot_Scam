# Agentic Honey-Pot for Scam Detection & Intelligence Extraction

**GUVI Hackathon Project**

A production-ready REST API that detects scam attempts and deploys an autonomous AI agent to engage scammers, extract intelligence, and report findings.

---

## 🎯 Features

✅ **Scam Detection**: AI-powered classification using DeepSeek-R1 via OpenRouter  
✅ **Autonomous Agent**: Human-like persona (Ramesh Kumar) to engage scammers  
✅ **Intelligence Extraction**: Extracts UPI IDs, phone numbers, bank accounts, phishing links  
✅ **Multi-turn Conversations**: Session-based conversation management  
✅ **Secure API**: Protected with x-api-key header authentication  
✅ **GUVI Integration**: Automatic callback with extracted intelligence  
✅ **Render.com Ready**: Direct deployment without ngrok  

---

## 📁 Project Structure

```
honeypot-scam-detector/
├── main.py                      # FastAPI application & routing
├── scam_detector.py             # LLM-based scam detection
├── agent_engine.py              # Agentic response generation
├── intelligence_extractor.py    # Regex-based intelligence extraction
├── session_manager.py           # Session state management
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── render.yaml                  # Render deployment config
└── README.md                    # This file
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
# Navigate to project directory
cd honeypot-scam-detector

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` and add:

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
API_KEY=your-secret-api-key-here
PORT=8000
```

**Get OpenRouter API Key:**
1. Visit https://openrouter.ai/keys
2. Sign up / Login
3. Create new API key
4. Copy key to `.env`

### 3. Run Locally

```bash
python main.py
```

API will be available at: `http://localhost:8000`

Test health endpoint:
```bash
curl http://localhost:8000/
```

---

## 🌐 Deploy to Render.com

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit - GUVI Honeypot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/honeypot-scam-detector.git
git push -u origin main
```

### Step 2: Create Render Service

1. Go to https://render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `guvi-honeypot-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3: Set Environment Variables

In Render Dashboard → Environment:

```
OPENROUTER_API_KEY = sk-or-v1-xxxxxxxxxxxxx
API_KEY = your-secure-random-key-here
```

### Step 4: Deploy

Click **"Create Web Service"**

Your API will be live at: `https://guvi-honeypot-api.onrender.com`

---

## 📡 API Documentation

### Base URL
- **Local**: `http://localhost:8000`
- **Production**: `https://your-app.onrender.com`

### Endpoints

#### 1. Health Check
```http
GET /
```

**Response:**
```json
{
  "service": "Agentic Honey-Pot API",
  "status": "running",
  "version": "1.0.0"
}
```

---

#### 2. Chat Endpoint (Main)

```http
POST /api/chat
```

**Headers:**
```
x-api-key: your-secret-api-key
Content-Type: application/json
```

**Request Body:**
```json
{
  "sessionId": "session_123",
  "message": {
    "sender": "scammer",
    "text": "Dear customer, your bank account will be blocked in 24 hours. Click here to update KYC immediately.",
    "timestamp": 1704123456789
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "Oh my god, really sir? My account will be blocked? Please tell me what I should do. I am not good with these technical things."
}
```

---

#### 3. Get Session Details

```http
GET /api/sessions/{session_id}
```

**Headers:**
```
x-api-key: your-secret-api-key
```

**Response:**
```json
{
  "session_id": "session_123",
  "scam_detected": true,
  "agent_engaged": true,
  "extracted_intelligence": {
    "upi_ids": ["scammer@paytm"],
    "phone_numbers": ["9876543210"],
    "bank_accounts": [],
    "phishing_links": ["http://fake-bank.com/kyc"],
    "suspicious_keywords": ["kyc", "blocked", "urgent"]
  },
  "messages": [...]
}
```

---

## 🔄 Workflow

```
User Message → Scam Detection → Agent Engagement → Intelligence Extraction → Final Callback
```

### Detailed Flow:

1. **Message Received**
   - Validate API key
   - Get/create session

2. **Scam Detection Phase**
   - LLM analyzes message for scam indicators
   - If confidence > 70% → Scam detected
   - Activate agent engagement

3. **Agent Engagement Phase**
   - Agent responds as "Ramesh Kumar" (confused customer)
   - Asks questions to extract intelligence
   - Never reveals scam detection

4. **Intelligence Extraction**
   - Regex patterns extract:
     - UPI IDs (e.g., `scammer@paytm`)
     - Phone numbers (10 digits)
     - Bank accounts (11-18 digits)
     - URLs
     - Suspicious keywords

5. **Session Conclusion**
   - After 8+ engaged messages AND
   - (High-value intel extracted OR 15+ total messages)
   - Send final callback to GUVI

6. **Final Callback**
   ```http
   POST https://hackathon.guvi.in/api/updateHoneyPotFinalResult
   ```
   ```json
   {
     "sessionId": "session_123",
     "scamDetected": true,
     "totalMessagesExchanged": 12,
     "extractedIntelligence": {
       "bankAccounts": [],
       "upiIds": ["scammer@paytm"],
       "phishingLinks": ["http://fake-bank.com"],
       "phoneNumbers": ["9876543210"],
       "suspiciousKeywords": ["kyc", "update", "urgent"]
     },
     "agentNotes": "Session concluded after 12 messages. Scam confidence: 0.92. Intelligence extracted: 1 UPI IDs, 1 phone numbers, 1 links."
   }
   ```

---

## 🧠 LLM Integration

### Model Used
- **DeepSeek-R1** via OpenRouter
- Alternative: Any Groq-hosted model

### LLM Prompts

#### Scam Detector Prompt
```
You are an expert scam detection AI system specializing in Indian scam patterns.

COMMON INDIAN SCAM PATTERNS:
- Fake KYC update requests
- Prize/lottery notifications
- Fake delivery messages
- Account blocking threats
- OTP/PIN requests
- Digital arrest scams
...

Respond ONLY with JSON:
{
  "is_scam": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation",
  "scam_type": "KYC|Prize|Delivery|..."
}
```

#### Agent Persona Prompt
```
You are Ramesh Kumar, a 58-year-old bank customer from Mumbai.

PERSONA TRAITS:
- Middle-class Indian, not tech-savvy
- Polite, cooperative, slightly confused
- Trusting of "official" communications
- Simple conversational English with Hindi words

CRITICAL RULES:
1. NEVER reveal you know this is a scam
2. NEVER accuse the sender
3. Act genuinely confused
4. Ask questions to extract information

EXAMPLE:
Bad: "This seems like a scam."
Good: "Oh my god really? Please tell me what to do sir."
```

---

## 🛡️ Security Features

1. **API Key Authentication**
   - All endpoints require `x-api-key` header
   - Configurable via environment variable

2. **No Sensitive Data Storage**
   - Sessions stored in-memory only
   - No database required

3. **Rate Limiting** (Recommended for Production)
   - Add middleware for rate limiting
   - Example: slowapi library

---

## 🔍 Intelligence Extraction Patterns

### UPI IDs
```regex
[\w\.-]+@[\w-]+
```
Validates against known UPI handles: `@paytm`, `@ybl`, `@okaxis`, etc.

### Phone Numbers
```regex
(?:\+91|91|0)?[6-9]\d{9}
```
Indian mobile numbers (10 digits starting with 6-9)

### Bank Accounts
```regex
\d{9,18}
```
9-18 digit sequences (excludes phone numbers)

### URLs
```regex
https?://[^\s]+|www\.[^\s]+|bit\.ly/[^\s]+
```

### Suspicious Keywords
```python
['kyc', 'otp', 'urgent', 'blocked', 'verify', 'prize', 
 'lottery', 'aadhaar', 'pan', 'refund', 'arrest', ...]
```

---

## 🧪 Testing

### Test Scam Message
```bash
curl -X POST https://your-app.onrender.com/api/chat \
  -H "x-api-key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test_001",
    "message": {
      "sender": "scammer",
      "text": "URGENT: Your SBI account will be blocked. Update KYC at http://sbi-kyc.fake.com or call 9876543210",
      "timestamp": 1704123456789
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

### Expected Response
```json
{
  "status": "success",
  "reply": "Oh no sir! My SBI account? Please help me, what should I do? Should I call that number you mentioned?"
}
```

---

## 📊 Monitoring

### Session Status
```bash
curl -X GET https://your-app.onrender.com/api/sessions/test_001 \
  -H "x-api-key: your-api-key"
```

### Logs (Render Dashboard)
- View real-time logs in Render dashboard
- Monitor scam detection events
- Track callback success/failures

---

## ⚠️ Important Notes

### Ethical Guidelines
1. **No Real Identity Impersonation**: Agent uses fictional persona only
2. **No Illegal Instructions**: System does not facilitate illegal activities
3. **No Harassment**: Polite engagement only
4. **Responsible Handling**: Intelligence used for security research only

### Production Checklist
- [ ] Set strong `API_KEY` (use random generator)
- [ ] Configure `OPENROUTER_API_KEY`
- [ ] Test all endpoints before submission
- [ ] Verify GUVI callback URL is correct
- [ ] Monitor logs for errors
- [ ] Document any custom modifications

---

## 🐛 Troubleshooting

### Issue: "Invalid API Key"
**Solution**: Check `x-api-key` header matches environment variable

### Issue: "OpenRouter API error"
**Solution**: Verify `OPENROUTER_API_KEY` is valid and has credits

### Issue: "Callback failed"
**Solution**: Check GUVI endpoint URL and network connectivity

### Issue: Agent not engaging
**Solution**: Check scam detection confidence threshold (default: 0.7)

---

## 📝 Code Comments

All code files include:
- Function-level docstrings
- Inline comments explaining logic
- Type hints for clarity
- Error handling with logging

---

## 🏆 Hackathon Submission

This project is production-ready and includes:

✅ Complete FastAPI implementation  
✅ LLM integration (DeepSeek-R1)  
✅ Scam detection logic  
✅ Autonomous agent engine  
✅ Intelligence extraction  
✅ Session management  
✅ GUVI callback integration  
✅ Render.com deployment config  
✅ Comprehensive documentation  
✅ No placeholders or pseudocode  

---

## 📄 License

This project is created for GUVI Hackathon. For educational and security research purposes only.

---

## 👨‍💻 Support

For issues or questions during the hackathon, check:
1. This README
2. Code comments
3. Render deployment logs
4. OpenRouter API documentation

---

**Built for GUVI Hackathon 2024**  
*Protecting users through intelligent scam detection*
