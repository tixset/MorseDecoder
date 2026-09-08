# Декодер азбуки Морзе из аудио 🎵→📝

[![Русский](https://img.shields.io/badge/Language-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-blue)](README.md) [![English](https://img.shields.io/badge/Language-English-lightgrey)](README.en.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Language-Python-3776ab.svg)](https://www.python.org/)
[![Release](https://img.shields.io/github/v/release/tixset/MorseDecoder)](https://github.com/tixset/MorseDecoder/releases)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![GitHub Stars](https://img.shields.io/github/stars/tixset/MorseDecoder?style=social)](https://github.com/tixset/MorseDecoder/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/tixset/MorseDecoder?style=social)](https://github.com/tixset/MorseDecoder/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/tixset/MorseDecoder)](https://github.com/tixset/MorseDecoder/issues)
[![Last Commit](https://img.shields.io/github/last-commit/tixset/MorseDecoder)](https://github.com/tixset/MorseDecoder/commits)

Декодер аудиозаписей азбуки Морзе с русским и английским алфавитами, автоматическим подбором параметров и анализом процедурных кодов. Есть CLI и графический интерфейс для ручной настройки.

## ✨ Основные возможности

### 🎚️ Аудио и настройка

- ✅ Декодирование CW из записей радиоэфира и WebSDR: WAV, MP3, OGG.
- ✅ Выделение импульсов на фоне шума, автоматический поиск несущей и оценка скорости WPM.
- ✅ Представление текста русским и английским алфавитами.
- ✅ Настройка порогов импульсов, точек/тире, межсимвольных и межсловных пауз через Python API и GUI с ползунками.
- ✅ Автоматический подбор параметров: `fast` (12 комбинаций), `thorough` (560), `extreme` (3696).
- ✅ Пакетная обработка с несколькими потоками, повторное использование JSON-конфигурации, очистка временных WAV.
- ✅ Экспериментальная обработка нескольких частотных полос и случайный поиск параметров.

### 📡 Процедурные коды и радиограммы

Детектор готового текста поддерживает Q-, Z-, Y- и Щ-коды, CW-сокращения, российские процедурные сокращения, помеченные prosigns, морские и метеокоды. Он также извлекает поля `CHECK` и `NR`, ищет позывные, признаки структуры радиограммы и уровень срочности. Доступность данных через API шире, чем перечень категорий в консольной сводке.

Точное сопоставление включено по умолчанию; нечёткий поиск можно включить в API. Процедурный знак `<AR>` и отдельные буквы `AR` не равнозначны: слитность передачи имеет значение.

### 📊 Отчёты и производительность

TXT-отчёт автоподбора содержит информацию о записи, обе расшифровки, найденные коды и позывные, технические параметры и аналитику сигнала. JSON сохраняет параметры и эвристические метрики; `multi` дополнительно сохраняет результаты по полосам. Экспорта CSV в CLI нет.

Реализованы кэширование декодирования и нечёткого сопоставления, Numba-ускорение расстояния Левенштейна и отдельный асинхронный модуль поиска позывных через aiohttp. Наличие асинхронного модуля не означает, что каждый CLI-режим использует его. Фактическое ускорение зависит от данных, кэша, сети и оборудования.

## 🔧 Установка

Команды выполняются из корня репозитория. Используйте Python 3.10 или новее; полный набор тестов проверен в текущем окружении Python 3.13. Совместимость всех версий Python и ОС отдельно не проверялась.

```bash
git clone https://github.com/tixset/MorseDecoder.git
cd MorseDecoder
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

В Windows активируйте окружение командой `.venv\Scripts\activate` в cmd или `.venv\Scripts\Activate.ps1` в PowerShell; вместо `python3` можно использовать `py -3`.

Для MP3/OGG нужен системный **FFmpeg**, доступный в `PATH`. Для GUI дополнительно нужны Tkinter и графическая сессия. В Debian/Ubuntu системные компоненты можно установить так:

```bash
sudo apt install python3-venv python3-tk ffmpeg
ffmpeg -version
```

`pip install -r requirements.txt` не устанавливает FFmpeg или Tkinter. NumPy и SciPy обрабатывают сигнал; requests/aiohttp используются для сетевого поиска позывных, Numba — для ускорения, pydub — в отдельном конвертере. Основной CLI конвертирует MP3/OGG напрямую через FFmpeg. `tqdm` необязателен: без него нет полосы прогресса автоподбора.

## 🚀 Быстрый старт

```bash
python morse_cli.py auto recording.wav
python morse_cli.py auto recording.mp3 --ru
python morse_cli.py auto recording.wav --mode thorough
python morse_cli.py decode recording.wav --analyze
python morse_cli.py batch recordings --workers 4
python morse_tuner_gui.py
```

Подставьте путь к своей записи; `recordings` — ваша папка с WAV. `decode` требует конфигурацию, созданную командой `auto`. Для воспроизводимой проверки в репозитории есть [шумная запись](tests/fixtures/noisy_cw.mp3) и [эталон](tests/fixtures/noisy_cw.json):

```bash
python morse_cli.py auto tests/fixtures/noisy_cw.mp3 --ru
```

Консоль CLI по умолчанию английская. `--ru` разрешён до или после подкоманды и меняет язык консоли и справки. Обе расшифровки EN/RU сохраняются независимо от этого флага; заголовки TXT-отчётов и интерфейс GUI остаются русскими.

## 🎯 Возможности и ограничения

- `auto`: поиск несущей и подбор порогов для одного сигнала; TXT-отчёт и JSON-конфигурация рядом с аудио.
- `batch`: обработка `*.wav` непосредственно в указанной папке, с несколькими рабочими потоками.
- `decode`: повторное декодирование с сохранёнными параметрами, вывод в консоль.
- `multi`: экспериментальное разделение сигналов по частотам, TXT/JSON-отчёты.
- `experiment`: случайный поиск параметров с результатами в `experiment_results.json`.

Обрабатывается CW. Классификация PSK31/RTTY в аналитике не означает, что проект декодирует эти виды модуляции. Шум, дрейф частоты, наложение сигналов и необычные интервалы могут приводить к ошибкам. Больший перебор параметров не гарантирует улучшения.

`auto --analyze` не поддерживается: анализ кодов уже входит в `auto`; дополнительный флаг есть у `decode`. Российские сокращения доступны через Python API, но CLI не имеет переключателя принудительного вывода их полного списка. Пример — в [справочнике кодов](docs/SUPPORTED_CODES.md).

## 💻 Дополнительные примеры CLI

```bash
# Автоподбор с сетевым поиском позывных
python morse_cli.py auto recording.wav --lookup-callsigns
python morse_cli.py auto recording.wav --mode thorough --lookup-callsigns

# Папка WAV с поиском позывных или последовательной обработкой
python morse_cli.py batch recordings --lookup-callsigns --workers 4
python morse_cli.py batch recordings --workers 1

# Явный конфиг; сначала создайте его командой auto
python morse_cli.py decode recording.wav --config custom.config.json

# Несколько частотных полос и экспериментальный перебор
python morse_cli.py multi recording.wav --bands "400-800,1000-1400"
python morse_cli.py experiment recording.wav --iterations 50

# Русский язык до команды; справка отдельной команды
python morse_cli.py --ru batch recordings
python morse_cli.py decode --help --ru
python morse_cli.py --help
```

### 📡 Поиск позывных

`--lookup-callsigns` (алиас `--lookup`) включает сетевые запросы в `auto`, `batch` и `multi`. В `decode` флаг принимается, но обработчик его пока не использует. Реализованы обращения к HamQTH, RadioQTH, QRZ.RU и APRS.fi; доступность зависит от внешних сервисов.

Синхронный поиск хранит результаты в `callsign_cache/` до 7 дней. Предусмотрены преобразование кириллического представления позывных по соответствиям Морзе и пакетный поиск с задержками между запросами. Эти совпадения остаются кандидатами, а сетевой ответ не подтверждает правильность всей расшифровки.

## 🔧 Программное использование

Пример ручной настройки для контрольной записи (параметры не универсальны):

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

Для своей записи параметры можно подобрать автоматически:

```python
from modules.auto_tune import auto_tune_parameters
from modules.procedural_codes import ProceduralCodeDetector

result = auto_tune_parameters("recording.wav", mode="fast")
if result is not None:
    codes = ProceduralCodeDetector().detect_codes(result["text_ru"])
    print(codes["ru_procedural_abbr"])
```

Этот вызов сохраняет TXT и JSON рядом с аудио. Для фиксированной полосы используйте `MorseDecoder(auto_frequency=False, min_freq=400, max_freq=800)`. Значения `min_freq`/`max_freq` должны соответствовать записи. Подробности — в [справочнике API и кодов](docs/SUPPORTED_CODES.md).

## ⚙️ Как это работает

1. Загрузка WAV и преобразование в моно; MP3/OGG предварительно конвертируются через FFmpeg.
2. Поиск доминирующего тона в диапазоне 250–3000 Гц и фильтрация узкой полосы вокруг него. В фиксированном режиме используется заданная полоса.
3. Выделение и сглаживание амплитудной огибающей.
4. Детектирование начала и конца импульсов с двумя порогами переключения.
5. Оценка длительности точки и соотношения точек/тире 1:3; проверка надёжности.
6. Группировка в символы и слова по паузам; при надёжных интервалах используются отношения Морзе 1:3:7, иначе — запасная классификация по порогам.
7. Преобразование рисунков Морзе в EN/RU-текст, анализ кодов и формирование результатов.

### 🔊 Записи с шумом

Объединение разрывов короче 10 мс и отсечение импульсов короче 15 мс уменьшают дробление точек и тире. Длительности импульсов и пауз определяют текст без словаря ожидаемых фраз. Поле `auto_frequency` сохраняется в конфиге, чтобы `decode` повторял выбранный способ обработки; `multi` сохраняет отдельные полосы сигналов.

[Контрольная запись](tests/fixtures/noisy_cw.mp3) имеет пользовательский [эталон Морзе и русского текста](tests/fixtures/noisy_cw.json). Её точная расшифровка после автоподбора не гарантирует точность на других записях: сильные замирания, наложение сигналов и очень быстрый CW могут оставлять ошибки. Гарантированного диапазона WPM для всех записей нет.

## 🔤 Поддерживаемые символы и коды

В таблицах есть латинские и русские буквы, цифры 0–9 и знаки препинания. Для EN перечислены `. , ? ' ! / ( ) & : ; = + - _ " $ @`, для RU — `. , ? ' ! / ( ) : ; =`. Это состав таблиц, а не гарантия однозначного вывода: prosigns проверяются раньше символов. Например, `.-.-.` выводится как `<AR>` вместо `+`; текущие неоднозначности F/Ф/Э описаны в [справочнике](docs/SUPPORTED_CODES.md).

| Категория | Число записей | Примеры |
| --- | ---: | --- |
| Q-коды | 53 | `QSL` — подтверждаю приём; `QTH` — местоположение; `QRZ` — кто вызывает |
| Z-коды | 33 | `ZAA` — дисциплина в эфире; `ZAG` — прервать передачу |
| Y-коды | 26 | `YAA`, `YBB` |
| Щ-коды | 3 | `ЩРТ`, `ЩРЩ`, `ЩСА` |
| CW-сокращения | 25 | `RPT` — повторите; `DE` — от; `CQ` — общий вызов |
| Prosigns | 11 | `<AR>`, `<SK>`, `<BT>`, `<HH>`; часть названий — синонимы |
| Российские сокращения | 7 | `РПТ` — повторите; `АЛ` — всё, что только передано |
| Морские / метеокоды | 18 / 9 | `NC`, `WX` |
| Советские коды / SINPO | 12 / 5 | Отдельные категории словарей |

В `code_dictionaries.py` 18 словарей, включая вспомогательные таблицы позывных, фонетических алфавитов и RST. Не все словари являются категориями автоматического распознавания; значения отражают данные проекта и требуют контекста. Полный перечень — в [SUPPORTED_CODES.md](docs/SUPPORTED_CODES.md).

## 🏗️ Структура проекта

CLI, GUI и запускатель тестов находятся в корне; реализация — в `modules/`, инструменты — в `tools/`.

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

`TrainingData/` — необязательная локальная папка записей. Она, `reports/`, `callsign_cache/`, `.venv/` и результаты обработки исключены из Git. Назначение каждого модуля описано в [архитектуре](docs/ARCHITECTURE.md).

## 📊 Как понимать результат

`□` означает неизвестный символ; `?` — настоящий знак вопроса. Доля символов без `□` показывает покрытие словарём, а не точность расшифровки. `score` — эвристическая оценка для сравнения вариантов, может быть отрицательной. `transcription_verified: false` означает, что результат не сверялся с эталоном.

WPM оценивается по длительностям точек и тире. При ненадёжных интервалах скорость неизвестна (в данных — 0). Метрики сигнала и оценки оператора ориентировочные. Найденные позывные — кандидаты по шаблону; словарные совпадения кодов не доказывают смысл сообщения.

## 📚 Документация и проверка

- [Руководство CLI, форматы результатов и устранение проблем](docs/USAGE_GUIDE.md)
- [Коды, алфавиты и Python API](docs/SUPPORTED_CODES.md)
- [Несколько сигналов](docs/MULTI_SIGNAL_DECODING.md)
- [Структура проекта и вспомогательные инструменты](docs/ARCHITECTURE.md)
- [Участие в разработке и тестирование](CONTRIBUTING.md)
- [История изменений](CHANGELOG.md)

```bash
python run_all_tests.py
```

Отчёты тестов появляются в `reports/`. Для проверки MP3-регрессии нужен FFmpeg; без него соответствующие тесты пропускаются. Лицензия: [MIT](LICENSE).

## ⚠️ Устранение проблем

| Проблема | Что проверить |
| --- | --- |
| Импульсы не обнаружены | Есть ли слышимый CW; попробуйте порог импульсов в GUI и подходящую частотную полосу |
| Неверный текст или много `□` | Несущую, помехи и интервалы; попробуйте автоподбор или ручные параметры; сравните с аудио |
| Несовместимость NumPy/SciPy | Создайте отдельное `.venv` и установите `requirements.txt`, как в разделе установки |
| MP3/OGG не открывается | Наличие FFmpeg в `PATH`: `ffmpeg -version` |
| `auto --analyze` выдаёт ошибку | Уберите флаг у `auto` или выполните `decode --analyze` с готовым конфигом |
| GUI не запускается | Tkinter и доступность графической сессии |

Знак вопроса передаётся как `..--..`, а неизвестный рисунок обозначается `□`. Например, в `QRZ? DE IM4TET K □ TEST` вопросительный знак — распознанный символ, квадрат — неизвестный. Даже известный символ может быть распознан неверно при помехах.

Для лучших результатов используйте запись с различимым CW и минимальным наложением других сигналов. Дополнительные пояснения — в [руководстве CLI](docs/USAGE_GUIDE.md).

## 🆕 Исторические обновления и эксперименты

В обновлении от **7 января 2026 года** были выделены общие словари, устранено дублирование констант и добавлены оптимизации LRU, aiohttp и Numba. В старом README приводились замеры: ускорение fuzzy matching в 3–5 раз, поиска позывных — с 12 до 0,92 с, около 326 тысяч операций Левенштейна в секунду. Это исторические результаты отдельных измерений, а не проверенные здесь показатели текущей версии. История сохранена в [CHANGELOG](CHANGELOG.md).

Старый README также сообщал о **0 находках Q/Z-кодов в 40 экспериментах** на зашумлённых WebSDR-записях и совпадениях `Р` (6 раз), `ДЕ` (2 раза). Это результат прежней серии экспериментов: он не характеризует исправленный декодер и не подтверждает смысл словарных совпадений. Текущая регрессия на шумном CW использует отдельный эталон в `tests/fixtures/`.

## 📄 Лицензия и участие в проекте

Проект распространяется по [MIT License](LICENSE). Pull request'ы приветствуются; крупные изменения полезно предварительно обсудить в [Issues](https://github.com/tixset/MorseDecoder/issues). Инструкции по разработке и проверкам — в [CONTRIBUTING.md](CONTRIBUTING.md).

## 📞 Контакты

- **Автор:** Антон Зеленов
- **Email:** tixset@gmail.com
- **GitHub:** [tixset/MorseDecoder](https://github.com/tixset/MorseDecoder)

Разработано с ❤️ для радиолюбителей и специалистов радиосвязи.
