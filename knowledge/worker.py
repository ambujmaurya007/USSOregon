"""Controlled background worker for Emma's knowledge index."""

import hashlib
import json
from pathlib import Path
import re
import time
from typing import Any, Dict, Optional

from ai.providers.ollama_provider import OllamaProvider
from knowledge.knowledge_base import SUPPORTED_EXTENSIONS

METADATA_VERSION = 2


class KnowledgeWorker:
    """Analyze knowledge files and maintain derived metadata and index.md."""

    def __init__(self, config: Dict[str, Any]):
        knowledge_config = config.get("knowledge", {})
        self.root_path = Path(knowledge_config.get("root_path", "./knowledge"))
        self.root_path.mkdir(parents=True, exist_ok=True)
        self.derived_path = self.root_path / ".emma"
        self.metadata_path = self.derived_path / "metadata"
        self.state_path = self.derived_path / "processing.json"
        self.index_path = self.root_path / "index.md"
        worker_config = knowledge_config.get("worker", {})
        self.incoming_path = self.root_path / "incoming"
        self.incoming_path.mkdir(parents=True, exist_ok=True)
        self.analyze_with_ollama = worker_config.get("analyze_with_ollama", True)
        self.max_files_per_cycle = int(worker_config.get("max_files_per_cycle", 1))
        self.worker_model = worker_config.get("model")
        self.ollama = self._create_ollama(config)

    def sync(self, max_files: Optional[int] = None) -> int:
        """Process changed files, remove deleted metadata, and rebuild index.md."""
        self._message("Knowledge sync started")
        records = self._load_state()
        sources = self._source_files()
        current = {str(path.relative_to(self.root_path)): path for path in sources}
        changed = 0

        pending = [
            (source, path) for source, path in current.items()
            if (
                records.get(source, {}).get("sha256") != self._signature(path)
                or records.get(source, {}).get("metadata_version") != METADATA_VERSION
            )
        ]
        pending.sort(key=lambda item: (not item[1].is_relative_to(self.incoming_path), item[0]))
        if max_files is None:
            max_files = len(pending)

        self._message(
            f"Found {len(sources)} source file(s); {len(pending)} pending, "
            f"processing up to {max_files} this cycle"
        )

        for source, path in pending[:max_files]:
            signature = self._signature(path)
            self._message(f"Queued knowledge file: {source}")
            records[source] = self._process_file(path, signature)
            changed += 1

        for source in set(records) - set(current):
            self._message(f"Removing deleted knowledge file: {source}")
            records.pop(source, None)
            metadata_file = self.metadata_path / Path(source).with_suffix(".json")
            metadata_file.unlink(missing_ok=True)
            changed += 1

        self._save_state(records)
        self._write_index(records)
        self._message(f"Knowledge index updated: {self.index_path} ({changed} change(s))")
        return changed

    def watch(self) -> None:
        """Watch for source changes until interrupted."""
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer
        except ImportError as error:
            raise RuntimeError(
                "watchdog is required for background indexing. "
                "Install with: pip install watchdog"
            ) from error

        worker = self

        class ChangeHandler(FileSystemEventHandler):
            def on_any_event(self, event):
                if not event.is_directory and worker._is_source_path(Path(event.src_path)):
                    worker.sync(max_files=worker.max_files_per_cycle)

        observer = Observer()
        observer.schedule(ChangeHandler(), str(self.root_path), recursive=True)
        observer.start()
        self._message(
            f"Emma knowledge worker watching {self.root_path} "
            f"(model: {self.worker_model or 'configured Ollama model'}, "
            f"analysis: {'on' if self.analyze_with_ollama else 'off'})"
        )
        try:
            while True:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()

    def _process_file(self, path: Path, signature: str) -> Dict[str, Any]:
        content = self._read_source(path)
        relative = str(path.relative_to(self.root_path)).replace("\\", "/")
        self._message(f"Reading: {relative}")
        fallback = self._fallback_metadata(path, content)
        metadata = self._analyze(path, content) if self.analyze_with_ollama else {}
        merged = {**fallback, **metadata}
        merged.update({
            "file": relative,
            "sha256": signature,
            "metadata_version": METADATA_VERSION,
            "status": "indexed",
        })
        output = self.metadata_path / path.relative_to(self.root_path).with_suffix(".json")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(merged, indent=2), encoding="utf-8")
        self._message(
            f"Indexed: {relative} | category={merged.get('category', 'general')} | "
            f"topics={len(merged.get('topics', []))} | aliases={len(merged.get('aliases', []))}"
        )
        return merged

    def _analyze(self, path: Path, content: str) -> Dict[str, Any]:
        if not self.ollama or not self.ollama.is_available():
            self._message("Ollama analysis unavailable; using fallback metadata")
            return {}
        self._message(f"Asking Ollama to analyze: {path.name} (model: {self.ollama.model})")
        existing_index = ""
        if self.index_path.exists():
            existing_index = self.index_path.read_text(encoding="utf-8")[:4000]
        prompt = (
            "Analyze this local knowledge file for Emma. Return JSON only with keys "
            "title, category, aliases, topics, concepts, related, age_range, "
            "language, exact_recitation, and good_for. Do not rewrite the source. aliases, "
            "topics, concepts, related, and good_for must be arrays; "
            "exact_recitation must be boolean. Use the existing index to identify "
            "relationships, but do not invent facts not supported by the source.\n\n"
            f"Existing index:\n{existing_index}\n\n"
            f"File: {path.name}\nContent:\n{content[:6000]}"
        )
        try:
            response = self.ollama.generate(prompt, max_tokens=300, temperature=0.1)
            match = re.search(r"\{.*\}", response.text, re.DOTALL)
            value = json.loads(match.group(0)) if match else {}
            if not value:
                self._message(f"Ollama returned no metadata for {path.name}; using fallback")
            else:
                self._message(f"Ollama analysis complete: {path.name}")
            return value if isinstance(value, dict) else {}
        except (RuntimeError, ValueError, json.JSONDecodeError):
            self._message(f"Ollama analysis failed for {path.name}; using fallback metadata")
            return {}

    def _fallback_metadata(self, path: Path, content: str) -> Dict[str, Any]:
        first_line = next((line.strip(" #") for line in content.splitlines() if line.strip()), path.stem)
        category = path.parent.relative_to(self.root_path).parts[0] if path.parent != self.root_path else "general"
        return {
            "title": first_line[:120],
            "category": category,
            "aliases": [path.stem.replace("_", " ")],
            "topics": [category],
            "concepts": [],
            "related": [],
            "language": self._fallback_language(path, content),
            "age_range": "",
            "exact_recitation": category.casefold() in {"poem", "poems", "song", "songs"},
            "good_for": [],
        }

    def _fallback_language(self, path: Path, content: str) -> str:
        """Infer a useful default language label for Roman-Hindi content."""
        normalized = content.casefold()
        hindi_markers = {
            "mujhe", "kya", "kaise", "sunao", "kahani", "chanda", "chand",
            "mein", "hai", "haan", "nahi", "baccha", "ek baar",
        }
        hindi_count = sum(marker in normalized for marker in hindi_markers)
        if "hindi" in normalized or "hinglish" in normalized or hindi_count >= 2:
            return "hinglish"
        if "hindi" in str(path).casefold():
            return "hinglish"
        return "english"

    def _source_files(self):
        return sorted([
            path for path in self.root_path.rglob("*")
            if self._is_source_path(path)
        ], key=lambda path: (not path.is_relative_to(self.incoming_path), str(path)))

    def _is_source_path(self, path: Path) -> bool:
        return (
            path.is_file()
            and ".emma" not in path.parts
            and path.name.casefold() != "index.md"
            and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )

    def _read_source(self, path: Path) -> str:
        if path.suffix.lower() == ".pdf":
            import fitz
            document = fitz.open(path)
            return "\n".join(page.get_text() for page in document)
        return path.read_text(encoding="utf-8", errors="replace")

    def _create_ollama(self, config: Dict[str, Any]) -> Optional[OllamaProvider]:
        if not self.analyze_with_ollama:
            return None
        provider_config = config.get("llm", {}).get("providers", {}).get("ollama", {}).copy()
        if not provider_config.get("enabled", True):
            return None
        if self.worker_model:
            provider_config["model"] = self.worker_model
        return OllamaProvider(provider_config)

    def _load_state(self) -> Dict[str, Dict[str, Any]]:
        if not self.state_path.exists():
            return {}
        try:
            value = json.loads(self.state_path.read_text(encoding="utf-8"))
            return value if isinstance(value, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _save_state(self, records: Dict[str, Dict[str, Any]]) -> None:
        self.derived_path.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(records, indent=2), encoding="utf-8")

    def _write_index(self, records: Dict[str, Dict[str, Any]]) -> None:
        sections = ["# Emma Knowledge Index", "", "This index is generated from local source files. The source files remain authoritative.", ""]
        for category in sorted({record.get("category", "general") for record in records.values()}):
            sections.extend([f"## {category.title()}", ""])
            for source, record in sorted(records.items()):
                if record.get("category", "general") != category:
                    continue
                aliases = ", ".join(record.get("aliases", []))
                topics = ", ".join(record.get("topics", []))
                sections.extend([
                    f"### {record.get('title', Path(source).stem)}",
                    f"- File: {source}",
                    f"- Aliases: {aliases}",
                    f"- Topics: {topics}",
                    f"- Concepts: {', '.join(record.get('concepts', []))}",
                    f"- Related: {', '.join(record.get('related', []))}",
                    f"- Language: {record.get('language', 'english')}",
                    f"- Age: {record.get('age_range', '')}",
                    f"- Good for: {', '.join(record.get('good_for', []))}",
                    f"- Action: {'recite_exactly' if record.get('exact_recitation') else 'explain_or_adapt'}",
                    "",
                ])
        self.index_path.write_text("\n".join(sections), encoding="utf-8")

    def _signature(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _message(self, message: str) -> None:
        """Print worker progress immediately for terminal and service logs."""
        print(f"[Emma Knowledge] {message}", flush=True)
