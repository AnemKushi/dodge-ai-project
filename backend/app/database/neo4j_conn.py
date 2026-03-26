from neo4j import GraphDatabase
from app.config import settings

driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
)

def run_query(query: str, params: dict = None):
    """Execute a Cypher query and return raw results"""
    with driver.session() as session:
        result = session.run(query, params or {})
        return [record.data() for record in result]


def query_to_graph(cypher_query: str, params: dict = None):
    """Convert Cypher results to graph format (nodes + edges) for vis.js"""
    with driver.session() as session:
        try:
            result = session.run(cypher_query, params or {})
        except Exception as e:
            print(f"Query error: {str(e)}")
            return {"nodes": [], "edges": []}
        
        nodes = {}
        edges_set = set()
        
        for record in result:
            # CRITICAL: Don't use record.data() - it converts Neo4j objects to dicts
            # Access values directly to preserve Neo4j object types
            for value in record.values():
                if value is None:
                    continue
                    
                # NODE: Has labels attribute (Neo4j Node object)
                if hasattr(value, "labels") and hasattr(value, "element_id"):
                    try:
                        label = list(value.labels)[0] if value.labels else "Unknown"
                        node_id = str(value.element_id)  # Use element_id instead of identity
                        props = dict(value)
                        
                        # Create display label from common properties
                        display = (
                            props.get("id") or 
                            props.get("name") or 
                            props.get("billingDocument") or 
                            props.get("salesOrder") or 
                            props.get("deliveryDocument") or
                            props.get("accountingDocument") or
                            props.get("product") or
                            ""
                        )
                        
                        if node_id not in nodes:
                            nodes[node_id] = {
                                "id": node_id,
                                "label": f"{label}: {display}" if display else label,
                                "title": f"<strong>{label}</strong><br>" + "<br>".join([f"{k}: {v}" for k,v in list(props.items())[:5]]),
                                "group": label,
                                "color": get_node_color(label)
                            }
                    except Exception as e:
                        print(f"Error processing node: {str(e)}")
                        continue
                
                # EDGE: Has type attribute (Neo4j Relationship object)
                elif hasattr(value, "type") and hasattr(value, "start_node"):
                    try:
                        start_node = value.start_node
                        end_node = value.end_node
                        
                        start_id = str(start_node.element_id)  # Use element_id
                        end_id = str(end_node.element_id)      # Use element_id
                        
                        # Ensure both nodes exist in the nodes dict
                        if start_id not in nodes:
                            try:
                                start_label = list(start_node.labels)[0] if start_node.labels else "Unknown"
                                start_props = dict(start_node)
                                start_display = (
                                    start_props.get("id") or 
                                    start_props.get("name") or 
                                    start_props.get("product") or 
                                    ""
                                )
                                nodes[start_id] = {
                                    "id": start_id,
                                    "label": f"{start_label}: {start_display}" if start_display else start_label,
                                    "title": start_label,
                                    "group": start_label,
                                    "color": get_node_color(start_label)
                                }
                            except:
                                pass
                        
                        if end_id not in nodes:
                            try:
                                end_label = list(end_node.labels)[0] if end_node.labels else "Unknown"
                                end_props = dict(end_node)
                                end_display = (
                                    end_props.get("id") or 
                                    end_props.get("name") or 
                                    end_props.get("product") or 
                                    ""
                                )
                                nodes[end_id] = {
                                    "id": end_id,
                                    "label": f"{end_label}: {end_display}" if end_display else end_label,
                                    "title": end_label,
                                    "group": end_label,
                                    "color": get_node_color(end_label)
                                }
                            except:
                                pass
                        
                        # Create edge
                        edges_set.add((start_id, end_id, value.type))
                    except Exception as e:
                        print(f"Error processing edge: {str(e)}")
                        continue
        
        # Convert edges_set to list of dicts
        edges = [
            {
                "from": str(e[0]),
                "to": str(e[1]),
                "label": e[2],
                "arrows": "to",
                "smooth": {"type": "continuous"},
                "color": {"color": "#888888"}
            }
            for e in edges_set
        ]
        
        print(f"[GRAPH] Nodes: {len(nodes)}, Edges: {len(edges)}")
        
        return {
            "nodes": list(nodes.values()),
            "edges": edges
        }


def get_node_color(label: str) -> dict:
    """Get color for node based on label"""
    colors = {
        "Customer": "#3b82f6",
        "Order": "#8b5cf6",
        "Invoice": "#10b981",
        "Delivery": "#f97316",
        "Payment": "#06b6d4",
        "Product": "#f59e0b",
        "Plant": "#6366f1",
        "Address": "#ec4899",
        "Company": "#14b8a6"
    }
    return {
        "background": "#ffffff",
        "border": colors.get(label, "#64748b"),
        "highlight": {
            "background": colors.get(label, "#64748b"),
            "border": "#000000"
        }
    }



def close():
    """Close Neo4j connection"""
    driver.close()
