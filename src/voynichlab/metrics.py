from __future__ import annotations

from collections import Counter
import math
from typing import Iterable, Sequence

import numpy as np


def entropy(values: Iterable[str]) -> float:
    c = Counter(values)
    n = sum(c.values())
    if n == 0:
        return 0.0
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def type_token_ratio(values: Sequence[str]) -> float:
    return len(set(values)) / len(values) if values else 0.0


def jensen_shannon(p: dict[str, float], q: dict[str, float]) -> float:
    keys = sorted(set(p) | set(q))
    pa = np.array([p.get(k, 0.0) for k in keys], dtype=float)
    qa = np.array([q.get(k, 0.0) for k in keys], dtype=float)
    if pa.sum():
        pa /= pa.sum()
    if qa.sum():
        qa /= qa.sum()
    m = (pa + qa) / 2

    def kl(a, b):
        mask = (a > 0) & (b > 0)
        return float(np.sum(a[mask] * np.log2(a[mask] / b[mask])))

    return (kl(pa, m) + kl(qa, m)) / 2


def repeated_ngram_types(tokens: Sequence[str], n: int) -> int:
    if n <= 0 or len(tokens) < n:
        return 0
    counts = Counter(tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1))
    return sum(1 for count in counts.values() if count >= 2)
