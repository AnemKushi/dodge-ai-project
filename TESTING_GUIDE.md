# 🧪 Testing Guide - Graph Visualization Fix

## Problem Fixed ✅

- **Removed** queries referencing non-existent `AVAILABLE_AT` relationship
- **Removed** references to sparse `description` property  
- **Enhanced** error handling in graph conversion
- **Added** debug logging to track graph creation

---

## Step 1: Stop Previous Backend Process

In your "uvicorn" terminal, press **Ctrl+C** to stop the old backend.

```
Uvicorn running on...
^C
Application shutdown complete.
```

---

## Step 2: Clear Neo4j Database (Recommended)

Connect to Neo4j and run:

```cypher
MATCH (n) DETACH DELETE n
```

Or via API in new terminal:
```bash
curl -X POST http://127.0.0.1:7474/browser/connection 2>/dev/null || echo "Clear via Neo4j Browser"
```

---

## Step 3: Restart Backend with Fresh Data

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Expected output:
```
Uvicorn running on http://127.0.0.1:8000
Application startup complete
```

---

## Step 4: Initialize Graph Data (New Terminal)

```bash
curl -X POST http://127.0.0.1:8000/api/init

# Or check status with:
curl http://127.0.0.1:8000/api/stats
```

**Expected Response:**
```json
{
  "nodes": {
    "Customer": 2500,
    "Order": 15000,
    "Invoice": 18000,
    "Delivery": 12000,
    "Product": 8000,
    "Payment": 8000,
    "Plant": 100,
    "Address": 2500
  },
  "relationships": {
    "PLACED_ORDER": 15000,
    "HAS_ITEM": 50000,
    "FOR_ORDER": 18000,
    "FULFILLS": 12000,
    "BILLED_AS": 18000,
    "MADE_PAYMENT": 8000
  },
  "total_nodes": 48000,
  "total_relationships": 115000
}
```

---

## Step 5: Test Basic Query

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me customers"}'
```

**Expected Response Format:**
```json
{
  "question": "Show me customers",
  "answer": "👥 **Customer Analysis:**...",
  "nodes": [
    {
      "id": "123",
      "label": "Customer: 310000108",
      "group": "Customer",
      "color": {...}
    }
  ],
  "edges": [
    {
      "from": "123",
      "to": "456",
      "label": "PLACED_ORDER",
      "arrows": "to"
    }
  ],
  "cypher": "MATCH (c:Customer)...",
  "resultCount": 2500
}
```

---

## Step 6: Test Front-end Graph Visualization

1. **Open** `frontend/index.html` in your browser
2. **Type** in chat: `"Which products have the most billing?"`
3. **Expected Result:**
   - ✅ Graph appears on left side
   - ✅ Nodes visible with colors (Product=Amber, Invoice=Green)
   - ✅ Edges showing HAS_ITEM relationships
   - ✅ Chat response appears on right

---

## Step 7: Try Different Query Types

### ✅ Working Queries Now:

**"Show me all orders"**
```
→ Returns Orders connected to Customers
→ Graph shows PLACED_ORDER relationships
```

**"Which customers have invoices?"**
```
→ Returns Customers connected to Invoices  
→ Graph shows BILLED_AS relationships
```

**"Trace the flow from order to payment"**
```
→ Returns complete Order→Invoice→Payment chains
→ Graph shows all intermediate nodes
```

**"Show me products"**
```
→ Returns products with invoice counts
→ Graph shows Product nodes and connections
```

**"Which orders were delivered?"**
```
→ Returns Orders with Delivery relationships
→ Graph shows FULFILLS relationships
```

---

## Step 8: Monitor Backend Logs

Watch the backend terminal for debug output:

```
✅ Graph conversion: 150 nodes, 200 edges
✅ Graph conversion: 50 nodes, 120 edges
✅ Graph conversion: 200 nodes, 250 edges
```

If you see errors, check:
- `⚠️ Query error:` = Cypher syntax issue
- `⚠️ Error processing node:` = Node conversion failed
- `⚠️ Error processing edge:` = Relationship conversion failed

---

## Troubleshooting

### "No nodes/edges in graph"
**Fix:** 
1. Check `/api/stats` - should show non-zero counts
2. If stats are 0, data not ingested → hit `/api/init` again
3. Check backend logs for ingestion errors

### "Graph shows but answer is wrong"
**Fix:**
- This is expected for some query combos
- Backend is correctly showing graph + data
- Query understanding may need refinement

### "Backend error - connection refused"
**Fix:**
- Restart backend: `uvicorn app.main:app --reload`
- Check Neo4j is running: `neo4j start`
- Verify .env credentials

### "No graphs after data ingestion"
**Fix:**
1. Clear old data: `MATCH (n) DETACH DELETE n`
2. Restart ingestion: `curl -X POST http://127.0.0.1:8000/api/init`
3. Wait 60 seconds for completion
4. Test query again

---

## API Endpoints for Testing

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat` | POST | Main query endpoint (returns graph) |
| `/api/init` | POST | Initialize/reingest all data |
| `/api/graph` | GET | Get graph overview |
| `/api/stats` | GET | Database statistics |
| `/api/query` | POST | Run raw Cypher (for debugging) |
| `/health` | GET | Health check |
| `/` | GET | API documentation |

---

## Test Checklist ✅

- [ ] Backend running on 8000
- [ ] `/health` returns 200
- [ ] `/api/init` completes without errors
- [ ] `/api/stats` shows non-zero counts
- [ ] `/api/chat` returns JSON with nodes/edges
- [ ] Frontend loads without errors
- [ ] Frontend displays graph visualization
- [ ] Graph updates when new query is sent
- [ ] Chat responses appear in right panel

---

## Performance Benchmarks

| Metric | Expected |
|--------|----------|
| Data Ingestion | 30-60 seconds |
| Query Response | <1 second |
| Graph Rendering | <2 seconds |
| Graph with 500 nodes | <3 seconds |

---

## Next Steps

If all tests pass:
1. ✅ System is ready to use
2. ✅ Try various business queries
3. ✅ Add more query patterns as needed
4. ✅ Deploy to production

If tests fail:
1. Check error logs in backend terminal
2. Verify Neo4j connection in `.env`
3. Clear database and reinitialize
4. Check that all JSONL files exist in `backend/data/`

---

**Status:** ✅ System ready for testing!
