# 🎵 Декодирование нескольких сигналов

[![Русский](https://img.shields.io/badge/Language-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-blue)](MULTI_SIGNAL_DECODING.md) [![English](https://img.shields.io/badge/Language-English-lightgrey)](MULTI_SIGNAL_DECODING.en.md)

[Руководство CLI](USAGE_GUIDE.md) · [Структура проекта](ARCHITECTURE.md)

`multi` — экспериментальный режим для нескольких CW-сигналов на разных частотах. Для одного сигнала сначала используйте `auto`: спектральные пики могут оказаться гармониками или помехами, а не отдельными передачами.

## 💻 Команды

```bash
python morse_cli.py multi recording.wav
python morse_cli.py multi recording.mp3 --max-signals 2 --ru
python morse_cli.py multi recording.wav --bands "400-800,1000-1400"
python morse_cli.py multi recording.wav --lookup-callsigns
```

Автоопределение включено по умолчанию; `--auto-detect/-a` повторяет это значение. Поиск пиков ограничен 300–1500 Гц. `--max-signals/-m` задаёт число искомых пиков (по умолчанию 3), а не гарантию числа реальных сигналов. `--bands/-b` задаёт полосы в герцах и имеет приоритет над автоопределением; список ручных полос не ограничивается `--max-signals`.

Для ручной полосы задавайте положительные границы ниже половины частоты дискретизации, сначала нижнюю, затем верхнюю. Сжатые записи конвертируются в моно 8000 Гц. Полосы обрабатываются последовательно, внутри каждой подбираются параметры. Это разделение по частоте, а не полноценное выделение перекрывающихся источников.

Флаг `--speed-range/-s "10-50"` принимается парсером, но текущий обработчик его не использует. Он не ограничивает скорость декодирования. Отдельный метод Python `decode_with_multiple_speeds` является экспериментальным перебором порогов, а не гарантированным фильтром WPM.

## 📊 Результаты

Рядом с записью создаются `recording.multi.txt` и `recording.multi.json`; повторный запуск их перезаписывает. TXT содержит русские заголовки. JSON содержит `file`, `total_signals`, массив `signals` и, при наличии автоматического анализа пиков, `peak_analysis`.

Поля каждого сигнала: `frequency_band`, `center_frequency`, `text`, `wpm`, `quality`, `signal_strength`, `pulses`. JSON сохраняет WPM целым числом. Поле `quality` — доля символов без `□`, а не точность; сила сигнала — амплитуда огибающей, не калиброванная мощность. Результаты сортируются по `quality`. В JSON не сохраняются все внутренние данные Python API.

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

Возвращается словарь `signals`/`peak_info`, а не список. При ручных полосах `peak_info` равен `None`. Неудачная обработка отдельных полос может оставить неполный или пустой список результатов.

## ⚠️ Ограничения

Широкие и перекрывающиеся полосы могут захватить один сигнал несколько раз. Близкие частоты, слабый сигнал и дрейф затрудняют разделение. Предупреждение об одиночном сигнале эвристическое. Сравнивайте результат с записью; высокое `quality` не исключает бессмысленный текст. Тесты шумного одиночного CW не подтверждают точность многосигнального режима.
