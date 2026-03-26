import os
import json
from app.database.neo4j_conn import run_query

BASE_PATH = "data"

def load_jsonl_folder(folder):
    """Load all records from a folder of JSONL files"""
    records = []
    path = os.path.join(BASE_PATH, folder)
    
    if not os.path.exists(path):
        print(f"⚠️ Folder not found: {path}")
        return records

    for file in os.listdir(path):
        if file.endswith(".jsonl"):
            with open(os.path.join(path, file), "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        records.append(json.loads(line))
                    except:
                        continue

    return records


def ingest_all():
    """Run all ingestion functions"""
    print("🚀 Starting data ingestion...")
    ingest_customers()
    ingest_addresses()
    ingest_products()
    ingest_plants()
    ingest_products_plants()
    ingest_company()
    ingest_orders()
    ingest_order_items()
    ingest_deliveries()
    ingest_delivery_items()
    ingest_invoices()
    ingest_invoice_items()
    ingest_payments()
    print("✅ Ingestion complete!")


# ========== CORE ENTITIES ==========

def ingest_customers():
    """Ingest business partners as customers"""
    data = load_jsonl_folder("business_partners")
    
    for r in data:
        run_query("""
        MERGE (c:Customer {id: $id})
        SET c.name = $name,
            c.fullName = $fullName,
            c.country = $country
        """, {
            "id": r.get("businessPartner"),
            "name": r.get("businessPartnerName"),
            "fullName": r.get("businessPartnerFullName"),
            "country": "IN"
        })
    
    print(f"✅ Ingested {len(data)} customers")


def ingest_addresses():
    """Ingest addresses and link to customers"""
    data = load_jsonl_folder("business_partner_addresses")
    
    for r in data:
        run_query("""
        MERGE (addr:Address {id: $aid})
        SET addr.city = $city,
            addr.country = $country,
            addr.postalCode = $postalCode,
            addr.street = $street
        
        WITH addr
        MERGE (c:Customer {id: $cid})
        MERGE (c)-[:HAS_ADDRESS]->(addr)
        """, {
            "aid": r.get("addressId"),
            "city": r.get("cityName"),
            "country": r.get("country"),
            "postalCode": r.get("postalCode"),
            "street": r.get("streetName"),
            "cid": r.get("businessPartner")
        })
    
    print(f"✅ Ingested {len(data)} addresses")


def ingest_products():
    """Ingest products with descriptions"""
    data = load_jsonl_folder("products")
    
    for r in data:
        run_query("""
        MERGE (p:Product {id: $id})
        SET p.type = $type,
            p.unit = $unit,
            p.group = $group
        """, {
            "id": r.get("product"),
            "type": r.get("productType"),
            "unit": r.get("baseUnit"),
            "group": r.get("productGroup")
        })
    
    # Add descriptions
    desc_data = load_jsonl_folder("product_descriptions")
    for r in desc_data:
        run_query("""
        MATCH (p:Product {id: $id})
        SET p.description = $desc
        """, {
            "id": r.get("product"),
            "desc": r.get("productDescription")
        })
    
    print(f"✅ Ingested {len(data)} products")


def ingest_plants():
    """Ingest plants (warehouses/manufacturing locations)"""
    data = load_jsonl_folder("plants")
    
    for r in data:
        run_query("""
        MERGE (plant:Plant {id: $id})
        SET plant.name = $name,
            plant.location = $location
        """, {
            "id": r.get("plant"),
            "name": r.get("plantName"),
            "location": "India"
        })
    
    print(f"✅ Ingested {len(data)} plants")


# ========== ORDERS & DELIVERY FLOW ==========

def ingest_orders():
    """Ingest sales orders"""
    data = load_jsonl_folder("sales_order_headers")
    
    for r in data:
        run_query("""
        MERGE (o:Order {id: $id})
        SET o.type = $type,
            o.amount = $amount,
            o.currency = $currency,
            o.status = $status,
            o.creationDate = $date
        
        WITH o
        MERGE (c:Customer {id: $cid})
        MERGE (c)-[:PLACED_ORDER]->(o)
        """, {
            "id": r.get("salesOrder"),
            "type": r.get("salesOrderType"),
            "amount": float(r.get("totalNetAmount", 0)),
            "currency": r.get("transactionCurrency"),
            "status": r.get("overallDeliveryStatus"),
            "date": r.get("creationDate"),
            "cid": r.get("soldToParty")
        })
    
    print(f"✅ Ingested {len(data)} orders")


def ingest_order_items():
    """Ingest order line items"""
    data = load_jsonl_folder("sales_order_items")
    
    for r in data:
        run_query("""
        MERGE (o:Order {id: $oid})
        MERGE (p:Product {id: $pid})
        
        MERGE (o)-[rel:HAS_ITEM]->(p)
        SET rel.quantity = $qty,
            rel.unit = $unit,
            rel.amount = $amount
        """, {
            "oid": r.get("salesOrder"),
            "pid": r.get("material"),
            "qty": float(r.get("requestedQuantity", 0)),
            "unit": r.get("requestedQuantityUnit"),
            "amount": float(r.get("netAmount", 0))
        })
    
    print(f"✅ Ingested {len(data)} order items")


def ingest_deliveries():
    """Ingest outbound deliveries"""
    data = load_jsonl_folder("outbound_delivery_headers")
    
    for r in data:
        run_query("""
        MERGE (d:Delivery {id: $id})
        SET d.status = $status,
            d.pickingStatus = $picking,
            d.creationDate = $date,
            d.shippingPoint = $point
        """, {
            "id": r.get("deliveryDocument"),
            "status": r.get("overallGoodsMovementStatus"),
            "picking": r.get("overallPickingStatus"),
            "date": r.get("creationDate"),
            "point": r.get("shippingPoint")
        })
    
    print(f"✅ Ingested {len(data)} deliveries")


def ingest_delivery_items():
    """Link deliveries to orders and products"""
    data = load_jsonl_folder("outbound_delivery_items")
    
    for r in data:
        ref_order = r.get("referenceSdDocument")
        if ref_order:
            run_query("""
            MERGE (d:Delivery {id: $did})
            MERGE (o:Order {id: $oid})
            MERGE (d)-[rel:FULFILLS]->(o)
            SET rel.quantity = $qty, rel.unit = $unit
            """, {
                "did": r.get("deliveryDocument"),
                "oid": ref_order,
                "qty": float(r.get("actualDeliveryQuantity", 0)),
                "unit": r.get("deliveryQuantityUnit")
            })
        
        # Also link to plant
        plant = r.get("plant")
        if plant:
            run_query("""
            MERGE (d:Delivery {id: $did})
            MERGE (p:Plant {id: $pid})
            MERGE (d)-[:FROM_PLANT]->(p)
            """, {
                "did": r.get("deliveryDocument"),
                "pid": plant
            })
    
    print(f"✅ Ingested {len(data)} delivery items")


# ========== BILLING & PAYMENTS ==========

def ingest_invoices():
    """Ingest billing documents (invoices)"""
    data = load_jsonl_folder("billing_document_headers")
    
    for r in data:
        run_query("""
        MERGE (i:Invoice {id: $id})
        SET i.type = $type,
            i.amount = $amount,
            i.currency = $currency,
            i.isCancelled = $cancelled,
            i.date = $date
        
        WITH i
        MERGE (c:Customer {id: $cid})
        MERGE (c)-[:BILLED_AS]->(i)
        """, {
            "id": r.get("billingDocument"),
            "type": r.get("billingDocumentType"),
            "amount": float(r.get("totalNetAmount", 0)),
            "currency": r.get("transactionCurrency"),
            "cancelled": r.get("billingDocumentIsCancelled"),
            "date": r.get("billingDocumentDate"),
            "cid": r.get("soldToParty")
        })
    
    print(f"✅ Ingested {len(data)} invoices")


def ingest_invoice_items():
    """Link invoices to orders and products"""
    data = load_jsonl_folder("billing_document_items")
    
    for r in data:
        ref_order = r.get("referenceSdDocument")
        
        # Link invoice to product
        run_query("""
        MERGE (i:Invoice {id: $iid})
        MERGE (p:Product {id: $pid})
        MERGE (i)-[rel:HAS_ITEM]->(p)
        SET rel.quantity = $qty,
            rel.unit = $unit,
            rel.amount = $amount
        """, {
            "iid": r.get("billingDocument"),
            "pid": r.get("material"),
            "qty": float(r.get("billingQuantity", 0)),
            "unit": r.get("billingQuantityUnit"),
            "amount": float(r.get("netAmount", 0))
        })
        
        # Link invoice to order if reference exists
        if ref_order:
            run_query("""
            MERGE (i:Invoice {id: $iid})
            MERGE (o:Order {id: $oid})
            MERGE (i)-[:FOR_ORDER]->(o)
            """, {
                "iid": r.get("billingDocument"),
                "oid": ref_order
            })
    
    print(f"✅ Ingested {len(data)} invoice items")


def ingest_payments():
    """Ingest payments received"""
    data = load_jsonl_folder("payments_accounts_receivable")
    
    for r in data:
        run_query("""
        MERGE (pay:Payment {id: $id})
        SET pay.amount = $amount,
            pay.currency = $currency,
            pay.date = $date
        
        WITH pay
        MERGE (c:Customer {id: $cid})
        MERGE (c)-[:MADE_PAYMENT]->(pay)
        """, {
            "id": r.get("accountingDocument"),
            "amount": float(r.get("amountInTransactionCurrency", 0)),
            "currency": r.get("transactionCurrency"),
            "date": r.get("postingDate"),
            "cid": r.get("customer")
        })
    
    print(f"✅ Ingested {len(data)} payments")
# ========== RELATIONSHIPS ==========

def ingest_products_plants():
    """Link products to plants"""
    data = load_jsonl_folder("product_plants")

    for r in data:
        run_query("""
        MERGE (p:Product {id: $pid})
        MERGE (pl:Plant {id: $plid})
        MERGE (p)-[:AVAILABLE_AT]->(pl)
        """, {
            "pid": r.get("product"),
            "plid": r.get("plant")
        })

    print(f"✅ Ingested {len(data)} product-plant relationships")


def ingest_company():
    """Link customers to companies"""
    data = load_jsonl_folder("customer_company_assignments")

    for r in data:
        run_query("""
        MERGE (co:Company {id: $cid})
        MERGE (c:Customer {id: $cust})
        MERGE (c)-[:ASSIGNED_TO]->(co)
        """, {
            "cid": r.get("companyCode"),
            "cust": r.get("customer")
        })

    print(f"✅ Ingested {len(data)} company assignments")


if __name__ == "__main__":
    ingest_all()
