# 🔤 Supported codes and symbols

[![Русский](https://img.shields.io/badge/Language-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-lightgrey)](SUPPORTED_CODES.md) [![English](https://img.shields.io/badge/Language-English-blue)](SUPPORTED_CODES.en.md)

[CLI guide](USAGE_GUIDE.en.md) · [README](../README.en.md)

## 📋 What support means

The following lists the actual dictionaries in [code_dictionaries.py](../modules/code_dictionaries.py), not verified compliance with international or departmental standards. Meanings come from the project; their applicability depends on context. A short word matching a dictionary does not establish that a command was transmitted.

The audio decoder converts CW into text; `ProceduralCodeDetector` separately searches decoded text. By default it matches exact words after uppercasing and splitting on whitespace. Attached punctuation can prevent a match. Fuzzy matching is **disabled** by default; the API can enable it, but this increases false positives.

## 🇷🇺 Getting Russian abbreviations

The CLI has no switch to force complete Russian analysis. `--ru` translates console messages, `auto` analyzes codes in EN, and `decode --analyze` only adds brief counts without guaranteeing selection of Russian text. `auto --analyze` does not exist.

To reliably retrieve dictionary explanations from Russian text:

```python
from modules.procedural_codes import ProceduralCodeDetector

detector = ProceduralCodeDetector()
result = detector.detect_codes("РПТ АЛ")
for item in result["ru_procedural_abbr"]:
    print(item["code"], "—", item["meaning"])
```

Output (meanings are stored in Russian):

```text
РПТ — Повторите
АЛ — Всё, что только передано
```

These mean “Repeat” and “All just transmitted”. To obtain text from a recording, tune its parameters first. This call also saves TXT and configuration files beside the audio:

```python
from modules.auto_tune import auto_tune_parameters
from modules.procedural_codes import ProceduralCodeDetector

decoded = auto_tune_parameters("tests/fixtures/noisy_cw.mp3", mode="fast")
if decoded is None:
    raise RuntimeError("Decoding failed")
detector = ProceduralCodeDetector()
result = detector.detect_codes(decoded["text_ru"])
print(result["ru_procedural_abbr"])
```

Result fields include `q_codes`, `y_codes`, `z_codes`, `shch_codes`, `ru_procedural_abbr`, `soviet_codes`, `cw_abbreviations`, `prosigns`, `sinpo_codes`, `maritime_codes`, `meteo_codes`, `service_signals`, `urgency_level`, `callsigns`, `message_structure`, `check_field`, and `message_number`. Service signals use `signal` instead of the usual `code` key. `CHECK N` and `NR N` are extracted separately. Dictionary results have Russian `meaning` values; request a formatted report with `detector.format_analysis(result, language="en")`, but use the result dictionary for full category access.

To enable fuzzy matching, create `ProceduralCodeDetector(use_fuzzy_matching=True, max_errors=1)`. Its matches and some entry structures differ from exact mode; these are guesses about similar codes rather than verified text recovery.

## 📊 Dictionary inventory

Counts are the number of keys in each dictionary. Do not sum them as unique automatically detected commands: categories overlap, and phonetic alphabets and RST are helper data rather than separate `detect_codes` result categories. Codes and Russian phonetic words are preserved untranslated in both versions.

| Dictionary | Entries |
| --- | ---: |
| `Q_CODES` | 53 |
| `Y_CODES` | 26 |
| `Z_CODES` | 33 |
| `CW_ABBREVIATIONS` | 25 |
| `PROSIGNS` | 11 |
| `SHCH_CODES` | 3 |
| `RU_PROCEDURAL_ABBR` | 7 |
| `SINPO_CODES` | 5 |
| `MARITIME_CODES` | 18 |
| `SOVIET_CODES` | 12 |
| `METEO_CODES` | 9 |
| `URGENCY_LEVELS` | 4 |
| `SERVICE_SIGNALS` | 4 |
| `RST_CODES` | 1 |
| `INTERNATIONAL_PHONETIC` | 36 |
| `RUSSIAN_PHONETIC` | 31 |

Additionally, `DXCC_PREFIX_MAP` (58 keys) and `MORSE_RU_TO_LATIN_CALLSIGN` (31) support callsign lookup and rendering.

## 📡 Q codes

`Q_CODES` · 53

| Code | Meaning |
| --- | --- |
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
| QRW | Tell ... that I am calling |
| QSA | Signal strength (1-5) |
| QSP | Relay to... |
| QSX | Listening on frequency... |
| QSZ | Send each word twice |
| QTC | Number of messages |
| QTU | Station operating hours |
| QFE | Atmospheric pressure at airfield level |
| QNH | Sea-level pressure |
| QTF | Your position by bearing |
| QRO | Increase transmitter power |
| QRP | Reduce transmitter power (also: low power <10W) |
| QRH | Is the frequency varying? |
| QRI | Tone of my signal |
| QRJ | How many voice calls? |
| QRY | What is my turn? |
| QSD | Defective telegraphy |
| QSG | Send several telegrams |
| QSK | Can I hear between my signals? |
| QSM | Repeat the last telegram |
| QSN | Did you hear me on ... (frequency)? |
| QSU | Transmit on this frequency |
| QSV | Transmit a series of V characters |
| QSW | Transmit on ... (frequency) |
| QTA | Cancel telegram number... |
| QTB | Do you agree with my word count? |
| QTV | Keep watch on ... (frequency) |
| QTX | Stay in contact with me |
| QUA | Any news of...? |
| QUC | Last received telegram number... |
| QUD | Did you receive the urgency signal? |
| QUE | Can you speak ... (language)? |
| QUF | Distress signal received from... |
| QUM | Resume normal operation |

## ✈️ Y codes

`Y_CODES` · 26

| Code | Meaning |
| --- | --- |
| YAA | Unable to comply with instructions |
| YBB | Following instructions |
| YCC | Receipt and understanding confirmed |
| YDD | Dispatch control |
| YEE | Execute immediately |
| YFF | Flight conditions |
| YGG | Weather conditions |
| YHH | Hold position |
| YII | Identification required |
| YJJ | Join the formation |
| YKK | Maintain radio silence |
| YLL | Landing cleared |
| YMM | Medical assistance required |
| YNN | Navigation assistance |
| YOO | Target interception |
| YPP | Patrolling |
| YQQ | Request permission |
| YRR | Return to base |
| YSS | Search and rescue operation |
| YTT | Tactical information |
| YUU | Urgent message |
| YVV | Visual contact |
| YWW | Warning |
| YXX | Execute special instructions |
| YYY | Yes/confirmed |
| YZZ | Area of operations |

## 🎖️ Z codes

`Z_CODES` · 33

| Code | Meaning |
| --- | --- |
| ZAA | You are not observing radio discipline |
| ZAB | Your keying speed is incorrectly set |
| ZAC | Transmitting on ... / What frequency are you receiving? |
| ZAD | Your signal received as ... (1-5) |
| ZAE | Cannot receive you |
| ZAF | Connecting you to... |
| ZAG | Interrupt / Interrupting transmission |
| ZAH | Cannot transmit the message |
| ZAI | Start (test) |
| ZAJ | Cannot break through to you |
| ZAK | Transmission interrupted at... |
| ZAL | Your frequency is varying |
| ZAM | Transmitting blind |
| ZAN | Cannot read you |
| ZAO | Hearing you weakly |
| ZAP | Increase power |
| ZAQ | Reduce power |
| ZAR | My callsign is... |
| ZAS | Switch to frequency... |
| ZAT | My calling designation is... |
| ZAU | Backup frequency... |
| ZAV | Will listen on... |
| ZAW | Switch to backup channel |
| ZAX | Listening on frequency... |
| ZBK | Receiving my automatic transmission? |
| ZBW | Switch to backup frequency number... |
| ZNB | No breaks / Breaks |
| ZRP | Return to automatic relay |
| ZUA | Time request |
| ZUG | Your signal is distorted |
| ZUJ | Send in groups of... |
| ZUP | Interference from... |
| ZVA | Military precedence (level 1-5) |

## 📝 CW abbreviations

`CW_ABBREVIATIONS` · 25

| Code | Meaning |
| --- | --- |
| RPT | Repeat |
| DE | From |
| FB | Excellent |
| SK | End of contact |
| AR | End of message |
| BT | Separator |
| CQ | General call |
| TNX | Thank you |
| TU | Thank you |
| UR | Your |
| OM | Old friend |
| YL | Young lady |
| GA | Good afternoon |
| GE | Good evening |
| GM | Good morning |
| GN | Good night |
| WX | Weather |
| HW | How |
| CPY | Copy |
| PSE | Please |
| CFM | Confirmed |
| NIL | Nothing |
| MSG | Message |
| NR | Number |
| INFO | Information |

## 🔧 Prosigns

`PROSIGNS` · 11

| Code | Meaning |
| --- | --- |
| AR | End of transmission (•-•-•) |
| SK | End of contact (•••-•-) |
| BT | Separator (-•••-) |
| KA | Starting transmission (-•-•-) |
| KN | Only you (-•--•) |
| AS | Stand by (•-•••) |
| CT | Start of transmission (-•-•-) |
| HH | Error (••••••••) |
| SN | Understood (•••-•) |
| VA | End of work (•••-•-) |
| INT | Question (••-•) |

## 🇷🇺 Shch codes

`SHCH_CODES` · 3

| Code | Meaning |
| --- | --- |
| ЩРТ | Stop transmitting |
| ЩРЩ | Send faster |
| ЩСА | What is my signal strength? |

## 📋 Russian procedural abbreviations

`RU_PROCEDURAL_ABBR` · 7

| Code | Meaning |
| --- | --- |
| РПТ | Repeat |
| АЛ | All just transmitted |
| Р | Received |
| Ц | Yes |
| НВ | Starting transmission |
| АС | Wait |
| ДЕ | From |

## 📊 SINPO

`SINPO_CODES` · 5

| Code | Meaning |
| --- | --- |
| S | Signal strength (1-5) |
| I | Interference (1-5) |
| N | Noise (atmospheric noise: 1-5) |
| P | Propagation (propagation/fading: 1-5) |
| O | Overall (overall rating: 1-5) |

## ⚓ Maritime codes

`MARITIME_CODES` · 18

| Code | Meaning |
| --- | --- |
| AA | All vessels leave the area |
| AB | You must leave the area |
| AC | I am leaving the area |
| AD | In distress |
| AE | Must abandon ship |
| AF | Ship abandoned |
| AG | Unable to leave |
| CP | I/the vessel am/is proceeding to you |
| DX | Sinking vessel |
| EL | Repeat the signal |
| NC | In distress, assistance required |
| RY | You must act according to the code |
| SO | You should stop |
| SS | I/the vessel have/has stopped |
| ZL | Your signal received but not understood |
| ZM | You must act on this signal |
| ZN | No (negative) |
| ZO | Yes (affirmative) |

## 🚩 Soviet codes

`SOVIET_CODES` · 12

| Code | Meaning |
| --- | --- |
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

## 🌦️ Weather codes

`METEO_CODES` · 9

| Code | Meaning |
| --- | --- |
| WX | Weather |
| TEMP | Temperature |
| WIND | Wind |
| VIS | Visibility |
| PRESS | Pressure |
| CLOUD | Cloud cover |
| RAIN | Rain |
| SNOW | Snow |
| FOG | Fog |

## ⚠️ Urgency

`URGENCY_LEVELS` · 4

| Code | Meaning |
| --- | --- |
| SAMOLET | Low priority |
| MOLNIYA | Medium priority |
| VSPYSHKA | High priority |
| AVIA | Emergency |

## 🚨 Service signals

`SERVICE_SIGNALS` · 4

| Code | Meaning |
| --- | --- |
| SOS | Distress signal |
| MAYDAY | Distress (voice) |
| PAN | Urgency |
| SECURITY | Safety |

## 📈 RST reference

`RST_CODES` · 1

| Code | Meaning |
| --- | --- |
| RST | Readability-Strength-Tone |

## 🔤 International phonetic alphabet

`INTERNATIONAL_PHONETIC` · 36

| Code | Meaning |
| --- | --- |
| A | Alfa |
| B | Bravo |
| C | Charlie |
| D | Delta |
| E | Echo |
| F | Foxtrot |
| G | Golf |
| H | Hotel |
| I | India |
| J | Juliett |
| K | Kilo |
| L | Lima |
| M | Mike |
| N | November |
| O | Oscar |
| P | Papa |
| Q | Quebec |
| R | Romeo |
| S | Sierra |
| T | Tango |
| U | Uniform |
| V | Victor |
| W | Whiskey |
| X | X-ray |
| Y | Yankee |
| Z | Zulu |
| 0 | Zero |
| 1 | One |
| 2 | Two |
| 3 | Three |
| 4 | Four |
| 5 | Five |
| 6 | Six |
| 7 | Seven |
| 8 | Eight |
| 9 | Niner |

## 🔤 Russian phonetic alphabet

`RUSSIAN_PHONETIC` · 31

| Code | Meaning |
| --- | --- |
| A | Анна |
| Б | Борис |
| В | Василий |
| Г | Григорий |
| Д | Дмитрий |
| Е | Елена |
| Ж | Женя |
| З | Зинаида |
| И | Иван |
| Й | Иван краткий |
| К | Константин |
| Л | Леонид |
| М | Михаил |
| Н | Николай |
| О | Ольга |
| П | Павел |
| Р | Роман |
| С | Семён |
| Т | Татьяна |
| У | Ульяна |
| Ф | Фёдор |
| Х | Харитон |
| Ц | Цапля |
| Ч | Человек |
| Ш | Шура |
| Щ | Щука |
| Ы | Еры |
| Ь | Мягкий знак |
| Э | Эхо |
| Ю | Юрий |
| Я | Яков |

## 🔤 Morse alphabets and ambiguous signs

Exact EN/RU tables and `PROSIGNS_MORSE` are in [morse_decoder.py](../modules/morse_decoder.py). They cover Latin and Russian letters, digits, and punctuation. Prosigns are checked before ordinary characters, so a shared pattern can render as `<AR>`, `<BT>`, `<KN>`, or `<AS>` instead of punctuation. The current `..-.` → `<INT>` mapping also overrides F/Ф. This is an implementation limitation, not a universal alphabet definition. Unknown patterns render as `□`.

The text detector recognizes joined signs tagged as `<AR>`; plain `AR` can match a CW abbreviation. Not all 11 dictionary prosign names have distinct audio-decoder outputs: some are aliases.
