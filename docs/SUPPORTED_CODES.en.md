# Supported Codes and Characters in Morse Decoder

[Русский](SUPPORTED_CODES.md) | **English** | [README](../README.en.md)

**Updated:** January 6, 2026\
**Version:** 2.0

This translates the January 2026 reference, including its historical counts and examples. Current definitions are in [modules/code_dictionaries.py](../modules/code_dictionaries.py); the counts in the older reference and release notes differ. Fuzzy matching must be enabled explicitly in the detector. Cyrillic codes and Russian phonetic words below are intentionally preserved as data.

---

## 📋 Overview

The decoder includes a large collection of international and Russian procedural codes used in radio communication. Code detection supports fuzzy matching to compensate for decoding errors.

**Total support stated in this reference:** 250+ codes and characters

---

## 📡 Q Codes (International, ITU-R M.1172)

**Count:** 60+ codes\
**Purpose:** International radio codes that simplify communication

### Main Q Codes

| Code | Meaning |
|-----|----------|
| QSL | Reception confirmed |
| QTH | Your location? |
| QRZ | Who is calling me? |
| QRM | Interference from other stations |
| QRN | Atmospheric interference |
| QRV | Ready to receive |
| QRT | Stopping transmission |
| QRX | Stand by |
| QSB | Signal fading |
| QSO | Contact with... |
| QSY | Switch to another frequency |
| QTR | Exact time |
| QRA | Your station name |
| QRG | My exact frequency |
| QRK | Signal readability (1-5) |
| QRL | Is the channel busy? |
| QRQ | Send faster |
| QRS | Send more slowly |
| QRU | Any messages for me? |
| QSA | Signal strength (1-5) |
| QSP | Relay to... |
| QSX | Listening on frequency... |
| QSZ | Send each word twice |
| QTC | Number of messages |

### Additional Q Codes

| Code | Meaning |
|-----|----------|
| QRO | Increase transmitter power |
| QRP | Reduce power (<10W) |
| QSD | Defective telegraphy |
| QSK | Can I hear between my signals? |
| QFE | Airfield-level pressure |
| QNH | Sea-level pressure |
| QTF | Your position by bearing |
| QUA | Any news of...? |
| QUM | Resume normal operation |

**Full list:** this historical reference lists 60+ codes. See [code dictionaries](../modules/code_dictionaries.py) and the [detector](../modules/procedural_codes.py) for current definitions.

---

## ✈️ Y Codes (Aviation Procedural Codes)

**Count:** 26 codes\
**Purpose:** Aviation radio communication and dispatch control

| Code | Meaning |
|-----|----------|
| YAA | Unable to comply with instructions |
| YBB | Following instructions |
| YCC | Receipt and understanding confirmed |
| YDD | Dispatch control |
| YEE | Execute immediately |
| YFF | Flight conditions |
| YGG | Weather conditions |
| YII | Identification required |
| YKK | Maintain radio silence |
| YLL | Landing cleared |
| YMM | Medical assistance required |
| YNN | Navigation assistance |
| YSS | Search and rescue operation |
| YUU | Urgent message |
| YWW | Warning |
| YYY | Yes/confirmed |

---

## 🎖️ Z Codes (Procedural Signals, ACP-131)

**Count:** 29 codes\
**Purpose:** Procedural radio commands

| Code | Meaning |
|-----|----------|
| ZAA | You are not observing radio discipline |
| ZAB | Your keying speed is incorrectly set |
| ZAC | Transmitting on frequency... |
| ZAE | Cannot receive you |
| ZAG | Interrupt transmission |
| ZAM | Transmitting blind |
| ZAN | Cannot read you |
| ZAP | Increase power |
| ZAQ | Reduce power |
| ZAS | Switch to frequency... |
| ZBK | Receiving my automatic transmission? |
| ZNB | No breaks / Breaks |
| ZUA | Time request |
| ZUG | Your signal is distorted |
| ZVA | Procedural priority (1-5) |

---

## 🔧 Prosigns (Procedural Signs)

**Count:** 12 signs\
**Purpose:** Special signals used to control a transmission

| Code | Morse | Meaning |
|-----|-------|----------|
| AR | •-•-• | End of transmission |
| SK | •••-•- | End of contact |
| BT | -•••- | Separator |
| K | -•- | Transmitting |
| KN | -•--• | Only you |
| AS | •-••• | Stand by |
| CT | -•-•- | Start of transmission |
| HH | •••••••• | Error |
| SN | •••-• | Understood |
| VA | •••-•- | End of work |
| R | •-• | Understood/received |
| INT | ••-• | Question |

---

## 📝 CW Abbreviations (Amateur Radio)

**Count:** 25 codes\
**Purpose:** Common abbreviations used in CW communication

