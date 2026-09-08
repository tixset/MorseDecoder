# 📖 Руководство CLI

[![Русский](https://img.shields.io/badge/Language-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-blue)](USAGE_GUIDE.md) [![English](https://img.shields.io/badge/Language-English-lightgrey)](USAGE_GUIDE.en.md)

[Установка](../README.md) · [Несколько сигналов](MULTI_SIGNAL_DECODING.md) · [Коды](SUPPORTED_CODES.md)

## 📋 Команды и аргументы

```bash
python morse_cli.py --help
python morse_cli.py decode --help --ru
```

Все команды принимают `--ru`: это язык консоли, а не выбор алфавита декодирования. Для отдельного файла поддерживаются WAV/MP3/OGG, для сжатого аудио нужен FFmpeg.

| Команда | Аргументы |
| --- | --- |
| `auto FILE` | `--mode/-m fast\|thorough\|extreme`, `--lookup-callsigns/--lookup` |
| `batch FOLDER` | те же параметры, `--workers/-w N` (0 — автоматически, 1 — последовательно) |
| `decode FILE` | `--config/-c PATH`, `--analyze/-a`; `--lookup-callsigns/--lookup` принимается, но обработчик его не использует |
| `multi FILE` | `--auto-detect/-a`, `--bands/-b "400-800,1000-1400"`, `--max-signals/-m N` (3), `--lookup-callsigns/--lookup`; `--speed-range/-s` принимается, но не влияет на обработку |
| `experiment FILE` | `--iterations/-n N` (30; указывайте положительное число) |

Команд `procedural`, флагов `--fast` и экспорта CSV нет. `--mode fast` — режим по умолчанию в `auto` и `batch`.

## 🎛️ Подбор и повторное декодирование

```bash
python morse_cli.py auto recording.mp3 --ru
python morse_cli.py auto recording.wav --mode thorough
python morse_cli.py auto recording.wav --mode extreme
python morse_cli.py decode recording.wav --analyze
python morse_cli.py decode recording.wav --config custom.config.json
```

| Режим | Проверяемых комбинаций |
| --- | ---: |
| `fast` | 12 |
| `thorough` | 560 |
| `extreme` | 3696 |

Время зависит от длительности записи и компьютера. Начинайте с `fast`. `decode` требует `recording.config.json` рядом с аудио либо явно указанный конфиг. Сохраняемый раздел `parameters` содержит `auto_frequency`, `pulse_percentile`, `gap_percentile_dot_dash`, `gap_percentile_char`, `gap_percentile_word`. При надёжной оценке интервалов используются отношения Морзе 1:3:7; старые пороги разделения служат запасным вариантом.

`--analyze` принадлежит только `decode` и добавляет краткую сводку позывных, Q-кодов, prosigns и CW-сокращений. `auto` уже анализирует коды без этого флага. Для российских процедурных сокращений используйте [пример Python API](SUPPORTED_CODES.md): `--ru` не заставляет CLI выбирать русский анализ.

## 📁 Пакетная обработка и эксперименты

```bash
python morse_cli.py batch recordings --workers 4
python morse_cli.py batch recordings --workers 1 --mode thorough
python morse_cli.py experiment recording.wav --iterations 50
```

`batch` не обходит вложенные папки и выбирает шаблон `*.wav` (в Linux расширение в нижнем регистре). MP3/OGG обрабатывайте отдельными командами или предварительно конвертируйте. `experiment` использует случайные параметры и фиксированные частотные полосы; это исследовательский инструмент, результаты запусков могут отличаться.

## 📄 Файлы результатов

| Команда | Результат |
| --- | --- |
| `auto`, `batch` | `<имя>.txt` с расшифровками EN/RU и аналитикой; `<имя>.config.json` с параметрами и метриками |
| `decode` | Расшифровки и анализ в консоли; отдельный файл не создаётся |
| `multi` | `<имя>.multi.txt`, `<имя>.multi.json` рядом с аудио |
| `experiment` | `experiment_results.json` в рабочей папке |

Повторные запуски перезаписывают соответствующие результаты. Отчёты TXT имеют русские заголовки независимо от `--ru`. Временный WAV для MP3/OGG удаляется после обработки. Схема конфигурации на примере (метрики иллюстративные):

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

`error_count` считает `□`, а не ошибочные буквы, известные только при сравнении с эталоном. Нулевое значение не гарантирует правильную расшифровку. `auto` выбирает рабочий текст по длине (при равенстве RU), а коды ищет в EN. Это не определение языка по смыслу.

## 📡 Позывные и сеть

```bash
python morse_cli.py auto recording.wav --lookup-callsigns
python morse_cli.py batch recordings --lookup --workers 4
```

Флаг включает обращения к внешним справочникам (HamQTH, RadioQTH, APRS.fi, QRZ.RU). Их доступность зависит от сети и сервиса. Кэш сохраняется в `callsign_cache/`. Без флага сетевой поиск не нужен; найденные по шаблону позывные всё равно могут быть ложными. В `decode` флаг пока не подключён к обработчику.

## ⚠️ Устранение проблем

- `unrecognized arguments: --analyze`: уберите флаг у `auto` или используйте `decode --analyze` после создания конфига.
- Не найден конфиг: сначала выполните `auto` для того же файла или укажите `--config`.
- Ошибка FFmpeg: проверьте `ffmpeg -version` и наличие исполняемого файла в `PATH`.
- `ModuleNotFoundError`: активируйте окружение и выполните `python -m pip install -r requirements.txt`.
- Пустой результат, неизвестная скорость или бессмысленный текст: проверьте слышимость CW, частоту, интервалы и наложение сигналов; попробуйте ручные полосы `multi` или GUI. Отсутствие `□` не доказывает успех.
- GUI не запускается: нужен Tkinter и графический дисплей; `--ru` к GUI не относится.
