"""
S.O.I.L.E.R. RAG (Retrieval-Augmented Generation) Module

Simple document retrieval for grounded responses with citations.
"""

from core.rag.retriever import (
    RAGRetriever,
    Citation,
    SearchResult,
    load_corpus,
    search_corpus,
)

__all__ = [
    "RAGRetriever",
    "Citation",
    "SearchResult",
    "load_corpus",
    "search_corpus",
]
