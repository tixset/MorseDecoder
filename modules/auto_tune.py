"""
Автоматический подбор параметров для оптимального декодирования
"""
import sys
import json
from pathlib import Path
from .morse_decoder import MorseDecoder
from .procedural_codes import ProceduralCodeDetector
import itertools
from multiprocessing import Pool, cpu_count
from functools import partial

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    tqdm = None

def calculate_quality_score(text, stats, codes_analysis):
    """
    Оценка качества декодирования (чем выше, тем лучше)
    """
    if not text:
        return 0
    
    # Базовые метрики
    text_length = len(text)
    error_marks = text.count('□')  # нераспознанные символы
    question_ratio = error_marks / text_length if text_length > 0 else 1.0
    
    # Подсчет распознанных элементов
    total_codes = (
        len(codes_analysis.get('q_codes', [])) +
        len(codes_analysis.get('z_codes', [])) +
        len(codes_analysis.get('prosigns', [])) +
        len(codes_analysis.get('callsigns', []))
    )
    
    # Формула оценки качества
    score = 0
    
    # 1. Длина текста (хорошо, если есть контент)
    score += min(text_length / 10, 100)  # макс 100 баллов
    
    # 2. Штраф за "□" (нераспознанные символы - чем меньше, тем лучше)
    score -= question_ratio * 200  # максимальный штраф 200
    
    # 3. Бонус за распознанные коды
    score += total_codes * 10  # по 10 баллов за каждый код
    
    # 4. Бонус за позывные
    score += len(codes_analysis.get('callsigns', [])) * 5
    
    # 5. WPM должен быть в разумных пределах (5-40)
    wpm = stats.get('wpm', 0)
    if 5 <= wpm <= 40:
        score += 20
    else:
        score -= 30
    
    return score

def _test_params_wrapper(args):
    """Wrapper для multiprocessing - распаковывает аргументы"""
    filepath, pulse_p, dot_dash_p, char_p, word_p, verbose = args
    return test_parameter_combination(filepath, pulse_p, dot_dash_p, char_p, word_p, verbose)

def test_parameter_combination(filepath, pulse_p, dot_dash_p, char_p, word_p, verbose=False):
    """
    Тестирование одной комбинации параметров
    """
    try:
        decoder = MorseDecoder(
            pulse_percentile=pulse_p,
            gap_percentile_dot_dash=dot_dash_p,
            gap_percentile_char=char_p,
            gap_percentile_word=word_p
        )
        
        text_en, text_ru, stats = decoder.process_file(filepath, analyze_procedural=False, verbose=False)
        
        # Сохраняем оба варианта текста
        best_text = text_en if len(text_en) > len(text_ru) else text_ru
        
        # Анализируем коды НА АНГЛИЙСКОЙ ВЕРСИИ (позывные содержат латиницу)
        detector = ProceduralCodeDetector()
        codes = detector.detect_codes(text_en)
        
        # Вычисляем оценку
        score = calculate_quality_score(best_text, stats, codes)
        
        result = {
            'params': {
                'pulse': pulse_p,
                'dot_dash': dot_dash_p,
                'char': char_p,
                'word': word_p
            },
            'text': best_text,
            'text_en': text_en,
            'text_ru': text_ru,
            'stats': stats,
            'codes': codes,
            'score': score,
            'question_ratio': best_text.count('□') / len(best_text) if best_text else 1.0
        }
        
        if verbose:
            print(f"   [{pulse_p}/{dot_dash_p}/{char_p}/{word_p}] → Score: {score:.1f}, "
                  f"WPM: {stats.get('wpm', 0):.1f}, "
                  f"?: {result['question_ratio']*100:.1f}%, "
                  f"Codes: {len(codes.get('callsigns', []))}")
        
        return result
        
    except Exception as e:
        if verbose:
            print(f"   [{pulse_p}/{dot_dash_p}/{char_p}/{word_p}] → Error: {e}")
        return None

