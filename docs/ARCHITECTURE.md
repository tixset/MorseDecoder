# 🏗️ Структура проекта и разработка

[![Русский](https://img.shields.io/badge/Language-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-blue)](ARCHITECTURE.md) [![English](https://img.shields.io/badge/Language-English-lightgrey)](ARCHITECTURE.en.md)

[README](../README.md) · [Участие в разработке](../CONTRIBUTING.md)

## 📁 Расположение файлов

| Путь | Назначение |
| --- | --- |
| `morse_cli.py` | Общая точка входа CLI |
| `morse_tuner_gui.py` | Tkinter GUI: выбор записи, настройка порогов, EN/RU-текст |
| `run_all_tests.py` | Обнаружение unittest-тестов и сохранение отчёта |
| `requirements.txt` | Python-зависимости |
| `modules/` | Импортируемая реализация |
| `tools/convert_mp3_to_wav.py` | Пакетная конвертация MP3 в WAV |
| `tests/` | Автоматические тесты и демонстрации процедурных кодов |
| `tests/fixtures/` | Шумная запись и JSON с эталонной расшифровкой |
| `docs/` | Руководства на русском и английском |
| `.github/ISSUE_TEMPLATE/` | Шаблоны ошибок и предложений на двух языках |
| `.github/PULL_REQUEST_TEMPLATE.md` | Основной шаблон PR на русском |
| `.github/PULL_REQUEST_TEMPLATE/english.md` | Английский шаблон PR |
| `README*`, `CONTRIBUTING*`, `CHANGELOG*`, `LICENSE` | Введение, разработка, история, лицензия |

Пользовательские записи, `TrainingData/`, `reports/`, `callsign_cache/`, конфиги и результаты создаются локально и исключены из Git. Эти папки не нужны для чистой установки. Эталонный MP3 в `tests/fixtures/` — явное исключение в `.gitignore`. Файлы окружения `.venv/`, `__pycache__/` также не входят в репозиторий.

## ⚙️ Модули и поток данных

1. `audio_input.py` готовит WAV, запускает FFmpeg для MP3/OGG и удаляет временные файлы.
2. `morse_decoder.py` загружает сигнал и координирует обработку. `cw_frontend.py` ищет несущую (250–3000 Гц), фильтрует её узкую полосу и выделяет огибающую/импульсы.
3. `morse_timing.py` оценивает длительности точек/тире и надёжность; декодер собирает символы и текст в обоих алфавитах.
4. `auto_tune.py` сравнивает варианты параметров и записывает отчёт/конфиг. `multi_signal_decoder.py` обрабатывает фиксированные полосы отдельно.
5. `signal_analyzer.py` вычисляет эвристические характеристики сигнала. `procedural_codes.py` ищет коды в тексте по `code_dictionaries.py`; `fuzzy_matcher.py` и `levenshtein_optimized.py` обеспечивают нечёткий поиск.
6. `callsign_lookup.py` и `callsign_lookup_async.py` реализуют сетевые справочники. `analyze_codes.py` агрегирует ранее сохранённые расшифровки.
7. `console_i18n.py` и обязательный ресурс `console_en.json` переводят консоль CLI; русские исходные строки остаются в коде. `modules/__init__.py` экспортирует основные классы и функции.

## 🔧 Вспомогательные инструменты

```bash
python morse_tuner_gui.py
python tools/convert_mp3_to_wav.py recordings --output wav_recordings --max-files 10
```

GUI позволяет открыть файл и менять пороги с повторным декодированием; отдельной кнопки сохранения конфигурации нет. Для воспроизводимого конфига используйте `auto`.

Конвертер создаёт моно WAV 8000 Гц, пропускает существующие WAV, по умолчанию читает `TrainingData/`. Для MP3 требуется FFmpeg даже при использовании pydub. Импорт pydub необязателен: при его ошибке утилита пробует FFmpeg напрямую.

Старый агрегатор можно вызвать из Python:

```python
from modules.analyze_codes import analyze_all_decodings
analyze_all_decodings()
```

Он читает `TrainingData/*.txt` и пишет `code_analysis_results.json` в рабочую папку. Это инструмент для старых текстовых отчётов, а не универсальный парсер произвольной схемы; для нового кода передавайте чистый декодированный текст напрямую в `ProceduralCodeDetector`.

## 🧪 Проверка изменений

Следуйте [инструкциям для разработчиков](../CONTRIBUTING.md). Не меняйте пользовательский эталон ради прохождения тестов. Исправления обработки шумов проверяйте также на чистом CW, тишине, постоянном тоне и помехах. Совпадение с одной записью не гарантирует корректности других.