| Code | Meaning |
|-----|----------|
| CQ | General call |
| DE | From |
| TNX/TU | Thank you |
| UR | Your |
| PSE | Please |
| FB | Excellent (Fine Business) |
| OM | Old friend (Old Man) |
| YL | Young lady (Young Lady) |
| GA/GE/GM/GN | Greetings (afternoon/evening/morning/night) |
| WX | Weather |
| HW | How |
| CPY | Copy |
| CFM | Confirmed |
| NIL | Nothing |
| MSG | Message |
| NR | Number |
| INFO | Information |
| RPT | Repeat |

---

## 🇷🇺 Russian Shch Codes

**Count:** 3 codes\
**Purpose:** Russian procedural codes

| Code | Meaning |
|-----|----------|
| ЩРТ | Stop transmitting |
| ЩРЩ | Send faster |
| ЩСА | What is my signal strength? |

---

## 📋 Russian Procedural Abbreviations

**Count:** 7 codes\
**Purpose:** Traditional Russian radio abbreviations

| Code | Meaning |
|-----|----------|
| РПТ | Repeat |
| АЛ | All just transmitted |
| Р | Received |
| Ц | Yes |
| НВ | Starting transmission |
| АС | Wait |
| ДЕ | From |

---

## 🚩 Soviet Procedural Codes

**Count:** 12 codes\
**Purpose:** Codes used in Soviet radiograms

| Code | Meaning |
|-----|----------|
| ПРМ | Receiving |
| ПРД | Transmitting |
| КНЦ | End |
| ВСЁ | All transmitted |
| ПНЛ | Understood |
| НЕ ПНЛ | Not understood |
| РПТ | Repeat |
| ВЫЗОВ | Call |
| ОТВЕТ | Reply |
| СРОЧНО | Urgent telegram |
| ШИФР | Encrypted message |
| ОТКРЫТО | Plain text |

---

## ⚓ INTERCO Maritime Codes

**Count:** 16 codes\
**Purpose:** International code of signals for maritime vessels

| Code | Meaning |
|-----|----------|
| AA | All vessels leave the area |
| AB | You must leave the area |
| AC | I am leaving the area |
| AD | In distress |
| AE | Must abandon ship |
| CP | I/the vessel am/is proceeding to you |
| DX | Sinking vessel |
| EL | Repeat the signal |
| NC | In distress, assistance required |
| RY | You must act according to the code |
| SO | You should stop |
| SS | I/the vessel have/has stopped |
| ZL | Your signal received but not understood |
| ZN | No (negative) |
| ZO | Yes (affirmative) |

---

## 🌦️ Weather Codes

**Count:** 9 codes\
**Purpose:** Codes for transmitting weather data

| Code | Meaning |
|-----|----------|
| WX | Weather |
| TEMP | Temperature |
| WIND | Wind |
| VIS | Visibility |
| PRESS | Pressure |
| CLOUD | Cloud cover |
| RAIN | Rain |
| SNOW | Snow |
| FOG | Fog |

---

## 📊 SINPO Codes (Signal Quality Rating)

**Count:** 5 parameters\
**Purpose:** A radio signal rating system using scores from 1 to 5

| Parameter | Description |
|----------|----------|
| S | Signal strength |
| I | Interference from other stations |
| N | Noise (atmospheric noise) |
| P | Propagation/fading |
| O | Overall rating |

**Example:** SINPO 54554 (excellent signal quality)

---

## ⚠️ Priority Levels (Russian)

**Count:** 4 levels\
**Purpose:** Message priority classification

| Level | Meaning |
|---------|----------|
| SAMOLET | Low priority |
| MOLNIYA | Medium priority |
| VSPYSHKA | High priority |
| AVIA | Emergency |

---

## 🚨 Service Signals

**Count:** 4 signals\
**Purpose:** Distress and urgency signals

| Signal | Meaning |
|--------|----------|
| SOS | Distress signal (•••---•••) |
| MAYDAY | Distress (voice) |
| PAN | Urgency |
| SECURITY | Safety |

---

## 🔤 Phonetic Alphabets

### International Phonetic Alphabet (ICAO/ITU)

**Count:** 26 letters + 10 digits

| Letter | Word | Digit | Word |
|-------|-------|-------|-------|
| A | Alfa | 0 | Zero |
| B | Bravo | 1 | One |
| C | Charlie | 2 | Two |
| D | Delta | 3 | Three |
| E | Echo | 4 | Four |
| F | Foxtrot | 5 | Five |
| G | Golf | 6 | Six |
| H | Hotel | 7 | Seven |
| I | India | 8 | Eight |
| J | Juliett | 9 | Niner |
| K | Kilo | | |
| L | Lima | | |
| M | Mike | | |
| N | November | | |
| O | Oscar | | |
| P | Papa | | |
| Q | Quebec | | |
| R | Romeo | | |
| S | Sierra | | |
| T | Tango | | |
| U | Uniform | | |
| V | Victor | | |
| W | Whiskey | | |
| X | X-ray | | |
| Y | Yankee | | |
| Z | Zulu | | |

