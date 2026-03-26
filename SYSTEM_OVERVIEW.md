# Graph-Based Query System - System Overview

## 🏗 Architecture

This system converts fragmented business data (orders, deliveries, invoices, payments) into a **connected knowledge graph** and enables natural language queries using Neo4j and LLMs.

### Components:

1. **Backend API** (`backend/app/`)
   - FastAPI server with CORS enabled
   - Neo4j graph database connection
   - LLM integration for natural language processing
   - Data ingestion pipeline from JSONL files

2. **Frontend** (`frontend/index.html`)
   - vis.js network visualization
   - TailwindCSS styling
   - Real-time chat interface
   - Dynamic graph rendering

3. **Data Pipeline** (`backend/data/`)
   - 19 JSONL data sources
   - Entities: Customers, Products, Orders, Deliveries, Invoices, Payments, Plants, Addresses, Companies

---

## 📊 Data Model

### Entities & Relationships:

```
┌─────────────────────────────────────────────────────┐
│                    CUSTOMER                         │
│  • ID, Name, FullName, Country                      │
│  ├─ HAS_ADDRESS → ADDRESS                           │
│  ├─ ASSIGNED_TO → COMPANY                           │
│  ├─ PLACED_ORDER → ORDER                            │
│  ├─ BILLED_AS → INVOICE                             │
│  └─ MADE_PAYMENT → PAYMENT                          │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                     ORDER                           │
│  • ID, Type, Amount, Currency, Status, Date         │
│  ├─ HAS_ITEM → PRODUCT                              │
│  ├─ FULFILLS → DELIVERY (via reverse)               │
│  └─ FOR_ORDER ← INVOICE (via reverse)               │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                    DELIVERY                         │
│  • ID, Status, PickingStatus, CreationDate         │
│  ├─ FULFILLS → ORDER                                │
│  └─ FROM_PLANT → PLANT                              │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                    INVOICE                          │
│  • ID, Type, Amount, Currency, IsCancelled, Date    │
│  ├─ HAS_ITEM → PRODUCT                              │
│  └─ FOR_ORDER → ORDER                               │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                    PAYMENT                          │
│  • ID, Amount, Currency, Date                       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                    PRODUCT                          │
│  • ID, Type, Unit, Group, Description               │
│  ├─ AVAILABLE_AT → PLANT                            │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Setup & Deployment

### Prerequisites:
- Python 3.9+
- Neo4j 5.0+ (running locally or remote)
- 2GB+ available memory

### Installation:

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment (if not exists)
python -m venv ../venv

# 3. Activate virtual environment
# On Windows:
..\venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure .env file
# Check backend/.env for Neo4j credentials
# Update OPENROUTER_API_KEY if using different LLM

# 6. Start backend server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Initialize Data:

```bash
# Option 1: Via API
curl -X POST http://127.0.0.1:8000/api/init

# Option 2: Direct Python
cd backend
python app/services/ingestion.py
```

### Run Frontend:

```bash
# Option 1: Open directly in browser
open frontend/index.html

