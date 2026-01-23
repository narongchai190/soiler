"""
S.O.I.L.E.R. RAG Retriever

Simple TF-IDF based document retrieval with citations.
No external dependencies required beyond scikit-learn.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict
import hashlib


@dataclass
class Citation:
    """A citation to a source document."""
    document_id: str
    document_title: str
    source: str
    relevance_score: float
    excerpt: str
    section: Optional[str] = None

    def to_string(self) -> str:
        """Format citation as string."""
        return f"[{self.document_id}] {self.document_title} - {self.source}"


@dataclass
class SearchResult:
    """Result of a RAG search."""
    query: str
    results: List[Citation] = field(default_factory=list)
    total_docs_searched: int = 0

    def get_citations(self) -> List[str]:
        """Get list of citation strings."""
        return [c.to_string() for c in self.results]

    def get_context(self, max_chars: int = 2000) -> str:
        """Get combined context from all results."""
        context_parts = []
        total_chars = 0
        for result in self.results:
            if total_chars + len(result.excerpt) > max_chars:
                break
            context_parts.append(f"[{result.document_id}]: {result.excerpt}")
            total_chars += len(result.excerpt)
        return "\n\n".join(context_parts)


@dataclass
class Document:
    """A document in the corpus."""
    id: str
    title: str
    source: str
    content: str
    sections: Dict[str, str] = field(default_factory=dict)
    file_path: str = ""


class RAGRetriever:
    """
    Simple TF-IDF based document retriever.

    Uses basic text matching for retrieval.
    No external ML dependencies required.
    """

    def __init__(self, corpus_path: Optional[str] = None):
        """
        Initialize retriever.

        Args:
            corpus_path: Path to corpus directory. Defaults to data/corpus/
        """
        if corpus_path is None:
            # Default to project's data/corpus directory
            project_root = Path(__file__).parent.parent.parent
            corpus_path = str(project_root / "data" / "corpus")

        self.corpus_path = Path(corpus_path)
        self.documents: List[Document] = []
        self._loaded = False

    def load(self) -> int:
        """
        Load all documents from corpus.

        Returns:
            Number of documents loaded
        """
        self.documents = []

        if not self.corpus_path.exists():
            return 0

        for file_path in self.corpus_path.glob("*.md"):
            doc = self._parse_document(file_path)
            if doc:
                self.documents.append(doc)

        self._loaded = True
        return len(self.documents)

    def _parse_document(self, file_path: Path) -> Optional[Document]:
        """Parse a markdown document."""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Extract title from first # heading
            title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            title = title_match.group(1) if title_match else file_path.stem

            # Extract source from "Source:" line
            source_match = re.search(r"Source:\s*(.+)$", content, re.MULTILINE)
            source = source_match.group(1) if source_match else "Unknown"

            # Extract document ID from "Document ID:" line
            id_match = re.search(r"Document ID:\s*(.+)$", content, re.MULTILINE)
            doc_id = id_match.group(1) if id_match else self._generate_id(file_path)

            # Extract sections (## headings)
            sections = {}
            section_pattern = re.compile(r"^##\s+(.+?)$\n(.*?)(?=^##|\Z)", re.MULTILINE | re.DOTALL)
            for match in section_pattern.finditer(content):
                section_title = match.group(1).strip()
                section_content = match.group(2).strip()
                sections[section_title] = section_content

            return Document(
                id=doc_id,
                title=title,
                source=source,
                content=content,
                sections=sections,
                file_path=str(file_path),
            )

        except Exception:
            return None

    def _generate_id(self, file_path: Path) -> str:
        """Generate document ID from file path."""
        return f"DOC-{hashlib.md5(str(file_path).encode()).hexdigest()[:8].upper()}"

    def search(self, query: str, top_k: int = 3) -> SearchResult:
        """
        Search corpus for relevant documents.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            SearchResult with citations
        """
        if not self._loaded:
            self.load()

        if not self.documents:
            return SearchResult(query=query, results=[], total_docs_searched=0)

        # Simple keyword matching with scoring
        query_terms = self._tokenize(query.lower())
        scored_docs = []

        for doc in self.documents:
            score = self._score_document(doc, query_terms)
            if score > 0:
                scored_docs.append((doc, score))

        # Sort by score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # Build results
        results = []
        for doc, score in scored_docs[:top_k]:
            excerpt = self._extract_relevant_excerpt(doc, query_terms)
            section = self._find_relevant_section(doc, query_terms)

            results.append(Citation(
                document_id=doc.id,
                document_title=doc.title,
                source=doc.source,
                relevance_score=min(score / 10, 1.0),  # Normalize to 0-1
                excerpt=excerpt,
                section=section,
            ))

        return SearchResult(
            query=query,
            results=results,
            total_docs_searched=len(self.documents),
        )

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        # Split on whitespace and punctuation
        tokens = re.findall(r"\b\w+\b", text.lower())
        # Filter out very short tokens
        return [t for t in tokens if len(t) > 2]

    def _score_document(self, doc: Document, query_terms: List[str]) -> float:
        """Score document relevance to query."""
        doc_text = doc.content.lower()
        score = 0.0

        for term in query_terms:
            # Count occurrences
            count = doc_text.count(term)
            if count > 0:
                score += 1 + (count * 0.1)  # Base score + frequency bonus

            # Bonus for title match
            if term in doc.title.lower():
                score += 2

        return score

    def _extract_relevant_excerpt(self, doc: Document, query_terms: List[str], max_length: int = 300) -> str:
        """Extract most relevant excerpt from document."""
        content = doc.content
        best_excerpt = ""
        best_score = 0

        # Try each paragraph
        paragraphs = content.split("\n\n")
        for para in paragraphs:
            if len(para) < 20:  # Skip very short paragraphs
                continue

            para_lower = para.lower()
            score = sum(1 for term in query_terms if term in para_lower)

            if score > best_score:
                best_score = score
                best_excerpt = para

        # Truncate if needed
        if len(best_excerpt) > max_length:
            best_excerpt = best_excerpt[:max_length] + "..."

        return best_excerpt.strip()

    def _find_relevant_section(self, doc: Document, query_terms: List[str]) -> Optional[str]:
        """Find most relevant section in document."""
        best_section = None
        best_score = 0

        for section_title, section_content in doc.sections.items():
            section_text = (section_title + " " + section_content).lower()
            score = sum(1 for term in query_terms if term in section_text)

            if score > best_score:
                best_score = score
                best_section = section_title

        return best_section

    def get_document_by_id(self, doc_id: str) -> Optional[Document]:
        """Get document by ID."""
        if not self._loaded:
            self.load()

        for doc in self.documents:
            if doc.id == doc_id:
                return doc
        return None

    def list_documents(self) -> List[Dict[str, str]]:
        """List all documents in corpus."""
        if not self._loaded:
            self.load()

        return [
            {
                "id": doc.id,
                "title": doc.title,
                "source": doc.source,
            }
            for doc in self.documents
        ]


# =============================================================================
# Convenience Functions
# =============================================================================

_default_retriever: Optional[RAGRetriever] = None


def load_corpus(corpus_path: Optional[str] = None) -> int:
    """
    Load corpus into default retriever.

    Args:
        corpus_path: Optional custom corpus path

    Returns:
        Number of documents loaded
    """
    global _default_retriever
    _default_retriever = RAGRetriever(corpus_path)
    return _default_retriever.load()


def search_corpus(query: str, top_k: int = 3) -> SearchResult:
    """
    Search corpus using default retriever.

    Args:
        query: Search query
        top_k: Number of results

    Returns:
        SearchResult with citations
    """
    global _default_retriever
    if _default_retriever is None:
        load_corpus()
    return _default_retriever.search(query, top_k)
