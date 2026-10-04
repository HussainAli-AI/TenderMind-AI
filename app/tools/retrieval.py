import re
from rank_bm25 import BM25Okapi
from typing import List, Dict

def tokenize(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())

class FastBM25Retriever:
    def __init__(self, pages, chunk_size: int = 800, overlap: int = 150):
        self.chunks: List[Dict] = []
        for p in pages:
            text = p.text
            if not text.strip():
                continue
            for start in range(0, max(len(text), 1), max(chunk_size - overlap, 1)):
                chunk = text[start:start + chunk_size]
                if chunk.strip():
                    self.chunks.append({"page": p.page_num, "text": chunk})
        
        if not self.chunks:
            self.chunks.append({"page": 1, "text": "No readable text extracted from document."})

        tokenized_corpus = [tokenize(c["text"]) for c in self.chunks]
        # Avoid empty token lists for BM25
        tokenized_corpus = [tok if tok else ["empty"] for tok in tokenized_corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def retrieve(self, query: str, top_k: int = 6) -> List[Dict]:
        tokenized_query = tokenize(query)
        if not tokenized_query:
            return self.chunks[:top_k]
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        matched = [self.chunks[i] for i in top_indices if scores[i] > 0]
        # If no positive BM25 score, return top chunks anyway for safety
        if not matched and self.chunks:
            return self.chunks[:min(top_k, len(self.chunks))]
        return matched
