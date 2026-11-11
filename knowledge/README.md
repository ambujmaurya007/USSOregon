# Emma Knowledge Library

Add local content under these folders:

- `poems/`
- `stories/`
- `songs/`
- `animals/`
- `numbers/`
- `educational/`
- `family_rules/`

For a batch of new files, you can place them in `incoming/`. The background
worker processes that queue before the other knowledge folders, one file per
cycle by default, so Emma's conversation process is not blocked by a large
import.

Supported files are `.txt`, `.md`, and `.pdf`. The first version indexes files on demand when Emma receives a request. It notices added, changed, and deleted files without retraining Ollama.

For optional metadata, add a JSON file beside the source file with the same name:

```json
{
  "title": "Twinkle Twinkle Little Star",
  "category": "poem",
  "aliases": ["twinkle", "twinkle twinkle", "star poem"],
  "exact_recitation": true,
  "age_range": "2-5"
}
```

Keep private material in `family_rules/`. It is processed locally and is never sent to a cloud provider by the default router.

## Knowledge Worker

Run a one-time controlled sync:

```powershell
.\venv\Scripts\python.exe scripts/knowledge_worker.py --once
```

Run the background watcher:

```powershell
.\venv\Scripts\python.exe scripts/knowledge_worker.py
```

The worker uses Ollama to propose metadata only. It writes derived metadata to
`.emma/metadata/` and a human-readable map to `index.md`; it never changes the
original knowledge files.

The knowledge worker can use a different Ollama model from Emma. Set
`knowledge.worker.model` in `config/teddy.yaml` when a larger model should be
used for slow background analysis.
