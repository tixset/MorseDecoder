# Changelog

[![Русский](https://img.shields.io/badge/Language-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-lightgrey)](CHANGELOG.md) [![English](https://img.shields.io/badge/Language-English-blue)](CHANGELOG.en.md)

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

This is a translation of the release history. Performance figures, file sizes, and implementation descriptions below refer to the releases in which they were recorded.

## [Unreleased]

### Added and changed

- English CLI by default, with `--ru` before/after the subcommand; Russian messages retained.
- Shared WAV/MP3/OGG input, FFmpeg conversion, and temporary-file cleanup.
- Carrier detection, narrow-band noisy CW processing, dot/dash timing estimates, and WPM reliability checks.
- Heuristic metrics without accuracy claims; a noisy reference recording and regression tests.
- `requirements.txt` for Python dependency installation.
- Current Russian and English guides covering CLI, output formats, dictionaries, API, structure, and limitations; shields.io language navigation.
- English PR template moved to `.github/PULL_REQUEST_TEMPLATE/english.md`.

### Fixed

- Tests are discovered automatically; import errors are no longer ignored, and skips are not counted as passed tests.
- The MP3 converter can use FFmpeg even when pydub is unavailable.
- Documentation links to removed files, obsolete commands, and incorrect dictionary counts.

Entries below describe past releases. Their performance measurements and old file inventories do not describe the current checkout.

## [1.1.0] - 2026-01-07

### Added

- ⚡ **Performance improvements**
  - LRU caching (`@lru_cache(maxsize=1024)`) for fuzzy matching functions.
  - Asynchronous callsign lookup in [modules/callsign_lookup_async.py](modules/callsign_lookup_async.py).
    - Parallel requests using aiohttp.
    - A 13× speedup: 12.02 s → 0.92 s for six callsigns.
  - Numba JIT compilation of Levenshtein distance in [modules/levenshtein_optimized.py](modules/levenshtein_optimized.py).
    - Performance: 326,394 operations/s.
- 🏗️ **Code structure refactoring**
  - Added [modules/code_dictionaries.py](modules/code_dictionaries.py).
    - Centralized storage for all code dictionaries, totaling 440 lines at that release.
    - Eighteen dictionaries, including Q_CODES, Z_CODES, Y_CODES, PROSIGNS, and CW_ABBREVIATIONS.
  - Reduced [modules/procedural_codes.py](modules/procedural_codes.py) from 1,080 to 752 lines, a 30% reduction.
  - Removed duplicated DXCC_PREFIX_MAP definitions between modules.
- 🧪 **Quality checks**
  - A script to check all code dictionaries.
  - Automated recognition tests for ten code types.
  - Verification that the detector uses all eighteen dictionaries.

### Changed

- 📊 Improved modularity by separating data from logic.
- 🔧 Updated module imports to use code_dictionaries.

### Fixed

- 🐛 Removed circular dependencies between modules.
- 🐛 Fixed imports after refactoring.

## [1.0.0] - 2026-01-06

### Added

- 🎯 **Extended signal analysis** in [modules/signal_analyzer.py](modules/signal_analyzer.py).
  - Modulation detection (CW/PSK31/RTTY) with a confidence level.
  - Signal purity analysis: chirp, clicks, noise_level, SNR, and QRM.
  - Operator skill estimates: timing stability, rhythm consistency, and dot/dash ratio.
  - Automatic interpretation of results in Russian.
  - Extended analysis in TXT reports, with emoji.
- 📡 **Multi-signal decoding** in [modules/multi_signal_decoder.py](modules/multi_signal_decoder.py).
  - Automatic detection of multiple parallel signals.
  - Frequency separation over a configurable range, initially 300–1500 Hz.
  - Detection of single versus multiple signals.
  - Warnings about false separation caused by harmonics or artifacts.
  - A `--max-signals` parameter to control the number of signals.
  - A detailed comparison report was recorded as `docs/AUTO_VS_MULTI_COMPARISON.md`; that historical file is not present in this checkout.
- 🔤 **Distinction between question marks and decoding errors**
  - Unrecognized Morse symbols use `□` (U+25A1, white square).
  - A literal question mark uses `?` (Morse: `··--··`).
  - Updated error counting throughout the modules.
  - Added explanations to the README and TXT reports.
- 📁 **Improved project organization**
  - A `docs/` folder for documentation.
  - An updated `.gitignore` with a complete exclusion list.
  - A contributor guide in `CONTRIBUTING.md`.
  - An up-to-date `CHANGELOG.md`.

### Changed

- ⚡ Optimized fast mode: twelve combinations instead of 560.
- 📈 Improved WPM estimation by using median duration rather than minimum duration.
- 🎨 Expanded TXT reports to eight detailed sections.
- 🔧 Limited multi-mode frequency search to 300–1500 Hz.
- 📊 Improved output formatting and visualization with emoji.

### Fixed

- 🐛 Correct handling of callsigns containing `(?)`.
- 🐛 Correct error counting (`□` instead of `?`).
- 🐛 Corrected the SNR output key (`snr_estimate` instead of `snr`).
- 🐛 Improved single-signal detection when three or more peaks occupy a narrow range.
- 🐛 Fixed automatic frequency detection (2560 Hz → 600 Hz).

### Removed

- 🗑️ Outdated reports: `*_REPORT.md`, `*_SUMMARY.md`, and `*_ANALYSIS.md`.
- 🗑️ Temporary test files: `comparison_test/` and `code_analysis_results.json`.
- 🗑️ Helper scripts: `batch_multi_test.py`, `compare_auto_vs_multi.py`, and `generate_report.py`.

## [0.9.0] - 2025-12-20

### Added

- 📁 A unified CLI in [morse_cli.py](morse_cli.py).
  - `auto`: automatic parameter selection (`fast`, `thorough`, `extreme`).
  - `batch`: multithreaded batch processing.
  - `decode`: decoding with existing parameters.
  - `experiment`: experimental parameter search.
- 📊 A modular architecture in `modules/`.
  - `auto_tune.py`: automatic parameter selection.
  - `morse_decoder.py`: core decoder.
  - `procedural_codes.py`: Q/Z code and prosign detection.
  - `fuzzy_matcher.py`: fuzzy matching using Levenshtein distance.
  - `callsign_lookup.py`: lookup through four APIs (HamQTH, RadioQTH, QRZ.RU, APRS.fi).
- 📝 Documentation.
  - `README.md`: main documentation and examples.
  - `USAGE_GUIDE.md`: detailed user guide.
  - `SUPPORTED_CODES.md`: more than 280 supported codes.
  - `PROJECT_CONTEXT.md`: architecture and project context; this historical file is not present in this checkout.
- 🧪 A general-purpose test runner, originally named `run_tests.py`; the current runner is [run_all_tests.py](run_all_tests.py).

### Changed

- Improved processing of noisy signals.
- Optimized the bandpass filter (400–1200 Hz).

## [0.8.0] - 2025-11-15

### Added

- A basic Morse decoder.
- English and Russian support.
- Q code recognition (QRZ, QTH, QSL, and others).
- Z code recognition (Soviet commands).
- Prosign recognition (AR, SK, BT, CT, KN, and others).
- Radio station callsign detection.
- A slider-based GUI in [morse_tuner_gui.py](morse_tuner_gui.py).

### Features

- Adaptive sending-speed handling, described at that release as 5–100 WPM.
- WAV, MP3, and OGG format support.
- Automatic conversion through FFmpeg.

---

## Versioning

The project follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: incompatible API changes.
- **MINOR**: backward-compatible new functionality.
- **PATCH**: backward-compatible bug fixes.

## Change Types

- `Added`: new features.
- `Changed`: changes to existing functionality.
- `Deprecated`: features that will be removed soon.
- `Removed`: removed features.
- `Fixed`: bug fixes.
- `Security`: vulnerability fixes.
