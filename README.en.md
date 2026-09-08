# Morse Code Audio Decoder 🎵→📝

[Русский](README.md) | **English**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-0078d4.svg)](https://github.com/tixset/MorseDecoder)
[![Language](https://img.shields.io/badge/Language-Python%203.9+-3776ab.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-1.1.0-blue)](https://github.com/tixset/MorseDecoder/releases)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](https://github.com/tixset/MorseDecoder)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.en.md)

[![GitHub Stars](https://img.shields.io/github/stars/tixset/MorseDecoder?style=social)](https://github.com/tixset/MorseDecoder/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/tixset/MorseDecoder?style=social)](https://github.com/tixset/MorseDecoder/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/tixset/MorseDecoder)](https://github.com/tixset/MorseDecoder/issues)
[![Last Commit](https://img.shields.io/github/last-commit/tixset/MorseDecoder)](https://github.com/tixset/MorseDecoder/commits)

A tool for decoding Morse code from radio audio recordings, with procedural commands, code detection, and configurable processing parameters.

## 🆕 Update of January 7, 2026

- ⚡ **Performance improvements**
  - LRU caching for fuzzy matching (reported speedup: 3–5×).
  - Asynchronous callsign lookup with aiohttp (reported speedup: 13×, from 12 s to 0.92 s).
  - Numba JIT compilation of Levenshtein distance (326k operations/s).
- 🏗️ **Code organization**
  - Added [modules/code_dictionaries.py](modules/code_dictionaries.py) as a central store for code dictionaries.
  - Reduced [modules/procedural_codes.py](modules/procedural_codes.py) from 1,080 to 752 lines at that release, a 30% reduction.
  - Removed duplicated constants between modules.
- 📚 **Code inventory** — checked all 18 dictionaries:
  - Q codes (53), Z codes (33), Y codes (26), and Russian Shch codes (3).
  - CW abbreviations (25), prosigns (11), and maritime codes (18).
  - Weather codes (9), Soviet codes (12), and SINPO parameters (5).
  - All codes were successfully recognized by the detector.

These figures describe the January 2026 release. Current noise processing and result interpretation are described below.

## 🎯 Main Features in 2026

- ⭐ **Unified CLI** ([morse_cli.py](morse_cli.py)): one entry point for all operations.
- 📁 **Modular structure**: processing code in `modules/`.
- 🧪 **Test runner** ([run_all_tests.py](run_all_tests.py)): runs the project's test suites.
- 📡 **Callsign lookup** (`--lookup`): lookup using four API sources.
- 🎨 **Detailed TXT reports**: eight sections with decoding information.
- ⚡ **Fast mode** (`--mode fast`): a small search over parameter combinations.
- 🔬 **Experimental mode**: search for suitable decoding parameters.
- 📊 **Detailed guides**:
  - [CLI usage guide](docs/USAGE_GUIDE.en.md).
  - [Supported codes](docs/SUPPORTED_CODES.en.md), including the historical 280+ code inventory.
  - [Multi-signal decoding](docs/MULTI_SIGNAL_DECODING.en.md).

**Historical experiment result:** in 40 tests on real WebSDR recordings, the earlier decoder did not detect Q/Z codes. The original report attributed this to interference. Only simple Russian procedural codes `Р` (6 occurrences) and `ДЕ` (2 occurrences) were found. This is not a benchmark of the current noise-processing implementation.

## ✨ Features

### Basic Functionality

- Processing of noisy audio recordings.
- Automatic estimation of sending speed; the timing model searches 2–100 WPM, but successful decoding across that entire range is not guaranteed.
- English and Russian decoding.
- Interference filtering; current automatic processing isolates a narrow band around the detected carrier. Fixed-band processing is also available.
- Batch processing with parallel workers.
- WAV, MP3, and OGG input, with FFmpeg conversion for compressed audio.

### Procedural Codes and Radiograms

- **Q codes**, including QRZ, QTH, and QSL.
- **Z codes**, including Soviet procedural commands.
- **Prosigns**, including AR, SK, BT, K, and HH.
- Extraction of **CHECK** and **NR** message fields.
- Radiogram structure analysis.
- Callsign candidate detection.
- Message priority detection.

### Features Added in 2026

- 🎚️ **GUI sliders** for adjusting parameters interactively.
- 📊 **JSON/CSV export** for examining results, as described in the original feature inventory.
- ⚙️ **Configurable thresholds** without editing source code.
- ⚡ **Parallel file processing**, with reported historical speedups of 3–4×.
- 🧹 **Automatic cleanup** of temporary WAV files.
- 📈 **WPM statistics** (words per minute).
- 🛡️ **Improved error handling** with detailed messages.
- 📡 **Callsign Lookup System**:
  - Four API sources: HamQTH, RadioQTH, QRZ.RU, and APRS.fi.
  - Automatic transliteration of Cyrillic callsigns.
  - Seven-day result caching.
  - Batch lookup with delays between requests.

## 🚀 Quick Start

### Unified CLI

```bash
# Activate an existing environment on Windows
.venv\Scripts\activate

# Process one file (fast mode is the default)
python morse_cli.py auto "file.wav"

# Look up callsigns online
python morse_cli.py auto "file.wav" --lookup-callsigns

# Thorough processing
python morse_cli.py auto "file.wav" --mode thorough

# Thorough processing with callsign lookup
python morse_cli.py auto "file.wav" --mode thorough --lookup-callsigns

# Process a folder
python morse_cli.py batch TrainingData

# Batch processing with four workers
python morse_cli.py batch TrainingData --workers 4

# Batch processing with callsign lookup
python morse_cli.py batch TrainingData --lookup-callsigns

# Decode using a .config.json file
python morse_cli.py decode "file.wav"
python morse_cli.py decode "file.wav" --config custom.config.json
python morse_cli.py decode "file.wav" --analyze

# Experimental parameter search
python morse_cli.py experiment "file.wav" --iterations 50

# Help
python morse_cli.py --help
```

CLI messages and help are in English by default. Add `--ru` before the command or after its arguments to use Russian:

```bash
python morse_cli.py auto recording.wav --ru
python morse_cli.py --ru batch TrainingData
python morse_cli.py decode --help --ru
```

This flag changes console messages. It does not translate decoded text or change the language of saved reports.

### Installation and Other Ways to Run

#### Installation

```bash
# Clone the repository
git clone https://github.com/tixset/MorseDecoder.git
cd MorseDecoder

# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

MP3 and OGG require **FFmpeg** to be available in `PATH`. For example, on Debian/Ubuntu:

```bash
sudo apt install ffmpeg
python morse_cli.py auto recording.mp3
```

Compressed input is automatically converted to a temporary WAV file, which is removed after processing. The `.txt` report and `.config.json` file are saved beside the original audio. The `batch` command selects WAV files.

If NumPy and SciPy report incompatible versions, install the dependencies in a separate virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

#### GUI

```bash
# Open the parameter tuning GUI
python morse_tuner_gui.py
```

#### Python API

```python
from modules.morse_decoder import MorseDecoder

# Configurable parameters
decoder = MorseDecoder(
    sample_rate=8000,
    pulse_percentile=85,         # Pulse threshold control
    gap_percentile_dot_dash=62,  # Gap threshold control
    gap_percentile_char=90,      # Character gap percentile
    gap_percentile_word=92       # Word gap percentile
)

text_en, text_ru, stats = decoder.process_file('audio.wav')

print(f"Speed: {stats['wpm']} WPM")
print(f"English: {text_en}")
print(f"Russian: {text_ru}")
```

## How It Works

1. **Load audio**: read WAV data or convert compressed input, then convert to mono.
2. **Filter the signal**: isolate the carrier band; the legacy fixed band is 400–1200 Hz.
3. **Detect the envelope**: extract the signal's amplitude envelope.
4. **Detect pulses**: determine the start and end of keyed signals.
5. **Classify pulses**: separate dots and dashes by duration.
6. **Group symbols**: use gaps to form letters and words.
7. **Decode**: convert Morse sequences into text.

## Project Structure

### Main Scripts

- **morse_cli.py** ⭐: unified CLI (`auto`, `batch`, `decode`, `multi`, `experiment`).
- **morse_tuner_gui.py**: GUI sliders for manual tuning.
- **run_all_tests.py**: test suite runner.

### Utilities (`tools/`)

- **convert_mp3_to_wav.py**: MP3-to-WAV conversion (8 kHz mono).

### Modules (`modules/`)

- **morse_decoder.py**: main decoder class.
- **procedural_codes.py**: detection of Q/Z codes and prosigns.
- **callsign_lookup.py**: callsign information lookup through APIs.
- **auto_tune.py**: automatic parameter selection.
- **analyze_codes.py**: analysis of detected codes.
- **fuzzy_matcher.py**: fuzzy code matching.

### File Layout

```text
MorseDecoder/
├── morse_cli.py                       # Unified CLI
├── morse_tuner_gui.py                 # Parameter tuning GUI
├── run_all_tests.py                   # Test runner
├── requirements.txt                  # Dependencies
├── LICENSE                           # MIT License
├── CHANGELOG.en.md                    # English change history
├── CONTRIBUTING.en.md                 # English contributor guide
├── modules/                          # Decoder modules
│   ├── morse_decoder.py              # Main decoder
│   ├── signal_analyzer.py            # Signal analysis
│   ├── multi_signal_decoder.py       # Multi-signal decoding
│   ├── procedural_codes.py           # Procedural code detector
│   ├── code_dictionaries.py          # Central code dictionaries
│   ├── callsign_lookup.py            # Synchronous callsign lookup
│   ├── callsign_lookup_async.py      # Asynchronous callsign lookup
│   ├── auto_tune.py                  # Parameter tuning
│   ├── analyze_codes.py              # Code analysis
│   ├── fuzzy_matcher.py              # Fuzzy matching with LRU cache
│   ├── levenshtein_optimized.py      # Numba-optimized Levenshtein distance
│   ├── audio_input.py                # Compressed audio preparation
│   ├── console_i18n.py               # Console language selection
│   ├── console_en.json               # English console translations
│   ├── cw_frontend.py                # Carrier filtering and keying detection
│   └── morse_timing.py               # Dot/dash timing estimation
├── docs/                             # Documentation in both languages
│   ├── USAGE_GUIDE.en.md             # CLI guide
│   ├── SUPPORTED_CODES.en.md         # Code reference
│   └── MULTI_SIGNAL_DECODING.en.md    # Multi-signal guide
├── tools/
│   └── convert_mp3_to_wav.py         # MP3-to-WAV converter
├── tests/                            # Test scripts and reference fixture
└── TrainingData/                     # Local test recordings, when provided
```

## Supported Characters

### English Alphabet

A–Z, 0–9, and punctuation (`. , ? ' ! / ( ) & : ; = + - _ " $ @`).

### Russian Alphabet

А–Я, 0–9, and punctuation (`. , ? ' ! / ( ) : ; =`).

### Procedural Codes

#### Q Codes (International)

- QSL: reception confirmed.
- QTH: your location?
- QRZ: who is calling me?
- QRM: interference from other stations.
- QRN: atmospheric interference.
- And others.

#### Z Codes (Procedural, ACP-131)

- ZAA: you are not observing radio discipline.
- ZAB: your keying speed is incorrectly set.
- ZAG: interrupt transmission.
- ZAK: transmission interrupted at…
- ZRP: return to automatic relay.
- And others.

#### CW Abbreviations

- RPT: repeat.
- DE: from.
- SK: end of contact.
- AR: end of message.
- CQ: general call.
- And others.

See the [full code reference](docs/SUPPORTED_CODES.en.md).

## 📚 Additional Documentation

- [CLI usage guide](docs/USAGE_GUIDE.en.md).
- [Supported code reference](docs/SUPPORTED_CODES.en.md).
- [Multi-signal decoding guide](docs/MULTI_SIGNAL_DECODING.en.md).
- English GitHub templates: [bug report](.github/ISSUE_TEMPLATE/bug_report.en.md), [feature request](.github/ISSUE_TEMPLATE/feature_request.en.md), and [pull request](.github/PULL_REQUEST_TEMPLATE.en.md).

## ⚠️ Troubleshooting

**No pulses detected:** use the GUI (`morse_tuner_gui.py`) to adjust thresholds.

**Incorrect recognition:** try different GUI threshold settings or decoder parameters.

**Many `□` characters:** check the source audio and the frequency band. Current automatic mode detects the carrier; fixed-band mode uses the range you configure.

## 📝 Notes

### Understanding the Decoded Output

- **`□` (white square)** is an unrecognized Morse symbol. It appears when the decoder encounters an unknown dot/dash sequence and may indicate interference or distortion.
- **`?` (question mark)** is an actual Morse question mark, `··--··` (`..--..` in the program). Do not treat it as a decoding failure.

```text
QRZ? DE IM4TET K □ TEST
   ↑            ↑
question mark   unrecognized symbol
```

### General Guidance

- Decoding quality depends on the source signal.
- Clear recordings with little noise generally produce better results.
- The decoder estimates sending speed automatically. The original guide targeted roughly 5–40 WPM; current noisy-audio regression cases cover 12–50 WPM.
- Supported inputs are WAV, MP3, and OGG, with FFmpeg conversion for compressed formats.

## 📄 License

MIT License — see [LICENSE](LICENSE).

## 🤝 Contributing

Pull requests are welcome. For larger changes, open an issue first to discuss the proposal.

See [CONTRIBUTING.en.md](CONTRIBUTING.en.md).

## 📞 Contact

- **Author:** Anton Zelenov.
- **Email:** tixset@gmail.com.
- **GitHub:** https://github.com/tixset/MorseDecoder.

---

**Made with ❤️ for amateur radio operators and radio communications specialists.**

### Interpreting Result Metrics

`Heuristic score` is an internal score for comparing tested parameters, not an accuracy percentage. The fraction of characters without `□` does not establish transcription accuracy either. Callsigns matched by a pattern are listed as candidates.

WPM is estimated from dot duration and the 1:3 dot/dash duration ratio. When timing data is insufficient or inconsistent, speed is marked as unknown. Operator skill is not classified when signal evidence is unreliable or affected by interference.

### Decoding Noisy Recordings

In `auto` mode, the program searches for a dominant tone between 250 and 3000 Hz, isolates a narrow band around it, and smooths the envelope. Two switching thresholds, bridging of dropouts shorter than 10 ms, and rejection of pulses shorter than 15 ms reduce the fragmentation of dots and dashes. Symbols are determined from pulse and gap durations, without a dictionary of expected phrases.

The JSON configuration stores `auto_frequency`, so `decode` uses the same processing method. To use a fixed band through the Python API, set `MorseDecoder(auto_frequency=False, min_freq=400, max_freq=800)`. The `multi` command retains separate frequency bands for separate signals.

The reference recording and user-supplied transcription are in `tests/fixtures/`. Correctly decoding one recording does not guarantee accuracy on every recording: overlapping signals, deep fading, and very fast CW can still cause errors.
