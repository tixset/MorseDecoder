"""
Модуль для распознавания военных команд и кодов в азбуке Морзе
Основан на международных Q-кодах и военных Z-кодах (ACP-131)
С поддержкой нечеткого поиска (fuzzy matching)
"""
from functools import partial
from .console_i18n import console_text

import re
from .fuzzy_matcher import smart_code_detection, fuzzy_match_callsign, contextual_code_enhancement
from .code_dictionaries import (
    ARRL_QN_CODES, RU_Z_CODES, SOVIET_URGENCY_LEVELS,
    Q_CODES, Y_CODES, Z_CODES, CW_ABBREVIATIONS, PROSIGNS,
    SHCH_CODES, RU_PROCEDURAL_ABBR, SINPO_CODES, MARITIME_CODES,
    SOVIET_CODES, METEO_CODES, URGENCY_LEVELS, SERVICE_SIGNALS,
    RST_CODES, INTERNATIONAL_PHONETIC, RUSSIAN_PHONETIC,
    MORSE_RU_TO_LATIN_CALLSIGN
)

# Скомпилированные regex паттерны для быстрого поиска
CALLSIGN_PATTERN = re.compile(
    r'\b[A-Z]{1,2}\d[A-Z0-9]{1,4}\b',  # Стандартный позывной: 1-2 буквы + цифра + 1-4 символа
    re.IGNORECASE
)

# Паттерн для позывных, разделенных пробелами (R 3 D C -> R3DC)
SPACED_CALLSIGN_PATTERN = re.compile(
    r'(?:\b[A-Z]{1,2}\b\s+\b\d\b\s+\b[A-Z0-9]{1,4}\b)',
    re.IGNORECASE
)

