# 🔤 Supported codes and symbols

[![Русский](https://img.shields.io/badge/Language-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-lightgrey)](SUPPORTED_CODES.md) [![English](https://img.shields.io/badge/Language-English-blue)](SUPPORTED_CODES.en.md)

[CLI guide](USAGE_GUIDE.en.md) · [README](../README.en.md)

## 📋 What support means

The following lists the actual dictionaries in [code_dictionaries.py](../modules/code_dictionaries.py), not verified compliance with international or departmental standards. Meanings come from the project; their applicability depends on context. A short word matching a dictionary does not establish that a command was transmitted.

The audio decoder converts CW into text; `ProceduralCodeDetector` separately searches decoded text. By default it matches exact words after uppercasing and splitting on whitespace. Surrounding punctuation is removed; a Q/Shch/QN question mark is retained in `is_question`. Characters inside a word are preserved. Multiword `НЕ ПНЛ` and `PAN PAN` are matched at token boundaries. Fuzzy matching is **disabled** by default; the API can enable it, but this increases false positives.

## 🇷🇺 Getting Russian abbreviations

`--ru` changes console language, not the recording alphabet. `decode` prints one combined EN/RU report, including extended categories. Shared structure and matching entries are not doubled; different structures are labelled EN/RU. Duplicate Russian codes in the legacy category are hidden only in this report; API data is retained. `auto`/`batch` save both analyses in TXT; tuning scores still use EN and receive no extra bonuses from expanding the Russian dictionary. `multi` analyzes its text across all categories. `auto --analyze` does not exist; `decode --analyze` remains for compatibility and does not add a duplicate summary.

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
РПТ — Повторите / я повторяю
АЛ — Всё, что только было передано
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

Counts are the number of keys in each dictionary. Do not sum them as unique automatically detected commands: categories overlap, and phonetic alphabets are helper data. RST is now extracted into `rst_reports` only after an explicit `RST` marker. Codes and Russian phonetic words are preserved untranslated in both versions.

| Dictionary | Entries |
| --- | ---: |
| `Q_CODES` | 53 |
| `ARRL_QN_CODES` | 26 |
| `Y_CODES` | 26 |
| `Z_CODES` | 33 |
| `CW_ABBREVIATIONS` | 55 |
| `PROSIGNS` | 15 |
| `SHCH_CODES` | 22 |
| `RU_Z_CODES` | 4 |
| `RU_PROCEDURAL_ABBR` | 169 |
| `SINPO_CODES` | 5 |
| `MARITIME_CODES` | 18 |
| `SOVIET_CODES` | 12 |
| `METEO_CODES` | 9 |
| `URGENCY_LEVELS` | 4 |
| `SOVIET_URGENCY_LEVELS` | 4 |
| `SERVICE_SIGNALS` | 8 |
| `RST_CODES` | 1 |
| `INTERNATIONAL_PHONETIC` | 36 |
| `RUSSIAN_PHONETIC` | 31 |

Additionally, `DXCC_PREFIX_MAP` (58 keys) and `MORSE_RU_TO_LATIN_CALLSIGN` (31) support callsign lookup and rendering.

## 📡 Q codes

`Q_CODES` · 53

| Code | Meaning |
| --- | --- |
| QSL | Reception confirmed / Can you acknowledge reception? |
| QTH | My location is ... / What is your location? |
| QRZ | You are being called by ... / Who is calling me? |
| QRM | Interference from other stations |
| QRN | Atmospheric interference |
| QRV | I am ready / Are you ready? |
| QRT | Stop transmitting / I am stopping transmission |
| QRX | I will call again at ... / When will you call again? |
| QSB | Your signals are fading |
| QSO | Contact with ... / Can you contact ...? |
| QSY | Change to another frequency |
| QTR | The exact time is ... / What is the exact time? |
| QRA | My station name is ... / What is your station name? |
| QRG | Your exact frequency is ... / What is my exact frequency? |
| QRK | Signal readability, 1–5 |
| QRL | I am busy / Is the frequency busy? |
| QRQ | Send faster |
| QRS | Send slower |
| QRU | Nothing for you / Have you anything for me? |
| QRW | Tell ... that I am calling them |
| QSA | Signal strength, 1–5 |
| QSP | I am relaying ... / Will you relay for ...? |
| QSX | Listening to ... on frequency ... |
| QSZ | Send each word / group twice or the specified number of times |
| QTC | I have ... messages / How many messages have you? |
| QTU | Station operating hours are ... |
| QFE | Atmospheric pressure at aerodrome level |
| QNH | Pressure reduced to sea level |
| QTF | Position determined by radio bearings |
| QRO | Increase transmitter power |
| QRP | Reduce transmitter power |
| QRH | Your frequency varies / Does my frequency vary? |
| QRI | Transmission tone rating, 1–3 |
| QRJ | Number of radiotelephone calls |
| QRY | Your turn is number ... / What is my turn? |
| QSD | Your keying is defective |
| QSG | Send ... telegrams in succession |
| QSK | I can hear between signals / you may interrupt me |
| QSM | Repeat the last telegram |
| QSN | I heard you on ... / Did you hear me on ...? |
| QSU | Transmit / listen on this or the specified frequency |
| QSV | Send a series of V |
| QSW | Transmit on ... |
| QTA | Cancel telegram number ... |
| QTB | Do you agree with my word count? |
| QTV | Keep watch / listen on my behalf on ... |
| QTX | Stay in contact until ... |
| QUA | Any news of ...? |
| QUC | Number of the last received telegram is ... |
| QUD | Has an urgency signal been received? |
| QUE | Can you speak the specified language? |
| QUF | A distress signal has been received from ... |
| QUM | Normal operation may resume |


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

`CW_ABBREVIATIONS` · 55

| Code | Meaning |
| --- | --- |
| RPT | Repeat / I repeat |
| DE | From / this is |
| FB | Fine business / excellent, good |
| SK | End of contact |
| AR | End of message |
| BT | Separator between parts of a message |
| CQ | General call |
| TNX | Thanks |
| TU | Thank you |
| UR | Your / you're, depending on context |
| OM | Old man / friendly address to an operator |
| YL | Young lady / female operator |
| GA | Go ahead; also good afternoon, depending on context |
| GE | Good evening |
| GM | Good morning |
| GN | Good night |
| WX | Weather |
| HW | How |
| CPY | Copy / receiving |
| PSE | Please |
| CFM | Confirm / I confirm |
| NIL | Nothing / no messages |
| MSG | Message |
| NR | Number |
| INFO | Information |
| AA | All after; also an address-separator prosign when sent without a gap |
| AB | All before |
| ADEE | Addressee |
| ADR | Address |
| AGN | Again |
| ARL | ARRL numbered radiogram text follows |
| AS | Wait / stand by |
| B | More / another message follows |
| BK | Break / permission for a brief interruption |
| BN | All between ... and ... |
| C | Correct / yes |
| CK | Check / word count |
| CL | Closing station |
| CUL | See you later |
| DX | Long-distance communication |
| HR | Here |
| IMI | Repeat / I repeat |
| K | Go ahead / invitation for any station to transmit |
| KN | Go only / only the called station may transmit |
| N | No / negative |
| NW | Now |
| PBL | Preamble / message heading |
| R | Received |
| SIG | Signature |
| TKS | Thanks |
| TXT | Text |
| WA | Word after |
| WB | Word before |
| 73 | Best regards |
| 88 | Love and kisses / traditional telegraph greeting |


## 🔧 Prosigns

`PROSIGNS` · 15

| Code | Meaning |
| --- | --- |
| AR | End of message / formal message transmission (.-.-.) |
| SK | End of contact / end of communication (...-.-) |
| BT | Separator between parts of a message (-...-) |
| KA | Start of transmission / attention (-.-.-) |
| KN | Only the called station may transmit (-.--.) |
| AS | Wait / stand by (.-...) |
| CT | Start of transmission / attention (-.-.-) |
| HH | Error; repeat from the last correctly transmitted word (........) |
| SN | Understood (•••-•) |
| VA | End of contact / end of communication (...-.-) |
| INT | Question (••-•) |
| IMI | Repeat / question mark, depending on context (..--..) |
| K | Invitation to transmit (-.-) |
| SOS | Distress signal (...---...) |
| CL | Closing station / leaving the air; used in amateur practice (-.-..-..) |


## 🇷🇺 Shch codes

`SHCH_CODES` · 22

| Code | Meaning |
| --- | --- |
| ЩРЖ | Are you ready? / I am ready |
| ЩРИ | What is the tone of my transmission? / Your tone is (1–5) |
| ЩРМ | Are you experiencing interference? / I am experiencing interference |
| ЩРН | Atmospheric interference is affecting reception |
| ЩРС | Send slower |
| ЩРЩ | Send faster |
| ЩРТ | Stop transmitting |
| ЩРУ | What have you for me? / I have nothing for you |
| ЩРЬ | When will you call me? / I will call you at the stated time / frequency |
| ЩСА | What is my signal strength? / Your signal strength is (1–5) |
| ЩСБ | Your signal strength varies |
| ЩСД | Your keying is poor |
| ЩСЗ | Send each word / group twice |
| ЩСЛ | Can you confirm? / I acknowledge reception |
| ЩСО | Can you contact ...? / I can contact ... |
| ЩСЫ | Change to another / reserve frequency |
| ЩТЖ | Listen on my behalf on the stated frequency / at the stated time |
| ЩТР | What is the exact time? / The exact time is ... (Moscow time) |
| ЩТЦ | Have you any radiograms? / Receive a radiogram |
| ЩЦЗ | You are violating radio traffic procedures |
| ЩЦМ | Your transmitter is faulty |
| ЩЦО | Cannot receive the radiogram |


## 📋 Russian procedural abbreviations

`RU_PROCEDURAL_ABBR` · 169

| Code | Meaning |
| --- | --- |
| РПТ | Repeat / I repeat |
| АЛ | All just transmitted |
| Р | Received / acknowledgement |
| Ц | Yes |
| НВ | Starting transmission |
| АС | Wait |
| ДЕ | Separates the called and calling station callsigns; from / this is |
| АА | All after ... |
| АБ | All before ... |
| АБЖ | Repeat / I repeat figures in abbreviated form |
| АБТ | About / approximately |
| АГН | Again |
| АД | Aerodrome |
| АДЗ | Advise / inform |
| АДС | Address ... |
| АМ | Before noon |
| АНС | Answer on wavelength / frequency ... |
| АНТ | Before |
| АПР | After ... (time or point) |
| АР | End of transmission; sent as one procedural sign |
| АРР | Arrive / arrival |
| АТП | At ... (time or point) |
| АТЦ | Air traffic control service |
| АЦЦ | Area control service |
| АЦФТ | Aircraft |
| БД | Bad |
| БК | Interrupt the ongoing transmission |
| БЛИНД | Transmit / transmitting without agreement |
| БН | All between ... and ... |
| БТН | Between |
| БЩ | Reply to a request |
| В | Word(s) or group(s) |
| ВА | Word after ... |
| ВБ | Word before ... |
| ВР | Outside a scheduled flight |
| ВРГ | Working |
| ВРК | To work |
| ВС | Aircraft returning |
| ВЬ | Weather |
| ГА | Resume transmission |
| ГБ | Goodbye |
| ГД | Good afternoon |
| ГЕ | Good evening |
| ГМ | Good morning |
| ГН | Good night |
| ГР | Group(s) |
| ГУХОР | Cannot hear you |
| ДС | Adjust transmitter: the minimum of your signal is too broad |
| ДСВ | Goodbye |
| ДЧ | Daytime frequency |
| ДЬ | Long-distance communication / distant station |
| ЕР | Here; also hereby ... |
| ЕРБ | Landing outside the runway is permitted |
| ЕТА | Estimated time of arrival |
| ЕТД | Estimated time of departure |
| ЕТИ | Information is provisional |
| ЖЖЖ | Test transmission / tuning signal |
| ОМ | Dear comrade |
| ОП | Operator |
| ОРД | Order designation |
| ПБЛ | Heading / message preamble |
| ПВЬ | Forecast |
| ПГ | Confirm readiness |
| ПМ | After noon |
| ПРИГ | Prepare |
| ПСЕ | Please |
| ПЧТ | Mail |
| РДО | Radio |
| РЕЖС | Send dots |
| РЕП | Airborne report sending point |
| РЕФ | Reference to ... / refer to ... |
| РЗ | Flight delayed |
| РМ | Location |
| РО | Flight cancelled |
| РОН | Receive only |
| РП | Urgent |
| РТ | Transmit / transmitting the message to ... addressees |
| РЧ | Reserve frequency |
| РЩ | Request indicator |
| САП | As soon as possible |
| СЖЦ | Service-message indicator |
| СЗ | Medical mission |
| ЖИО | Severe (interference level) |
| ЖЫ | Very |
| З | See the Cyrillic Z-code table |
| ИМТ | Immediately |
| ИМ | A series of dashes permits transmission; a series of dots stops it |
| К | Invitation to transmit |
| КЫ | Morse key |
| ЛР | The last message I received was ... |
| ЛС | The last message I sent was ... |
| МИ | My |
| МИС | Missing ... (message serial number) |
| МН | Minute(s) |
| МОМ | Moment |
| МСК | Moscow time |
| МЦ | Make a copy for delivery to ... |
| НД | Cannot transmit to the specified aircraft; advise the originator |
| НИЛ | I have nothing to transmit to you |
| НМЛ | Normal |
| НМЧ | Equipment failure |
| НО | No |
| НОВ | Now |
| НОЧ | Overnight stay |
| НР | Number / quantity |
| ОК | Agreed / correct |
| СИГ | Signature |
| СК | End of contact; sent as one procedural sign |
| СКЕД | Schedule |
| СЛВ | Slowly |
| СЛД | Monitor |
| СЛЖ | Monitoring |
| СОС | Distress signal |
| СР | Special flight |
| СФ | Aircraft station name indicator |
| СЫС | Refer to your service message |
| ТАФ | Abbreviated aerodrome forecast |
| ТАФОР | Aerodrome forecast |
| ТВР | Control tower |
| ТЕСТ | Test / trial operation |
| ТИКАС | Pay attention |
| ТИЛ | Until |
| ТКС | Thank you |
| ТМР | Tomorrow |
| ТО | To ... (point) |
| ТОДЫ | Today |
| ТТ | Teletype |
| ТУ | Thank you |
| ТФЦ | Traffic exchange |
| ТЬТ | Text |
| У | You |
| УА | Have you agreed? |
| УАБ | Until you are advised ... |
| УР | Your |
| УФН | Until further notice |
| ФБ | Good |
| ФИ | Repeat / I repeat figures |
| ФЛТ | Flight |
| ФОНЕ | Telephone |
| ФОР | For |
| ФМ | From |
| ХЕЛ | Helicopter |
| ХЖ | Have |
| ХЖТН | Do not have |
| ХР | Hours / period of time |
| ЦЛ | I am switching on my station |
| ЦЛР | Cleared to ... |
| ЦОЛ | Check / I will check |
| ЦОР | Correction |
| ЦП | General call to two or more specified stations |
| ЦС | Callsign / request to state callsign |
| ЦФМ | Confirm / I confirm |
| ЦЩ | General call to all stations |
| ЧА | Aerodrome is waterlogged |
| ЧВ | Availability |
| ЧГ | Cargo |
| ЧЗ | Prohibited |
| ЧН | Flight plan |
| ЧО | Providing / are you providing |
| ЧР | Permission granted |
| ЧХ | Load |
| ЩУАД | Grid square |
| Щ | See the Shch-code table |
| ЫР | Your |
| ЫС | Refer to your service notice / reply to it |
| Ь | Mobile radio station |
| ЬС | Atmospheric interference |
| ЫЩ | Service note |
| ЬЬЬ | Urgency signal: repeat the group three times before the call |


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

`SERVICE_SIGNALS` · 8

| Code | Meaning |
| --- | --- |
| SOS | Distress signal |
| MAYDAY | Distress (voice) |
| PAN | Urgency |
| SECURITY | Safety |
| PAN PAN | Radiotelephony urgency signal |
| SECURITE | Radiotelephony safety signal |
| SÉCURITÉ | Radiotelephony safety signal |
| ЬЬЬ | Urgency signal before a call |


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
| А | Анна |
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

Exact EN/RU tables and `PROSIGNS_MORSE` are in [morse_decoder.py](../modules/morse_decoder.py). They cover Latin and Russian letters, digits, and punctuation. Prosigns are checked before ordinary characters, so a shared pattern can render as `<AR>`, `<BT>`, `<KN>`, or `<AS>` instead of punctuation. Pattern `..-.` decodes as F/Ф, and `..-..` as Э in RU; the old `<INT>` override is fixed. `..--..` remains `?` and `-.-` remains K/К. Joined `...---...` and `-.-..-..` decode as `<SOS>` and `<CL>`. Unknown patterns render as `□`.

The text detector recognizes joined signs tagged as `<AR>`; plain `AR` can match a CW abbreviation. Not all 15 dictionary prosign names have distinct audio-decoder outputs: some are aliases.

## 📻 ARRL QN signals for CW nets

`ARRL_QN_CODES` · 26

| Code | Meaning |
| --- | --- |
| QNA | Answer in the prearranged order |
| QNB | Act as relay between ... and ... |
| QNC | All net stations must copy the following message |
| QND | The net is directed |
| QNE | Entire net, stand by |
| QNF | The net is free / undirected |
| QNG | Take over net control |
| QNH | Your net frequency is too high |
| QNI | Check into the net / I am checking in |
| QNJ | Can you copy me / station ...? |
| QNK | Transmit the message for ... to station ... |
| QNL | Your net frequency is too low |
| QNM | You are interfering with the net; stand by |
| QNN | The net control station is ... |
| QNO | Station is leaving the net |
| QNP | Cannot copy you / station ... |
| QNQ | Move to ... and wait until the exchange ends, then send traffic |
| QNR | Answer ... and receive traffic |
| QNS | List of stations in the net / request for the list |
| QNT | Request permission to leave the net for ... minutes |
| QNU | The net has traffic for you; stand by |
| QNV | Contact ... and, after contact, move to ... |
| QNW | How should messages for ... be routed? |
| QNX | You are excused from the net / request to be excused |
| QNY | Move to another frequency to exchange traffic with ... |
| QNZ | Zero-beat your frequency with mine |

Intended for organized amateur CW nets. Here `QNH` means the net frequency is too high; in `Q_CODES` it means pressure. Profile `all` returns both meanings in separate categories; `arrl_traffic` selects the net dictionary.

## 🇷🇺 Soviet Cyrillic Z codes

`RU_Z_CODES` · 4

| Code | Meaning |
| --- | --- |
| ЗАН | Reception is absolutely impossible |
| ЗАС | Monitor the operation of my transmitter |
| ЗЖП | Send the Russian letter Zhe for tuning |
| ЗНН | No traffic |

Kept separate from Latin Z codes: `ЗАН` and `ZAN` remain distinct keys and systems.

## ⚠️ Soviet departmental priority categories

`SOVIET_URGENCY_LEVELS` · 4

| Code | Meaning |
| --- | --- |
| ШТОРМ | Out of turn (priority 1) |
| МЕДПОМОЩЬ | Out of turn (priority 1) |
| МОЛНИЯ | Very urgent (priority 2) |
| ЛЕСАВИА | Urgent (priority 3) |

Order: out of turn (1), very urgent (2), urgent (3), ordinary without a marker (4). An absent marker does not create a detector match. The old `SAMOLET / MOLNIYA / VSPYSHKA / AVIA` set remains separate in `URGENCY_LEVELS`; it does not replace this table.

## 🧠 Profiles, context, and metadata

```python
from modules.procedural_codes import ProceduralCodeDetector

result = ProceduralCodeDetector(profile="ru_soviet").detect_codes(
    "РПТ АА 24 К ЩРЖ? ЗАН ШТОРМ RST 599"
)
print(result["shch_codes"][0]["is_question"])  # True
print(result["ru_z_codes"])
print(result["soviet_urgency_levels"])
print(result["rst_reports"])
```

| API profile | Categories |
| --- | --- |
| `all` (default) | All dictionaries; a code can have multiple interpretations |
| `ham_cw` | General Q codes and CW abbreviations |
| `arrl_traffic` | Net QN signals and CW abbreviations |
| `ru_soviet` | Shch, Cyrillic Z, Russian abbreviations, Soviet legacy codes and priorities |
| `maritime` | General Q and maritime codes |

All profiles retain prosigns, service signals, and RST; callsigns and general structure heuristics are analyzed independently. The CLI uses `all`; no profile argument is exposed yet. In `all`, short `К`, `Р`, `Ц`, `У`, `В`, `З`, `Щ`, `Ь` also yield dictionary matches; choose a profile for targeted analysis. Interpret two-letter matches using nearby markers rather than treating them as evidence of commands.

Category entries contain `code_system`, `source`, and `exact_match`; tagged prosigns have `is_prosign`, and Q/Shch/QN entries have `is_question`. `source` identifies the imported table's provenance, not individual verification of each row. Numeric `confidence` is provided by the older fuzzy matcher; exact dictionary matches receive no invented probability. New QN/Cyrillic Z codes, Russian abbreviations, and priorities use exact matching even with `use_fuzzy_matching=True`.

`SOVIET_CODES_LEGACY` is a compatible alias of `SOVIET_CODES`; `soviet_codes` remains the result key. `ПРМ`, `ПРД`, `КНЦ`, and other legacy entries are not presented as a single official table. Y codes depend on service and period. The maritime dictionary is a limited selection, not the entire international code. `SECURITE`/`SÉCURITÉ` were added as safety signals; old `SECURITY` remains for compatibility. `PAN PAN` is matched as a phrase, while legacy `PAN` also remains.

## 📡 Radio exchange examples

- `ЦЩ ЦЩ ЦЩ ДЕ <CALLSIGN>`: general call to all stations.
- `<CALLSIGN> ДЕ <CALLSIGN> ЩРЖ? К`: readiness query and invitation to reply.
- `АС 10 К`: wait (10 minutes in this example), then invitation to transmit.
- `РПТ ГР 12 15 К`: repeat groups 12 and 15.
- `РПТ АА 24 К`: repeat everything after group 24.
- `РПТ АБ 5 К`: repeat everything before group 5.
- `РПТ БН 3 12 К`: repeat everything between groups 3 and 12.
- `АР`: end of message; `СК`: end of contact; `ЖЖЖ`: tuning.

These are human interpretations. The detector identifies dictionary groups; it does not build a semantic “repeat groups” instruction or infer time units from a number alone. `<CALLSIGN>` is a placeholder for a real callsign. Plain `АР`/`СК` in text do not prove the signs were joined in the audio.

## 📈 RST interpretation

`RST` means Readability / Strength / Tone. The detector accepts `RST 599`: R=1–5, S=1–9, T=1–9. Bare `599` is not interpreted as RST; `RST 699` is rejected. Missing tones and automatic voice RS detection are not implemented here.

| R | Readability |
| --- | --- |
| 1 | Unreadable |
| 2 | Barely readable, occasional words |
| 3 | Readable with considerable difficulty |
| 4 | Readable with practically no difficulty |
| 5 | Perfectly readable |

| S | Signal strength |
| --- | --- |
| 1 | Barely perceptible |
| 2 | Very weak |
| 3 | Weak |
| 4 | Moderate |
| 5 | Fairly good |
| 6 | Good |
| 7 | Moderately strong |
| 8 | Strong |
| 9 | Very strong |

T is tone quality, 1–9. These transmitted ratings are distinct from `signal_analyzer.py` measurements. Soviet `ВЬ` (weather), `ПВЬ` (forecast), `ТАФ`, and `ТАФОР` are in Russian abbreviations; `QFE`/`QNH` are in the general Q dictionary.

## 📚 Sources cited by the imported reference

- [MorseDecoder](https://github.com/tixset/MorseDecoder/blob/main/docs/SUPPORTED_CODES.md)
- [USSR forestry radio rules, 1982, appendix 6](https://base.garant.ru/400731259/7dede6ac8f25be619ed07c17ed1c62c9/)
- [USSR forestry radio rules, 1982, appendix 7](https://base.garant.ru/400731259/1a3794674ba91fb6f13d1885dca9f9e1/)
- [Mirror of the 1982 rules](https://meganorm.ru/mega_doc/norm/akt_forma/1/pravila_organizatsii_radiosvyazi_i_tekhnicheskoy.html)
- [Russian emergency ministry radio guide](https://base.garant.ru/72152196/)
- [ARRL Ham Radio Glossary](https://www.arrl.org/ham-radio-glossary)
- [ARRL QN Signals / Abbreviations / Prosigns (FSD-218)](https://www.arrl.org/files/file/Public%20Service/fsd218.pdf)
- [ARRL Quick Reference Operating Aids](https://www.arrl.org/quick-reference-operating-aids)

Historical and departmental codes depend on country, service, and period. Links are retained from the supplied extension; they do not imply independent verification of every dictionary entry. Profile and context remain necessary even for exact matches.
