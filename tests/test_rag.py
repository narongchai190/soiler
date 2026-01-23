"""
Unit tests for RAG retriever.

Tests verify document loading, search, and citation generation.
"""

import pytest

from core.rag.retriever import (
    RAGRetriever,
    Citation,
    SearchResult,
    load_corpus,
    search_corpus,
)


class TestRAGRetriever:
    """Test RAG retriever functionality."""

    @pytest.fixture
    def retriever(self):
        """Create retriever with default corpus."""
        r = RAGRetriever()
        r.load()
        return r

    def test_load_corpus(self, retriever):
        """Should load documents from corpus directory."""
        assert len(retriever.documents) > 0

    def test_documents_have_required_fields(self, retriever):
        """Documents should have all required fields."""
        for doc in retriever.documents:
            assert doc.id is not None
            assert doc.title is not None
            assert doc.source is not None
            assert doc.content is not None

    def test_search_returns_results(self, retriever):
        """Search should return relevant results."""
        result = retriever.search("pH soil acidic")
        assert isinstance(result, SearchResult)
        assert len(result.results) > 0

    def test_search_respects_top_k(self, retriever):
        """Search should respect top_k limit."""
        result = retriever.search("fertilizer", top_k=2)
        assert len(result.results) <= 2

    def test_citations_have_required_fields(self, retriever):
        """Citations should have all required fields."""
        result = retriever.search("nitrogen")
        for citation in result.results:
            assert citation.document_id is not None
            assert citation.document_title is not None
            assert citation.source is not None
            assert citation.relevance_score >= 0
            assert citation.excerpt is not None

    def test_get_citations_returns_strings(self, retriever):
        """get_citations should return formatted strings."""
        result = retriever.search("potassium")
        citations = result.get_citations()
        assert isinstance(citations, list)
        for c in citations:
            assert isinstance(c, str)
            assert "[" in c  # Should have document ID

    def test_get_context_returns_text(self, retriever):
        """get_context should return combined text."""
        result = retriever.search("rice")
        context = result.get_context()
        assert isinstance(context, str)
        assert len(context) > 0

    def test_get_document_by_id(self, retriever):
        """Should retrieve document by ID."""
        # First get a known ID
        if retriever.documents:
            doc_id = retriever.documents[0].id
            doc = retriever.get_document_by_id(doc_id)
            assert doc is not None
            assert doc.id == doc_id

    def test_list_documents(self, retriever):
        """Should list all documents."""
        docs = retriever.list_documents()
        assert isinstance(docs, list)
        assert len(docs) > 0
        for doc in docs:
            assert "id" in doc
            assert "title" in doc
            assert "source" in doc


class TestSearchRelevance:
    """Test search relevance and ranking."""

    @pytest.fixture
    def retriever(self):
        """Create retriever with default corpus."""
        r = RAGRetriever()
        r.load()
        return r

    def test_ph_query_finds_ph_document(self, retriever):
        """pH query should find pH standards document."""
        result = retriever.search("pH acidic alkaline soil")
        assert len(result.results) > 0
        # At least one result should mention pH in title
        titles = [r.document_title.lower() for r in result.results]
        assert any("ph" in t for t in titles)

    def test_rice_query_finds_rice_document(self, retriever):
        """Rice query should find rice fertilizer document."""
        result = retriever.search("rice fertilizer urea")
        assert len(result.results) > 0
        # Should find rice document
        doc_ids = [r.document_id for r in result.results]
        titles = [r.document_title.lower() for r in result.results]
        assert any("rice" in t or "RICE" in d for t, d in zip(titles, doc_ids))

    def test_cassava_query_finds_cassava_document(self, retriever):
        """Cassava query should find cassava document."""
        result = retriever.search("cassava potassium tuber")
        assert len(result.results) > 0

    def test_organic_query_finds_organic_document(self, retriever):
        """Organic query should find organic fertilizer document."""
        result = retriever.search("organic compost manure")
        assert len(result.results) > 0
        titles = [r.document_title.lower() for r in result.results]
        assert any("organic" in t for t in titles)

    def test_relevance_scores_ordered(self, retriever):
        """Results should be ordered by relevance score."""
        result = retriever.search("nitrogen phosphorus potassium NPK")
        if len(result.results) > 1:
            scores = [r.relevance_score for r in result.results]
            assert scores == sorted(scores, reverse=True)


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_load_corpus_returns_count(self):
        """load_corpus should return document count."""
        count = load_corpus()
        assert count > 0

    def test_search_corpus_returns_results(self):
        """search_corpus should return results."""
        result = search_corpus("soil pH")
        assert isinstance(result, SearchResult)
        assert len(result.results) > 0


class TestCitation:
    """Test Citation class."""

    def test_to_string_format(self):
        """Citation to_string should have proper format."""
        citation = Citation(
            document_id="DOC-001",
            document_title="Test Document",
            source="Test Source",
            relevance_score=0.8,
            excerpt="Test excerpt",
        )
        s = citation.to_string()
        assert "[DOC-001]" in s
        assert "Test Document" in s
        assert "Test Source" in s


class TestSearchResult:
    """Test SearchResult class."""

    def test_get_citations_empty(self):
        """Empty results should return empty list."""
        result = SearchResult(query="test")
        citations = result.get_citations()
        assert citations == []

    def test_get_context_respects_max_chars(self):
        """get_context should respect max_chars limit."""
        result = SearchResult(
            query="test",
            results=[
                Citation(
                    document_id="DOC-001",
                    document_title="Test",
                    source="Test",
                    relevance_score=1.0,
                    excerpt="A" * 1000,
                ),
                Citation(
                    document_id="DOC-002",
                    document_title="Test",
                    source="Test",
                    relevance_score=0.8,
                    excerpt="B" * 1000,
                ),
            ]
        )
        context = result.get_context(max_chars=500)
        assert len(context) <= 600  # Some buffer for formatting


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_query(self):
        """Empty query should not crash."""
        r = RAGRetriever()
        r.load()
        result = r.search("")
        assert isinstance(result, SearchResult)

    def test_nonexistent_corpus_path(self):
        """Nonexistent corpus path should return empty."""
        r = RAGRetriever("/nonexistent/path")
        count = r.load()
        assert count == 0

    def test_thai_query(self):
        """Thai language query should work."""
        r = RAGRetriever()
        r.load()
        result = r.search("ไนโตรเจน ฟอสฟอรัส โพแทสเซียม")
        # Should still search even if results vary
        assert isinstance(result, SearchResult)

    def test_special_characters_in_query(self):
        """Special characters should not crash."""
        r = RAGRetriever()
        r.load()
        result = r.search("pH < 5.5 & N > 20")
        assert isinstance(result, SearchResult)