class ProceduralCodeDetector:
    """Детектор процедурных кодов и команд в расшифрованном тексте"""
    
    def __init__(self, use_fuzzy_matching=False, max_errors=1, profile="all"):
        """
        Args:
            use_fuzzy_matching: использовать нечеткий поиск (рекомендуется)
            max_errors: максимальное количество ошибок для fuzzy matching (1-2)
        """
        if profile not in ('all', 'ham_cw', 'ru_soviet', 'arrl_traffic', 'maritime'):
            raise ValueError('Unsupported code profile: ' + profile)
        self.profile = profile
        self.q_codes = Q_CODES
        self.y_codes = Y_CODES
        self.z_codes = Z_CODES
        self.cw_abbr = CW_ABBREVIATIONS
        self.prosigns = PROSIGNS
        self.shch_codes = SHCH_CODES
        self.ru_procedural_abbr = RU_PROCEDURAL_ABBR
        self.soviet_codes = SOVIET_CODES
        self.urgency = URGENCY_LEVELS
        self.service = SERVICE_SIGNALS
        self.sinpo = SINPO_CODES
        self.maritime = MARITIME_CODES
        self.meteo = METEO_CODES
        self.intl_phonetic = INTERNATIONAL_PHONETIC
        self.ru_phonetic = RUSSIAN_PHONETIC
        self.use_fuzzy = use_fuzzy_matching
        self.max_errors = max_errors
    
    def detect_codes(self, text):
        """
        Обнаружение всех кодов и команд в тексте
        
        Args:
            text: расшифрованный текст
            
        Returns:
            dict с обнаруженными кодами и их расшифровками
        """
        text = text.upper().strip()
        # A question mark belongs to the transmission, not the dictionary key.
        # Keep internal punctuation and <prosign> tags intact.
        original_words = text.split()
        words = [word.strip('.,;:!?()"') for word in original_words]
        words = [word for word in words if word]
        normalized = ' '.join(words)
        if self.use_fuzzy:
            detected = self._detect_codes_fuzzy(normalized, words)
        else:
            detected = self._detect_codes_exact(words)
        self._detect_extended(detected, words, original_words)
        self._apply_profile(detected)
        return detected

    def _detect_extended(self, detected, words, original_words):
        """Exact, service-specific additions in both exact and fuzzy modes."""
        for field, dictionary in (
            ('arrl_qn_codes', ARRL_QN_CODES),
            ('ru_z_codes', RU_Z_CODES),
            ('soviet_urgency_levels', SOVIET_URGENCY_LEVELS),
        ):
            detected[field] = [dict(code=word, meaning=dictionary[word])
                               for word in words if word in dictionary]

        if self.use_fuzzy:
            # Tagged signs are exact audio evidence; fuzzy guesses about plain
            # letters are kept distinguishable via is_prosign=False.
            for word in words:
                for code in re.findall(r'<([A-Z]+)>', word):
                    if code in self.prosigns:
                        detected['prosigns'].append(dict(
                            code=code, meaning=self.prosigns[code],
                            original_word='<' + code + '>', exact_match=True))

        # Match phrases by token boundaries, including the legacy НЕ ПНЛ.
        for field, dictionary, key in (
            ('soviet_codes', self.soviet_codes, 'code'),
            ('service_signals', self.service, 'signal'),
        ):
            for phrase, meaning in dictionary.items():
                parts = phrase.split()
                if len(parts) > 1:
                    for i in range(len(words) - len(parts) + 1):
                        if words[i:i + len(parts)] == parts:
                            detected[field].append({key: phrase, 'meaning': meaning})
        if any(item['code'] == 'НЕ ПНЛ' for item in detected['soviet_codes']):
            # Do not report the affirmative ПНЛ for the negated occurrence.
            count = sum(item['code'] == 'НЕ ПНЛ' for item in detected['soviet_codes'])
            for item in detected['soviet_codes'][:]:
                if count and item['code'] == 'ПНЛ':
                    detected['soviet_codes'].remove(item)
                    count -= 1

        # Tag each Q/Щ occurrence, retaining question vs statement order.
        for field in ('q_codes', 'shch_codes', 'arrl_qn_codes'):
            occurrences = {}
            for token in original_words:
                key = token.strip('.,;:!?()"')
                occurrences.setdefault(key, []).append('?' in token)
            for item in detected[field]:
                flags = occurrences.get(item['code'], [])
                if flags:
                    item['is_question'] = flags.pop(0)

        detected['rst_reports'] = []
        for i, word in enumerate(words[:-1]):
            value = words[i + 1]
            if word == 'RST' and re.fullmatch(r'[1-5][1-9][1-9]', value):
                detected['rst_reports'].append(dict(
                    code='RST', value=value, readability=int(value[0]),
                    strength=int(value[1]), tone=int(value[2])))

    def _apply_profile(self, detected):
        """Label code families and optionally restrict ambiguous service matches."""
        systems = {
            'q_codes': ('international_q', 'Project Q dictionary'),
            'arrl_qn_codes': ('arrl_qn', 'ARRL FSD-218'),
            'ru_z_codes': ('soviet_z', 'USSR radio rules, 1982, appendix 6'),
            'shch_codes': ('soviet_shch', 'USSR radio rules, 1982, appendix 6'),
            'ru_procedural_abbr': ('ru_procedural', 'USSR radio rules, 1982, appendix 7'),
            'soviet_urgency_levels': ('soviet_priority', 'USSR radio rules, 1982'),
            'soviet_codes': ('soviet_legacy', 'Project legacy heuristics'),
            'cw_abbreviations': ('ham_cw', 'Extended CW reference'),
            'prosigns': ('prosigns', 'Project and extended prosign tables'),
            'z_codes': ('latin_z', 'Project Latin Z dictionary'),
            'y_codes': ('y_codes', 'Project Y dictionary'),
            'maritime_codes': ('maritime', 'Project maritime dictionary'),
            'meteo_codes': ('weather', 'Project weather dictionary'),
            'sinpo_codes': ('sinpo', 'Project SINPO dictionary'),
            'service_signals': ('service', 'Project and extended service signals'),
        }
        common = {'prosigns', 'service_signals', 'rst_reports'}
        profiles = {
            'ham_cw': common | {'q_codes', 'cw_abbreviations'},
            'arrl_traffic': common | {'arrl_qn_codes', 'cw_abbreviations'},
            'ru_soviet': common | {'shch_codes', 'ru_z_codes', 'ru_procedural_abbr',
                                  'soviet_codes', 'soviet_urgency_levels'},
            'maritime': common | {'q_codes', 'maritime_codes'},
        }
        for field, (system, source) in systems.items():
            if self.profile != 'all' and field not in profiles[self.profile]:
                detected[field] = []
            for item in detected.get(field, []):
                item['code_system'] = system
                item['source'] = source
                # A dictionary match is not evidence of transcription accuracy.
                item.setdefault('exact_match', True)
                if field == 'prosigns':
                    item['is_prosign'] = ('original_word' not in item or
                                          '<' in item['original_word'])
        if self.profile != 'all':
            detected['urgency_level'] = None  # legacy transliterated priority labels
        detected['profile'] = self.profile

    def _detect_codes_fuzzy(self, text, words):
        """
        Обнаружение кодов с нечетким поиском и контекстным анализом
        """
        # Используем smart_code_detection из fuzzy_matcher
        fuzzy_results = smart_code_detection(
            text, 
            self.q_codes, 
            self.prosigns,
            z_codes=self.z_codes,
            max_errors=self.max_errors
        )
        
        detected = {
            'q_codes': [],
            'y_codes': [],
            'z_codes': [],
            'shch_codes': [],
            'ru_procedural_abbr': [],
            'soviet_codes': [],
            'cw_abbreviations': [],
            'prosigns': [],
            'urgency_level': None,
            'service_signals': [],
            'sinpo_codes': [],
            'maritime_codes': [],
            'meteo_codes': [],
            'callsigns': [],
            'message_structure': self._analyze_structure(words),
            'check_field': self._extract_check(words),
            'message_number': self._extract_nr(words),
            'fuzzy_match_stats': fuzzy_results.get('confidence_stats', {}),
        }
        
        # Преобразуем результаты fuzzy matching в формат detected
        for q_match in fuzzy_results.get('q_codes', []):
            detected['q_codes'].append({
                'code': q_match['matched_code'],
                'meaning': q_match['meaning'],
                'original_word': q_match['word'],
                'confidence': q_match['confidence'],
                'exact_match': q_match['exact_match']
            })
        
        for z_match in fuzzy_results.get('z_codes', []):
            detected['z_codes'].append({
                'code': z_match['matched_code'],
                'meaning': z_match['meaning'],
                'original_word': z_match['word'],
                'confidence': z_match['confidence'],
                'exact_match': z_match['exact_match']
            })
        
        for prosign_match in fuzzy_results.get('prosigns', []):
            detected['prosigns'].append({
                'code': prosign_match['matched_code'],
                'meaning': prosign_match['meaning'],
                'original_word': prosign_match['word'],
                'confidence': prosign_match['confidence'],
                'exact_match': prosign_match['exact_match']
            })
        
        for callsign_match in fuzzy_results.get('callsigns', []):
            detected['callsigns'].append({
                'callsign': callsign_match['matched_callsign'],
                'original_word': callsign_match['word'],
                'confidence': callsign_match['confidence'],
                'exact_match': callsign_match['exact_match']
            })
        
        # Дополнительная проверка для российских кодов и сокращений (точное совпадение)
        for word in words:
            if word in self.y_codes:
                detected['y_codes'].append({
                    'code': word,
                    'meaning': self.y_codes[word]
                })
            
            if word in self.shch_codes:
                detected['shch_codes'].append({
                    'code': word,
                    'meaning': self.shch_codes[word]
                })
            
            if word in self.ru_procedural_abbr:
                detected['ru_procedural_abbr'].append({
                    'code': word,
                    'meaning': self.ru_procedural_abbr[word]
                })
            
            if word in self.soviet_codes:
                detected['soviet_codes'].append({
                    'code': word,
                    'meaning': self.soviet_codes[word]
                })
            
            if word in self.cw_abbr:
                detected['cw_abbreviations'].append({
                    'code': word,
                    'meaning': self.cw_abbr[word]
                })
            
            if word in self.maritime:
                detected['maritime_codes'].append({
                    'code': word,
                    'meaning': self.maritime[word]
                })
            
            if word in self.meteo:
                detected['meteo_codes'].append({
                    'code': word,
                    'meaning': self.meteo[word]
                })
            
            if word in self.sinpo:
                detected['sinpo_codes'].append({
                    'code': word,
                    'meaning': self.sinpo[word]
                })
            
            if word in self.urgency:
                detected['urgency_level'] = {
                    'level': word,
                    'meaning': self.urgency[word]
                }
            
            if word in self.service:
                detected['service_signals'].append({
                    'signal': word,
                    'meaning': self.service[word]
                })
        
        # Попытаемся найти позывные из склеенных соседних слов (для текстов с пробелами между буквами)
        spaced_callsigns = self._find_spaced_callsigns(words)
        for cs in spaced_callsigns:
            # Проверим, нет ли уже такого позывного
            if not any(c.get('callsign') == cs for c in detected['callsigns']):
                detected['callsigns'].append({
                    'callsign': cs,
                    'original_word': cs,
                    'confidence': 0.7,  # средняя уверенность для склеенных позывных
                    'exact_match': True
                })
        
        return detected
    
    def _detect_codes_exact(self, words):
        """
        Точное обнаружение кодов (старый метод без fuzzy matching)
        """
        detected = {
            'q_codes': [],
            'y_codes': [],
            'z_codes': [],
            'shch_codes': [],
            'ru_procedural_abbr': [],
            'soviet_codes': [],
            'cw_abbreviations': [],
            'prosigns': [],
            'urgency_level': None,
            'service_signals': [],
            'sinpo_codes': [],
            'maritime_codes': [],
            'meteo_codes': [],
            'callsigns': [],
            'message_structure': self._analyze_structure(words),
            'check_field': self._extract_check(words),
            'message_number': self._extract_nr(words),
        }
        
        for word in words:
            # ПРИОРИТЕТ 1: Prosigns в формате <CODE> из морзе-декодера
            # Извлекаем prosigns с помощью regex, т.к. они могут слиться с соседними символами
            import re
            prosign_matches = re.findall(r'<([A-Z]+)>', word)
            for prosign_code in prosign_matches:
                if prosign_code in self.prosigns:
                    detected['prosigns'].append({
                        'code': prosign_code,
                        'meaning': self.prosigns[prosign_code]
                    })
            
            # Если слово состоит только из prosign, переходим к следующему
            if word.startswith('<') and word.endswith('>'):
                continue
            
            # Q-коды
            if word in self.q_codes:
                detected['q_codes'].append({
                    'code': word,
                    'meaning': self.q_codes[word]
                })
            
            # Y-коды
            if word in self.y_codes:
                detected['y_codes'].append({
                    'code': word,
                    'meaning': self.y_codes[word]
                })
            
            # Z-коды
            if word in self.z_codes:
                detected['z_codes'].append({
                    'code': word,
                    'meaning': self.z_codes[word]
                })
            
            # Щ-коды (российские)
            if word in self.shch_codes:
                detected['shch_codes'].append({
                    'code': word,
                    'meaning': self.shch_codes[word]
                })
            
            # Российские процедурные сокращения
            if word in self.ru_procedural_abbr:
                detected['ru_procedural_abbr'].append({
                    'code': word,
                    'meaning': self.ru_procedural_abbr[word]
                })
            
            # Советские коды
            if word in self.soviet_codes:
                detected['soviet_codes'].append({
                    'code': word,
                    'meaning': self.soviet_codes[word]
                })
            
            # CW-сокращения
            if word in self.cw_abbr:
                detected['cw_abbreviations'].append({
                    'code': word,
                    'meaning': self.cw_abbr[word]
                })
            
            # Морские коды
            if word in self.maritime:
                detected['maritime_codes'].append({
                    'code': word,
                    'meaning': self.maritime[word]
                })
            
            # Метеокоды
            if word in self.meteo:
                detected['meteo_codes'].append({
                    'code': word,
                    'meaning': self.meteo[word]
                })
            
            # SINPO коды
            if word in self.sinpo:
                detected['sinpo_codes'].append({
                    'code': word,
                    'meaning': self.sinpo[word]
                })
            
            # Уровень срочности
            if word in self.urgency:
                detected['urgency_level'] = {
                    'level': word,
                    'meaning': self.urgency[word]
                }
            
            # Служебные сигналы
            if word in self.service:
                detected['service_signals'].append({
                    'signal': word,
                    'meaning': self.service[word]
                })
            
            # Позывные (простая эвристика)
            if self._is_callsign(word):
                detected['callsigns'].append(word)
        
        # Попытаемся найти позывные из склеенных соседних слов (для текстов с пробелами между буквами)
        detected['callsigns'].extend(self._find_spaced_callsigns(words))
        # Удаляем дубликаты
        detected['callsigns'] = sorted(set(detected['callsigns']))
        
        return detected
    
    def _extract_check(self, words):
        """Извлечение поля CHECK (число групп в сообщении)"""
        for i, word in enumerate(words):
            if word == 'CHECK' and i + 1 < len(words):
                try:
                    return int(words[i + 1])
                except ValueError:
                    pass
        return None
    
    def _extract_nr(self, words):
        """Извлечение номера сообщения (NR)"""
        for i, word in enumerate(words):
            if word == 'NR' and i + 1 < len(words):
                try:
                    return int(words[i + 1])
                except ValueError:
                    pass
        return None
    
    def _is_callsign(self, word):
        """
        Проверка, является ли слово позывным
        Использует regex для быстрой проверки
        """
        if not word or len(word) < 3 or len(word) > 10:
            return False
        
        # Быстрая проверка через regex
        return bool(CALLSIGN_PATTERN.match(word))
        digit_pos = next((i for i, c in enumerate(word) if c.isdigit()), -1)
        if digit_pos > 0 and digit_pos <= 3:  # цифра на позиции 1-3
            prefix_len = digit_pos
            suffix = word[digit_pos+1:]
            # Префикс 1-3 буквы, суффикс 1-3 буквы (не больше!)
            # Суффикс обычно 1-3 символа, редко 4
            if 1 <= prefix_len <= 3 and 1 <= len(suffix) <= 3 and suffix.isalpha():
                return True
        
        return False
    
    def _convert_russian_callsign(self, word):
        """
        Конвертация русского позывного в латинский формат
        Использует таблицу транслитерации морзе-букв
        
        Пример: "РУА3ИКС" → "RUA3IKS" (если это позывной)
        """
        if not word:
            return word
        
        # Конвертируем каждую букву
        result = []
        for char in word.upper():
            if char in MORSE_RU_TO_LATIN_CALLSIGN:
                result.append(MORSE_RU_TO_LATIN_CALLSIGN[char])
            else:
                result.append(char)
        
        return ''.join(result)
    
    def _find_spaced_callsigns(self, words):
        """
        Поиск позывных, разделенных пробелами (например "I I 2 V V A" -> "II2VVA")
        Использует оптимизированный подход с regex и хеш-множествами
        """
        all_candidates = []
        window_size = 10  # максимальная длина позывного в словах
        
        # Оптимизация: предварительно отфильтровываем короткие слова
        short_words_indices = [i for i, w in enumerate(words) if len(w) <= 2]
        
        if len(short_words_indices) < 3:
            return []  # Недостаточно коротких слов для позывного
        
        # Находим все возможные позывные
        for idx, i in enumerate(short_words_indices):
            # Ограничиваем окно следующими короткими словами
            max_idx = min(idx + window_size, len(short_words_indices))
            
            for end_idx in range(idx + 3, max_idx + 1):  # минимум 3 слова
                j = short_words_indices[end_idx - 1]
                
                # Проверяем, что слова идут подряд или почти подряд
                if j - i > window_size:
                    break
                
                window_words = words[i:j+1]
                # Объединяем только односимвольные/двусимвольные слова
                if all(len(w) <= 2 for w in window_words):
                    candidate = ''.join(window_words)
                    
                    # Пытаемся конвертировать из русского в латинский
                    if any('\u0400' <= c <= '\u04FF' for c in candidate):
                        candidate = self._convert_russian_callsign(candidate)
                    
                    # Быстрая проверка через regex
                    if CALLSIGN_PATTERN.match(candidate):
                        score = self._score_callsign(candidate)
                        all_candidates.append({
                            'callsign': candidate,
                            'start': i,
                            'end': j + 1,
                            'score': score
                        })
        
        # Выбираем непересекающиеся позывные с максимальным счётом
        all_candidates.sort(key=lambda x: (-x['score'], -len(x['callsign'])))
        
        selected = []
        used_positions = set()
        
        for candidate in all_candidates:
            positions = set(range(candidate['start'], candidate['end']))
            if not positions.intersection(used_positions):
                selected.append(candidate['callsign'])
                used_positions.update(positions)
        
        return selected
    
    def _score_callsign(self, callsign):
        """Оценка качества позывного (выше = лучше)"""
        score = 0
        
        # Бонус за российские префиксы
        russian_prefixes = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 
                           'RA', 'RU', 'RV', 'RW', 'RX', 'RY', 'RZ',
                           'U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'U8', 'U9',
                           'UA', 'UB', 'UC', 'UD', 'UE', 'UF', 'UG', 'UH', 'UI']
        for prefix in russian_prefixes:
            if callsign.startswith(prefix):
                score += 20
                break
        
        # Бонус за двухбуквенные итальянские префиксы (II, I)
        if callsign.startswith('II') and len(callsign) >= 6:
            score += 15
        elif callsign.startswith('I') and len(callsign) >= 5:
            score += 10
        
        # Идеальная длина 5-7 символов
        if 5 <= len(callsign) <= 7:
            score += 10
        elif len(callsign) == 8:
            score += 5
        
        # Штраф за слишком длинные
        if len(callsign) > 8:
            score -= 10
        
        return score
    
    def _analyze_structure(self, words):
        """Анализ структуры сообщения"""
        structure = {
            'has_start': False,
            'has_end': False,
            'has_separator': False,
            'has_callsign': False,
            'probable_type': 'unknown',
        }
        
        # Проверка начала и конца
        if 'CQ' in words or 'DE' in words:
            structure['has_start'] = True
        
        if 'SK' in words or 'AR' in words:
            structure['has_end'] = True
        
        if 'BT' in words:
            structure['has_separator'] = True
        
        # Проверка на позывные
        for word in words:
            if self._is_callsign(word):
                structure['has_callsign'] = True
                break
        
        # Определение типа сообщения
        if any(w in self.z_codes for w in words):
            structure['probable_type'] = 'procedural_command'
        elif any(w in self.q_codes for w in words):
            structure['probable_type'] = 'operational_message'
        elif any(w in self.service for w in words):
            structure['probable_type'] = 'emergency'
        elif structure['has_callsign']:
            structure['probable_type'] = 'general_communication'
        
        return structure
    
    def format_bilingual_analysis(self, text_en, text_ru, language='ru'):
        """One display report; keep the per-alphabet detector results unchanged."""
        en = self.detect_codes(text_en or '')
        ru = self.detect_codes(text_ru or '')
        combined = dict(en)
        for field, value in en.items():
            if isinstance(value, list):
                combined[field] = list(value)
                # Retain occurrence counts within each alphabet; do not double
                # the same occurrences merely because both alphabets matched.
                remaining = list(value)
                for item in ru.get(field, []):
                    if item in remaining:
                        remaining.remove(item)
                    else:
                        combined[field].append(item)
        for field in ('check_field', 'message_number', 'urgency_level'):
            if not combined.get(field):
                combined[field] = ru.get(field)
        combined['message_structures'] = [('EN', en['message_structure'])]
        if en['message_structure'] != ru['message_structure']:
            combined['message_structures'].append(('RU', ru['message_structure']))
        else:
            combined['message_structures'][0] = ('EN/RU', en['message_structure'])
        primary = {item['code'] for item in combined['ru_procedural_abbr']}
        combined['soviet_codes'] = [item for item in combined['soviet_codes']
                                    if item['code'] not in primary]
        return self.format_analysis(combined, language=language)

    def format_analysis(self, detected, language='ru'):
        """Форматированный вывод анализа"""
        _ = partial(console_text, language=language)
        lines = []
        lines.append('\n' + '=' * 70)
        lines.append(_('АНАЛИЗ ПРОЦЕДУРНЫХ КОДОВ И КОМАНД'))
        lines.append('=' * 70)

        # Identical EN/RU structure is displayed once. Different structures
        # stay explicitly labelled instead of silently choosing an alphabet.
        structures = detected.get('message_structures', [(None, detected['message_structure'])])
        lines.append(_('\n📋 СТРУКТУРА СООБЩЕНИЯ:'))
        for alphabet, structure in structures:
            if alphabet:
                lines.append('   ' + alphabet + ':')
            lines.append(_('   Тип: {0}', _(self._type_name(structure['probable_type']))))
            lines.append(_('   Имеет начало: {0}', '✓' if structure['has_start'] else '✗'))
            lines.append(_('   Имеет конец: {0}', '✓' if structure['has_end'] else '✗'))
            lines.append(_('   Имеет позывные: {0}', '✓' if structure['has_callsign'] else '✗'))

        # Позывные
        if detected['callsigns']:
            lines.append(_('\n📡 ОБНАРУЖЕННЫЕ ПОЗЫВНЫЕ:'))
            for callsign in detected['callsigns']:
                lines.append(f'   • {callsign}')

        # Номер сообщения и CHECK
        if detected['message_number']:
            lines.append(_('\n🔢 НОМЕР СООБЩЕНИЯ: {0}', detected['message_number']))

        if detected['check_field']:
            lines.append(_('\n✓ CHECK: {0} групп(ы)', detected['check_field']))

        # Уровень срочности
        if detected['urgency_level']:
            lines.append(_('\n⚠️  УРОВЕНЬ СРОЧНОСТИ:'))
            urg = detected['urgency_level']
            lines.append(f"   {urg['level']} — {_(urg['meaning'])}")

        # Prosigns
        if detected['prosigns']:
            lines.append(_('\n🔧 ПРОЦЕДУРНЫЕ ЗНАКИ (PROSIGNS):'))
            for item in detected['prosigns']:
                lines.append(f"   • {item['code']}{'?' if item.get('is_question') else ''} — {_(item['meaning'])}")

        # Q-коды
        if detected['q_codes']:
            lines.append(_('\n🔤 Q-КОДЫ (Международные):'))
            for item in detected['q_codes']:
                lines.append(f"   • {item['code']}{'?' if item.get('is_question') else ''} — {_(item['meaning'])}")

        # Y-коды
        if detected['y_codes']:
            lines.append(_('\n✈️  Y-КОДЫ (Авиационные):'))
            for item in detected['y_codes']:
                lines.append(f"   • {item['code']}{'?' if item.get('is_question') else ''} — {_(item['meaning'])}")

        # Z-коды
        if detected['z_codes']:
            lines.append(_('\n🎖️  Z-КОДЫ (Процедурные):'))
            for item in detected['z_codes']:
                lines.append(f"   • {item['code']}{'?' if item.get('is_question') else ''} — {_(item['meaning'])}")

        # Щ-коды (российские)
        if detected['shch_codes']:
            lines.append(_('\n🇷🇺 Щ-КОДЫ (Российские процедурные):'))
            for item in detected['shch_codes']:
                lines.append(f"   • {item['code']}{'?' if item.get('is_question') else ''} — {_(item['meaning'])}")

        # Российские процедурные сокращения
        if detected.get('ru_procedural_abbr'):
            lines.append(_('\n📋 РОССИЙСКИЕ ПРОЦЕДУРНЫЕ СОКРАЩЕНИЯ:'))
            for item in detected['ru_procedural_abbr']:
                lines.append(f"   • {item['code']}{'?' if item.get('is_question') else ''} — {_(item['meaning'])}")

        # Советские коды
        if detected.get('soviet_codes'):
            lines.append(_('\n🚩 СОВЕТСКИЕ ПРОЦЕДУРНЫЕ КОДЫ:'))
            for item in detected['soviet_codes']:
                lines.append(f"   • {item['code']}{'?' if item.get('is_question') else ''} — {_(item['meaning'])}")

        # Морские коды
        if detected.get('maritime_codes'):
            lines.append(_('\n⚓ МОРСКИЕ КОДЫ (INTERCO):'))
            for item in detected['maritime_codes']:
                lines.append(f"   • {item['code']}{'?' if item.get('is_question') else ''} — {_(item['meaning'])}")

        # Метеокоды
        if detected.get('meteo_codes'):
            lines.append(_('\n🌦️  МЕТЕОРОЛОГИЧЕСКИЕ КОДЫ:'))
            for item in detected['meteo_codes']:
                lines.append(f"   • {item['code']}{'?' if item.get('is_question') else ''} — {_(item['meaning'])}")

        # SINPO коды
        if detected.get('sinpo_codes'):
            lines.append(_('\n📊 SINPO КОДЫ (Оценка качества):'))
            for item in detected['sinpo_codes']:
                lines.append(f"   • {item['code']}{'?' if item.get('is_question') else ''} — {_(item['meaning'])}")

        # CW-сокращения
        if detected['cw_abbreviations']:
            lines.append(_('\n📝 CW-СОКРАЩЕНИЯ:'))
            for item in detected['cw_abbreviations']:
                lines.append(f"   • {item['code']}{'?' if item.get('is_question') else ''} — {_(item['meaning'])}")

        # Служебные сигналы
        if detected['service_signals']:
            lines.append(_('\n🚨 СЛУЖЕБНЫЕ СИГНАЛЫ:'))
            for item in detected['service_signals']:
                lines.append(f"   • {item['signal']} — {_(item['meaning'])}")

        for field, heading in (
            ('arrl_qn_codes', '\n📻 ARRL QN-СИГНАЛЫ:'),
            ('ru_z_codes', '\n🇷🇺 СОВЕТСКИЕ З-КОДЫ:'),
            ('soviet_urgency_levels', '\n⚠️ СОВЕТСКИЕ КАТЕГОРИИ СРОЧНОСТИ:'),
        ):
            if detected.get(field):
                lines.append(_(heading))
                for item in detected[field]:
                    lines.append(f"   • {item['code']}{'?' if item.get('is_question') else ''} — {_(item['meaning'])}")
        if detected.get('rst_reports'):
            lines.append('\n📈 RST:')
            for item in detected['rst_reports']:
                lines.append(f"   • RST {item['value']} (R={item['readability']}, "
                             f"S={item['strength']}, T={item['tone']})")

        # Итог
        total_codes = (
            len(detected['q_codes']) + 
            len(detected.get('y_codes', [])) +
            len(detected['z_codes']) + 
            len(detected['shch_codes']) + 
            len(detected.get('ru_procedural_abbr', [])) +
            len(detected.get('soviet_codes', [])) +
            len(detected.get('maritime_codes', [])) +
            len(detected.get('meteo_codes', [])) +
            len(detected.get('sinpo_codes', [])) +
            len(detected['cw_abbreviations']) + 
            len(detected['prosigns'])
        )
        total_codes += sum(len(detected.get(field, [])) for field in
                           ('arrl_qn_codes', 'ru_z_codes', 'soviet_urgency_levels',
                            'rst_reports', 'service_signals'))
        if total_codes == 0 and not detected.get('urgency_level'):
            lines.append(_('\n💬 Обычное сообщение без специальных кодов'))

        lines.append('\n' + '=' * 70)

        return "\n".join(lines)

    def _type_name(self, type_code):
        """Перевод типа сообщения"""
        types = {
            'procedural_command': 'Процедурная команда',
            'operational_message': 'Оперативное сообщение',
            'emergency': 'Экстренное сообщение',
            'general_communication': 'Общая связь',
            'unknown': 'Неопределено',
        }
        return types.get(type_code, 'Неизвестно')


