# Audio Morse Decoder 🎵→📝

[![Русский](https://img.shields.io/badge/Language-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-lightgrey)](README.md) [![English](https://img.shields.io/badge/Language-English-blue)](README.en.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Language-Python-3776ab.svg)](https://www.python.org/)
[![Release](https://img.shields.io/github/v/release/tixset/MorseDecoder)](https://github.com/tixset/MorseDecoder/releases)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.en.md)
[![GitHub Stars](https://img.shields.io/github/stars/tixset/MorseDecoder?style=social)](https://github.com/tixset/MorseDecoder/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/tixset/MorseDecoder?style=social)](https://github.com/tixset/MorseDecoder/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/tixset/MorseDecoder)](https://github.com/tixset/MorseDecoder/issues)
[![Last Commit](https://img.shields.io/github/last-commit/tixset/MorseDecoder)](https://github.com/tixset/MorseDecoder/commits)

An audio Morse decoder with English and Russian alphabets, automatic parameter tuning, and procedural code analysis. Includes a CLI and a GUI for manual tuning.

## ✨ Main features

### 🎚️ Audio and tuning

- ✅ CW decoding from radio and WebSDR recordings: WAV, MP3, OGG.
- ✅ Pulse extraction in noise, automatic carrier detection, and WPM estimation.
- ✅ Text rendered in both Russian and English alphabets.
- ✅ Pulse, dot/dash, character-gap, and word-gap thresholds adjustable through the Python API and slider GUI.
- ✅ Automatic tuning: `fast` (12 combinations), `thorough` (560), `extreme` (3696).
- ✅ Batch processing with multiple threads, reusable JSON configurations, and temporary WAV cleanup.
- ✅ Experimental processing of multiple frequency bands and random parameter search.

### 📡 Procedural codes and messages

The decoded-text detector supports Q, Z, Y, and Shch codes, CW abbreviations, Russian procedural abbreviations, tagged prosigns, maritime codes, and weather codes. It also extracts `CHECK` and `NR`, finds callsign candidates, and identifies message-structure and urgency indicators. The API exposes more categories than the console summary lists.

Exact matching is the default; fuzzy matching can be enabled through the API. The prosign `<AR>` and separate letters `AR` are not equivalent: joined transmission matters.

### 📊 Reports and performance

The tuning TXT report contains recording information, both transcriptions, detected codes and callsigns, technical parameters, and signal analysis. JSON saves parameters and heuristic metrics; `multi` also saves results by band. The CLI has no CSV export.

The implementation includes decoding and fuzzy-matching caches, Numba acceleration for Levenshtein distance, and a separate asynchronous callsign module using aiohttp. Having an asynchronous module does not mean every CLI command uses it. Actual speedups depend on data, caching, networking, and hardware.

## 🔧 Installation

Run commands from the repository root. Use Python 3.10 or newer; the full test suite was checked in the current Python 3.13 environment. Other Python and OS combinations have not been individually verified.

```bash
git clone https://github.com/tixset/MorseDecoder.git
cd MorseDecoder
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate` in cmd or `.venv\Scripts\Activate.ps1` in PowerShell; you can use `py -3` instead of `python3`.

MP3/OGG input requires system **FFmpeg** in `PATH`. The GUI also requires Tkinter and a graphical session. On Debian/Ubuntu, install system components with:

```bash
sudo apt install python3-venv python3-tk ffmpeg
ffmpeg -version
```

`pip install -r requirements.txt` does not install FFmpeg or Tkinter. NumPy and SciPy process signals; requests/aiohttp handle callsign requests, Numba provides acceleration, and pydub is used by the separate converter. The main CLI converts MP3/OGG directly through FFmpeg. `tqdm` is optional: tuning works without its progress bar.

## 🚀 Quick start

```bash
python morse_cli.py auto recording.wav
python morse_cli.py auto recording.mp3 --ru
python morse_cli.py auto recording.wav --mode thorough
python morse_cli.py decode recording.wav --analyze
python morse_cli.py batch recordings --workers 4
python morse_tuner_gui.py
```

Supply your own recording path; `recordings` is your WAV folder. `decode` requires a configuration created by `auto`. The repository includes a [noisy recording](tests/fixtures/noisy_cw.mp3) and its [reference transcription](tests/fixtures/noisy_cw.json) for a reproducible check:

```bash
python morse_cli.py auto tests/fixtures/noisy_cw.mp3 --ru
```

CLI messages are English by default. `--ru` works before or after the subcommand and changes console messages and help. Both EN/RU transcriptions are saved independently of this flag; TXT report headings and the GUI remain Russian.

## 🎯 Features and limitations

- `auto`: carrier detection and threshold tuning for one signal; TXT report and JSON configuration beside the audio.
- `batch`: process `*.wav` directly within a folder, with multiple worker threads.
- `decode`: decode again using saved parameters, with console output.
- `multi`: experimental frequency separation of signals, with TXT/JSON reports.
- `experiment`: random parameter search, saved to `experiment_results.json`.

The decoder handles CW. PSK31/RTTY classification in the analyzer does not mean those modulations can be decoded. Noise, frequency drift, overlapping signals, and unusual timing can cause errors. A larger parameter search does not guarantee improvement.

`auto --analyze` is unsupported: `auto` already includes code analysis; the extra flag belongs to `decode`. Russian abbreviations are available through the Python API, but the CLI has no switch that forces their complete listing. See the [code reference](docs/SUPPORTED_CODES.en.md) for an example.

## 💻 More CLI examples

```bash
# Tuning with network callsign lookup
python morse_cli.py auto recording.wav --lookup-callsigns
python morse_cli.py auto recording.wav --mode thorough --lookup-callsigns

# WAV folder with callsign lookup or sequential processing
python morse_cli.py batch recordings --lookup-callsigns --workers 4
python morse_cli.py batch recordings --workers 1

# Explicit configuration; create it with auto first
python morse_cli.py decode recording.wav --config custom.config.json

# Multiple frequency bands and experimental search
python morse_cli.py multi recording.wav --bands "400-800,1000-1400"
python morse_cli.py experiment recording.wav --iterations 50

# Russian language before the command; command-specific help
python morse_cli.py --ru batch recordings
python morse_cli.py decode --help --ru
python morse_cli.py --help
```

### 📡 Callsign lookup

`--lookup-callsigns` (alias `--lookup`) enables network requests in `auto`, `batch`, and `multi`. In `decode`, the flag is accepted but not used by the handler yet. Requests to HamQTH, RadioQTH, QRZ.RU, and APRS.fi are implemented; availability depends on external services.

Synchronous lookup caches results in `callsign_cache/` for up to 7 days. The implementation includes Cyrillic callsign conversion using Morse equivalents and batch lookup with delays between requests. Matches remain candidates, and a network response does not verify the entire transcription.

## 🔧 Python usage

Manual tuning example for the reference recording (these parameters are not universal):

```python
from modules.morse_decoder import MorseDecoder

decoder = MorseDecoder(
    sample_rate=8000,
    auto_frequency=True,
    pulse_percentile=70,
    gap_percentile_dot_dash=55,
    gap_percentile_char=75,
    gap_percentile_word=90,
)
text_en, text_ru, stats = decoder.process_file(
    "tests/fixtures/noisy_cw.mp3", analyze_procedural=False, verbose=False
)
if stats.get("error"):
    raise RuntimeError(stats["error"])
print(f"WPM: {stats['wpm']}")
print(text_en)
print(text_ru)
```

For your own recording, tune parameters automatically:

```python
from modules.auto_tune import auto_tune_parameters
from modules.procedural_codes import ProceduralCodeDetector

result = auto_tune_parameters("recording.wav", mode="fast")
if result is not None:
    codes = ProceduralCodeDetector().detect_codes(result["text_ru"])
    print(codes["ru_procedural_abbr"])
```

This call saves TXT and JSON beside the audio. For a fixed band, use `MorseDecoder(auto_frequency=False, min_freq=400, max_freq=800)`. Choose `min_freq`/`max_freq` for your recording. See the [API and code reference](docs/SUPPORTED_CODES.en.md).

## ⚙️ How it works

1. Load WAV and convert to mono; MP3/OGG are first converted through FFmpeg.
2. Search for the dominant tone within 250–3000 Hz and filter a narrow band around it. Fixed mode uses the specified band.
3. Extract and smooth the amplitude envelope.
4. Detect pulse starts and ends with two switching thresholds.
5. Estimate dot duration and the 1:3 dot/dash ratio; check timing reliability.
6. Group symbols and words using gaps; reliable timing uses Morse ratios 1:3:7, otherwise a threshold-based fallback is used.
7. Convert Morse patterns to EN/RU text, analyze codes, and produce results.

### 🔊 Noisy recordings

Bridging gaps shorter than 10 ms and rejecting pulses shorter than 15 ms reduces noise-induced fragmentation of dots and dashes. Pulse and gap durations determine the text without a dictionary of expected phrases. The configuration saves `auto_frequency` so `decode` reuses the selected processing method; `multi` retains separate signal bands.

The [reference recording](tests/fixtures/noisy_cw.mp3) has a user-provided [Morse and Russian transcription](tests/fixtures/noisy_cw.json). Exact recovery after tuning does not guarantee accuracy elsewhere: deep fading, overlapping signals, and very fast CW can still cause errors. There is no guaranteed WPM range for every recording.

## 🔤 Supported symbols and codes

The tables contain Latin and Russian letters, digits 0–9, and punctuation. EN lists `. , ? ' ! / ( ) & : ; = + - _ " $ @`; RU lists `. , ? ' ! / ( ) : ; =`. This describes table contents, not unambiguous output: prosigns are checked first. For example, `.-.-.` renders as `<AR>` rather than `+`; current F/Ф/Э ambiguities are explained in the [reference](docs/SUPPORTED_CODES.en.md).

| Category | Entries | Examples |
| --- | ---: | --- |
| Q codes | 53 | `QSL`: acknowledge reception; `QTH`: location; `QRZ`: who is calling |
| Z codes | 33 | `ZAA`: radio discipline; `ZAG`: interrupt transmission |
| Y codes | 26 | `YAA`, `YBB` |
| Shch codes | 3 | `ЩРТ`, `ЩРЩ`, `ЩСА` |
| CW abbreviations | 25 | `RPT`: repeat; `DE`: from; `CQ`: general call |
| Prosigns | 11 | `<AR>`, `<SK>`, `<BT>`, `<HH>`; some names are aliases |
| Russian abbreviations | 7 | `РПТ`: repeat; `АЛ`: all just transmitted |
| Maritime / weather codes | 18 / 9 | `NC`, `WX` |
| Soviet codes / SINPO | 12 / 5 | Separate dictionary categories |

`code_dictionaries.py` contains 18 dictionaries, including callsign helpers, phonetic alphabets, and RST. Not every dictionary is an automatic detection category; meanings reflect project data and require context. See [SUPPORTED_CODES.en.md](docs/SUPPORTED_CODES.en.md) for the complete inventory.

## 🏗️ Project structure

The CLI, GUI, and test runner live in the root; implementation is in `modules/`, and helper tools are in `tools/`.

```text
MorseDecoder/
├── morse_cli.py
├── morse_tuner_gui.py
├── run_all_tests.py
├── requirements.txt
├── LICENSE
├── README.md / README.en.md
├── CHANGELOG.md / CHANGELOG.en.md
├── CONTRIBUTING.md / CONTRIBUTING.en.md
├── modules/
│   ├── __init__.py
│   ├── audio_input.py
│   ├── cw_frontend.py
│   ├── morse_timing.py
│   ├── morse_decoder.py
│   ├── auto_tune.py
│   ├── multi_signal_decoder.py
│   ├── signal_analyzer.py
│   ├── procedural_codes.py
│   ├── code_dictionaries.py
│   ├── callsign_lookup.py
│   ├── callsign_lookup_async.py
│   ├── analyze_codes.py
│   ├── fuzzy_matcher.py
│   ├── levenshtein_optimized.py
│   ├── console_i18n.py
│   └── console_en.json
├── docs/
│   ├── USAGE_GUIDE.md / USAGE_GUIDE.en.md
│   ├── SUPPORTED_CODES.md / SUPPORTED_CODES.en.md
│   ├── MULTI_SIGNAL_DECODING.md / MULTI_SIGNAL_DECODING.en.md
│   └── ARCHITECTURE.md / ARCHITECTURE.en.md
├── tools/
│   └── convert_mp3_to_wav.py
├── tests/
│   ├── __init__.py
│   ├── test_*.py
│   └── fixtures/
│       ├── noisy_cw.mp3
│       └── noisy_cw.json
└── .github/
    ├── ISSUE_TEMPLATE/
    ├── PULL_REQUEST_TEMPLATE.md
    └── PULL_REQUEST_TEMPLATE/english.md
```

`TrainingData/` is an optional local recording folder. It, `reports/`, `callsign_cache/`, `.venv/`, and generated outputs are ignored by Git. See the [architecture guide](docs/ARCHITECTURE.en.md) for each module’s purpose.

## 📊 Interpreting result metrics

`□` denotes an unknown symbol; `?` is a real question mark. The proportion without `□` measures dictionary coverage, not transcription accuracy. `score` is a heuristic for comparing candidates and can be negative. `transcription_verified: false` means the result was not checked against a reference.

WPM is estimated from dot and dash durations. Unreliable timing produces an unknown speed (0 in the data). Signal metrics and operator ratings are approximate. Callsigns are pattern candidates; dictionary code matches do not establish a message's meaning.

## 📚 Documentation and verification

- [CLI guide, output formats, and troubleshooting](docs/USAGE_GUIDE.en.md)
- [Codes, alphabets, and Python API](docs/SUPPORTED_CODES.en.md)
- [Multiple signals](docs/MULTI_SIGNAL_DECODING.en.md)
- [Project structure and helper tools](docs/ARCHITECTURE.en.md)
- [Contributing and testing](CONTRIBUTING.en.md)
- [Changelog](CHANGELOG.en.md)

```bash
python run_all_tests.py
```

Test reports appear in `reports/`. FFmpeg is required for the MP3 regression; related tests are skipped without it. License: [MIT](LICENSE).

## ⚠️ Troubleshooting

| Problem | What to check |
| --- | --- |
| No pulses detected | Check for audible CW; try the GUI pulse threshold and a suitable frequency band |
| Incorrect text or many `□` symbols | Check carrier, interference, and timing; try tuning or manual parameters and compare against the audio |
| NumPy/SciPy incompatibility | Create a separate `.venv` and install `requirements.txt` as described in installation |
| MP3/OGG does not open | Check FFmpeg in `PATH`: `ffmpeg -version` |
| `auto --analyze` fails | Omit the flag from `auto`, or run `decode --analyze` with a saved configuration |
| GUI fails to start | Check Tkinter and availability of a graphical session |

A question mark is transmitted as `..--..`; an unknown pattern is shown as `□`. In `QRZ? DE IM4TET K □ TEST`, the question mark is a recognized character and the square is unknown. Even a recognized character can be incorrect under interference.

For best results, use recordings with distinguishable CW and minimal overlap from other signals. More guidance is available in the [CLI guide](docs/USAGE_GUIDE.en.md).

## 🆕 Historical updates and experiments

The **January 7, 2026** update centralized dictionaries, removed duplicated constants, and added LRU, aiohttp, and Numba optimizations. The old README quoted 3–5× faster fuzzy matching, callsign lookup reduced from 12 to 0.92 seconds, and about 326,000 Levenshtein operations per second. These are historical individual measurements, not current-version benchmarks verified here. See the [changelog](CHANGELOG.en.md) for history.

The old README also reported **zero Q/Z code detections in 40 experiments** on noisy WebSDR recordings, with `Р` matched six times and `ДЕ` twice. This describes an earlier experiment series; it does not characterize the corrected decoder or establish the meaning of dictionary matches. The current noisy-CW regression uses a separate reference in `tests/fixtures/`.

## 📄 License and contributions

The project uses the [MIT License](LICENSE). Pull requests are welcome; major changes benefit from prior discussion in [Issues](https://github.com/tixset/MorseDecoder/issues). See [CONTRIBUTING.en.md](CONTRIBUTING.en.md) for development and validation instructions.

## 📞 Contact

- **Author:** Anton Zelenov
- **Email:** tixset@gmail.com
- **GitHub:** [tixset/MorseDecoder](https://github.com/tixset/MorseDecoder)

Made with ❤️ for amateur radio operators and radio communication specialists.
