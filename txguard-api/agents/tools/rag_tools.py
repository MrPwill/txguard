from crewai.tools import tool
from agents.rag.store import query_collection

@tool("search_fraud_typologies")
def search_fraud_typologies(query: str) -> str:
    """
    RAG search over curated fraud pattern library (card testing, structuring, ATO, mule accounts, layering).
    Input: search query (string) describing the suspicious behavior.
    """
    results = query_collection("fraud_typologies", query)
    return "\n".join(results) if results else "No matching fraud typologies found."

@tool("search_aml_regulations")
def search_aml_regulations(query: str) -> str:
    """
    RAG search over AML/CFT regulatory documents.
    Input: search query (string) for specific AML rules or CTR/SAR thresholds.
    """
    results = query_collection("aml_regulations", query)
    return "\n".join(results) if results else "No matching AML regulations found."

@tool("get_similar_past_investigations")
def get_similar_past_investigations(query: str) -> str:
    """
    RAG search over prior TxGuard investigation reports for precedent.
    Input: search query (string) describing the transaction or account behavior.
    """
    results = query_collection("past_investigations", query)
    return "\n".join(results) if results else "No similar past investigations found."
