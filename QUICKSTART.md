# 🚀 Quick Start Guide

## Step 1: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
& .\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

## Step 2: Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

## Step 3: Initialize Graph Data (New Terminal)

```bash
# With venv activated:
curl -X POST http://127.0.0.1:8000/api/init
```

Or visit in browser: http://127.0.0.1:8000/api/init

You should see a success message with data counts.

## Step 4: Open Frontend

Simply open `frontend/index.html` in your web browser, or:

```bash
cd frontend
python -m http.server 8080
```

Then visit: http://127.0.0.1:8080

## Step 5: Try Sample Queries

Once the frontend loads, try these queries:

1. **"Which products have the most invoices?"**
   - Shows product analysis with invoice counts
   
2. **"Show me the full order to payment flow"**
   - Displays complete customer transaction journey
   
3. **"Which orders were delivered but not billed?"**
   - Identifies broken business processes
   
4. **"Top 5 customers by total invoice amount"**
   - Customer analysis with invoice volumes

---

## 📊 Checking the System Status

### Check Backend Health:
```bash
curl http://127.0.0.1:8000/health
```

### Check API Docs:
Visit: http://127.0.0.1:8000/docs

### Check Neo4j Connection:
Visit: http://localhost:7474 (Neo4j Browser)

---

## ⚠️ Common Issues

### "Connection refused" on backend startup
- Neo4j might not be running
- Update `.env` file with correct Neo4j credentials
- Try: `neo4j start` or check Docker container

### Frontend shows "Backend error"
- Make sure backend is running on http://127.0.0.1:8000
- Check browser console (F12) for detailed errors
- Verify CORS is enabled

### No data in graph
- Initialize data first: `curl -X POST http://127.0.0.1:8000/api/init`
- This takes 30-60 seconds depending on your setup
- Check Neo4j logs for any errors

### Query returns "No data found"
- Data might not be ingested yet
- Check Neo4j has data: http://localhost:7474
- Run: `MATCH (n) RETURN COUNT(n)`

---

## 🎮 Demo Workflow

1. **Open Frontend** → See empty graph initially
2. **Ask Question** → "Which customers placed the most orders?"
3. **Backend processes:**
   - Checks if query is about dataset (guardrail check) ✅
   - Generates Cypher query ✅
   - Executes on Neo4j ✅
   - Converts results to graph format ✅
   - Generates natural language answer ✅
4. **Frontend displays:**
   - Chat response with answer
   - Graph visualization with nodes/edges
   - Customer nodes highlighted with connections

---

## 📚 Example Queries & Expected Results

### Query 1: Product Analysis
```
Input: "Which products are in the most invoices?"
Graph: Shows Product nodes connected to Invoice nodes
Answer: "📦 **Top Products by Billing Count:**
1. S8907367001003: 45 invoices
2. B8907367041603: 38 invoices
..."
```

### Query 2: Order Flow
```
Input: "Trace the complete flow for customer 310000108"
Graph: Customer → Order → Delivery → Invoice → Payment chain
Answer: "🔄 **Complete Order to Cash Flow:**
Customer 310000108 → Order 740506
  📦 Products: 2
  🚚 Deliveries: 1
  📄 Invoices: 1
  💳 Payments: 1"
```

### Query 3: Broken Flows
```
Input: "Show orders delivered but not billed"
Graph: Delivery nodes not connected to Invoice nodes
Answer: "⚠️ **Incomplete Flows:**
Order 740507 (₹5000) - 1 delivery without billing
Order 740508 (₹3500) - 2 deliveries without billing"
```

---

## 🔍 Advanced Features

### View the Generated Cypher:
Every response includes `"cypher"` field showing the query used

### Check Result Count:
Every response includes `"resultCount"` field 

### Monitor Logs:
```bash
# Backend logs show ingestion progress:
🚀 Starting data ingestion...
✅ Ingested 2500 customers
✅ Ingested 1200 addresses
✅ Ingested 8000 products
...
✅ Ingestion complete!
```

---

## 🧹 Cleanup

### Clear Neo4j Database:
```bash
# Connect to Neo4j and run:
MATCH (n) DETACH DELETE n
```

### Reset Everything:
```bash
# 1. Stop backend (Ctrl+C)
# 2. Restart Neo4j
# 3. Hit /api/init again
# 4. Refresh frontend
```

---

## ✅ System Ready?

If you can answer YES to all:
- Backend running on 8000 ✅
- Frontend loads without errors ✅
- Can type query in chat box ✅
- Graph visualization appears ✅
- Answer shows in chat ✅

**You're ready to go!** 🎉

---

**Need Help?**
- Check SYSTEM_OVERVIEW.md for architecture details
- Check README.MD for project context
- Review error messages in browser console (F12)
- Check backend terminal for error logs
