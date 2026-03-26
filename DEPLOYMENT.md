# 🚀 Deployment Guide - FREE Hosting

This guide walks you through deploying the Dodge AI Project to the **free tier** of Railway.app or Render.com **without sharing account credentials**.

---

## 📋 Prerequisites

You'll need 3 free accounts (10 minutes to set up):

1. **GitHub Account** - To host your code (free)
2. **Neo4j Aura Account** - For your database (free tier: 200GB storage, up to 100k requests/month)
3. **OpenRouter Account** - For AI/LLM calls (free tier: \$5 credits to start)

---

## 🔧 Step 1: Set Up Your Free Neo4j Database

### 1.1 Create Neo4j Aura Account
- Go to **https://neo4j.com/cloud/platform/aura-graph-database/** 
- Click **"Start Free"**
- Sign up with email/password
- Verify email

### 1.2 Create Your First Instance
- Click **"Create Database"**
- Name: `dodge-ai-prod`
- Region: Choose closest to you
- Wait for instance to start (1-2 minutes)

### 1.3 Get Your Connection String
- Click on your instance
- Copy the **"Connection URI"** (looks like: `neo4j+ssc://xxxxx.neo4j.io`)
- Copy **"Username"** (default: `neo4j`)
- Copy **"Password"** (one-time display - save it!)

**⚠️ Save these securely - you'll need them for Railway config**

---

## 🔑 Step 2: Get Your OpenRouter API Key

### 2.1 Create OpenRouter Account
- Go to **https://openrouter.ai/**
- Click **"Sign in"** → **"Create account"**
- Sign up with email/password (or GitHub OAuth)

### 2.2 Generate API Key
- After signup, go to **https://openrouter.ai/keys**
- Click **"Create Key"**
- Name it: `dodge-ai`
- Copy the key (starts with `sk-or-`)

**⚠️ Save this key - you'll need it for Railway config**

---

## 📤 Step 3: Push Code to GitHub

### 3.1 Create GitHub Repository
- Go to **https://github.com/new**
- Repository name: `dodge-ai-project`
- Description: "Graph-based data modeling system"
- Choose **Public** (required for Railway free tier to connect)
- Click **"Create repository"**

### 3.2 Push Your Code
```bash
cd /path/to/dodge-ai-project
git init
git add .
git commit -m "Initial commit: Graph AI project ready for deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/dodge-ai-project.git
git push -u origin main
```

---

## 🚀 Step 4: Deploy to Railway.app

### 4.1 Create Railway Account
- Go to **https://railway.app**
- Click **"Create Account"**
- Sign in with GitHub (easiest option)
- Authorize Railway to access your GitHub account

### 4.2 Create New Project
- Click **"Create New Project"**
- Select **"Deploy from GitHub repo"**
- Install Railway GitHub app on your account
- Select `dodge-ai-project` repository
- Click **"Deploy"** (Railway will auto-detect Python + start deployment)

### 4.3 Set Environment Variables
Railway will open your project. Now set environment variables:

**In Railway Dashboard:**
1. Go to your project
2. Click on the **"Web Service"** (your Python app)
3. Click **"Variables"** tab
4. Add these variables:

```
NEO4J_URI             = neo4j+ssc://xxxxx.neo4j.io  [from Neo4j Aura]
NEO4J_USER            = neo4j                       [from Neo4j Aura]
NEO4J_PASSWORD        = your_password               [from Neo4j Aura]
OPENROUTER_API_KEY    = sk-or-xxxxxx               [from OpenRouter]
HOST                  = 0.0.0.0
PORT                  = 8000
RELOAD                = false
```

5. Click **"Add"** for each variable

### 4.4 Redeploy with Variables
- Railway will auto-redeploy after variables are set
- Wait 2-3 minutes for deployment to complete
- Look for green checkmark ✅ indicating successful deployment

### 4.5 Get Your Public URL
- In Railway dashboard, look for your app URL (something like)
- `https://dodge-ai-prod-production.up.railway.app`
- Copy this URL - it's your public API endpoint!

---

## 🌐 Step 5: Deploy Frontend

Your HTML frontend needs to point to the new API URL:

### 5.1 Update Frontend API Endpoint
Edit `frontend/index.html`:

