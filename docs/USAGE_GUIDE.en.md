# Morse CLI Usage Guide

[Русский](USAGE_GUIDE.md) | **English** | [README](../README.en.md)

## Overview

`morse_cli.py` is the unified command-line interface for the Morse decoder. It supports automatic parameter tuning, batch processing, decoding with saved configurations, and procedural code analysis.

This English copy retains the topics and historical examples from the Russian guide. Command names and runnable examples have been aligned with the current CLI. Historical timing estimates and report examples are identified as such.

## Commands

### ✅ Available Commands

1. **auto**: automatically tune parameters for a file.
2. **batch**: process a folder with parallel workers.
3. **decode**: decode using parameters from `.config.json`.
4. **multi**: decode signals in separate frequency bands; see the [multi-signal guide](MULTI_SIGNAL_DECODING.en.md).
5. **experiment**: experiment with decoding parameters.

The original guide listed a `procedural` command. That command is not exposed by the current CLI; use `decode --analyze` for procedural code analysis.

### 🎯 Features

- Automatic parameter tuning (`fast`, `thorough`, `extreme`).
- Parallel batch processing (`--workers`).
- Loading parameters from `.config.json`.
- English and Russian decoded output.
- Callsign lookup through APIs (`--lookup-callsigns`).
- Procedural code detection: Q codes, prosigns, and abbreviations.
- Detailed TXT reports and JSON configurations.

Console messages and help are English by default. Add `--ru` before or after the subcommand to use Russian. This does not translate the decoded message or the saved report.

## Usage

### 1. AUTO: Automatic Parameter Tuning

```powershell
# Fast mode (12 combinations)
python morse_cli.py auto "file.wav"

# With callsign lookup
python morse_cli.py auto "file.wav" --lookup-callsigns

# Thorough mode (560 combinations)
python morse_cli.py auto "file.wav" --mode thorough

# Extreme mode (3696 combinations in the current implementation)
python morse_cli.py auto "file.wav" --mode extreme

# Compressed input; FFmpeg must be installed
python morse_cli.py auto "recording.mp3"

# Russian console output
python morse_cli.py auto "file.wav" --ru
```

The older guide quoted approximately 10 seconds, 7 minutes, and 1 hour for these modes. Those were historical estimates, not runtime guarantees. The earlier count of 4,752 extreme-mode combinations differs from the current implementation.

### 2. BATCH: Folder Processing

```powershell
# Process a folder; worker count is selected automatically
python morse_cli.py batch TrainingData

# Use four workers
python morse_cli.py batch TrainingData --workers 4

# Use a single worker
python morse_cli.py batch TrainingData --workers 1

# Look up callsigns while processing with four workers
python morse_cli.py batch TrainingData --lookup-callsigns --workers 4

# Thorough mode for the folder
python morse_cli.py batch TrainingData --mode thorough
```

`batch` selects WAV files from the folder. Use `auto` directly for individual MP3 or OGG files.

### 3. DECODE: Use a Saved Configuration

```powershell
# Load parameters from file.config.json
python morse_cli.py decode "file.wav"

# Specify another configuration
python morse_cli.py decode "file.wav" --config custom.config.json

# Analyze procedural codes
python morse_cli.py decode "file.wav" --analyze
```

### 4. EXPERIMENT: Parameter Experiments

```powershell
# 30 iterations (default)
python morse_cli.py experiment "file.wav"

# 50 iterations
python morse_cli.py experiment "file.wav" --iterations 50
```

## Command-Line Arguments

### AUTO

| Argument | Type | Description | Values |
|----------|------|-------------|--------|
| `file` | string | Path to WAV, MP3, or OGG input | Required |
| `--mode` / `-m` | string | Tuning mode | `fast` (default), `thorough`, `extreme` |
| `--lookup-callsigns` / `--lookup` | flag | Look up callsigns through APIs | — |

### BATCH

| Argument | Type | Description | Values |
|----------|------|-------------|--------|
| `folder` | string | Folder containing WAV files | Required |
| `--mode` / `-m` | string | Tuning mode | `fast` (default), `thorough`, `extreme` |
| `--lookup-callsigns` / `--lookup` | flag | Look up callsigns through APIs | — |
| `--workers` / `-w` | integer | Worker count; 0 selects automatically | Default: 0 |

### DECODE

| Argument | Type | Description | Values |
|----------|------|-------------|--------|
| `file` | string | Path to WAV, MP3, or OGG input | Required |
| `--config` / `-c` | string | Path to `.config.json` | Default: beside the audio file |
| `--analyze` / `-a` | flag | Analyze procedural codes | — |
| `--lookup-callsigns` / `--lookup` | flag | Accepted by the CLI; the current `decode` handler does not perform this lookup | — |

### EXPERIMENT

| Argument | Type | Description | Values |
|----------|------|-------------|--------|
| `file` | string | Path to an audio file | Required |
| `--iterations` / `-n` | integer | Number of iterations | Default: 30 |

All commands also accept `--ru` for Russian console messages. Use `python morse_cli.py COMMAND --help` for the command's current help text.

## Output File Formats

### `.config.json`: Parameter Configuration

The current configuration includes the processing mode and heuristic metrics. For example:

