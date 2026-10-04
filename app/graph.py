from typing import TypedDict, List, Any
from langgraph.graph import StateGraph, END
from app.tools.retrieval import FastBM25Retriever
from app.agents.extractor import run_extractor
from app.agents.verifier import run_verifier
from app.agents.rules import evaluate_eligibility

class TenderState(TypedDict):
    pages: List[Any]
    profile: dict
    retriever: Any
    raw_extraction: dict
    verified_extraction: dict
    verdict: str
    rule_results: List[dict]

def retrieval_node(state: TenderState) -> dict:
    retriever = FastBM25Retriever(state["pages"])
    queries = [
        "submission deadline bid opening date time earnest money",
        "pec category license registration pakistan engineering council",
        "tax ntn strn active taxpayer fbr compliance",
        "mandatory required documents certificates experience audited",
        "estimated cost tender fee boq"
    ]
    chunks = []
    seen = set()
    for q in queries:
        for c in retriever.retrieve(q, top_k=4):
            key = (c["page"], c["text"][:60])
            if key not in seen:
                seen.add(key)
                chunks.append(c)

    # In case document is small or queries yielded few chunks, ensure all pages are covered
    if len(chunks) < 3 and retriever.chunks:
        for c in retriever.chunks:
            key = (c["page"], c["text"][:60])
            if key not in seen:
                seen.add(key)
                chunks.append(c)

    raw_extraction = run_extractor(chunks)
    return {"retriever": retriever, "raw_extraction": raw_extraction}

def verification_node(state: TenderState) -> dict:
    verified = run_verifier(state["raw_extraction"], state["pages"])
    return {"verified_extraction": verified}

def rules_node(state: TenderState) -> dict:
    verdict, results = evaluate_eligibility(state["verified_extraction"], state["profile"])
    return {"verdict": verdict, "rule_results": results}

def build_tender_graph():
    graph = StateGraph(TenderState)
    graph.add_node("retriever", retrieval_node)
    graph.add_node("verifier", verification_node)
    graph.add_node("rules", rules_node)
    
    graph.set_entry_point("retriever")
    graph.add_edge("retriever", "verifier")
    graph.add_edge("verifier", "rules")
    graph.add_edge("rules", END)
    
    return graph.compile()
