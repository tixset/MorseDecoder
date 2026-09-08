# 🏗️ Project structure and development

[![Русский](https://img.shields.io/badge/Language-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-lightgrey)](ARCHITECTURE.md) [![English](https://img.shields.io/badge/Language-English-blue)](ARCHITECTURE.en.md)

[README](../README.en.md) · [Contributing](../CONTRIBUTING.en.md)

## 📁 File placement

| Path | Purpose |
| --- | --- |
| `morse_cli.py` | Unified CLI entry point |
| `morse_tuner_gui.py` | Tkinter GUI: recording selection, threshold tuning, EN/RU text |
| `run_all_tests.py` | unittest discovery and saved reports |
| `requirements.txt` | Python dependencies |
| `modules/` | Importable implementation |
| `tools/convert_mp3_to_wav.py` | Batch MP3-to-WAV conversion |
| `tests/` | Automated tests and procedural code demonstrations |
| `tests/fixtures/` | Noisy recording and reference transcription JSON |
| `docs/` | Russian and English guides |
| `.github/ISSUE_TEMPLATE/` | Bug and feature templates in both languages |
| `.github/PULL_REQUEST_TEMPLATE.md` | Default Russian PR template |
| `.github/PULL_REQUEST_TEMPLATE/english.md` | English PR template |
| `README*`, `CONTRIBUTING*`, `CHANGELOG*`, `LICENSE` | Introduction, contribution guide, history, license |

User recordings, `TrainingData/`, `reports/`, `callsign_cache/`, configurations, and outputs are local and ignored by Git. These folders are not required for a clean installation. The reference MP3 in `tests/fixtures/` is explicitly excepted in `.gitignore`. Environment files such as `.venv/` and `__pycache__/` are also excluded.

## ⚙️ Modules and data flow

1. `audio_input.py` prepares WAV input, runs FFmpeg for MP3/OGG, and removes temporary files.
2. `morse_decoder.py` loads signals and coordinates processing. `cw_frontend.py` searches for a carrier (250–3000 Hz), filters its narrow band, and extracts the envelope/keying pulses.
3. `morse_timing.py` estimates dot/dash timing and reliability; the decoder assembles symbols and text in both alphabets.
4. `auto_tune.py` compares parameter candidates and writes reports/configurations. `multi_signal_decoder.py` processes fixed bands separately.
5. `signal_analyzer.py` computes heuristic signal characteristics. `procedural_codes.py` detects text codes using `code_dictionaries.py`; `fuzzy_matcher.py` and `levenshtein_optimized.py` provide approximate matching.
6. `callsign_lookup.py` and `callsign_lookup_async.py` implement network directories. `analyze_codes.py` aggregates saved transcriptions.
7. `console_i18n.py` and the required `console_en.json` resource translate CLI messages; Russian source strings remain in code. `modules/__init__.py` exports core classes and functions.

## 🔧 Helper tools

```bash
python morse_tuner_gui.py
python tools/convert_mp3_to_wav.py recordings --output wav_recordings --max-files 10
```

The GUI opens a file and allows threshold changes followed by decoding; it has no separate configuration-save button. Use `auto` for a reproducible configuration.

The converter produces mono WAV at 8000 Hz, skips existing WAV files, and defaults to `TrainingData/`. MP3 requires FFmpeg even when using pydub. The pydub import is optional: on import failure, the tool tries FFmpeg directly.

The legacy aggregator can be called from Python:

```python
from modules.analyze_codes import analyze_all_decodings
analyze_all_decodings()
```

It reads `TrainingData/*.txt` and writes `code_analysis_results.json` in the working directory. It targets older text reports rather than arbitrary report schemas; new code should pass clean decoded text directly to `ProceduralCodeDetector`.

## 🧪 Validating changes

Follow the [contribution guide](../CONTRIBUTING.en.md). Do not change the user reference simply to make tests pass. Validate noise-processing changes against clean CW, silence, constant tones, and interference as well. Matching one recording does not guarantee correctness on others.
