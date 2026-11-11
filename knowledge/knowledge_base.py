"""Local, file-backed knowledge retrieval for Emma.

Stage 1 deliberately uses a small local keyword index. It keeps source files as
truth and can later be replaced by an embedding store without changing callers.
"""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
from collections import Counter


SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}
SEARCH_STOP_WORDS = {
    "a", "an", "and", "are", "can", "do", "does", "for", "how", "i",
    "is", "it", "me", "of", "please", "tell", "the", "this", "to", "what",
    "when", "where", "who", "why", "would", "you",
}


@dataclass
class KnowledgeChunk:
    source: str
    category: str
    title: str
    content: str
    metadata: Dict[str, Any]


class KnowledgeBase:
    """Read and search local knowledge files, refreshing changed files on demand."""

    def __init__(self, root_path: str = "./knowledge", chunk_size: int = 900):
        self.root_path = Path(root_path)
        self.chunk_size = chunk_size
        self._file_signatures: Dict[str, str] = {}
        self._chunks: List[KnowledgeChunk] = []
        self.root_path.mkdir(parents=True, exist_ok=True)

    def refresh(self) -> None:
        """Index added or changed files and remove deleted files."""
        files = sorted(
            path for path in self.root_path.rglob("*")
            if path.is_file()
            and ".emma" not in path.parts
            and path.name.casefold() != "index.md"
            and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        current_signatures = {str(path): self._signature(path) for path in files}
        changed = {
            path for path, signature in current_signatures.items()
            if self._file_signatures.get(path) != signature
        }
        deleted = set(self._file_signatures) - set(current_signatures)
        if not changed and not deleted:
            return

        # Rebuild the small local index when files change so stale chunks cannot
        # survive a rename or metadata update.
        self._chunks = []
        for path in files:
            self._chunks.extend(self._index_file(path))
        self._file_signatures = current_signatures

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 4,
    ) -> List[KnowledgeChunk]:
        """Return the most relevant local chunks for a request."""
        self.refresh()
        query_terms = self._terms(query)
        if not query_terms:
            return []

        scored = []
        for chunk in self._chunks:
            if category and chunk.category.casefold() != category.casefold():
                continue
            searchable = self._terms(
                " ".join([
                    chunk.title,
                    chunk.category,
                    " ".join(chunk.metadata.get("aliases", [])),
                    chunk.content,
                ])
            )
            searchable_counts = Counter(searchable)
            score = sum(searchable_counts[term] for term in query_terms)
            if score:
                scored.append((score, chunk))
        scored.sort(key=lambda item: (-item[0], item[1].source))
        return [chunk for _, chunk in scored[:limit]]

    def find_exact(self, query: str, category: Optional[str] = None) -> Optional[KnowledgeChunk]:
        """Find source text intended for exact recitation, such as a poem."""
        matches = self.search(query, category=category, limit=20)
        for match in matches:
            if match.metadata.get("exact_recitation") or match.category.casefold() in {"poem", "poems", "song", "songs"}:
                return match
        return None

    def list_exact(self, category: Optional[str] = None) -> List[KnowledgeChunk]:
        """List unique exact-recitation sources available in the library."""
        self.refresh()
        results = []
        seen = set()
        for chunk in self._chunks:
            if not (chunk.metadata.get("exact_recitation") or chunk.category.casefold() in {"poem", "poems", "song", "songs"}):
                continue
            if category and chunk.category.casefold().rstrip("s") != category.casefold().rstrip("s"):
                continue
            if chunk.source in seen:
                continue
            seen.add(chunk.source)
            results.append(chunk)
        return results

    def format_for_prompt(self, matches: List[KnowledgeChunk]) -> str:
        """Format retrieved content while preserving source and exact text."""
        sections = []
        for match in matches:
            exact = match.metadata.get("exact_recitation", False)
            instruction = "Use this exact text when reciting." if exact else "Use this as local reference material."
            sections.append(
                f"Source: {match.source}\n"
                f"Title: {match.title}\n"
                f"{instruction}\n"
                f"Content:\n{match.content}"
            )
        return "\n\n".join(sections)

    def _index_file(self, path: Path) -> List[KnowledgeChunk]:
        content = self._read_file(path)
        if not content.strip():
            return []
        metadata = self._load_metadata(path)
        relative = path.relative_to(self.root_path)
        category = metadata.get("category") or (relative.parts[0] if len(relative.parts) > 1 else "general")
        title = metadata.get("title") or self._title_from_content(path, content)
        if category.casefold() in {"poem", "poems", "song", "songs"}:
            metadata["exact_recitation"] = True
        chunks = [content.strip()] if metadata.get("exact_recitation") else self._split(content)
        return [
            KnowledgeChunk(
                source=str(relative),
                category=category,
                title=title,
                content=chunk,
                metadata=metadata,
            )
            for chunk in chunks
        ]

    def _read_file(self, path: Path) -> str:
        if path.suffix.lower() == ".pdf":
            try:
                import fitz
            except ImportError as error:
                raise RuntimeError(
                    "PDF knowledge files require PyMuPDF. Install with: pip install pymupdf"
                ) from error
            document = fitz.open(path)
            return "\n".join(page.get_text() for page in document)
        return path.read_text(encoding="utf-8", errors="replace")

    def _load_metadata(self, path: Path) -> Dict[str, Any]:
        derived_path = self.root_path / ".emma" / "metadata" / path.relative_to(self.root_path)
        derived_path = derived_path.with_suffix(".json")
        metadata_path = path.with_suffix(".json")
        metadata = {}
        for candidate in (derived_path, metadata_path):
            if not candidate.exists():
                continue
            try:
                value = json.loads(candidate.read_text(encoding="utf-8"))
                if isinstance(value, dict):
                    metadata.update(value)
            except (OSError, json.JSONDecodeError):
                continue
        return metadata

    def _title_from_content(self, path: Path, content: str) -> str:
        for line in content.splitlines():
            line = line.strip().lstrip("#").strip()
            if line:
                return line[:120]
        return path.stem.replace("_", " ").title()

    def _split(self, content: str) -> List[str]:
        normalized = re.sub(r"\s+", " ", content).strip()
        return [normalized[index:index + self.chunk_size] for index in range(0, len(normalized), self.chunk_size)]

    def _signature(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _terms(self, text: str) -> List[str]:
        return [
            term for term in re.findall(r"[a-z0-9]+", text.casefold())
            if term not in SEARCH_STOP_WORDS
        ]