### Russian Phonetic Alphabet

**Count:** 33 letters

| Letter | Word | Letter | Word |
|-------|-------|-------|-------|
| А | Анна | П | Павел |
| Б | Борис | Р | Роман |
| В | Василий | С | Семён |
| Г | Григорий | Т | Татьяна |
| Д | Дмитрий | У | Ульяна |
| Е | Елена | Ф | Фёдор |
| Ж | Женя | Х | Харитон |
| З | Зинаида | Ц | Цапля |
| И | Иван | Ч | Человек |
| Й | Иван краткий | Ш | Шура |
| К | Константин | Щ | Щука |
| Л | Леонид | Ы | Еры |
| М | Михаил | Ь | Мягкий знак |
| Н | Николай | Э | Эхо |
| О | Ольга | Ю | Юрий |
| | | Я | Яков |

---

## 📈 Support Statistics

| Category | Count |
|-----------|------------|
| Q codes | 60+ |
| Y codes | 26 |
| Z codes | 29 |
| Prosigns | 12 |
| CW abbreviations | 25 |
| Russian Shch codes | 3 |
| Russian abbreviations | 7 |
| Soviet codes | 12 |
| INTERCO maritime codes | 16 |
| Weather codes | 9 |
| SINPO parameters | 5 |
| Priority levels | 4 |
| Service signals | 4 |
| International phonetic alphabet | 36 |
| Russian phonetic alphabet | 33 |
| **TOTAL** | **280+** |

---

## 🔍 Recognition Features

### Fuzzy Matching

The detector can use fuzzy matching to compensate for decoding errors:
- Allows one or two errors in a code.
- Takes message context into account.
- Computes a confidence level.

**Examples from the original reference:**
- `QRZ` may be recognized from `QR?`, `?RZ`, or `QBZ`.
- `SK` may be recognized from `S?` or `?K`.

### Language Handling

The original reference describes analyzing English and Russian renderings and choosing the one with fewer errors. Current automatic tuning selects its working text by length, with Russian chosen on a tie, and uses the English rendering for code analysis. Neither method verifies the language semantically.

### Structural Analysis

The presence of characteristic codes is used to classify a message:
- **Procedural command**: contains Z/Y codes.
- **Operational message**: contains Q codes.
- **Emergency**: contains SOS or MAYDAY.
- **General communication**: contains callsigns and prosigns.

---

## 📚 Sources and Standards

- **ITU-R M.1172**: international Q codes.
- **ACP-131**: procedural communication signals (Z codes).
- **ICAO Annex 10**: aeronautical telecommunications.
- **IMO INTERCO**: International Code of Signals.
- **Russian radio communication standards**: Shch codes and procedures.

---

## 🔧 Python Usage

```python
from modules.procedural_codes import ProceduralCodeDetector

# Create a detector with fuzzy matching enabled
detector = ProceduralCodeDetector(use_fuzzy_matching=True, max_errors=1)

# Analyze the text
detected = detector.detect_codes("CQ CQ DE R1ABC QRZ K")

# Display the analysis in English
print(detector.format_analysis(detected, language='en'))
```

**Illustrative output translated from the original reference:**
```
======================================================================
PROCEDURAL CODE AND COMMAND ANALYSIS
======================================================================

📋 MESSAGE STRUCTURE:
   Type: General communication
   Has start: ✓
   Has end: ✗
   Has callsigns: ✓

📡 DETECTED CALLSIGNS:
   • R1ABC

🔧 PROCEDURAL SIGNS (PROSIGNS):
   • K — Transmitting (-•-)

🔤 Q CODES (International):
   • QRZ — Who is calling me?

📝 CW ABBREVIATIONS:
   • CQ — General call
   • DE — From
```

---

## 📄 Update History

### v2.0 (06.01.2026)
- Expanded the Q code list: 31 → 60+.
- Added Y codes (26 aviation codes).
- Added the international phonetic alphabet (36 characters).
- Added INTERCO maritime codes (16 codes).
- Added weather codes (9 codes).
- Added SINPO codes (5 parameters).
- Added Soviet procedural codes (12 codes).
- Replaced "military" with "procedural" throughout the descriptions.

### v1.0 (05.01.2026)
- Basic Q code support (31).
- Z codes (29).
- ✅ Prosigns (12)
- CW abbreviations (25).
- Russian codes (10).
- Fuzzy matching.

---

The original inventory summarizes support as **280+ codes** across **14 categories**, with automatic recognition and fuzzy matching.
