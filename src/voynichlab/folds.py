from __future__ import annotations

import hashlib

N_FOLDS = 5
DEVELOPMENT_FOLDS = (0, 1, 2)
HOLDOUT_FOLDS = (3, 4)


def folio_fold(folio: str) -> int:
    """Deterministic, transcription-agnostic fold for a folio id (E006 frozen split)."""
    h = hashlib.sha256(folio.lower().encode("utf-8")).hexdigest()
    return int(h, 16) % N_FOLDS


def is_holdout(folio: str) -> bool:
    return folio_fold(folio) in HOLDOUT_FOLDS


def is_development(folio: str) -> bool:
    return folio_fold(folio) in DEVELOPMENT_FOLDS