def analyze_procedural_message(text_en, text_ru):
    """
    Анализ сообщения на наличие процедурных кодов
    
    Args:
        text_en: текст на английском
        text_ru: текст на русском
        
    Returns:
        tuple: (анализ английского, анализ русского)
    """
    detector = ProceduralCodeDetector()
    
    analysis_en = detector.detect_codes(text_en) if text_en else None
    analysis_ru = detector.detect_codes(text_ru) if text_ru else None
    
    return analysis_en, analysis_ru


if __name__ == "__main__":
    # Примеры для тестирования
    test_messages = [
        "CQ CQ DE R1ABC R1ABC PSE K",
        "R2DEF DE R1ABC QSL QTH MOSCOW AR",
        "ZAG ZAK MOLNIYA U5XYZ",
        "SOS SOS DE SHIP123 QTH 45N 30E",
        "QRZ QRM RPT PSE",
    ]
    
    detector = ProceduralCodeDetector()
    
    print("\n🧪 ТЕСТИРОВАНИЕ ДЕТЕКТОРА ПРОЦЕДУРНЫХ КОДОВ\n")
    
    for msg in test_messages:
        print(f"Сообщение: {msg}")
        detected = detector.detect_codes(msg)
        print(detector.format_analysis(detected))
        print("\n")
