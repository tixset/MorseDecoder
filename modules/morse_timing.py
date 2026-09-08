"""Estimate the Morse dot duration from the 1:3 dot/dash timing model."""

from functools import lru_cache

import numpy as np


def estimate_timing(pulses):
    # Parameter searches reuse pulse timings while varying character/word gaps.
    return dict(_estimate_durations(tuple(float(p['duration']) for p in pulses)))


@lru_cache(maxsize=128)
def _estimate_durations(values):
    durations = np.asarray(values, dtype=float)
    durations = durations[np.isfinite(durations) & (durations > 0)]
    unknown = {'dot_duration': 0.0, 'wpm': 0.0, 'reliable': False, 'fit_ratio': 0.0}
    if len(durations) < 6:
        return unknown
    # Search 2-100 WPM, without clipping an implausible result to a valid speed.
    seeds = np.percentile(durations, np.linspace(5, 95, 19))
    candidates = np.unique(np.concatenate((seeds, seeds / 3)))
    best = None
    for unit in candidates:
        if not 0.012 <= unit <= 0.6:
            continue
        for _ in range(3):
            lengths = np.where(durations < 2 * unit, 1.0, 3.0)
            residual = np.abs(durations / (lengths * unit) - 1)
            inliers = residual <= 0.3
            if not np.any(inliers):
                break
            unit = float(np.median(durations[inliers] / lengths[inliers]))
        lengths = np.where(durations < 2 * unit, 1.0, 3.0)
        residual = np.abs(durations / (lengths * unit) - 1)
        inliers = residual <= 0.3
        dots = np.count_nonzero(inliers & (lengths == 1))
        dashes = np.count_nonzero(inliers & (lengths == 3))
        # One pulse class alone cannot distinguish dots from dashes.
        if min(dots, dashes) < 3:
            continue
        fit = float(np.mean(inliers))
        error = float(np.median(residual))
        rank = (fit, -error)
        if best is None or rank > best[0]:
            reliable = fit >= 0.8 and error <= 0.2 and 0.012 <= unit <= 0.6
            best = (rank, {'dot_duration': unit, 'wpm': round(1.2 / unit, 1) if reliable else 0.0,
                           'reliable': reliable, 'fit_ratio': fit})
    return best[1] if best else unknown
