"""
Модуль нечеткого поиска (fuzzy matching) для распознавания кодов с ошибками
Используется для улучшения обнаружения Q-кодов, позывных и других элементов
"""
from difflib import SequenceMatcher
from functools import lru_cache
import re

# Попытка использовать оптимизированную версию Левенштейна
try:
    from .levenshtein_optimized import levenshtein_fast
    USE_OPTIMIZED_LEVENSHTEIN = True
except ImportError:
    USE_OPTIMIZED_LEVENSHTEIN = False


@lru_cache(maxsize=1024)
def levenshtein_distance(s1, s2):
    """
    Вычисление расстояния Левенштейна между двумя строками
    (минимальное количество вставок, удалений, замен)
    Кешируется для ускорения повторных вызовов
    Использует оптимизированную numba-версию если доступна
    """
    # Используем оптимизированную версию если доступна
    if USE_OPTIMIZED_LEVENSHTEIN:
        return levenshtein_fast(s1, s2)
    
    # Fallback на стандартную реализацию
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # j+1 вместо j так как previous_row и current_row на 1 длиннее s2
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]
@lru_cache(maxsize=512)
def similarity_ratio(s1, s2):
    """
    Вычисление коэффициента схожести (0.0 - 1.0)
    1.0 = полное совпадение, 0.0 = полностью разные
    Кешируется для ускорения повторных вызовов
    Вычисление коэффициента схожести (0.0 - 1.0)
    1.0 = полное совпадение, 0.0 = полностью разные
    """
    return SequenceMatcher(None, s1, s2).ratio()


def fuzzy_match_q_code(word, q_codes_dict, max_distance=1):
    """
    Нечеткий поиск Q-кода с допуском ошибок
    
    Args:
        word: слово для проверки
        q_codes_dict: словарь Q-кодов {код: описание}
        max_distance: максимальное расстояние Левенштейна (обычно 1-2)
    
    Returns:
        tuple (matched_code, meaning, confidence) или None
    """
    word = word.upper()
    
    # Точное совпадение
    if word in q_codes_dict:
        return (word, q_codes_dict[word], 1.0)
    
    # Нечеткий поиск
    best_match = None
    best_distance = float('inf')
    
    for code in q_codes_dict:
        distance = levenshtein_distance(word, code)
        
        if distance <= max_distance and distance < best_distance:
            best_distance = distance
            best_match = code
    
    if best_match:
        # Вычисляем уверенность (confidence)
        # 0 ошибок = 1.0, 1 ошибка = 0.8, 2 ошибки = 0.6
        confidence = 1.0 - (best_distance * 0.2)
        return (best_match, q_codes_dict[best_match], confidence)
    
    return None


def fuzzy_match_callsign(word, known_callsigns=None, max_distance=1):
    """
    Нечеткий поиск позывного с учетом типичных ошибок
    
    Args:
        word: слово для проверки
        known_callsigns: список известных позывных (опционально)
        max_distance: максимальное расстояние
    
    Returns:
        tuple (matched_callsign, confidence) или (word, confidence_as_callsign)
    """
    word = word.upper()
    
    # Проверка формата позывного (улучшенная эвристика)
    if not _is_likely_callsign(word):
        return None
    
    # Если есть список известных позывных, ищем в нём
    if known_callsigns:
        best_match = None
        best_distance = float('inf')
        
        for callsign in known_callsigns:
            distance = levenshtein_distance(word, callsign)
            
            if distance <= max_distance and distance < best_distance:
                best_distance = distance
                best_match = callsign
        
        if best_match:
            confidence = 1.0 - (best_distance * 0.2)
            return (best_match, confidence)
    
    # Если совпадений нет, но слово похоже на позывной
    confidence = _calculate_callsign_confidence(word)
    if confidence > 0.5:
        return (word, confidence)
    
    return None


