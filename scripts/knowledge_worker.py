"""Run Emma's controlled knowledge index worker."""

import argparse
from pathlib import Path
import sys

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge.worker import KnowledgeWorker


def main():
    parser = argparse.ArgumentParser(description="Emma local knowledge worker")
    parser.add_argument("--config", default="config/teddy.yaml", help="Emma YAML configuration")
    parser.add_argument("--once", action="store_true", help="Index files once and exit")
    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file) or {}

    worker = KnowledgeWorker(config)
    changed = worker.sync() if args.once else worker.sync(
        max_files=worker.max_files_per_cycle
    )
    print(f"Knowledge sync complete; changed files: {changed}")
    if not args.once:
        worker.watch()


if __name__ == "__main__":
    main()
