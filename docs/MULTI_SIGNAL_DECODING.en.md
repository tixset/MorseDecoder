# 🎵 Decoding Multiple Parallel Signals

[Русский](MULTI_SIGNAL_DECODING.md) | **English** | [README](../README.en.md)

## Overview

`multi_signal_decoder.py` can decode multiple parallel Morse signals from one recording, distinguishing them by:

- **Frequency (pitch)**: signals occupy different frequency bands.
- **Sending speed (WPM)**: signals may use different speeds.
- **Amplitude (volume)**: signals may have different strengths.

This mode is experimental. The examples below translate the original guide; historical percentages are not verified transcription accuracy.

## Usage

### Automatic Frequency Detection

```bash
python morse_cli.py multi recording.wav --auto-detect
```

The system finds spectral peaks and creates a separate decoder for each frequency band.

### Manual Frequency Bands

```bash
python morse_cli.py multi recording.wav --bands "400-800,900-1300,1500-1900"
```

The original guide suggested up to three comma-separated bands in `min-max` form. The CLI accepts a list of bands; `--max-signals` controls the maximum number of automatically detected peaks.

### With Callsign Information Lookup

```bash
python morse_cli.py multi recording.wav --auto-detect --lookup-callsigns
```

Add `--ru` for Russian console output.

## Example Output

This is a translated illustrative example from the original guide, not a newly measured result:

```text
🎵 DECODING MULTIPLE PARALLEL SIGNALS
📁 File: websdr (1).wav
================================================================================

🔍 Automatically detecting frequency bands...
   Frequency bands found: 2
   1. 400-800 Hz (center: 600 Hz)
   2. 900-1300 Hz (center: 1100 Hz)

📡 Processing signal #1: 400-800 Hz
   ✅ WPM: 25, Quality: 87.5%, Pulses: 208

📡 Processing signal #2: 900-1300 Hz
   ✅ WPM: 30, Quality: 72.0%, Pulses: 185

================================================================================
✅ SIGNALS FOUND: 2
================================================================================

📡 Signal #1
   Frequency: 600 Hz (400-800 Hz)
   Speed: 25 WPM
   Quality: 87.5%

   📝 Text:
      CQ CQ DE RA3ABC RA3ABC K

   🔍 Detected codes:
      📡 Callsigns: RA3ABC
      🔔 Prosigns: CT, SK

📡 Signal #2
   Frequency: 1100 Hz (900-1300 Hz)
   Speed: 30 WPM
   Quality: 72.0%

   📝 Text:
      QRZ DE W1AW W1AW K
```

## How It Works

1. **Spectrum analysis**: use an FFT to locate frequency peaks in the audio.
2. **Filter creation**: create a bandpass filter for each selected range.
3. **Independent decoding**: process each frequency band separately.
4. **Result ranking**: sort by a decoding-quality heuristic. The original guide described this as a percentage of correctly recognized characters; it should not be interpreted as measured accuracy.

## Automatic Detection Parameters

The original guide listed the following defaults:

- **min_freq**: minimum search frequency, 300 Hz.
- **max_freq**: maximum search frequency, 3000 Hz.
- **num_peaks**: maximum number of signals, 3.
- **peak_threshold**: minimum peak amplitude relative to the strongest peak; 0.1 means 10%.
- **bandwidth**: filter width around a peak, ±200 Hz.

These are algorithm-level parameters rather than a list of CLI flags. The current implementation may use narrower search defaults; see [modules/multi_signal_decoder.py](../modules/multi_signal_decoder.py) and `python morse_cli.py multi --help` for the available CLI controls. Manually selected bands are preserved instead of being replaced by single-signal automatic carrier selection.

## Output Files

The command saves a `.multi.txt` report and `.multi.json` data beside the input. Saved TXT report headings remain Russian. Example JSON data from the original guide:

```json
{
  "file": "recording.wav",
  "total_signals": 2,
  "signals": [
    {
      "frequency_band": [400, 800],
      "center_frequency": 600.0,
      "text": "CQ CQ DE RA3ABC K",
      "wpm": 25,
      "quality": 87.5,
      "signal_strength": 0.234,
      "pulses": 208
    },
    {
      "frequency_band": [900, 1300],
      "center_frequency": 1100.0,
      "text": "QRZ DE W1AW K",
      "wpm": 30,
      "quality": 72.0,
      "signal_strength": 0.156,
      "pulses": 185
    }
  ]
}
```

The current writer can include additional fields. This is an illustrative sample, not a complete schema.

## Limitations

- Signals need **sufficient frequency separation**; the original guide suggested at least 100–200 Hz.
- Weak signals require an adequate signal-to-noise ratio.
- Simultaneous transmissions on nearby frequencies can interfere with each other.
- The original guide described roughly three to five simultaneous signals, depending on recording quality; this is not a guaranteed capacity.

## Use Cases

### 1. WebSDR Recordings with Several Stations

```bash
python morse_cli.py multi websdr_7mhz.wav --auto-detect --lookup-callsigns
```

### 2. Contest Recordings with Multiple Stations on Air

```bash
python morse_cli.py multi contest_recording.wav --bands "500-700,800-1000,1100-1300"
```

### 3. Searching for Weak Signals on Different Frequencies

```bash
python morse_cli.py multi dx_recording.wav --auto-detect
```

## Python API

```python
from modules.multi_signal_decoder import MultiSignalDecoder

# Create a decoder
decoder = MultiSignalDecoder(
    sample_rate=8000,
    auto_detect=True  # Or frequency_bands=[(400, 800), (900, 1300)]
)

# Decode the recording
result = decoder.decode_multi_signal(
    'recording.wav',
    pulse_percentile=85,
    verbose=True
)

# The current API returns a dictionary with a 'signals' list.
for decoded_signal in result['signals']:
    print(f"Frequency: {decoded_signal['center_frequency']:.0f} Hz")
    print(f"Text: {decoded_signal['text']}")
    print(f"Quality heuristic: {decoded_signal['quality']:.1f}%")
```

The original guide iterated over the return value directly; the example above follows the current dictionary return format.

## Tips for Better Results

1. **Narrow bands**: select narrow frequency ranges, such as 400 Hz-wide bands, for better separation.
2. **Pre-filtering**: consider reducing interference before processing, while avoiding distortion of the CW signal.
3. **Parameter tuning**: experiment with `pulse_percentile` for each signal.
4. **Manual bands**: if automatic detection fails, specify the frequency ranges yourself.

## Differences from Single-Signal Mode

| Property | Single-signal mode | Multi-signal mode |
|----------|--------------------|-------------------|
| Number of signals | One | Several; the original guide suggested up to 3–5 |
| Frequency filter | Automatic narrow carrier band; fixed bands also available | Several separately selected bands |
| Processing speed | Faster | Slower, roughly increasing with signal count |
| Quality per signal | Often higher for isolated signals | Can be lower |
| Ease of use | Simpler | May need tuning |

The original comparison described the single-signal filter as one wide band. Current `auto` mode instead detects a carrier and isolates a narrow band around it.

---

**⚠️ Feature status**

Multi-signal decoding is **experimental**. Tests on real WebSDR recordings identified these problems:

- Harmonics can be mistaken for separate signals.
- Splitting into narrow bands can reduce decoding quality.
- Automatic parameter tuning can be difficult.

For most single-signal recordings, use `auto` or `batch`. Multi-signal mode is intended for recordings containing genuinely parallel transmissions on different frequencies.

---

**Note:** this feature supplements the main decoder. It does not replace `auto` and `batch` for single-signal recordings.