# Option 2: Via simple HTTP server
cd frontend
python -m http.server 8080
# Then visit: http://localhost:8080
```

---

## 🔗 API Endpoints

### GET `/` - Health Check
Returns system info and available endpoints

### POST `/api/init` - Initialize Graph
Ingests all JSONL data into Neo4j graph

**Response:**
```json
{
  "status": "success",
  "message": "Data ingestion complete",
  "stats": {
    "customers": 2500,
    "orders": 15000,
    "invoices": 18000,
    "deliveries": 12000,
    "payments": 8000
  }
}
```

### POST `/api/chat` - Query Graph
Accepts natural language questions and returns graph visualization + answers

**Request:**
```json
{
  "question": "Which products are associated with the highest number of billing documents?"
}
```

**Response:**
```json
{
  "question": "Which products are associated with the highest number of billing documents?",
  "answer": "📦 **Top Products by Billing Count:**\n1. S8907367001003 - Product X: 45 invoices\n2. B8907367041603 - Product Y: 38 invoices",
  "nodes": [{id: "1", label: "Product: S8907367001003", group: "Product", color: {...}}],
  "edges": [{from: "1", to: "2", label: "HAS_ITEM", arrows: "to"}],
  "cypher": "MATCH (i:Invoice)-[:HAS_ITEM]->(p:Product)...",
  "resultCount": 45
}
```

### GET `/api/graph` - Get Initial Graph Overview
Returns statistics on all node types

---

## 🤖 Query Examples

### ✅ Valid Queries (Will Work):
- "Which products have the most invoices?"
- "Show me the complete flow from order to payment for customer X"
- "Identify orders that were delivered but not billed"
- "Which customers haven't made payments yet?"
- "List all cancelled invoices"
- "Trace the billing documents for order 740506"

### ❌ Invalid Queries (Will Be Rejected):
- "Write me a poem"
- "How do I make pasta?"
- "Who is the President?"
- "Tell me a joke"
- "Can you help me with my homework?"

---

## 🛡️ Guardrails & Safety

### 1. Input Validation:
- Rejects off-topic/creative writing prompts
- Restricts queries to dataset domain
- Prevents prompt injection

### 2. Query Generation:
- Rule-based Cypher generation (no LLM code execution)
- Pattern matching for common queries
- Safe fallback for unknown queries

### 3. Output Processing:
- Results limited to 50-100 records per query
- Formatted as natural language, not raw data
- Includes context in responses

### 4. Error Handling:
- Graceful Neo4j connection failures
- Timeout protection on long queries
- Safe JSON response on errors

---

## 📈 Query Patterns Supported

| Pattern | Example | Returns |
|---------|---------|---------|
| **Product Analysis** | "Which products have the most invoices?" | Top products by billing frequency |
| **Full Flow Trace** | "Trace order 740506" | Complete Order→Delivery→Invoice→Payment chain |
| **Incomplete Flows** | "Show me orders not billed" | Orders missing invoice data |
| **Customer Analysis** | "Top customers by invoice volume" | Customers with highest transaction counts |
| **Payment Analysis** | "What's the total payment received?" | Payment amounts and dates |
| **Delivery Status** | "All pending deliveries" | Delivery status breakdown |
| **Cancelled Items** | "Cancelled invoices" | Cancelled transactions with amounts |

---

## 🧪 Testing

### Test Graph Ingestion:
```bash
curl -X POST http://127.0.0.1:8000/api/init
```

### Test Chat Endpoint:
```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How many products are there?"}'
```

### Test Frontend:
1. Open `frontend/index.html` in browser
2. Type: "Which products have the most invoices?"
3. Should see graph visualization with nodes/edges
4. Chat response should show formatted answer

---

## 🐛 Troubleshooting

### "Connection refused" error
- **Issue**: Neo4j not running
- **Solution**: Start Neo4j service
- **Windows**: `neo4j start`
- **Linux**: `sudo systemctl start neo4j`

### "No nodes/edges showing in graph"
- **Issue**: Backend not initialized
- **Solution**: Hit `/api/init` first
- **Verify**: Check Neo4j browser (http://localhost:7474)

### "Query execution error"
- **Issue**: Invalid Cypher syntax
- **Solution**: Check query in Neo4j browser
- **Debug**: Look at response.cypher field for query

### Frontend shows "Backend error"
- **Issue**: API endpoint unreachable
- **Solution**: 
  - Verify backend is running on 8000
  - Check CORS settings in main.py
  - Try http://127.0.0.1:8000/health

---

## 📚 Technologies Used

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | FastAPI, Python 3.9 | REST API, data ingestion |
| Database | Neo4j | Property graph database |
| Frontend | HTML5, TailwindCSS, vis.js | Web UI with graph visualization |
| LLM Integration | OpenRouter API | Natural language processing |
| Environment | python-dotenv | Configuration management |

---

## 🎯 Key Features

✅ **Graph Visualization** - Real-time interactive network diagram  
✅ **Natural Language Interface** - Ask questions in plain English  
✅ **Smart Query Generation** - Rule-based Cypher translation  
✅ **Guardrails** - Rejects off-topic and harmful prompts  
✅ **Data-Backed Answers** - All responses grounded in dataset  
✅ **Complete Flows** - Trace Order→Delivery→Invoice→Payment  
✅ **Missing Data Detection** - Identify incomplete business processes  
✅ **Error Handling** - Graceful failures and helpful messages  

---

## 📝 Next Steps

### To Deploy:
1. Set up permanent Neo4j instance (Neo4j Cloud, Docker)
2. Deploy backend to cloud (AWS, GCP, Azure, Vercel)
3. Deploy frontend to CDN
4. Set up environment variables for production
5. Configure HTTPS/SSL certificates

### To Extend:
1. Add more query patterns for domain-specific insights
2. Implement conversation memory (store previous queries)
3. Add semantic search using vector embeddings
4. Create scheduled reports/analytics
5. Add authentication/authorization
6. Implement streaming responses from LLM

---

## 📞 Support

For issues or questions:
1. Check error messages in browser console
2. Review Neo4j logs
3. Test endpoints with curl/Postman
4. Verify .env configuration
5. Check data ingestion status

---

**Last Updated:** March 26, 2026  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