```json
{
  "audio_file": "filename.wav",
  "parameters": {
    "auto_frequency": true,
    "pulse_percentile": 70,
    "gap_percentile_dot_dash": 55,
    "gap_percentile_char": 75,
    "gap_percentile_word": 90
  },
  "quality_metrics": {
    "score": -2.4,
    "score_type": "heuristic",
    "transcription_verified": false,
    "timing_reliable": true,
    "wpm": 22.7,
    "text_length": 49,
    "error_count": 0,
    "error_ratio": 0.0,
    "callsigns_found": 0
  }
}
```

The Russian guide's older sample used `en_quality`, `ru_quality`, and `selected_language`. The current writer uses the fields above. A zero `error_ratio` does not prove the transcription is correct.

### `.txt`: Decoding Results

The following is an English rendering of the older guide's report example, for explanation. Saved TXT reports still contain Russian headings, and current reports label character coverage and heuristic scores explicitly rather than presenting them as accuracy.

```text
================================================================================
MORSE CODE: DECODED RECORDING
================================================================================

## RECORDING INFORMATION

File:           example.wav
Decoded at:     2026-01-06 12:00:00
Duration:       143.0 sec
Speed:          9.3 WPM
Quality:        89.2% (errors: 10.8%) [historical label, not verified accuracy]
Language:       EN
Characters:     467

## DETECTED ELEMENTS

Callsigns:      5
Q codes:        3
Prosigns:       257
CW abbreviations: 7

## DETECTED CALLSIGNS

• IE6I
  Country:   Ireland
  Source:    HamQTH

## DETECTED Q CODES

• QFE

## DETECTED PROSIGNS

• K - Transmitting (-•-) (244×)
• BT - Pause (-•••-) (8×)
• R - Received (-•-) (3×)
• AR - End of message (-•-•-) (1×)
• SK - End of contact (•••-•-) (1×)

================================================================================
DECODED TEXT (EN)
================================================================================

[Decoded English text]

================================================================================
DECODED TEXT (RU)
================================================================================

[Decoded Russian text]

================================================================================
TECHNICAL PARAMETERS
================================================================================

Pulse Detection:    70
Dot-Dash Gap:       60
Character Gap:      75
Word Gap:           90
Pulses detected:    1909
Frequency filter:  400-1200 Hz
```

This historical example is illustrative, including its callsign and prosign annotations; it is not a verified reference transmission. Current `auto` mode reports the actual carrier filter band.

## Examples

### Process One File

```powershell
# Fast processing
python morse_cli.py auto "recording.wav"

# With callsign lookup
python morse_cli.py auto "recording.wav" --lookup-callsigns

# Thorough processing
python morse_cli.py auto "recording.wav" --mode thorough
```

### Batch Processing

```powershell
# One worker
python morse_cli.py batch TrainingData --workers 1

# Four workers
python morse_cli.py batch TrainingData --workers 4

# Four workers with callsign lookup
python morse_cli.py batch TrainingData --lookup-callsigns --workers 4
```

### Decode with Existing Parameters

```powershell
# After auto-tuning has created file.config.json
python morse_cli.py decode "file.wav"

# Include code analysis
python morse_cli.py decode "file.wav" --analyze
```

## Tuning Modes

| Mode | Combinations | Historical time estimate | Use case |
|------|--------------|--------------------------|----------|
| **fast** | 12 | About 10 s | Routine processing and quick results |
| **thorough** | 560 | About 7 min | More difficult recordings and a broader search |
| **extreme** | 3696 currently; 4752 in the older guide | About 1 hour | A large parameter search for difficult input |

Actual time depends on recording length, hardware, and software version. A larger search does not guarantee a correct transcription.

## Tips

1. **Start with fast mode.** The original guide suggested it was sufficient in 90% of cases; this was not a general accuracy guarantee.
2. **Use `decode`** to reuse saved parameters.
3. **Enable `--lookup-callsigns` only when needed**, because network requests add processing time.
4. **Use parallel workers** for batch processing; historical reports described a 3–4× speedup.
5. **Check `.config.json`** for the selected parameters.

## Technical Details

### Result Metrics

The older guide calculated a percentage from `?` counts. That is obsolete: `?` is an actual question mark, while `□` denotes an unrecognized Morse symbol.

```python
unrecognized_ratio = text.count('□') / len(text) if text else 1.0
character_coverage = 100 * (1 - unrecognized_ratio)
```

Character coverage is not transcription accuracy. `Heuristic score` ranks candidates using decoding and timing evidence. Speed is marked unknown when dot/dash timing cannot be estimated reliably. See [result metrics](../README.en.md#interpreting-result-metrics).

### Language Handling

The decoder produces both English and Russian renderings. The automatic tuning code currently selects its working text by length, with Russian chosen on a tie; it does not verify the language semantically. Procedural code analysis in tuning uses the English rendering. Console language is selected independently with `--ru`.

### Callsign Lookup

- Sources: HamQTH, RadioQTH, APRS.fi, and QRZ.RU.
- Results are cached in `callsign_cache/`.
- The historical guide described a limit of ten callsigns per file for performance. Limits depend on the calling code; a pattern match is only a callsign candidate.

## Change History

### 2026-01-06

- Added `decode` with `.config.json` loading.
- Optimized fast mode: 560 → 12 combinations, reported as 47× faster.
- Removed the earlier denoising step because it degraded CW signals; this historical removal predates the current CW-specific noise processing.
- Fixed prosign output formatting by grouping entries and counting occurrences.
- Consolidated `decode_coast_stations.py` into `morse_cli.py decode`.
