"""
Rune efficiency equivalence calculator (Monte Carlo, 6★ legendary).

Model for b good subs:
  - 4 total subs: first b from template are "good", rest are irrelevant
  - Initial value per sub i: uniform [1, max_i]
  - 4 rolls at +3/+6/+9/+12: each targets one of 4 subs uniformly,
    adding uniform [1, max_i] to that sub
  - Only good subs contribute:  eff = (1 + Σ v_i/(max_i·5)) / 2.8

Equivalence definition: given threshold T at bucket b,
find T' at bucket b' such that P(eff ≥ T | b) = P(eff ≥ T' | b').
"""
import threading

import numpy as np


EFF_DIVISOR = 2.8
EFF_TEMPLATES = {
    "eff_support": [("SPD", 6), ("ATK%", 8), ("HP%", 8), ("DEF%", 8)],
    "eff_dps":     [("SPD", 6), ("ATK%", 8), ("CR",  6), ("CD",  7)],
}
BUCKETS = [2, 3, 4]
N_SIMS = 400_000


# ── core simulation ───────────────────────────────────────────────────────────

def _simulate(n_good: int, template: list, n_sims: int, rng) -> np.ndarray:
    """Returns n_sims efficiency samples for n_good good subs (legendary model)."""
    maxes = np.array([m for _, m in template[:n_good]], dtype=np.int32)

    # Initial value for each good sub
    totals = np.stack([
        rng.integers(1, int(m) + 1, n_sims) for m in maxes
    ]).astype(np.float64)  # shape (n_good, n_sims)

    # 4 rolls, each targeting one of 4 subs uniformly
    roll_targets = rng.integers(0, 4, size=(4, n_sims))
    for r in range(4):
        t = roll_targets[r]
        for i, m in enumerate(maxes):
            mask = (t == i)
            totals[i] += rng.integers(1, int(m) + 1, n_sims) * mask

    # eff formula
    normalized = totals / (maxes[:, np.newaxis] * 5)
    return (1.0 + normalized.sum(axis=0)) / EFF_DIVISOR


# ── CDF ───────────────────────────────────────────────────────────────────────

def _p_exceed(value: float, sorted_eff: np.ndarray) -> float:
    """Empirical P(eff >= value)."""
    idx = int(np.searchsorted(sorted_eff, value, side="left"))
    return 1.0 - idx / len(sorted_eff)


def _inv_exceed(p_exc: float, sorted_eff: np.ndarray) -> float:
    """Minimum threshold v such that P(eff >= v) ≈ p_exc."""
    n = len(sorted_eff)
    p_below = 1.0 - p_exc
    idx = max(0, min(int(p_below * n), n - 1))
    return float(sorted_eff[idx])


# ── public API ────────────────────────────────────────────────────────────────

class EffEquivCalc:
    """Computes CDFs on first use (lazy); thread-safe."""

    def __init__(self):
        self._cdfs: dict | None = None
        self._lock = threading.Lock()

    def _ensure_ready(self):
        if self._cdfs is None:
            with self._lock:
                if self._cdfs is None:
                    rng = np.random.default_rng(42)
                    cdfs: dict = {}
                    for eff_key, template in EFF_TEMPLATES.items():
                        cdfs[eff_key] = {}
                        for b in BUCKETS:
                            effs = _simulate(b, template, N_SIMS, rng)
                            cdfs[eff_key][b] = np.sort(effs)
                    self._cdfs = cdfs

    @property
    def is_ready(self) -> bool:
        return self._cdfs is not None

    def find_equiv(self, eff_value: float, source_bucket: int, eff_key: str) -> dict:
        """
        Returns {2: float, 3: float, 4: float} — equivalent thresholds at each
        bucket having the same P(eff >= threshold) as eff_value at source_bucket.
        """
        self._ensure_ready()
        src = self._cdfs[eff_key][source_bucket]
        p_exc = _p_exceed(eff_value, src)
        return {b: round(_inv_exceed(p_exc, self._cdfs[eff_key][b]), 3) for b in BUCKETS}


calc = EffEquivCalc()