def auto_tune_parameters(filepath, mode='fast', lookup_callsigns=False):
    """
    Автоматический подбор параметров
    
    Args:
        filepath: путь к WAV-файлу
        mode: 'fast' - быстрый (меньше комбинаций)
              'thorough' - тщательный (больше комбинаций)
              'extreme' - экстремальный (все возможные комбинации)
        lookup_callsigns: выполнить поиск информации о позывных
    """
    filepath = Path(filepath)
    
    print("="*80)
    print("🎛️  АВТОМАТИЧЕСКИЙ ПОДБОР ПАРАМЕТРОВ")
    print("="*80)
    print(f"Файл: {filepath.name}")
    print(f"Режим: {mode.upper()}")
    print()
    
    # Определяем диапазоны параметров в зависимости от режима
    if mode == 'fast':
        # Быстрый режим - самые популярные значения (12 комбинаций)
        pulse_range = [60, 70, 80]
        dot_dash_range = [55, 60]
        char_range = [75, 85]
        word_range = [90]
    elif mode == 'thorough':
        # Тщательный режим - расширенный диапазон (560 комбинаций)
        pulse_range = [50, 60, 70, 75, 80, 85, 90]
        dot_dash_range = [50, 55, 60, 65]
        char_range = [70, 75, 80, 85, 90]
        word_range = [85, 90, 92, 94]
    else:  # extreme
        # Экстремальный режим - все возможные комбинации (4752 комбинации)
        pulse_range = range(40, 91, 5)  # 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90
        dot_dash_range = range(50, 71, 3)  # 50, 53, 56, 59, 62, 65, 68
        char_range = range(70, 94, 3)  # 70, 73, 76, 79, 82, 85, 88, 91
        word_range = range(85, 96, 2)  # 85, 87, 89, 91, 93, 95
    
    # Генерируем все комбинации
    combinations = list(itertools.product(
        pulse_range,
        dot_dash_range,
        char_range,
        word_range
    ))
    
    total = len(combinations)
    print(f"🔬 Тестирование {total} комбинаций параметров...")
    
    # Определяем количество воркеров (по умолчанию все ядра)
    workers = cpu_count()
    use_parallel = mode in ['thorough', 'extreme'] and total > 50
    
    if use_parallel:
        print(f"⚡ Параллельная обработка на {workers} ядрах")
    print()
    
    best_score = -float('inf')
    best_result = None
    
    # Подготовка аргументов для параллельной обработки
    verbose_flag = (mode == 'extreme')
    args_list = [(filepath, p, d, c, w, False) for p, d, c, w in combinations]
    
    # Параллельная или последовательная обработка
    if use_parallel:
        # Используем multiprocessing Pool
        with Pool(workers) as pool:
            if HAS_TQDM:
                results = list(tqdm(
                    pool.imap(_test_params_wrapper, args_list),
                    total=total,
                    desc="Подбор параметров",
                    unit="комбинация"
                ))
            else:
                results = []
                for i, result in enumerate(pool.imap(_test_params_wrapper, args_list), 1):
                    results.append(result)
                    if i % max(1, total // 10) == 0:
                        print(f"Прогресс: {i}/{total} ({i*100//total}%)")
    else:
        # Последовательная обработка для fast режима
        results = []
        iterator = tqdm(args_list, desc="Подбор параметров", unit="комб") if HAS_TQDM else args_list
        
        for i, args in enumerate(iterator, 1):
            if not HAS_TQDM and i % max(1, total // 10) == 0:
                print(f"Прогресс: {i}/{total} ({i*100//total}%)")
            
            result = _test_params_wrapper(args)
            results.append(result)
    
    # Поиск лучшего результата
    for result in results:
        if result and result['score'] > best_score:
            best_score = result['score']
            best_result = result
    
    print()
    print("="*80)
    print("✅ ОПТИМАЛЬНЫЕ ПАРАМЕТРЫ НАЙДЕНЫ")
    print("="*80)
    
    if best_result:
        params = best_result['params']
        print(f"\n📊 Параметры:")
        print(f"   Pulse Detection:    {params['pulse']}")
        print(f"   Dot-Dash Gap:       {params['dot_dash']}")
        print(f"   Character Gap:      {params['char']}")
        print(f"   Word Gap:           {params['word']}")
        
        print(f"\n📈 Метрики:")
        print(f"   Оценка качества:    {best_result['score']:.1f}")
        print(f"   Скорость:           {best_result['stats'].get('wpm', 0):.1f} WPM")
        print(f"   Символов:           {len(best_result['text'])}")
        print(f"   Ошибок (□):         {best_result['text'].count('□')} ({best_result['question_ratio']*100:.1f}%)")
        print(f"   Позывных:           {len(best_result['codes'].get('callsigns', []))}")
        
        print(f"\n📝 Расшифрованный текст (EN):")
        print(f"{best_result['text_en'][:200]}{'...' if len(best_result['text_en']) > 200 else ''}")
        print(f"\n📝 Расшифрованный текст (RU):")
        print(f"{best_result['text_ru'][:200]}{'...' if len(best_result['text_ru']) > 200 else ''}")
        
        if best_result['codes'].get('callsigns'):
            print(f"\n📡 Обнаруженные позывные:")
            for call_data in best_result['codes']['callsigns'][:10]:
                call = call_data if isinstance(call_data, str) else call_data.get('callsign', '')
                if call:
                    print(f"   • {call}")
        
        print("\n" + "="*80)
        
        # Сохранение результатов в файлы
        save_results(filepath, best_result, params, lookup_callsigns=lookup_callsigns)
        
        return best_result
    else:
        print("❌ Не удалось найти подходящие параметры")
        return None

def save_results(audio_filepath, result, params, lookup_callsigns=False):
    """
    Сохранение результатов в текстовый файл и конфиг
    
    Args:
        audio_filepath: путь к аудиофайлу
        result: результаты декодирования
        params: параметры декодирования
        lookup_callsigns: выполнить поиск информации о позывных
    """
    from datetime import datetime
    from modules.callsign_lookup import CallsignLookup
    
    audio_path = Path(audio_filepath)
    base_path = audio_path.with_suffix('')
    
    # Поиск информации о позывных если запрошено
    callsign_info = {}
    if lookup_callsigns and result['codes'].get('callsigns'):
        print(f"\n🔍 Поиск информации о {len(result['codes']['callsigns'])} позывных...")
        lookup = CallsignLookup()
        for callsign_data in result['codes']['callsigns']:
            # callsign может быть строкой или dict
            callsign = callsign_data if isinstance(callsign_data, str) else callsign_data.get('callsign', '')
            if not callsign:
                continue
            info = lookup.lookup(callsign)
            if info and info.get('found'):
                callsign_info[callsign] = info
                print(f"   ✅ {callsign}: {info.get('country', 'Unknown')}")
            else:
                print(f"   ⚪ {callsign}: информация не найдена")
    
    # Сохранение расшифровки в .txt
    txt_path = base_path.with_suffix('.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("МОРЗЕ-КОД: ДЕКОДИРОВАННАЯ ЗАПИСЬ\n")
        f.write("="*80 + "\n\n")
        
        # Информация о записи
        f.write("## ИНФОРМАЦИЯ О ЗАПИСИ\n\n")
        f.write(f"Файл:           {audio_path.name}\n")
        f.write(f"Дата декодир.:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Длительность:   {result['stats'].get('duration', 0):.1f} сек\n")
        f.write(f"Скорость:       {result['stats'].get('wpm', 0):.1f} WPM\n")
        f.write(f"Качество:       {100 - result['question_ratio']*100:.1f}% (ошибок: {result['question_ratio']*100:.1f}%)\n")
        f.write(f"Язык:           AUTO\n")
        f.write(f"Символов:       {len(result['text'])}\n\n")
        
        # Обнаруженные элементы
        f.write("## ОБНАРУЖЕННЫЕ ЭЛЕМЕНТЫ\n\n")
        
        codes = result['codes']
        callsigns_count = len(codes.get('callsigns', []))
        q_codes_count = len(codes.get('q_codes', []))
        prosigns = codes.get('prosigns', [])
        prosigns_count = len(prosigns) if isinstance(prosigns, (list, dict)) else 0
        cw_abbr_count = len(codes.get('cw_abbreviations', []))
        
        f.write(f"Позывные:       {callsigns_count}\n")
        f.write(f"Q-коды:         {q_codes_count}\n")
        f.write(f"Prosigns:       {prosigns_count}\n")
        f.write(f"CW-сокращения:  {cw_abbr_count}\n\n")
        
        # Расшифрованный текст (английский)
        f.write("="*80 + "\n")
        f.write("РАСШИФРОВАННЫЙ ТЕКСТ (EN)\n")
        f.write("="*80 + "\n\n")
        f.write(result['text_en'] + "\n\n")
        
        # Расшифрованный текст (русский)
        f.write("="*80 + "\n")
        f.write("РАСШИФРОВАННЫЙ ТЕКСТ (RU)\n")
        f.write("="*80 + "\n\n")
        f.write(result['text_ru'] + "\n\n")
        
        # Морзе-код (исходный)
        morse_code = result['stats'].get('morse_code', '')
        if morse_code:
            f.write("="*80 + "\n")
            f.write("МОРЗЕ-КОД (ИСХОДНЫЙ)\n")
            f.write("="*80 + "\n\n")
            f.write(morse_code + "\n\n")
        
        # Технические параметры
        f.write("="*80 + "\n")
        f.write("ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ ДЕКОДИРОВАНИЯ\n")
        f.write("="*80 + "\n\n")
        f.write(f"Порог импульса:        {params['pulse']}\n")
        f.write(f"Обнаружено импульсов:  {result['stats'].get('pulses', 0)}\n")
        f.write(f"Метод декодирования:   Адаптивный (auto-tune)\n")
        f.write(f"Частотный фильтр:      400-1200 Hz\n")
        f.write(f"Оценка качества:       {result['score']:.1f}\n\n")
        
        f.write("Параметры gap-detection:\n")
        f.write(f"  • Dot-Dash Gap:      {params['dot_dash']}\n")
        f.write(f"  • Character Gap:     {params['char']}\n")
        f.write(f"  • Word Gap:          {params['word']}\n\n")
        
        # Расширенная аналитика сигналов (если доступна)
        signal_analysis = result['stats'].get('signal_analysis')
        if signal_analysis:
            f.write("="*80 + "\n")
            f.write("РАСШИРЕННАЯ АНАЛИТИКА СИГНАЛА\n")
            f.write("="*80 + "\n\n")
            
            # Тип модуляции
            modulation = signal_analysis.get('modulation', {})
            f.write("🔊 ТИП МОДУЛЯЦИИ\n")
            f.write("-"*80 + "\n")
            f.write(f"  Тип:                 {modulation.get('type', 'N/A')}\n")
            f.write(f"  Уверенность:         {modulation.get('confidence', 0)}%\n")
            chars = modulation.get('characteristics', {})
            f.write(f"  Доминирующая частота: {chars.get('dominant_frequency', 0):.1f} Hz\n")
            f.write(f"  Ширина полосы:       {chars.get('bandwidth', 0):.1f} Hz\n")
            f.write(f"  Количество пиков:    {chars.get('num_peaks', 0)}\n\n")
            
            # Чистота сигнала
            purity = signal_analysis.get('purity', {})
            f.write("✨ ЧИСТОТА СИГНАЛА\n")
            f.write("-"*80 + "\n")
            f.write(f"  Общая оценка:        {purity.get('purity_score', 0):.1f}/100\n")
            f.write(f"  Дрейф частоты:       {purity.get('chirp', 0):.1f}\n")
            f.write(f"  Щелчки/клики:        {purity.get('clicks', 0)}\n")
            f.write(f"  Уровень шума:        {purity.get('noise_level', 0):.1f}%\n")
            f.write(f"  SNR (оценка):        {purity.get('snr_estimate', 0):.1f} dB\n")
            qrm = 'Да ⚠️' if purity.get('qrm_detected') else 'Нет ✓'
            f.write(f"  QRM (помехи):        {qrm}\n\n")
            
            # Мастерство оператора
            skill = signal_analysis.get('operator_skill', {})
            f.write("👤 МАСТЕРСТВО ОПЕРАТОРА\n")
            f.write("-"*80 + "\n")
            f.write(f"  Уровень:             {skill.get('skill_level', 'N/A')}\n")
            f.write(f"  Общая оценка:        {skill.get('skill_score', 0):.1f}/100\n")
            f.write(f"  Стабильность тайминга: {skill.get('timing_stability', 0):.1f}/100\n")
            f.write(f"  Консистентность ритма: {skill.get('rhythm_consistency', 0):.1f}/100\n")
            f.write(f"  Точка/Тире (ratio):  {skill.get('dot_dash_ratio', 0):.2f} (идеал: 3.0)\n")
            f.write(f"  Вариация:            {skill.get('variance_score', 0):.1f}/100\n\n")
            
            # Интерпретация результатов
            f.write("📊 ИНТЕРПРЕТАЦИЯ\n")
            f.write("-"*80 + "\n")
            
            # Интерпретация чистоты
            purity_score = purity.get('purity_score', 0)
            if purity_score >= 80:
                f.write("  Чистота:             Отличная - минимальные помехи\n")
            elif purity_score >= 60:
                f.write("  Чистота:             Хорошая - допустимый уровень помех\n")
            elif purity_score >= 40:
                f.write("  Чистота:             Средняя - заметные помехи\n")
            else:
                f.write("  Чистота:             Низкая - сильные помехи/искажения\n")
            
            # Интерпретация мастерства
            skill_level = skill.get('skill_level', 'UNKNOWN')
            interpretations = {
                'EXPERT': 'Профессиональный оператор - стабильный и точный',
                'ADVANCED': 'Опытный оператор - хорошая техника',
                'INTERMEDIATE': 'Средний уровень - есть место для улучшений',
                'BEGINNER': 'Начинающий - нестабильный тайминг'
            }
            f.write(f"  Оператор:            {interpretations.get(skill_level, 'Недостаточно данных')}\n\n")
        
        # Детали обнаруженных элементов
        if callsigns_count > 0:
            f.write("="*80 + "\n")
            f.write("ОБНАРУЖЕННЫЕ ПОЗЫВНЫЕ\n")
            f.write("="*80 + "\n\n")
            for call_data in codes['callsigns']:
                # Извлекаем строку позывного
                call = call_data if isinstance(call_data, str) else call_data.get('callsign', '')
                if not call:
                    continue
                    
                # Если есть информация о позывном, добавляем её
                if call in callsign_info:
                    info = callsign_info[call]
                    f.write(f"  • {call}")
                    details = []
                    if info.get('country'):
                        details.append(info['country'])
                    if info.get('name'):
                        details.append(info['name'])
                    if info.get('qth'):
                        details.append(f"QTH: {info['qth']}")
                    if details:
                        f.write(f" ({', '.join(details)})")
                    f.write("\n")
                else:
                    f.write(f"  • {call} (?)\n")
            f.write("\n")
        
        if q_codes_count > 0:
            f.write("="*80 + "\n")
            f.write("Q-КОДЫ\n")
            f.write("="*80 + "\n\n")
            for qcode in codes['q_codes']:
                if isinstance(qcode, dict):
                    f.write(f"  • {qcode.get('code', '?')} - {qcode.get('meaning', 'Unknown')}\n")
                else:
                    f.write(f"  • {qcode}\n")
            f.write("\n")
        
        if prosigns_count > 0:
            f.write("="*80 + "\n")
            f.write("ПРОЦЕДУРНЫЕ ЗНАКИ (PROSIGNS)\n")
            f.write("="*80 + "\n\n")
            
            # Группируем prosigns и подсчитываем повторения
            prosign_counts = {}
            if isinstance(prosigns, dict):
                # Уже сгруппировано
                prosign_counts = prosigns
            elif isinstance(prosigns, list):
                # Группируем список
                for sign in prosigns:
                    if isinstance(sign, dict):
                        code = sign.get('code', '?')
                        meaning = sign.get('meaning', 'Unknown')
                        key = f"{code} - {meaning}"
                        prosign_counts[key] = prosign_counts.get(key, 0) + 1
                    else:
                        prosign_counts[str(sign)] = prosign_counts.get(str(sign), 0) + 1
            
            # Выводим сгруппированные prosigns
            for sign, count in sorted(prosign_counts.items()):
                if count > 1:
                    f.write(f"  • {sign} ({count}×)\n")
                else:
                    f.write(f"  • {sign}\n")
            f.write("\n")
        
        if cw_abbr_count > 0:
            f.write("="*80 + "\n")
            f.write("CW-СОКРАЩЕНИЯ\n")
            f.write("="*80 + "\n\n")
            for abbr in codes['cw_abbreviations']:
                if isinstance(abbr, dict):
                    f.write(f"  • {abbr.get('code', '?')} - {abbr.get('meaning', 'Unknown')}\n")
                else:
                    f.write(f"  • {abbr}\n")
            f.write("\n")
    
    print(f"\n💾 Расшифровка сохранена: {txt_path}")
    
    # Сохранение конфига параметров в .json
    config_path = base_path.with_suffix('.config.json')
    config = {
        'audio_file': audio_path.name,
        'parameters': {
            'pulse_percentile': params['pulse'],
            'gap_percentile_dot_dash': params['dot_dash'],
            'gap_percentile_char': params['char'],
            'gap_percentile_word': params['word']
        },
        'quality_metrics': {
            'score': result['score'],
            'wpm': result['stats'].get('wpm', 0),
            'text_length': len(result['text']),
            'error_count': result['text'].count('□'),  # нераспознанные символы
            'error_ratio': result['question_ratio'],
            'callsigns_found': len(result['codes'].get('callsigns', []))
        }
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Конфигурация сохранена: {config_path}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python auto_tune.py <файл.wav> [режим]")
        print("Режимы: fast (по умолчанию), thorough, extreme")
        sys.exit(1)
    
    filepath = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else 'fast'
    
    auto_tune_parameters(filepath, mode)
