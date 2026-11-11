from pathlib import Path

from knowledge.worker import KnowledgeWorker


def _make_worker(tmp_path):
    root = tmp_path / "knowledge"
    root.mkdir(parents=True, exist_ok=True)
    config = {
        "knowledge": {
            "root_path": str(root),
            "worker": {
                "enabled": True,
                "analyze_with_ollama": False,
                "max_files_per_cycle": 10,
            },
        }
    }
    return KnowledgeWorker(config), root


def test_worker_indexes_new_file_and_updates_index(tmp_path):
    worker, root = _make_worker(tmp_path)
    story = root / "Stories"
    story.mkdir(parents=True, exist_ok=True)
    path = story / "lion_story.txt"
    original = "A brave lion lived in the jungle.\n"
    path.write_text(original, encoding="utf-8")

    changed = worker.sync()

    assert changed == 1
    state = worker._load_state()
    assert "Stories/lion_story.txt" in state
    assert "lion_story" in worker.index_path.read_text(encoding="utf-8")
    assert path.read_text(encoding="utf-8") == original


def test_worker_reprocesses_modified_files_and_removes_deleted_entries(tmp_path):
    worker, root = _make_worker(tmp_path)
    story = root / "Stories"
    story.mkdir(parents=True, exist_ok=True)
    path = story / "fox_story.txt"
    path.write_text("A fox danced in the moonlight.\n", encoding="utf-8")
    worker.sync()

    path.write_text("A fox danced in the moonlight and sang softly.\n", encoding="utf-8")
    changed = worker.sync()
    assert changed == 1
    state = worker._load_state()
    assert state["Stories/fox_story.txt"]["sha256"] == worker._signature(path)

    path.unlink()
    changed = worker.sync()
    assert changed == 1
    state = worker._load_state()
    assert "Stories/fox_story.txt" not in state
    index = worker.index_path.read_text(encoding="utf-8")
    assert "fox_story" not in index