Find the line that initializes the API URL (usually near the top or in a config section):

```javascript
// OLD (local):
const API_URL = "http://localhost:8000";

// NEW (production):
const API_URL = "https://your-railway-url.up.railway.app";
```

Replace `https://your-railway-url.up.railway.app` with your actual Railway URL from Step 4.5

### 5.2 Push Changes to GitHub
```bash
git add frontend/index.html
git commit -m "Update API endpoint for production deployment"
git push
```

### 5.3 (Optional) Deploy Frontend to Netlify
If you want the frontend hosted too (it's just HTML):

1. Go to **https://netlify.com**
2. Sign up with GitHub
3. Click **"Add new site"** → **"Import an existing project"**
4. Select your `dodge-ai-project` repository
5. Build command: (leave empty - it's just HTML)
6. Publish directory: `frontend`
7. Click **"Deploy"**

Your frontend will be at `https://your-site.netlify.app`

---

## ✅ Step 6: Initialize Your Graph Database

Your backend is running, but the Neo4j database is empty. Initialize it:

```bash
# Replace with your Railway URL
curl -X POST https://your-railway-url.up.railway.app/api/init
```

You should see a response like:
```json
{
  "status": "success",
  "customers": 1234,
  "orders": 5678,
  "invoices": 9012,
  "...": "..."
}
```

---

## 🧪 Step 7: Test Your Deployment

### Test Backend API
```bash
curl https://your-railway-url.up.railway.app/docs
```

This should open the API documentation page.

### Test Query Endpoint
```bash
curl -X POST https://your-railway-url.up.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the top products by revenue?"}'
```

You should get back a natural language response + graph data.

### Access Frontend
- If deployed on Netlify: `https://your-site.netlify.app`
- If local: Open `frontend/index.html` in your browser and ensure API URL is set correctly

---

## 📊 Free Tier Limits

### Railway.app
- **$5/month free credit** (usually lasts 2-3 weeks)
- After free trial: $0.50/month if you stay under minimal resource usage
- No credit card required until you exceed limits

### Neo4j Aura Free
- **200GB storage** (way more than you'll need)
- **120k requests/month** (for small projects)
- Automatic backups

### OpenRouter Free
- **$5 starting credit**
- **Pay-as-you-go after credit runs out** (~$0.001 per API call)

---

## 🔄 Continuous Deployment

Once everything is set up, **deployment is automatic**:

1. You make changes locally
2. `git push` to GitHub
3. Railway automatically pulls the changes and redeploys! 🎉

---

## ❌ Troubleshooting

### "Connection refused" error
- ✅ Check Neo4j URI, username, password in Railway variables
- ✅ Make sure Neo4j Aura instance is running (not hibernated)

### "API key invalid" error
- ✅ Verify `OPENROUTER_API_KEY` is correct (starts with `sk-or-`)
- ✅ Check OpenRouter account has active credits

### Frontend can't reach backend
- ✅ Make sure `API_URL` in frontend is set to Railway URL, not localhost
- ✅ Check browser console for CORS errors

### "Port already in use" error (shouldn't happen on Railway)
- ✅ Railway automatically assigns PORT via environment variable
- ✅ Make sure `run_server.py` reads `PORT` from `os.getenv("PORT", 8000)`

### Data not loading
- ✅ Run `/api/init` endpoint to populate database
- ✅ Check Neo4j database has data: `https://your-aura-instance.neo4j.io` → run `MATCH (n) RETURN COUNT(n)`

---

## 📱 Alternative Platforms

If Railway doesn't work for you:

### Render.com (Free Web Service)
- Similar to Railway
- https://render.com
- Free tier: stops after 15 minutes of inactivity (better if low traffic)

### PythonAnywhere
- Simpler Python-specific hosting
- Free tier limitations (more restrictive)
- https://www.pythonanywhere.com

### Heroku (Paid, but cheapest paid option)
- Free tier discontinued (as of Nov 2022)
- Starting at $7/month

---

## 🎉 You're Done!

Your app is now live! Share your Railway URL with others to start using the app.

**To monitor your deployment:**
- Go to Railway Dashboard
- Check **"Logs"** for errors
- Check **"Deployments"** tab for history

**Questions?** Check your platform's documentation or the README.md in the project.
