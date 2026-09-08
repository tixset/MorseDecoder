# 🎵 Decoding multiple signals

[![Русский](https://img.shields.io/badge/Language-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-lightgrey)](MULTI_SIGNAL_DECODING.md) [![English](https://img.shields.io/badge/Language-English-blue)](MULTI_SIGNAL_DECODING.en.md)

[CLI guide](USAGE_GUIDE.en.md) · [Project structure](ARCHITECTURE.en.md)

`multi` is experimental support for several CW signals at different frequencies. Start with `auto` for one signal: spectral peaks can be harmonics or interference rather than separate transmissions.

## 💻 Commands

```bash
python morse_cli.py multi recording.wav
python morse_cli.py multi recording.mp3 --max-signals 2 --ru
python morse_cli.py multi recording.wav --bands "400-800,1000-1400"
python morse_cli.py multi recording.wav --lookup-callsigns
```

Automatic detection is enabled by default; `--auto-detect/-a` repeats that setting. Peak search is limited to 300–1500 Hz. `--max-signals/-m` sets the requested peak count (default 3), not a guaranteed number of actual signals. `--bands/-b` supplies bands in hertz and takes precedence over automatic detection; `--max-signals` does not limit the manual band list.

For manual bands, supply positive bounds below half the sample rate, lower bound first. Compressed recordings are converted to mono at 8000 Hz. Bands are processed sequentially, with parameter tuning within each band. This separates frequencies; it is not full source separation for overlapping signals.

The parser accepts `--speed-range/-s "10-50"`, but the current handler does not use it. It does not constrain decoding speed. The separate Python method `decode_with_multiple_speeds` is an experimental threshold search, not a guaranteed WPM filter.

## 📊 Output

`recording.multi.txt` and `recording.multi.json` are created beside the audio and overwritten on repeated runs. TXT headings are Russian. JSON contains `file`, `total_signals`, a `signals` array, and `peak_analysis` when automatic peak information is available.

Each signal has `frequency_band`, `center_frequency`, `text`, `wpm`, `quality`, `signal_strength`, and `pulses`. JSON saves WPM as an integer. `quality` is the proportion without `□`, not accuracy; signal strength is envelope amplitude, not calibrated power. Results are sorted by `quality`. JSON does not retain all internal Python API data.

## 🔧 Python API

```python
from modules.multi_signal_decoder import MultiSignalDecoder

decoder = MultiSignalDecoder(
    frequency_bands=[(400, 800), (1000, 1400)],
    auto_detect=False,
)
result = decoder.decode_multi_signal("recording.wav", verbose=False)
for signal in result["signals"]:
    print(signal["frequency_band"], signal["text"], signal["wpm"])
print(result["peak_info"])
```

The return value is a dictionary with `signals`/`peak_info`, not a list. Manual bands produce `peak_info=None`. Failures in individual bands can leave an incomplete or empty result list.

## ⚠️ Limitations

Wide or overlapping bands can capture the same signal more than once. Close frequencies, weak signals, and drift complicate separation. Single-signal warnings are heuristic. Compare output against the recording; high `quality` does not rule out meaningless text. Noisy single-CW tests do not establish multi-signal accuracy.
