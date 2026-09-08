# Декодер азбуки Морзе из аудио 🎵→📝

**Русский** | [English](README.en.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-0078d4.svg)](https://github.com/tixset/MorseDecoder)
[![Language](https://img.shields.io/badge/Language-Python%203.9+-3776ab.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-1.1.0-blue)](https://github.com/tixset/MorseDecoder/releases)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](https://github.com/tixset/MorseDecoder)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[![GitHub Stars](https://img.shields.io/github/stars/tixset/MorseDecoder?style=social)](https://github.com/tixset/MorseDecoder/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/tixset/MorseDecoder?style=social)](https://github.com/tixset/MorseDecoder/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/tixset/MorseDecoder)](https://github.com/tixset/MorseDecoder/issues)
[![Last Commit](https://img.shields.io/github/last-commit/tixset/MorseDecoder)](https://github.com/tixset/MorseDecoder/commits)

Продвинутый инструмент для расшифровки аудио файлов с азбукой Морзе из радиоэфира с поддержкой процедурных команд, кодов и настраиваемых параметров.

## 🆕 ОБНОВЛЕНИЕ от 7 января 2026

- ⚡ **Оптимизация производительности**
  - LRU кэширование для fuzzy matching (ускорение в 3-5 раз)
  - Асинхронный поиск позывных через aiohttp (ускорение в 13 раз: 12с → 0.92с)
  - Numba JIT компиляция расстояния Левенштейна (326k операций/сек)
  
- 🏗️ **Рефакторинг структуры кода**
  - Создан [modules/code_dictionaries.py](modules/code_dictionaries.py) - централизованное хранилище всех кодов
  - Сокращён [modules/procedural_codes.py](modules/procedural_codes.py) с 1080 до 752 строк (30%)
  - Устранено дублирование констант между модулями
  
- 📚 **Полная инвентаризация кодов** - проверены все 18 словарей:
  - ✅ Q-коды (53), Z-коды (33), Y-коды (26), Щ-коды (3)
  - ✅ CW сокращения (25), Prosigns (11), морские коды (18)
  - ✅ Метеокоды (9), советские коды (12), SINPO (5)
  - ✅ Все коды успешно распознаются детектором

## 🎯 Основные возможности 2026

- ⭐ **Единый CLI интерфейс** ([morse_cli.py](morse_cli.py)) - одна команда для всех операций
- 📁 **Модульная структура** - все модули в папке [modules/](modules/)
- 🧪 **Универсальные тесты** ([run_tests.py](run_tests.py)) - автоматический запуск всех тестов
- 📡 **Поиск позывных** (--lookup) - автоматический поиск через 4 API источника
- 🎨 **Расширенный формат TXT** - 8 блоков с подробной информацией
- ⚡ **Быстрый режим** (--fast) - оптимальные параметры без перебора
- 🔬 **Экспериментальный режим** - автоматический поиск лучших параметров
- 📊 **Детальные отчёты:**
  - [docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md) - руководство по morse_cli.py
  - [docs/SUPPORTED_CODES.md](docs/SUPPORTED_CODES.md) - полный список поддерживаемых кодов (280+)
  - [docs/MULTI_SIGNAL_DECODING.md](docs/MULTI_SIGNAL_DECODING.md) - документация multi-signal режима

**Главный вывод экспериментов:** При работе с реальными WebSDR записями Q/Z-коды не обнаружены (0/40 экспериментов) из-за высокого уровня помех. Найдены только простые процедурные коды "Р" (6×) и "ДЕ" (2×).

## ✨ Основные возможности

### Базовые функции
- ✅ Обработка шумных аудио записей
- ✅ Автоматическая адаптация к разной скорости передачи (2-100 WPM)
- ✅ Поддержка английского и русского языков
- ✅ Фильтрация помех и шумов (полосовой фильтр 400-1200 Гц)
- ✅ Пакетная обработка файлов с параллельным выполнением
- ✅ Поддержка форматов: WAV, MP3, OGG (конвертация через FFmpeg)

### Процедурные коды и радиограммы
- ✅ Распознавание **Q-кодов** (QRZ, QTH, QSL, и др.)
- ✅ Распознавание **Z-кодов** (советские процедурные команды)
- ✅ Обнаружение **процедурных знаков** (Prosigns): AR, SK, BT, K, HH
- ✅ Извлечение полей **CHECK** и **NR** (номер сообщения)
- ✅ Анализ структуры радиограмм
- ✅ Детектирование позывных
- ✅ Определение уровня срочности

### Новые возможности (2026)
- 🎚️ **GUI с ползунками** для настройки параметров в реальном времени
- 📊 **Экспорт в JSON/CSV** для анализа результатов
- ⚙️ **Настраиваемые percentile пороги** (без изменения кода)
- ⚡ **Параллельная обработка** файлов (ускорение в 3-4 раза)
- 🧹 **Автоочистка** временных WAV файлов
- 📈 **WPM статистика** (слова в минуту)
- 🛡️ **Улучшенная обработка ошибок** с детальными сообщениями
- 📡 **Callsign Lookup System:**
  - 4 API источника (HamQTH, RadioQTH, QRZ.RU, APRS.fi)
  - Автоматическая транслитерация кириллицы
  - Кэширование результатов (7 дней)
  - Batch обработка с задержкой между запросами

## 🚀 Быстрый старт

### Новый единый CLI (рекомендуется)

```bash
# Активировать окружение
.venv\Scripts\activate

# Обработать один файл (быстрый режим - по умолчанию)
python morse_cli.py auto "файл.wav"

# С поиском позывных
python morse_cli.py auto "файл.wav" --lookup-callsigns

# Обработать с поиском позывных в интернете
python morse_cli.py auto "файл.wav" --lookup-callsigns

# Тщательный режим обработки
python morse_cli.py auto "файл.wav" --mode thorough

# Комбинированный: thorough + lookup
python morse_cli.py auto "файл.wav" --mode thorough --lookup-callsigns

# Обработать всю папку
python morse_cli.py batch TrainingData

# Batch с многопоточностью
python morse_cli.py batch TrainingData --workers 4

# Batch с lookup всех позывных
python morse_cli.py batch TrainingData --lookup-callsigns

# Декодирование с параметрами из .config.json
python morse_cli.py decode "файл.wav"
python morse_cli.py decode "файл.wav" --config custom.config.json
python morse_cli.py decode "файл.wav" --analyze

# Экспериментальный поиск лучших параметров
python morse_cli.py experiment "файл.wav" --iterations 50

# Справка
python morse_cli.py --help
```

Сообщения CLI и справка выводятся на английском по умолчанию. Для русского
языка добавьте `--ru` перед командой или после её аргументов:

```bash
python morse_cli.py auto recording.wav --ru
python morse_cli.py --ru batch TrainingData
python morse_cli.py decode --help --ru
```

Переключатель меняет язык сообщений консоли; расшифрованный текст и формат
сохраняемых отчётов остаются прежними.

### Альтернативные способы

#### Установка

```bash
# Клонируйте репозиторий
git clone https://github.com/tixset/MorseDecoder.git
cd morseDecoder

# Создайте виртуальное окружение
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # Linux/Mac

# Установите зависимости
pip install -r requirements.txt
```

Для MP3 и OGG необходим **FFmpeg**, доступный в `PATH`. Например, в Debian/Ubuntu:

```bash
sudo apt install ffmpeg
python morse_cli.py auto recording.mp3
```

Сжатый файл автоматически преобразуется во временный WAV; после обработки
временный файл удаляется. Отчёты `.txt` и `.config.json` сохраняются рядом
с исходным аудио. Команда `batch` по-прежнему выбирает WAV-файлы.

Если появляется предупреждение о несовместимых версиях NumPy и SciPy,
установите зависимости в отдельное виртуальное окружение:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```


#### Альтернативные способы запуска

```bash
# GUI для настройки параметров
python morse_tuner_gui.py
```

#### Программное использование

```python
from morse_decoder import MorseDecoder

# Настраиваемые параметры
decoder = MorseDecoder(
    sample_rate=8000,
    pulse_percentile=85,         # Порог импульсов (70-95)
    gap_percentile_dot_dash=62,  # Разделение точек/тире (50-70)
    gap_percentile_char=90,      # Разделение символов (85-95)
    gap_percentile_word=92       # Разделение слов (90-98)
)

text_en, text_ru, stats = decoder.process_file('audio.wav')

print(f"Скорость: {stats['wpm']} WPM")
print(f"Английский: {text_en}")
print(f"Русский: {text_ru}")
```

## Как это работает

1. **Загрузка аудио** - чтение WAV файла и преобразование в моно
2. **Полосовая фильтрация** - удаление шумов вне частотного диапазона Морзе (400-1200 Гц)
3. **Детектирование огибающей** - выделение амплитудной огибающей сигнала
4. **Детектирование импульсов** - определение начала и конца каждого сигнала
5. **Классификация** - разделение на точки и тире на основе длительности
6. **Группировка** - объединение в буквы и слова по паузам
7. **Декодирование** - преобразование морзе-кода в текст

## Структура проекта

### Основные скрипты

- **morse_cli.py** ⭐ - единый CLI интерфейс (auto/batch/decode/procedural/experiment)
- **morse_tuner_gui.py** - GUI с ползунками для ручной настройки
- **run_tests.py** - универсальный запуск всех тестов

### Утилиты (tools/)

- **convert_mp3_to_wav.py** - конвертация MP3 → WAV (8kHz mono)

### Модули (modules/)

- **morse_decoder.py** - основной класс декодера
- **procedural_codes.py** - детекция процедурных кодов (Q/Z-коды, prosigns)
- **callsign_lookup.py** - поиск информации о позывных через API
- **auto_tune.py** - автонастройка параметров
- **analyze_codes.py** - анализ найденных кодов
- **fuzzy_matcher.py** - нечёткое сопоставление кодов

### Структура файлов

```
morseDecoder/
├── morse_cli.py                       # ⭐ Единый CLI интерфейс
├── morse_tuner_gui.py                 # GUI с настройками
├── run_tests.py                       # Универсальный тестер
├── requirements.txt                   # Зависимости
├── LICENSE                            # MIT License
├── CHANGELOG.md                       # История изменений
├── CONTRIBUTING.md                    # Руководство для контрибьюторов
├── modules/                           # Модули декодера
│   ├── morse_decoder.py               # Основной декодер
│   ├── signal_analyzer.py             # Анализ сигналов
│   ├── multi_signal_decoder.py        # Multi-signal декодирование
│   ├── procedural_codes.py            # Детектор кодов (752 строки)
│   ├── code_dictionaries.py           # ⭐ Словари кодов (440 строк, 18 словарей)
│   ├── callsign_lookup.py             # Поиск позывных (sync)
│   ├── callsign_lookup_async.py       # ⚡ Асинхронный поиск (13x быстрее)
│   ├── auto_tune.py                   # Автонастройка
│   ├── analyze_codes.py               # Анализ кодов
│   ├── fuzzy_matcher.py               # Нечёткое сопоставление (с LRU cache)
│   └── levenshtein_optimized.py       # ⚡ Numba-оптимизированный Левенштейн
├── docs/                              # ⭐ Документация
│   ├── USAGE_GUIDE.md                 # Руководство morse_cli.py
│   ├── SUPPORTED_CODES.md             # Список кодов (280+)
│   └── MULTI_SIGNAL_DECODING.md       # Multi-signal документация
├── tools/                             # Утилиты
│   └── convert_mp3_to_wav.py          # MP3→WAV конвертер
├── tests/                             # Тестовые скрипты
└── TrainingData/                      # Тестовые аудио
```

## Поддерживаемые символы

### Английский алфавит
A-Z, 0-9, знаки препинания (. , ? ' ! / ( ) & : ; = + - _ " $ @)

### Русский алфавит  
А-Я, 0-9, знаки препинания (. , ? ' ! / ( ) : ; =)

### Процедурные коды

#### Q-коды (международные)
- QSL - Подтверждаю прием
- QTH - Ваше местоположение?
- QRZ - Кто меня вызывает?
- QRM - Помехи от других станций
- QRN - Атмосферные помехи
- И другие...

#### Z-коды (процедурные, ACP-131)
- ZAA - Вы не соблюдаете дисциплину в эфире
- ZAB - Ваш ключ скорости неправильно настроен
- ZAG - Прервать...
- ZAK - Передача прервана в...
- ZRP - Вернитесь к автоматической ретрансляции
- И другие...

#### CW-сокращения
- RPT - Повторите
- DE - От (from)
- SK - Конец контакта
- AR - Конец сообщения
- CQ - Общий вызов
- И другие...

Полный справочник см. в [docs/SUPPORTED_CODES.md](docs/SUPPORTED_CODES.md)

## 📚 Дополнительная документация

- **[docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md)** - Подробное руководство по morse_cli.py
- **[docs/SUPPORTED_CODES.md](docs/SUPPORTED_CODES.md)** - Полный список поддерживаемых кодов (280+)
- **[docs/MULTI_SIGNAL_DECODING.md](docs/MULTI_SIGNAL_DECODING.md)** - Документация multi-signal режима

## ⚠️ Troubleshooting

**Проблема**: Импульсы не обнаружены  
**Решение**: Используйте GUI (`morse_tuner_gui.py`) для настройки percentile параметров

**Проблема**: Неправильное распознавание  
**Решение**: Попробуйте изменить пороги через ползунки в GUI или параметры декодера

**Проблема**: Много символов "□"  
**Решение**: Проверьте качество аудио и настройте частотный диапазон (400-1200 Гц)

## 📝 Примечания

### Понимание результатов расшифровки

- **Символ '□' (белый квадрат)** - нераспознанный символ морзе
  - Появляется когда декодер встречает неизвестную комбинацию точек/тире
  - Может означать сильные помехи или искаженный сигнал
  
- **Символ '?' (знак вопроса)** - настоящий знак вопроса в морзе
  - Код морзе: `··--··` (..--.. в программе)
  - Это НАСТОЯЩИЙ символ, переданный оператором
  - Не путать с ошибкой распознавания!

**Пример:**
```
QRZ? DE IM4TET K □ TEST
     ↑              ↑
настоящий ?    ошибка □
```

### Общие рекомендации

- Качество расшифровки зависит от чистоты исходного сигнала
- Для лучших результатов используйте записи с четким сигналом и минимальным шумом
- Декодер автоматически адаптируется к скорости передачи (поддержка 5-40 WPM)
- Поддержка форматов: WAV, MP3, OGG (автоконвертация через FFmpeg)

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE)

## 🤝 Вклад в проект

Приветствуются pull request'ы! Для крупных изменений сначала откройте issue для обсуждения.

Подробнее см. [CONTRIBUTING.md](CONTRIBUTING.md)

## 📞 Контакты

- **Автор:** Антон Зеленов
- **Email:** tixset@gmail.com
- **GitHub:** https://github.com/tixset/MorseDecoder

---

**Разработано с ❤️ для радиолюбителей и специалистов радиосвязи**


### Оценки результата

`Heuristic score` — внутренние баллы для сравнения проверенных параметров,
а не процент точности. Доля символов без `□` также не подтверждает правильность
расшифровки. Позывные, найденные по шаблону, выводятся как кандидаты.

Скорость WPM оценивается по длительности точки и соотношению точек/тире 1:3.
При недостаточных или нестабильных данных скорость отмечается как неизвестная.
При помехах или ненадёжном выделении импульсов уровень оператора не определяется.

### Декодирование записей с шумом

В режиме `auto` программа ищет доминирующий тон в диапазоне 250–3000 Гц,
выделяет узкую полосу вокруг него и сглаживает огибающую. Два порога
переключения, объединение разрывов короче 10 мс и отсечение импульсов короче
15 мс уменьшают дробление точек и тире из-за шума. Длительности импульсов и
пауз определяют символы, без словаря ожидаемых фраз.

В JSON сохраняется `auto_frequency`, чтобы команда `decode` использовала тот
же способ обработки. Для программного использования фиксированной полосы
задайте `MorseDecoder(auto_frequency=False, min_freq=400, max_freq=800)`.
Команда `multi` сохраняет отдельные частотные диапазоны сигналов.

Контрольная запись с пользовательским эталоном находится в `tests/fixtures/`.
Точная расшифровка одной записи не гарантирует точность на любой другой:
наложенные сигналы, сильные замирания и очень быстрый CW могут оставлять ошибки.