def _is_likely_callsign(word):
    """Проверка, похоже ли слово на позывной"""
    if len(word) < 3 or len(word) > 10:
        return False
    
    # Должны быть и буквы, и цифры
    has_letter = any(c.isalpha() for c in word)
    has_digit = any(c.isdigit() for c in word)
    
    if not (has_letter and has_digit):
        return False
    
    # Российские префиксы
    russian_prefixes = ['R', 'U', 'RA', 'RU', 'UA', 'RK', 'RN', 'RZ', 'RW', 'RV']
    for prefix in russian_prefixes:
        if word.startswith(prefix):
            return True
    
    # Другие популярные префиксы
    common_prefixes = ['K', 'W', 'N', 'G', 'DL', 'F', 'I', 'JA', 'VE', 'VK', 'ZL', 'OH']
    for prefix in common_prefixes:
        if word.startswith(prefix):
            return True
    
    # Общий формат: буквы + цифра + буквы
    pattern = r'^[A-Z]{1,3}\d[A-Z]{1,4}$'
    if re.match(pattern, word):
        return True
    
    return False


def _calculate_callsign_confidence(word):
    """Вычисление уверенности что слово - позывной (0.0-1.0)"""
    confidence = 0.0
    
    # Длина в правильном диапазоне
    if 4 <= len(word) <= 7:
        confidence += 0.3
    elif 3 <= len(word) <= 8:
        confidence += 0.2
    
    # Есть цифра
    if any(c.isdigit() for c in word):
        confidence += 0.2
    
    # Российский префикс
    if word.startswith(('R', 'U', 'RA', 'RU', 'UA')):
        confidence += 0.3
    
    # Соотношение букв/цифр
    letters = sum(c.isalpha() for c in word)
    digits = sum(c.isdigit() for c in word)
    if 1 <= digits <= 2 and letters >= 3:
        confidence += 0.2
    
    return min(confidence, 1.0)


def fuzzy_match_prosign(word, prosigns_dict, max_distance=1):
    """
    Нечеткий поиск процедурного знака
    
    Args:
        word: слово для проверки
        prosigns_dict: словарь prosigns {код: описание}
        max_distance: максимальное расстояние
    
    Returns:
        tuple (matched_prosign, meaning, confidence) или None
    """
    word = word.upper()
    
    # Точное совпадение
    if word in prosigns_dict:
        return (word, prosigns_dict[word], 1.0)
    
    # Нечеткий поиск
    best_match = None
    best_distance = float('inf')
    
    for prosign in prosigns_dict:
        distance = levenshtein_distance(word, prosign)
        
        if distance <= max_distance and distance < best_distance:
            best_distance = distance
            best_match = prosign
    
    if best_match:
        confidence = 1.0 - (best_distance * 0.25)  # Строже для prosigns
        return (best_match, prosigns_dict[best_match], confidence)
    
    return None


def contextual_code_enhancement(words, position, detected_codes):
    """
    Контекстный анализ для улучшения распознавания кодов
    
    Args:
        words: список всех слов в тексте
        position: позиция текущего слова
        detected_codes: уже обнаруженные коды
    
    Returns:
        dict с рекомендациями по интерпретации
    """
    context = {
        'is_message_end': False,
        'is_message_start': False,
        'likely_callsign_context': False,
        'likely_number': False
    }
    
    current_word = words[position] if position < len(words) else ''
    prev_word = words[position - 1] if position > 0 else ''
    next_word = words[position + 1] if position + 1 < len(words) else ''
    
    # Проверка на конец сообщения
    # "73" обычно в конце, часто после "TU" (Thank You)
    if current_word in ['73', '88']:
        # Проверяем, близко ли к концу текста
        if position > len(words) * 0.7:
            context['is_message_end'] = True
    
    # Проверка на начало сообщения
    # "CQ" обычно в начале, "DE" перед позывным
    if current_word == 'CQ' and position < len(words) * 0.3:
        context['is_message_start'] = True
    
    if prev_word == 'DE' or current_word == 'DE':
        context['likely_callsign_context'] = True
    
    # Контекст числовых значений
    # "NR" (номер сообщения), "CHECK" (количество слов)
    if prev_word in ['NR', 'CHECK', 'RST']:
        context['likely_number'] = True
    
    return context


