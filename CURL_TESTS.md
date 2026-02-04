# API Testing with cURL

This file contains ready-to-use cURL commands for testing the Honeypot API.

## Setup

Replace these placeholders:
- `YOUR_API_KEY` - Your API key from environment variable
- `YOUR_RENDER_URL` - Your Render.com deployment URL (or `http://localhost:8000` for local)

---

## 1. Health Check

```bash
curl -X GET https://guvi-honeypot-api.onrender.com/
```

---

## 2. Test KYC Scam Detection

```bash
curl -X POST https://guvi-honeypot-api.onrender.com/api/chat \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "kyc_scam_001",
    "message": {
      "sender": "scammer",
      "text": "URGENT: Your SBI account will be blocked within 24 hours. Update KYC immediately at http://sbi-kyc-update.com or call 9876543210 now.",
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

---

## 3. Test Prize Scam

```bash
curl -X POST https://guvi-honeypot-api.onrender.com/api/chat \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "prize_scam_001",
    "message": {
      "sender": "scammer",
      "text": "Congratulations! You won Rs 10 lakh in KBC lottery. Send processing fee Rs 5000 to UPI: winnerlottery@paytm to claim your prize.",
      "timestamp": 1704123456789
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "WhatsApp",
      "language": "English",
      "locale": "IN"
    }
  }'
```

---

## 4. Test Delivery Scam

```bash
curl -X POST https://guvi-honeypot-api.onrender.com/api/chat \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "delivery_scam_001",
    "message": {
      "sender": "scammer",
      "text": "Your parcel from Amazon is held at customs. Pay Rs 500 customs duty at bit.ly/customs-payment or contact 8765432109 for assistance.",
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

---

## 5. Test OTP Scam

```bash
curl -X POST https://guvi-honeypot-api.onrender.com/api/chat \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "otp_scam_001",
    "message": {
      "sender": "scammer",
      "text": "Your HDFC Bank OTP is 948372. Do NOT share this with anyone. If you did not request this, call our fraud department at 9123456789 immediately.",
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

---

## 6. Test Multi-Turn Conversation

### First Message (Scammer)
```bash
curl -X POST https://guvi-honeypot-api.onrender.com/api/chat \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "conversation_001",
    "message": {
      "sender": "scammer",
      "text": "Dear customer, your PAN card is linked to illegal activities. You must verify immediately or you will be arrested.",
      "timestamp": 1704123456789
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "WhatsApp",
      "language": "English",
      "locale": "IN"
    }
  }'
```

### Second Message (Continue Conversation)
```bash
curl -X POST https://guvi-honeypot-api.onrender.com/api/chat \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "conversation_001",
    "message": {
      "sender": "scammer",
      "text": "Sir, we need your Aadhaar number and bank account details to clear your name from the investigation.",
      "timestamp": 1704123457000
    },
    "conversationHistory": [
      {
        "sender": "scammer",
        "text": "Dear customer, your PAN card is linked to illegal activities. You must verify immediately or you will be arrested.",
        "timestamp": 1704123456789
      },
      {
        "sender": "user",
        "text": "What? Illegal activities? I have not done anything wrong sir. How can I verify?",
        "timestamp": 1704123456800
      }
    ],
    "metadata": {
      "channel": "WhatsApp",
      "language": "English",
      "locale": "IN"
    }
  }'
```

---

## 7. Get Session Details

```bash
curl -X GET https://guvi-honeypot-api.onrender.com/api/sessions/kyc_scam_001 \
  -H "x-api-key: YOUR_API_KEY"
```

---

## 8. Test Legitimate Message (Should NOT Trigger Agent)

```bash
curl -X POST https://guvi-honeypot-api.onrender.com/api/chat \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "legitimate_001",
    "message": {
      "sender": "user",
      "text": "Hi, I wanted to check if you received my payment for last month?",
      "timestamp": 1704123456789
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "Chat",
      "language": "English",
      "locale": "IN"
    }
  }'
```

---

## 9. Test Investment Scam

```bash
curl -X POST https://guvi-honeypot-api.onrender.com/api/chat \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "investment_scam_001",
    "message": {
      "sender": "scammer",
      "text": "Guaranteed returns! Invest Rs 50,000 in cryptocurrency and earn Rs 5 lakh in 30 days. Limited slots available. Register at crypto-invest-india.com or WhatsApp 9988776655.",
      "timestamp": 1704123456789
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "WhatsApp",
      "language": "English",
      "locale": "IN"
    }
  }'
```

---

## 10. Test Digital Arrest Scam

```bash
curl -X POST https://guvi-honeypot-api.onrender.com/api/chat \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "digital_arrest_001",
    "message": {
      "sender": "scammer",
      "text": "This is CBI officer speaking. Your Aadhaar is used in drug trafficking case. You are under digital arrest. Send Rs 2 lakh to clear your name to account 123456789012. Call 9876543210.",
      "timestamp": 1704123456789
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "WhatsApp",
      "language": "English",
      "locale": "IN"
    }
  }'
```

---

## Testing Workflow

1. **Start with Health Check** - Verify API is running
2. **Test Individual Scams** - Run scam scenarios one by one
3. **Check Session Details** - Verify intelligence extraction
4. **Test Multi-Turn** - Engage in longer conversation
5. **Verify GUVI Callback** - Check logs for callback execution

---

## Expected Responses

### Successful Response Format:
```json
{
  "status": "success",
  "reply": "Agent's response here..."
}
```

### Error Response (Wrong API Key):
```json
{
  "detail": "Invalid API Key"
}
```

### Session Details Response:
```json
{
  "session_id": "kyc_scam_001",
  "scam_detected": true,
  "agent_engaged": true,
  "scam_confidence": 0.92,
  "extracted_intelligence": {
    "upi_ids": ["winnerlottery@paytm"],
    "phone_numbers": ["9876543210"],
    "bank_accounts": [],
    "phishing_links": ["http://sbi-kyc-update.com"],
    "suspicious_keywords": ["urgent", "blocked", "kyc", "update"]
  },
  "messages": [...]
}
```

---

## Quick Test Script (Bash)

```bash
#!/bin/bash

API_URL="https://guvi-honeypot-api.onrender.com"
API_KEY="your-api-key-here"

echo "Testing Honeypot API..."

# Health Check
echo -e "\n1. Health Check"
curl -s "$API_URL/" | jq

# Test Scam
echo -e "\n2. Test Scam Detection"
curl -s -X POST "$API_URL/api/chat" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test_001",
    "message": {
      "sender": "scammer",
      "text": "Your account will be blocked. Update KYC now at fake-bank.com",
      "timestamp": 1704123456789
    },
    "conversationHistory": [],
    "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
  }' | jq

echo -e "\nTests Complete!"
```

Save as `test.sh`, make executable with `chmod +x test.sh`, and run with `./test.sh`

---

## Notes

- Replace `YOUR_API_KEY` with actual key from `.env`
- Replace `guvi-honeypot-api.onrender.com` with your actual Render URL
- Use `http://localhost:8000` for local testing
- Add ` | jq` at the end for formatted JSON output (requires jq installed)
