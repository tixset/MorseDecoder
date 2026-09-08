# 📖 CLI guide

[![Русский](https://img.shields.io/badge/Language-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-lightgrey)](USAGE_GUIDE.md) [![English](https://img.shields.io/badge/Language-English-blue)](USAGE_GUIDE.en.md)

[Installation](../README.en.md) · [Multiple signals](MULTI_SIGNAL_DECODING.en.md) · [Codes](SUPPORTED_CODES.en.md)

## 📋 Commands and arguments

```bash
python morse_cli.py --help
python morse_cli.py decode --help --ru
```

Every command accepts `--ru`: it selects console language, not the decoding alphabet. Individual input files can be WAV/MP3/OGG; compressed audio needs FFmpeg.

| Command | Arguments |
| --- | --- |
| `auto FILE` | `--mode/-m fast\|thorough\|extreme`, `--lookup-callsigns/--lookup` |
| `batch FOLDER` | Same options, plus `--workers/-w N` (0: automatic, 1: sequential) |
| `decode FILE` | `--config/-c PATH`, `--analyze/-a`; `--lookup-callsigns/--lookup` is accepted but unused by the handler |
| `multi FILE` | `--auto-detect/-a`, `--bands/-b "400-800,1000-1400"`, `--max-signals/-m N` (3), `--lookup-callsigns/--lookup`; `--speed-range/-s` is accepted but has no effect |
| `experiment FILE` | `--iterations/-n N` (30; supply a positive number) |

There is no `procedural` command, `--fast` flag, or CSV export. `--mode fast` is the default for `auto` and `batch`.

## 🎛️ Tuning and decoding again

```bash
python morse_cli.py auto recording.mp3 --ru
python morse_cli.py auto recording.wav --mode thorough
python morse_cli.py auto recording.wav --mode extreme
python morse_cli.py decode recording.wav --analyze
python morse_cli.py decode recording.wav --config custom.config.json
```

| Mode | Parameter combinations |
| --- | ---: |
| `fast` | 12 |
| `thorough` | 560 |
| `extreme` | 3696 |

Runtime depends on recording length and hardware. Start with `fast`. `decode` requires `recording.config.json` beside the audio or an explicit configuration path. The saved `parameters` section contains `auto_frequency`, `pulse_percentile`, `gap_percentile_dot_dash`, `gap_percentile_char`, and `gap_percentile_word`. Reliable timing uses Morse ratios 1:3:7; legacy separation thresholds provide a fallback.

`--analyze` belongs only to `decode` and adds counts of callsigns, Q codes, prosigns, and CW abbreviations. `auto` already analyzes codes without it. For Russian procedural abbreviations, use the [Python API example](SUPPORTED_CODES.en.md): `--ru` does not force Russian analysis in the CLI.

## 📁 Batch processing and experiments

```bash
python morse_cli.py batch recordings --workers 4
python morse_cli.py batch recordings --workers 1 --mode thorough
python morse_cli.py experiment recording.wav --iterations 50
```

`batch` does not recurse and selects `*.wav` (lowercase extension on Linux). Process MP3/OGG individually or convert them first. `experiment` uses random parameters and fixed frequency bands; it is an exploratory tool, and repeated runs can differ.

## 📄 Output files

| Command | Output |
| --- | --- |
| `auto`, `batch` | `<name>.txt` with EN/RU transcriptions and analysis; `<name>.config.json` with parameters and metrics |
| `decode` | Transcriptions and analysis in the console; no separate output file |
| `multi` | `<name>.multi.txt`, `<name>.multi.json` beside the audio |
| `experiment` | `experiment_results.json` in the working directory |

Repeated runs overwrite the corresponding outputs. TXT report headings are Russian regardless of `--ru`. Temporary WAV files for MP3/OGG are removed after processing. Example configuration schema (illustrative metrics):

```json
{
  "audio_file": "recording.wav",
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

`error_count` counts `□`, not incorrect letters that can only be identified against a reference. Zero does not guarantee a correct transcription. `auto` chooses its working text by length (RU on ties), while code detection uses EN. This does not determine language semantically.

## 📡 Callsigns and networking

```bash
python morse_cli.py auto recording.wav --lookup-callsigns
python morse_cli.py batch recordings --lookup --workers 4
```

The flag queries external directories (HamQTH, RadioQTH, APRS.fi, QRZ.RU). Availability depends on the network and service. Results are cached in `callsign_cache/`. Without the flag, network lookup is unnecessary; pattern matches can still be false callsigns. The flag is not wired into the `decode` handler yet.

## ⚠️ Troubleshooting

- `unrecognized arguments: --analyze`: omit it from `auto`, or use `decode --analyze` after creating a configuration.
- Missing configuration: run `auto` for the same file first or supply `--config`.
- FFmpeg errors: check `ffmpeg -version` and its presence in `PATH`.
- `ModuleNotFoundError`: activate your environment and run `python -m pip install -r requirements.txt`.
- Empty output, unknown speed, or meaningless text: check CW audibility, frequency, timing, and overlapping signals; try manual `multi` bands or the GUI. Absence of `□` does not establish success.
- GUI startup errors: Tkinter and a graphical display are required; `--ru` does not apply to the GUI.
