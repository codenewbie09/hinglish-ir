"""Config loading and global seeding."""
from __future__ import annotations

import os
import random
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


@lru_cache(maxsize=1)
def load_config() -> dict:
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def path(*parts: str) -> Path:
    p = ROOT.joinpath(*parts)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def corpus_mode() -> str:
    """'sample' (default) or 'full'; set by --full / HIR_MODE."""
    return os.environ.get("HIR_MODE", "sample")


def seed_everything(seed: int | None = None) -> int:
    seed = load_config()["seed"] if seed is None else seed
    random.seed(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except ImportError:
        pass
    return seed
