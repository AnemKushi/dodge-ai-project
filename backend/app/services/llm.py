import requests
from app.config import settings

API_KEY = settings.OPENROUTER_API_KEY


def is_valid_question(question: str) -> bool:
    """Check if question is related to dataset - with guardrails"""
    q = question.lower().strip()
    
    # ❌ REJECT: Creative, off-topic, or harmful prompts
    reject_patterns = [
        "write a poem", "write a story", "tell me a joke", "how to hack",
        "how to bomb", "how to make", "recipe", "cook", "weather",
        "who is", "tell me about", "what is the meaning of", "philosophy",
        "generate", "create a", "draw me", "song", "music", "movie",
        "learn python", "teach me", "help me with homework"
    ]
    
    for pattern in reject_patterns:
        if pattern in q:
            return False
    
    # ✅ ACCEPT: Dataset-related keywords
    keywords = [
        "product", "order", "invoice", "customer", "delivery", "billing",
        "payment", "sales", "plant", "supplier", "address", "flow", "trace",
        "complete", "broken", "missing", "billed", "delivered", "amount",
        "highest", "which", "who", "where", "how many", "how much",
        "total", "count", "list", "show", "find", "search", "get", "all",
        "relationship", "connection", "link", "associate", "cancel", "status"
    ]
    
    return any(k in q for k in keywords)


def generate_cypher(question: str) -> str:
    """Generate Cypher query from natural language question - returns actual nodes/relationships"""
    q = question.lower()

    # ========== SPECIFIC PATTERNS - Return actual graph structures ==========
    
    # Q1: Products with most invoices/bills
    if any(x in q for x in ["product", "products"]) and any(x in q for x in ["invoice", "bill", "billing", "billed", "highest", "most"]):
        return """
        MATCH (i:Invoice)-[rel:HAS_ITEM]->(p:Product)
        RETURN p, rel, i
        LIMIT 100
        """
    
    # Q2: Trace document flow (Sales Order → Delivery → Invoice → Payment)
    if any(x in q for x in ["trace", "flow", "path", "pipeline", "full flow"]):
        return """
        MATCH (c:Customer)-[r1:PLACED_ORDER]->(o:Order)
        OPTIONAL MATCH (o)-[r2:HAS_ITEM]->(p:Product)
        OPTIONAL MATCH (d:Delivery)-[r3:FULFILLS]->(o)
        OPTIONAL MATCH (c)-[r4:BILLED_AS]->(i:Invoice)
        OPTIONAL MATCH (i)-[r5:FOR_ORDER]->(o)
        OPTIONAL MATCH (c)-[r6:MADE_PAYMENT]->(pay:Payment)
        RETURN c, r1, o, r2, p, r3, d, r4, i, r5, r6, pay
        LIMIT 50
        """
    
    # Q3: Incomplete flows (delivered but not billed)
    if any(x in q for x in ["incomplete", "missing", "broken", "unfulfilled", "not billed"]):
        return """
        MATCH (o:Order)-[r:FULFILLS]-(d:Delivery)
        WHERE NOT exists((o)-[:FOR_ORDER|:BILLED_AS]->(:Invoice))
        RETURN o, r, d
        LIMIT 50
        """
    
    # Q4: Customers with invoices and payments
    if any(x in q for x in ["customer", "customers"]) and any(x in q for x in ["invoice", "bill", "billing", "payment"]):
        return """
        MATCH (c:Customer)-[r1:BILLED_AS]->(i:Invoice)
        OPTIONAL MATCH (c)-[r2:MADE_PAYMENT]->(p:Payment)
        RETURN c, r1, i, r2, p
        LIMIT 100
        """
    
    # Q5: All orders with their details
    if any(x in q for x in ["all orders", "list orders", "show orders"]):
        return """
        MATCH (c:Customer)-[r1:PLACED_ORDER]->(o:Order)
        OPTIONAL MATCH (o)-[r2:HAS_ITEM]->(p:Product)
        RETURN c, r1, o, r2, p
        LIMIT 100
        """
    
    # Q6: Invoice details and reconciliation
    if "invoice" in q and not any(x in q for x in ["product", "order", "customer", "flow"]):
        return """
        MATCH (c:Customer)-[r1:BILLED_AS]->(i:Invoice)
        OPTIONAL MATCH (i)-[r2:FOR_ORDER]->(o:Order)
        OPTIONAL MATCH (i)-[r3:HAS_ITEM]->(p:Product)
        RETURN c, r1, i, r2, o, r3, p
        LIMIT 100
        """
    
    # Q7: Delivery status and tracking
    if any(x in q for x in ["delivery", "deliver", "shipment", "shipping"]):
        return """
        MATCH (d:Delivery)-[r1:FULFILLS]->(o:Order)
        OPTIONAL MATCH (d)-[r2:FROM_PLANT]->(plant:Plant)
        RETURN d, r1, o, r2, plant
        LIMIT 100
        """
    
    # Q8: Customer address information  
    if any(x in q for x in ["customer", "address", "location", "city"]):
        return """
        MATCH (c:Customer)-[r:HAS_ADDRESS]->(a:Address)
        RETURN c, r, a
        LIMIT 100
        """
    
    # Q9: Product analysis
    if "product" in q:
        return """
        MATCH (p:Product)<-[r1:HAS_ITEM]-(i:Invoice)
        OPTIONAL MATCH (p)<-[r2:HAS_ITEM]-(o:Order)
        RETURN p, r1, i, r2, o
        LIMIT 100
        """
    
    # Q10: Payment analysis
    if any(x in q for x in ["payment", "paid", "receive", "collection"]):
        return """
        MATCH (c:Customer)-[r1:MADE_PAYMENT]->(pay:Payment)
        OPTIONAL MATCH (c)-[r2:BILLED_AS]->(i:Invoice)
        RETURN c, r1, pay, r2, i
        LIMIT 100
        """
    
    # Q11: Order cancellations
    if any(x in q for x in ["cancel", "cancelled", "cancellation"]):
        return """
        MATCH (c:Customer)-[r1:BILLED_AS]->(i:Invoice {isCancelled: true})
        OPTIONAL MATCH (i)-[r2:FOR_ORDER]->(o:Order)
        RETURN c, r1, i, r2, o
        LIMIT 100
        """
    
    # ========== GENERIC FALLBACK ==========
    return """
    MATCH (c:Customer)-[r1:PLACED_ORDER|BILLED_AS|MADE_PAYMENT]->(n)
    OPTIONAL MATCH (n)-[r2]->(m)
    RETURN c, r1, n, r2, m
    LIMIT 100
    """