def smart_code_detection(text, q_codes, prosigns, z_codes=None, max_errors=1):
    """
    Интеллектуальное обнаружение кодов с нечетким поиском и контекстным анализом
    
    Args:
        text: текст для анализа
        q_codes: словарь Q-кодов
        prosigns: словарь процедурных знаков
        z_codes: словарь Z-кодов (опционально)
        max_errors: максимальное количество ошибок (1-2)
    
    Returns:
        dict с обнаруженными кодами и уверенностью
    """
    words = text.upper().split()
    
    results = {
        'q_codes': [],
        'prosigns': [],
        'callsigns': [],
        'z_codes': [],
        'confidence_stats': {
            'high_confidence': 0,  # >= 0.9
            'medium_confidence': 0,  # 0.7-0.9
            'low_confidence': 0,  # < 0.7
        }
    }
    
    for i, word in enumerate(words):
        # Контекстный анализ
        context = contextual_code_enhancement(words, i, results)
        
        # Поиск Q-кодов
        q_match = fuzzy_match_q_code(word, q_codes, max_distance=max_errors)
        if q_match:
            code, meaning, confidence = q_match
            results['q_codes'].append({
                'word': word,
                'matched_code': code,
                'meaning': meaning,
                'confidence': confidence,
                'exact_match': word == code
            })
            _update_confidence_stats(results['confidence_stats'], confidence)
        
        # Поиск процедурных знаков
        prosign_match = fuzzy_match_prosign(word, prosigns, max_distance=max_errors)
        if prosign_match:
            code, meaning, confidence = prosign_match
            results['prosigns'].append({
                'word': word,
                'matched_code': code,
                'meaning': meaning,
                'confidence': confidence,
                'exact_match': word == code
            })
            _update_confidence_stats(results['confidence_stats'], confidence)
        
        # Поиск Z-кодов
        if z_codes:
            z_match = fuzzy_match_q_code(word, z_codes, max_distance=max_errors)
            if z_match:
                code, meaning, confidence = z_match
                results['z_codes'].append({
                    'word': word,
                    'matched_code': code,
                    'meaning': meaning,
                    'confidence': confidence,
                    'exact_match': word == code
                })
                _update_confidence_stats(results['confidence_stats'], confidence)
        
        # Поиск позывных
        if not q_match and not prosign_match:  # Не ищем позывные в словах, уже определенных как коды
            callsign_match = fuzzy_match_callsign(word)
            if callsign_match:
                matched, confidence = callsign_match
                # Повышаем уверенность если контекст подходящий
                if context['likely_callsign_context']:
                    confidence = min(confidence + 0.1, 1.0)
                
                results['callsigns'].append({
                    'word': word,
                    'matched_callsign': matched,
                    'confidence': confidence,
                    'exact_match': word == matched,
                    'context': context
                })
                _update_confidence_stats(results['confidence_stats'], confidence)
    
    return results


def _update_confidence_stats(stats, confidence):
    """Обновление статистики уверенности"""
    if confidence >= 0.9:
        stats['high_confidence'] += 1
    elif confidence >= 0.7:
        stats['medium_confidence'] += 1
    else:
        stats['low_confidence'] += 1


if __name__ == "__main__":
    # Тестирование модуля
    print("🔍 Модуль Fuzzy Matching для Morse Decoder")
    print("\nПримеры:")
    
    # Тест Q-кодов с ошибками
    q_codes_test = {
        'QRZ': 'Кто меня вызывает?',
        'QTH': 'Мое местоположение',
        'QSL': 'Подтверждаю прием'
    }
    
    test_words = ['QRX', 'QTB', 'QSL', 'QR2']  # QRX близко к QRZ, QTB близко к QTH
    
    for word in test_words:
        match = fuzzy_match_q_code(word, q_codes_test, max_distance=1)
        if match:
            code, meaning, conf = match
            print(f"  '{word}' → '{code}' ({meaning}) [уверенность: {conf:.2f}]")
        else:
            print(f"  '{word}' → не найдено")
    
    # Тест позывных
    print("\nТест позывных:")
    test_callsigns = ['RA3XYZ', 'UA1ABC', 'R5DX', 'K3LR', 'W1AW', 'HELLO', 'TEST123']
    
    for call in test_callsigns:
        match = fuzzy_match_callsign(call)
        if match:
            matched, conf = match
            print(f"  '{call}' → позывной [уверенность: {conf:.2f}]")
        else:
            print(f"  '{call}' → не позывной")
