from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.llm import generate_cypher, is_valid_question, generate_answer
from app.database.neo4j_conn import query_to_graph, run_query

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.get("/graph")
def get_initial_graph():
    """Get initial graph overview - all core entities"""
    try:
        cypher = """
        MATCH (n)
        WITH labels(n)[0] as type, count(*) as count
        RETURN type, count
        ORDER BY count DESC
        """
        
        overview = run_query(cypher)
        
        # Get sample relationships
        cypher_graph = """
        MATCH (n)-[r]->(m)
        RETURN DISTINCT labels(n)[0] as from_type, type(r) as rel_type, labels(m)[0] as to_type, count(*) as count
        ORDER BY count DESC
        LIMIT 50
        """
        
        relationships = run_query(cypher_graph)
        
        return {
            "overview": overview,
            "relationships": relationships,
            "status": "ok"
        }
    except Exception as e:
        return {
            "overview": [],
            "relationships": [],
            "error": str(e),
            "status": "error"
        }


@router.post("/chat")
def chat(request: ChatRequest):
    """Chat endpoint that returns both answer and graph visualization"""
    question = request.question
    
    if not question or len(question.strip()) == 0:
        return {
            "question": question,
            "answer": "Please ask a question about the dataset.",
            "nodes": [],
            "edges": [],
            "cypher": None
        }

    # ✅ Guardrail - reject off-topic questions
    if not is_valid_question(question):
        return {
            "question": question,
            "answer": "This system is designed to answer questions related to the dataset only. Please ask about orders, customers, invoices, deliveries, products, or payments.",
            "nodes": [],
            "edges": [],
            "cypher": None
        }

    # ✅ Generate Cypher
    try:
        cypher_query = generate_cypher(question)
    except Exception as e:
        return {
            "question": question,
            "answer": f"Error generating query: {str(e)}",
            "nodes": [],
            "edges": [],
            "cypher": None
        }

    # ✅ Run query and convert to graph format
    try:
        graph_result = query_to_graph(cypher_query)
        raw_result = run_query(cypher_query)
    except Exception as e:
        return {
            "question": question,
            "answer": f"Query execution error: {str(e)}",
            "nodes": [],
            "edges": [],
            "cypher": cypher_query
        }

    # ✅ Generate natural language answer
    try:
        answer = generate_answer(question, raw_result)
    except Exception as e:
        # If answer generation fails, create a simple answer from the raw data
        answer = f"Found {len(raw_result)} results. " + str(raw_result[:50])

    return {
        "question": question,
        "answer": answer,
        "nodes": graph_result.get("nodes", []),
        "edges": graph_result.get("edges", []),
        "cypher": cypher_query,
        "resultCount": len(raw_result)
    }


@router.post("/query")
def query_graph(request: ChatRequest):
    """Execute a raw Cypher query for testing"""
    try:
        result = run_query(request.question)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats")
def get_stats():
    """Get database statistics"""
    try:
        # Count by type
        stats = {}
        nodes_result = run_query("MATCH (n) WITH labels(n)[0] as type, count(*) as count RETURN type, count")
        for row in nodes_result:
            stats[row.get("type", "Unknown")] = row.get("count", 0)
        
        # Count relationships
        rel_result = run_query("MATCH ()-[r]->() RETURN type(r) as rel_type, count(*) as count ORDER BY count DESC")
        rels = {}
        for row in rel_result:
            rels[row.get("rel_type", "Unknown")] = row.get("count", 0)
        
        return {
            "nodes": stats,
            "relationships": rels,
            "total_nodes": sum(stats.values()),
            "total_relationships": sum(rels.values())
        }
    except Exception as e:
        return {"error": str(e)}