def generate_answer(question: str, results: list) -> str:
    """Convert query results to natural language answer"""
    
    if not results:
        return "❌ No data found for this query. The requested information may not exist in the dataset."
    
    try:
        first = results[0]
        
        # ===== PRODUCT ANALYSIS =====
        if "product" in first and "invoice_count" in first:
            answer = "📦 **Top Products by Billing Count:**\n"
            for i, row in enumerate(results[:10], 1):
                product = row.get("product", "Unknown")
                count = row.get("invoice_count", 0)
                answer += f"{i}. {product}: **{count} invoices**\n"
            answer += f"\n✅ Found {len(results)} products in total"
            return answer
        
        # ===== COMPLETE FLOW =====  
        elif "products" in first or (isinstance(first.get("products"), list)):
            answer = "🔄 **Complete Order to Cash Flow:**\n"
            for row in results[:10]:
                cust = row.get("customer", "N/A")
                order = row.get("order_id", "N/A")
                products = row.get("products", [])
                deliveries = row.get("deliveries", [])
                invoices = row.get("invoices", [])
                payments = row.get("payments", [])
                
                answer += f"\n**Customer {cust} → Order {order}**\n"
                answer += f"  📦 Products: {len(products)}\n"
                answer += f"  🚚 Deliveries: {len(deliveries)}\n"
                answer += f"  📄 Invoices: {len(invoices)}\n"
                answer += f"  💳 Payments: {len(payments)}\n"
            return answer
        
        # ===== INCOMPLETE FLOWS =====
        elif "order_id" in first and "deliveries_without_billing" in first:
            answer = "⚠️ **Incomplete Flows (Delivered but Not Billed):**\n"
            count = 0
            for row in results:
                if row.get("deliveries_without_billing", 0) > 0:
                    order = row.get("order_id", "N/A")
                    amount = row.get("order_amount", 0)
                    answer += f"Order {order} (₹{amount}) - {row.get('deliveries_without_billing')} deliveries without billing\n"
                    count += 1
            if count == 0:
                return "✅ **No incomplete flows found** - All deliveries are properly billed!"
            return answer
        
        # ===== CUSTOMER ANALYSIS =====
        elif "customer_id" in first and ("invoice_count" in first or "total_billed" in first):
            answer = "👥 **Customer Invoice & Payment Analysis:**\n"
            for i, row in enumerate(results[:10], 1):
                cust_name = row.get("customer_name", "Unknown")
                cust_id = row.get("customer_id", "N/A")
                inv_count = row.get("invoice_count", 0)
                total_billed = row.get("total_billed", 0)
                pay_count = row.get("payment_count", 0)
                total_paid = row.get("total_paid", 0)
                outstanding = row.get("outstanding", 0)
                
                answer += f"\n{i}. **{cust_name}** ({cust_id})\n"
                answer += f"   📄 Invoices: {inv_count} (₹{total_billed})\n"
                answer += f"   💳 Payments: {pay_count} (₹{total_paid})\n"
                if outstanding > 0:
                    answer += f"   ⚠️  Outstanding: ₹{outstanding}\n"
            return answer
        
        # ===== ORDERS =====
        elif "order_id" in first and "amount" in first:
            answer = "📋 **Orders Summary:**\n"
            total_amount = 0
            for i, row in enumerate(results[:15], 1):
                cust_name = row.get("customer_name", "Unknown")
                order = row.get("order_id", "N/A")
                amount = float(row.get("amount", 0))
                status = row.get("status", "Unknown")
                items = row.get("item_count", 0)
                total_amount += amount
                answer += f"{i}. Order {order} - ₹{amount} ({status}) - {items} items - {cust_name}\n"
            answer += f"\n**Total Order Value: ₹{total_amount}** ({len(results)} orders)"
            return answer
        
        # ===== INVOICE DETAILS =====
        elif "invoice_id" in first:
            answer = "📄 **Invoice Details:**\n"
            total_invoiced = 0
            for i, row in enumerate(results[:15], 1):
                inv_id = row.get("invoice_id", "N/A")
                amount = float(row.get("invoice_amount", 0))
                date = row.get("invoice_date", "Unknown date")
                cust_name = row.get("customer_name", "Unknown")
                order = row.get("order_id", "N/A")
                items = row.get("line_items", 0)
                total_invoiced += amount
                answer += f"{i}. Invoice {inv_id} (₹{amount}) - {cust_name} - Order {order} - {items} items ({date})\n"
            answer += f"\n**Total Invoiced: ₹{total_invoiced}** ({len(results)} invoices)"
            return answer
        
        # ===== DELIVERY STATUS =====
        elif "delivery_id" in first and "delivery_status" in first:
            answer = "📦 **Delivery Status:**\n"
            status_count = {}
            for row in results:
                deliv = row.get("delivery_id", "N/A")
                status = row.get("delivery_status", "Unknown")
                order = row.get("order_id", "N/A")
                plant = row.get("plant_name", "N/A")
                
                status_count[status] = status_count.get(status, 0) + 1
                answer += f"Delivery {deliv} ({status}) ← Order {order} from {plant}\n"
            
            answer += "\n**Status Summary:**\n"
            for status, count in status_count.items():
                answer += f"  {status}: {count}\n"
            return answer
        
        # ===== PAYMENT STATUS =====
        elif "payment_id" in first or "payment_amount" in first:
            answer = "💳 **Payments Received:**\n"
            total = 0
            for i, row in enumerate(results[:15], 1):
                cust = row.get("customer_name", "Unknown")
                amount = float(row.get("payment_amount", 0) or 0)
                pay_date = row.get("payment_date", "N/A")
                total += amount
                answer += f"{i}. {cust}: ₹{amount} (Date: {pay_date})\n"
            answer += f"\n**Total Payments: ₹{total}** ({len(results)} payments)"
            return answer
        
        # ===== PRODUCT ANALYSIS =====
        elif "product_id" in first and ("order_count" in first or "invoice_count" in first):
            answer = "📦 **Product Analysis:**\n"
            for i, row in enumerate(results[:15], 1):
                prod_id = row.get("product_id", "N/A")
                prod_type = row.get("product_type", "Unknown")
                orders = row.get("order_count", 0)
                invoices = row.get("invoice_count", 0)
                
                answer += f"{i}. {prod_id} ({prod_type})\n"
                answer += f"   📋 Orders: {orders}, 📄 Invoices: {invoices}\n"
            return answer
        
        # ===== CANCELLED INVOICES =====
        elif "cancelled_invoice" in first:
            answer = "❌ **Cancelled Invoices:**\n"
            total_cancelled = 0
            for row in results:
                inv_id = row.get("cancelled_invoice", "N/A")
                amount = float(row.get("amount", 0))
                cust = row.get("customer_name", "Unknown")
                order = row.get("order_id", "N/A")
                total_cancelled += amount
                answer += f"Invoice {inv_id} (₹{amount}) - Customer {cust}, Order {order}\n"
            answer += f"\n**Total Cancelled Amount: ₹{total_cancelled}**"
            return answer
        
        # ===== FALLBACK =====
        else:
            answer = "📊 **Query Results:**\n"
            for i, row in enumerate(results[:10], 1):
                row_str = ", ".join([f"{k}: {v}" for k, v in list(row.items())[:4]])
                answer += f"{i}. {row_str}\n"
            if len(results) > 10:
                answer += f"\n... and {len(results) - 10} more results"
            return answer
    
    except Exception as e:
        return f"✅ Retrieved {len(results)} records.\n\n(Note: Answer formatting encountered an issue: {str(e)[:50]})"
