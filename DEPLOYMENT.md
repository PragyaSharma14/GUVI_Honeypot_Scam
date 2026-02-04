# Render.com Deployment Guide

## Step-by-Step Deployment Instructions

### Prerequisites
1. GitHub account
2. Render.com account (free tier works)
3. GROQ API KEY 

---

## Part 1: Prepare Repository

### 1. Push Code to GitHub

```bash
# Initialize git repository
cd honeypot-scam-detector
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: GUVI Honeypot API"

# Create main branch
git branch -M main

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/honeypot-scam-detector.git

# Push to GitHub
git push -u origin main
```

---

## Part 2: Deploy to Render

### 1. Create New Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** button (top right)
3. Select **"Web Service"**

### 2. Connect GitHub Repository

1. Click **"Connect a repository"**
2. Authorize Render to access your GitHub
3. Select **"honeypot-scam-detector"** repository
4. Click **"Connect"**

### 3. Configure Service Settings

**Basic Settings:**
- **Name**: `guvi-honeypot-api` (or any name you prefer)
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- Select **"Free"** (sufficient for hackathon)

### 4. Set Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

| Key | Value | Notes |
|-----|-------|-------|
| `OPENROUTER_API_KEY` | `sk-or-v1-xxxxx` | Your OpenRouter key |
| `API_KEY` | `your-secure-key` | Generate random string |
| `PYTHON_VERSION` | `3.11.0` | Python version |

**To generate secure API_KEY:**
```bash
# On Linux/Mac
openssl rand -hex 32

# Or use Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (2-3 minutes)
3. Render will:
   - Clone your repository
   - Install dependencies
   - Start the server
   - Assign a public URL

### 6. Get Your API URL

After deployment succeeds:
- Your API URL: `https://guvi-honeypot-api.onrender.com`
- Copy this URL for testing

---

## Part 3: Verify Deployment

### Test Health Endpoint

```bash
curl https://guvi-honeypot-api.onrender.com/
```

**Expected Response:**
```json
{
  "service": "Agentic Honey-Pot API",
  "status": "running",
  "version": "1.0.0"
}
```

### Test Chat Endpoint

```bash
curl -X POST https://guvi-honeypot-api.onrender.com/api/chat \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test_001",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked. Update KYC now.",
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

## Part 4: Monitor & Debug

### View Logs

1. Go to Render Dashboard
2. Select your service
3. Click **"Logs"** tab
4. See real-time logs

### Common Issues

#### ❌ Build Failed
**Cause**: Missing dependencies or syntax error

**Solution**:
1. Check logs for error message
2. Fix code locally
3. Push changes to GitHub
4. Render auto-deploys

#### ❌ Service Crashed
**Cause**: Missing environment variable

**Solution**:
1. Check logs: "OPENROUTER_API_KEY must be set"
2. Add missing env var in Render settings
3. Click **"Manual Deploy"** → **"Deploy latest commit"**

#### ❌ 403 Forbidden
**Cause**: Wrong API key

**Solution**:
- Check `x-api-key` header matches `API_KEY` env var
- Verify no extra spaces

---

## Part 5: Update After Changes

### Update Code

```bash
# Make changes to code
git add .
git commit -m "Update: description of changes"
git push origin main
```

Render will automatically detect changes and redeploy!

### Update Environment Variables

1. Go to Render Dashboard
2. Select service
3. Click **"Environment"** tab
4. Edit variables
5. Click **"Save Changes"**
6. Service will restart automatically

---

## Part 6: Free Tier Limitations

**Render Free Tier:**
- ✅ 750 hours/month (sufficient)
- ✅ Automatic HTTPS
- ✅ Custom domains
- ⚠️ Spins down after 15 min inactivity (cold start ~30 sec)
- ⚠️ 512 MB RAM limit

**Tips:**
- For hackathon demo, ping endpoint before presenting
- Upgrade to paid tier ($7/month) for always-on service

---

## Part 7: For Hackathon Submission

### Share These URLs:

**API Base URL:**
```
https://guvi-honeypot-api.onrender.com
```

**Health Check:**
```
https://guvi-honeypot-api.onrender.com/
```

**Chat Endpoint:**
```
https://guvi-honeypot-api.onrender.com/api/chat
```

**API Key:** (Provide separately, don't commit to Git)

---

## Part 8: Post-Deployment Checklist

- [ ] Deployment successful (green status in Render)
- [ ] Health endpoint returns 200 OK
- [ ] Chat endpoint accepts requests
- [ ] Environment variables configured
- [ ] Logs show no errors
- [ ] Test with sample scam message
- [ ] GUVI callback URL verified
- [ ] API documentation ready
- [ ] Demo ready for presentation

---

## Need Help?

### Render Issues
- Check: https://render.com/docs
- Status: https://status.render.com

### OpenRouter Issues
- Docs: https://openrouter.ai/docs
- Check credits: https://openrouter.ai/credits

### Code Issues
- Review logs in Render Dashboard
- Check README.md troubleshooting section
- Verify all environment variables are set

---

**You're All Set! 🚀**

Your honeypot API is now live and ready for the hackathon!
