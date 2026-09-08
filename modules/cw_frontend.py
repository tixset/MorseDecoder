"""Narrow-band CW extraction and hysteresis keying detection."""

import numpy as np
from scipy import ndimage, signal


def select_carrier(audio, sample_rate):
    """Find a tonal peak in the speech/CW audio range, independent of the text."""
    frequencies, power = signal.welch(audio, sample_rate, nperseg=min(8192, len(audio)))
    eligible = (frequencies >= 250) & (frequencies <= min(3000, sample_rate * 0.45))
    if not np.any(eligible) or not np.any(power[eligible] > 0):
        return None
    # A broad noise spectrum is not evidence of a CW carrier.
    noise = np.median(power[eligible])
    peak = np.argmax(power[eligible])
    if power[eligible][peak] < max(noise * 10, np.finfo(float).tiny):
        return None
    return float(frequencies[eligible][peak])


def filter_carrier(audio, sample_rate, center, half_width=40):
    low = max(10, center - half_width)
    high = min(sample_rate * 0.49, center + half_width)
    sos = signal.butter(4, [low, high], fs=sample_rate, btype='bandpass', output='sos')
    return signal.sosfiltfilt(sos, audio), (low, high)


def smooth_envelope(audio, sample_rate):
    amplitude = np.abs(signal.hilbert(audio))
    sos = signal.butter(2, min(30, sample_rate * 0.1), fs=sample_rate, output='sos')
    return np.maximum(signal.sosfiltfilt(sos, amplitude), 0)


def detect_keying(envelope, sample_rate, sensitivity):
    """Keep threshold regions with a stronger core; merge brief dropouts."""
    floor, level = np.percentile(envelope, [10, 90])
    if level <= floor + np.finfo(float).eps or level - floor < level * 0.1:
        return [], []
    # The legacy percentile control now selects a fraction of the signal/noise range.
    fraction = np.clip((sensitivity - 20) / 200, 0.1, 0.4)
    low = floor + (level - floor) * fraction
    high = floor + (level - floor) * fraction * 1.1
    labels, count = ndimage.label(envelope > low)
    active = np.zeros(count + 1, dtype=bool)
    active[np.unique(labels[envelope > high])] = True
    active[0] = False
    keyed = active[labels]
    # Closing bridges dropouts shorter than 10 ms, leaving genuine CW gaps intact.
    keyed = ndimage.binary_closing(keyed, structure=np.ones(max(1, round(sample_rate * .01))))
    edges = np.diff(np.concatenate(([0], keyed, [0])))
    starts, ends = np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)
    keep = ends - starts >= sample_rate * .015
    starts, ends = starts[keep], ends[keep]
    pulses = [{'start': float(start / sample_rate), 'end': float(end / sample_rate),
               'duration': float((end - start) / sample_rate)} for start, end in zip(starts, ends)]
    gaps = ((starts[1:] - ends[:-1]) / sample_rate).tolist()
    return pulses, gaps
