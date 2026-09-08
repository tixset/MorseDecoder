#!/usr/bin/env python3
"""
Morse Decoder CLI - Единый интерфейс командной строки
Декодирование сигналов азбуки Морзе из аудиофайлов WebSDR

Автор: Антон Зеленов (tixset@gmail.com)
GitHub: https://github.com/tixset/MorseDecoder
Лицензия: MIT

Использование:
  python morse_cli.py auto <файл.wav> [--mode MODE] [--lookup-callsigns]
  python morse_cli.py batch <папка> [--mode MODE] [--lookup-callsigns] [--workers N]
  python morse_cli.py multi <файл.wav> [--auto-detect] [--bands BANDS] [--lookup-callsigns]
  python morse_cli.py decode <файл.wav> [--config CONFIG] [--analyze] [--lookup-callsigns]
  python morse_cli.py experiment <файл.wav> [--iterations N]

Примеры:
  python morse_cli.py auto "recording.wav" --mode fast
  python morse_cli.py auto "recording.wav" --lookup-callsigns
  python morse_cli.py batch TrainingData --mode thorough --lookup-callsigns
  python morse_cli.py batch TrainingData --workers 4
  python morse_cli.py multi "recording.wav" --auto-detect
  python morse_cli.py multi "recording.wav" --bands "400-800,1000-1400"
  python morse_cli.py decode "recording.wav" --lookup-callsigns
  python morse_cli.py decode "recording.wav" --config custom.config.json --analyze
  python morse_cli.py experiment "recording.wav" --iterations 50

Примечание:
  Все режимы автоматически распознают Q-коды, позывные и процедурные знаки.
  Используйте --lookup-callsigns для получения информации о позывных через интернет.
  Команда multi позволяет декодировать несколько параллельных сигналов на одной записи.
"""

from modules.console_i18n import console_text as _, set_console_language, get_console_language

from modules.audio_input import AudioLoadError

import argparse
import sys
import os
from pathlib import Path
import json

# Импорты из существующих модулей
from modules.auto_tune import auto_tune_parameters
from modules.analyze_codes import analyze_all_decodings
from modules.morse_decoder import MorseDecoder
from modules.procedural_codes import ProceduralCodeDetector
from modules.callsign_lookup import CallsignLookup, batch_lookup_callsigns
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing


def load_config_params(config_path):
    """
    Загрузка параметров из .config.json файла
    
    Args:
        config_path: путь к .config.json файлу
        
    Returns:
        dict с параметрами или None если файл не найден
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('parameters', {})
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(_('⚠️  Ошибка чтения конфига: {0}', e))
        return None


def cmd_auto(args):
    """Автоматическая оптимизация параметров для одного файла"""
    if not os.path.exists(args.file):
        print(_('❌ Файл не найден: {0}', args.file))
        return 1
    
    print(_('🎯 Автоматическая настройка параметров для: {0}', args.file))
    print(_('⚙️  Режим: {0}', args.mode))
    
    lookup = getattr(args, 'lookup_callsigns', False)
    result = auto_tune_parameters(args.file, mode=args.mode, lookup_callsigns=lookup)
    
    if result is None:
        print(_('❌ Не удалось обработать файл'))
        return 1
    
    print(_('\n✅ Результаты сохранены:'))
    base_name = os.path.splitext(args.file)[0]
    print(f"   📄 {base_name}.txt")
    print(f"   ⚙️  {base_name}.config.json")
    
    return 0


def cmd_batch(args):
    """Пакетная обработка всех WAV-файлов в папке"""
    if not os.path.exists(args.folder):
        print(_('❌ Папка не найдена: {0}', args.folder))
        return 1
    
    folder = Path(args.folder)
    wav_files = sorted(folder.glob("*.wav"))
    if not wav_files:
        print(_('❌ WAV-файлы не найдены в: {0}', args.folder))
        return 1
    
    # Определяем количество воркеров
    workers = getattr(args, 'workers', 0)
    if workers == 0:
        workers = multiprocessing.cpu_count()
    workers = min(workers, len(wav_files))  # Не больше чем файлов
    
    print(_('📂 Найдено файлов: {0}', len(wav_files)))
    print(_('⚙️  Режим анализа: {0}', args.mode))
    if workers > 1:
        print(_('🔄 Параллельных потоков: {0}', workers))
    print("="*80)
    
    results = []
    total_start = time.time()
    
    def process_file(idx_file_tuple):
        """Обработка одного файла (для параллелизации)"""
        idx, wav_file = idx_file_tuple
        try:
            start = time.time()
            lookup = getattr(args, 'lookup_callsigns', False)
            result = auto_tune_parameters(str(wav_file), args.mode, lookup_callsigns=lookup)
            elapsed = time.time() - start
            
            if result:
                file_result = {
                    'file': wav_file.name,
                    'score': result['score'],
                    'wpm': result['stats'].get('wpm', 0),
                    'text_length': len(result['text']),
                    'error_ratio': result['question_ratio'],
                    'callsigns': len(result['codes'].get('callsigns', [])) if isinstance(result['codes'], dict) else 0,
                    'time': elapsed,
                    'success': True
                }
                print(_('✅ [{0}/{1}] {2}: Score={3:.1f}, {4:.1f}с', idx, len(wav_files), wav_file.name, result['score'], elapsed))
                return file_result
            else:
                print(_('⚠️  [{0}/{1}] {2}: не удалось обработать', idx, len(wav_files), wav_file.name))
                return {'file': wav_file.name, 'success': False}
        except Exception as e:
            print(_('❌ [{0}/{1}] {2}: ошибка - {3}', idx, len(wav_files), wav_file.name, e))
            return {'file': wav_file.name, 'success': False, 'error': str(e)}
    
    # Параллельная обработка если workers > 1, иначе последовательная
    if workers > 1:
        print(_('\n🚀 Запуск параллельной обработки ({0} потоков)...\n', workers))
        completed_count = 0
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # Создаем задачи
            futures = {executor.submit(process_file, (idx, f)): f for idx, f in enumerate(wav_files, 1)}
            
            # Собираем результаты по мере выполнения
            for future in as_completed(futures):
                result = future.result()
                if result.get('success', False):
                    results.append(result)
                completed_count += 1
                # Показываем прогресс
                progress = (completed_count / len(wav_files)) * 100
                print(_('📊 Прогресс: {0}/{1} ({2:.1f}%)', completed_count, len(wav_files), progress))
    else:
        print(_('\n📝 Последовательная обработка...\n'))
        for idx, wav_file in enumerate(wav_files, 1):
            print(f"\n{'='*80}")
            print(_('📁 Файл {0}/{1}: {2}', idx, len(wav_files), wav_file.name))
            print(f"{'='*80}")
            
            result = process_file((idx, wav_file))
            if result.get('success', False):
                results.append(result)
    
    total_time = time.time() - total_start
    
    # Поиск информации о позывных если включён --lookup-callsigns
    if hasattr(args, 'lookup_callsigns') and args.lookup_callsigns and results:
        all_callsigns = []
        for r in results:
            # Извлекаем позывные из результата (предполагаем что они есть)
            # Здесь нужно будет получить позывные из файлов
            pass
        
        if all_callsigns:
            callsigns_file = f"{args.folder}/batch_callsigns.txt"
            print(_('\n🔍 Поиск информации о позывных...'))
            batch_lookup_callsigns(list(set(all_callsigns)), callsigns_file, delay=1.0)
    
    # Итоговая статистика
    print("\n\n" + "="*80)
    print(_('📊 ИТОГОВАЯ СТАТИСТИКА'))
    print("="*80)
    print(_('Обработано файлов: {0}/{1}', len(results), len(wav_files)))
    print(_('Общее время: {0:.1f} сек ({1:.1f} мин)', total_time, total_time / 60))
    
    if results:
        print(_('\nСредние показатели:'))
        avg_score = sum(r['score'] for r in results) / len(results)
        avg_wpm = sum(r['wpm'] for r in results) / len(results)
        avg_error = sum(r['error_ratio'] for r in results) / len(results)
        total_callsigns = sum(r['callsigns'] for r in results)
        
        print(_('   Средняя оценка качества: {0:.1f}', avg_score))
        print(_('   Средняя скорость: {0:.1f} WPM', avg_wpm))
        print(_('   Средний процент ошибок: {0:.1f}%', avg_error * 100))
        print(_('   Всего позывных: {0}', total_callsigns))
        
        print(_('\nЛучшие результаты (по оценке качества):'))
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
        for i, r in enumerate(sorted_results[:5], 1):
            print(_('   {0}. {1}: {2:.1f} баллов, {3:.1f} WPM, {4} позывных', i, r['file'], r['score'], r['wpm'], r['callsigns']))
    
    print("\n" + "="*80)
    print(_('\n✅ Обработка завершена'))
    print(_('   📊 Результаты сохранены в файлах *.txt и *.config.json'))
    
    return 0


def cmd_multi(args):
    """
    Декодирование нескольких параллельных сигналов на одной записи
    """
    from modules.multi_signal_decoder import MultiSignalDecoder
    
    if not os.path.exists(args.file):
        print(_('❌ Файл не найден: {0}', args.file))
        return 1
    
    print(_('🎵 ДЕКОДИРОВАНИЕ НЕСКОЛЬКИХ ПАРАЛЛЕЛЬНЫХ СИГНАЛОВ'))
    print(_('📁 Файл: {0}', Path(args.file).name))
    print("="*80)
    
    # Парсим частотные диапазоны если указаны вручную
    frequency_bands = None
    if args.bands:
        try:
            bands_list = []
            for band_str in args.bands.split(','):
                min_f, max_f = map(int, band_str.strip().split('-'))
                bands_list.append((min_f, max_f))
            frequency_bands = bands_list
            print(_('📊 Заданные частотные диапазоны:'))
            for i, (min_f, max_f) in enumerate(frequency_bands, 1):
                print(f"   {i}. {min_f}-{max_f} Hz")
        except Exception as e:
            print(_('⚠️  Ошибка парсинга диапазонов: {0}', e))
            print(_('   Используется автоопределение'))
            frequency_bands = None
    
    # Создаём декодер
    decoder = MultiSignalDecoder(
        sample_rate=8000,
        frequency_bands=frequency_bands,
        auto_detect=args.auto_detect or frequency_bands is None,
        num_peaks=args.max_signals
    )
    
    # Декодируем
    print()
    decode_result = decoder.decode_multi_signal(
        args.file,
        pulse_percentile=85,
        gap_dd=62,
        gap_char=90,
        gap_word=92,
        verbose=True
    )
    
    results = decode_result['signals']
    peak_info = decode_result.get('peak_info')
    
    if not results:
        print(_('\n❌ Сигналы не обнаружены'))
        return 1
    
    # Показываем результаты
    print(f"\n\n{'='*80}")
    print(_('✅ НАЙДЕНО СИГНАЛОВ: {0}', len(results)))
    print(f"{'='*80}\n")
    
    for idx, result in enumerate(results, 1):
        print(_('📡 Сигнал #{0}', idx))
        print(_('   Частота: {0:.0f} Hz ({1}-{2} Hz)', result['center_frequency'], result['frequency_band'][0], result['frequency_band'][1]))
        print(_('   Скорость: {0} WPM', result['wpm']))
        print(_('   Качество: {0:.1f}%', result['quality']))
        print(_('   Импульсов: {0}', result['pulses']))
        print(_('   Сила сигнала: {0:.3f}', result['signal_strength']))
        print(_('\n   📝 Текст:'))
        
        # Разбиваем текст на строки по 80 символов
        text = result['text']
        for i in range(0, len(text), 80):
            line = text[i:i+80]
            print(f"      {line}")
        
        # Анализируем коды
        detector = ProceduralCodeDetector()
        codes = detector.detect_codes(text)
        
        callsigns = codes.get('callsigns', [])
        q_codes = codes.get('q_codes', [])
        prosigns = codes.get('prosigns', [])
        
        if callsigns or q_codes or prosigns:
            print(_('\n   🔍 Обнаруженные коды:'))
            if callsigns:
                calls = [c if isinstance(c, str) else c.get('callsign', '') for c in callsigns]
                print(_('      📡 Позывные: {0}', ', '.join(calls[:5])))
            if q_codes:
                qcodes = [c if isinstance(c, str) else c.get('code', '') for c in q_codes]
                print(_('      📟 Q-коды: {0}', ', '.join(qcodes[:5])))
            if prosigns:
                ps = [c if isinstance(c, str) else c.get('code', '') for c in prosigns]
                print(f"      🔔 Prosigns: {', '.join(ps[:5])}")
        
        print()
    
    # Поиск информации о позывных если включён lookup
    if hasattr(args, 'lookup_callsigns') and args.lookup_callsigns:
        all_callsigns = []
        for result in results:
            detector = ProceduralCodeDetector()
            codes = detector.detect_codes(result['text'])
            callsigns = codes.get('callsigns', [])
            for c in callsigns:
                call = c if isinstance(c, str) else c.get('callsign', '')
                if call:
                    all_callsigns.append(call)
        
        if all_callsigns:
            print(_('\n🔍 Поиск информации о {0} уникальных позывных...', len(set(all_callsigns))))
            lookup = CallsignLookup()
            for call in set(all_callsigns):
                info = lookup.lookup(call)
                if info:
                    print(f"   ✅ {call}: {info.get('country', 'Unknown')}")
                else:
                    print(_('   ⚪ {0}: информация не найдена', call))
    
    # Сохраняем результаты в TXT
    txt_output = Path(args.file).with_suffix('.multi.txt')
    from datetime import datetime
    
    with open(txt_output, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("🎵 ДЕКОДИРОВАНИЕ НЕСКОЛЬКИХ ПАРАЛЛЕЛЬНЫХ СИГНАЛОВ\n")
        f.write("="*80 + "\n\n")
        
        f.write("📁 ИНФОРМАЦИЯ О ФАЙЛЕ\n")
        f.write("-"*80 + "\n\n")
        f.write(f"   Файл:              {Path(args.file).name}\n")
        f.write(f"   Дата обработки:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"   Обнаружено:        {len(results)} сигнал(ов)\n")
        
        # Добавляем предупреждение если это одиночный сигнал
        if peak_info and peak_info.get('is_single_signal'):
            f.write(f"\n⚠️  ВНИМАНИЕ\n")
            f.write("-"*80 + "\n\n")
            f.write(f"   {peak_info.get('warning', 'Обнаружен одиночный сигнал')}\n\n")
            f.write(f"   💡 РЕКОМЕНДАЦИЯ: Для одиночных сигналов рекомендуется использовать\n")
            f.write(f"      обычное декодирование, которое может дать лучшие результаты:\n\n")
            f.write(f"      morse_cli.py auto \"{Path(args.file).name}\"\n\n")
            f.write(f"   📊 ПРИЧИНА: Multi-signal режим разделяет один сигнал на несколько\n")
            f.write(f"      частотных диапазонов, что может привести к потере информации\n")
            f.write(f"      и меньшему количеству распознанных позывных и команд.\n")
        
        if peak_info:
            f.write(f"\n📡 АНАЛИЗ ЧАСТОТНОГО СПЕКТРА\n")
            f.write("-"*80 + "\n\n")
            f.write(f"   Обнаружено пиков:  {peak_info.get('count', 0)}\n")
            if peak_info.get('frequencies'):
                f.write(f"   Частоты пиков:     {', '.join(f'{f:.0f} Hz' for f in peak_info['frequencies'])}\n")
            if peak_info.get('amplitudes'):
                f.write(f"   Амплитуды:         {', '.join(f'{a:.2f}' for a in peak_info['amplitudes'])}\n")
        
        f.write("\n")
        
        for idx, result in enumerate(results, 1):
            f.write("\n" + "="*80 + "\n")
            f.write(f"📡 СИГНАЛ #{idx} из {len(results)}\n")
            f.write("="*80 + "\n\n")
            
            f.write("🔧 ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ\n")
            f.write("-"*80 + "\n\n")
            f.write(f"   Частотный диапазон:     {result['frequency_band'][0]}-{result['frequency_band'][1]} Hz\n")
            f.write(f"   Центральная частота:    {result['center_frequency']:.0f} Hz\n")
            f.write(f"   Скорость передачи:      {result['wpm']} WPM\n")
            f.write(f"   Качество декодирования: {result['quality']:.1f}%\n")
            f.write(f"   Обнаружено импульсов:   {result['pulses']}\n")
            f.write(f"   Сила сигнала:           {result['signal_strength']:.3f}\n\n")
            
            # Расширенная аналитика сигнала (если доступна)
            if result.get('signal_analysis'):
                analysis = result['signal_analysis']
                
                f.write("="*80 + "\n")
                f.write("📊 РАСШИРЕННАЯ АНАЛИТИКА СИГНАЛА\n")
                f.write("="*80 + "\n\n")
                
                # Тип модуляции
                if 'modulation' in analysis:
                    mod = analysis['modulation']
                    f.write("🔊 ТИП МОДУЛЯЦИИ\n")
                    f.write("-"*80 + "\n")
                    f.write(f"   Тип:                 {mod.get('type', 'Н/Д')}\n")
                    f.write(f"   Уверенность:         {mod.get('confidence', 0):.1f}%\n")
                    f.write(f"   Доминирующая частота: {mod.get('dominant_frequency', 0):.1f} Hz\n")
                    f.write(f"   Ширина полосы:       {mod.get('bandwidth', 0):.1f} Hz\n")
                    if mod.get('num_peaks'):
                        f.write(f"   Количество пиков:    {mod['num_peaks']}\n")
                    f.write("\n")
                
                # Чистота сигнала
                if 'purity' in analysis:
                    pur = analysis['purity']
                    f.write("✨ ЧИСТОТА СИГНАЛА\n")
                    f.write("-"*80 + "\n")
                    f.write(f"   Общая оценка:        {pur.get('purity_score', 0):.1f}/100\n")
                    f.write(f"   Дрейф частоты:       {pur.get('chirp', 0):.1f}\n")
                    f.write(f"   Щелчки/клики:        {pur.get('clicks', 0)}\n")
                    f.write(f"   Уровень шума:        {pur.get('noise_level', 0):.1f}%\n")
                    f.write(f"   SNR (оценка):        {pur.get('snr_estimate', 0):.1f} dB\n")
                    f.write(f"   QRM (помехи):        {'Да ⚠️' if pur.get('qrm', False) else 'Нет ✅'}\n")
                    f.write("\n")
                
                # Мастерство оператора
                if 'operator_skill' in analysis:
                    skill = analysis['operator_skill']
                    f.write("👤 МАСТЕРСТВО ОПЕРАТОРА\n")
                    f.write("-"*80 + "\n")
                    f.write(f"   Уровень:             {skill.get('skill_level', 'Н/Д')}\n")
                    f.write(f"   Общая оценка:        {skill.get('skill_score', 0):.1f}/100\n")
                    f.write(f"   Стабильность тайминга: {skill.get('timing_stability', 0):.1f}/100\n")
                    f.write(f"   Консистентность ритма: {skill.get('rhythm_consistency', 0):.1f}/100\n")
                    f.write(f"   Точка/Тире (ratio):  {skill.get('dot_dash_ratio', 0):.2f} (идеал: 3.0)\n")
                    f.write(f"   Вариация:            {skill.get('variance_score', 0):.1f}/100\n")
                    f.write("\n")
                
                # Интерпретация
                f.write("📊 ИНТЕРПРЕТАЦИЯ\n")
                f.write("-"*80 + "\n")
                
                # Интерпретация чистоты
                if 'purity' in analysis:
                    purity_score = analysis['purity'].get('purity_score', 0)
                    if purity_score >= 80:
                        f.write("   Чистота:             Отличная - минимальные помехи\n")
                    elif purity_score >= 60:
                        f.write("   Чистота:             Хорошая - незначительные помехи\n")
                    elif purity_score >= 40:
                        f.write("   Чистота:             Средняя - заметные помехи\n")
                    else:
                        f.write("   Чистота:             Низкая - сильные помехи/искажения\n")
                
                # Интерпретация оператора
                if 'operator_skill' in analysis:
                    skill_level = analysis['operator_skill'].get('skill_level', 'UNKNOWN')
                    if skill_level == 'EXPERT':
                        f.write("   Оператор:            Эксперт - отличная техника\n")
                    elif skill_level == 'ADVANCED':
                        f.write("   Оператор:            Опытный оператор - хорошая техника\n")
                    elif skill_level == 'INTERMEDIATE':
                        f.write("   Оператор:            Средний уровень - есть над чем работать\n")
                    elif skill_level == 'BEGINNER':
                        f.write("   Оператор:            Начинающий - нестабильный тайминг\n")
                
                f.write("\n")
            
            f.write("="*80 + "\n")
            f.write("📝 РАСШИФРОВАННЫЙ ТЕКСТ\n")
            f.write("="*80 + "\n\n")
            
            # Разбиваем текст на строки по 75 символов с отступом
            text = result['text']
            if text:
                for i in range(0, len(text), 75):
                    line = text[i:i+75]
                    f.write(f"   {line}\n")
            else:
                f.write("   (пусто)\n")
            f.write("\n")
            
            # Анализируем коды для каждого сигнала
            detector = ProceduralCodeDetector()
            codes = detector.detect_codes(result['text'])
            
            callsigns = codes.get('callsigns', [])
            q_codes = codes.get('q_codes', [])
            prosigns = codes.get('prosigns', [])
            cw_abbrevs = codes.get('cw_abbreviations', [])
            
            if callsigns or q_codes or prosigns or cw_abbrevs:
                f.write("="*80 + "\n")
                f.write("🔍 ОБНАРУЖЕННЫЕ ЭЛЕМЕНТЫ\n")
                f.write("="*80 + "\n\n")
                
                if callsigns:
                    f.write(f"📡 Позывные ({len(callsigns)}):\n")
                    f.write("-"*80 + "\n")
                    for c in callsigns:
                        call = c if isinstance(c, str) else c.get('callsign', '')
                        f.write(f"   • {call}\n")
                    f.write("\n")
                
                if q_codes:
                    f.write(f"📟 Q-коды ({len(q_codes)}):\n")
                    f.write("-"*80 + "\n")
                    for q in q_codes:
                        if isinstance(q, dict):
                            f.write(f"   • {q.get('code', '')}: {q.get('meaning', '')}\n")
                        else:
                            f.write(f"   • {q}\n")
                    f.write("\n")
                
                if prosigns:
                    f.write(f"🔔 Процедурные знаки (Prosigns) ({len(prosigns)}):\n")
                    f.write("-"*80 + "\n")
                    for p in prosigns:
                        if isinstance(p, dict):
                            f.write(f"   • {p.get('code', '')}: {p.get('meaning', '')}\n")
                        else:
                            f.write(f"   • {p}\n")
                    f.write("\n")
                
                if cw_abbrevs:
                    f.write(f"✂️  CW-сокращения ({len(cw_abbrevs)}):\n")
                    f.write("-"*80 + "\n")
                    for cw in cw_abbrevs:
                        if isinstance(cw, dict):
                            f.write(f"   • {cw.get('code', '')}: {cw.get('meaning', '')}\n")
                        else:
                            f.write(f"   • {cw}\n")
                    f.write("\n")
            else:
                f.write("="*80 + "\n")
                f.write("🔍 ОБНАРУЖЕННЫЕ ЭЛЕМЕНТЫ\n")
                f.write("="*80 + "\n\n")
                f.write("   (элементы не обнаружены)\n\n")
        
        # Итоговая сводка
        f.write("\n" + "="*80 + "\n")
        f.write("📊 ИТОГОВАЯ СВОДКА\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"   Всего сигналов:          {len(results)}\n")
        avg_quality = sum(r['quality'] for r in results) / len(results) if results else 0
        avg_wpm = sum(r['wpm'] for r in results) / len(results) if results else 0
        total_pulses = sum(r['pulses'] for r in results)
        f.write(f"   Средняя скорость:        {avg_wpm:.1f} WPM\n")
        f.write(f"   Среднее качество:        {avg_quality:.1f}%\n")
        f.write(f"   Всего импульсов:         {total_pulses}\n\n")
        
        # Таблица сравнения сигналов
        if len(results) > 1:
            f.write("-"*80 + "\n")
            f.write("📈 СРАВНЕНИЕ СИГНАЛОВ\n")
            f.write("-"*80 + "\n\n")
            f.write("   №  | Частота (Hz) | WPM     | Качество | Импульсов\n")
            f.write("   " + "-"*60 + "\n")
            for idx, r in enumerate(results, 1):
                freq_str = f"{r['center_frequency']:.0f}"
                wpm_str = f"{r['wpm']}"
                qual_str = f"{r['quality']:.1f}%"
                pulses_str = f"{r['pulses']}"
                f.write(f"   {idx:<3}| {freq_str:^12} | {wpm_str:^7} | {qual_str:^8} | {pulses_str:^9}\n")
            f.write("\n")
        
        f.write("-"*80 + "\n")
        f.write("ℹ️  ПРИМЕЧАНИЯ\n")
        f.write("-"*80 + "\n\n")
        f.write("   • Сигналы отсортированы по качеству декодирования\n")
        f.write("     (от лучшего к худшему)\n")
        f.write("   • Символ '□' в тексте означает нераспознанный символ\n")
        f.write("   • Символ '?' - это настоящий знак вопроса из морзе (··--··)\n")
        f.write("   • WPM = Words Per Minute (слова в минуту)\n")
        f.write("   • Частотный диапазон показывает полосу фильтра\n\n")
        
        f.write("="*80 + "\n")
        f.write(f"✅ Обработка завершена: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n")
    
    # Сохраняем результаты в JSON
    output_file = Path(args.file).with_suffix('.multi.json')
    import json
    with open(output_file, 'w', encoding='utf-8') as f:
        # Конвертируем результаты для JSON (удаляем numpy типы)
        json_results = []
        for r in results:
            json_r = {
                'frequency_band': r['frequency_band'],
                'center_frequency': float(r['center_frequency']),
                'text': r['text'],
                'wpm': int(r['wpm']),
                'quality': float(r['quality']),
                'signal_strength': float(r['signal_strength']),
                'pulses': int(r['pulses'])
            }
            json_results.append(json_r)
        
        output_data = {
            'file': args.file,
            'total_signals': len(results),
            'signals': json_results
        }
        
        # Добавляем информацию о пиках если есть
        if peak_info:
            output_data['peak_analysis'] = {
                'peak_count': peak_info.get('count', 0),
                'frequencies': [float(f) for f in peak_info.get('frequencies', [])],
                'amplitudes': [float(a) for a in peak_info.get('amplitudes', [])],
                'is_single_signal': peak_info.get('is_single_signal', False),
                'warning': peak_info.get('warning')
            }
        
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(_('\n💾 Результаты сохранены:'))
    print(f"   📄 {txt_output}")
    print(f"   📊 {output_file}")
    print(_('\n✅ Декодирование завершено'))
    
    return 0


def cmd_decode(args):
    """
    Декодирование файла с параметрами из .config.json
    """
    if not os.path.exists(args.file):
        print(_('❌ Файл не найден: {0}', args.file))
        return 1
    
    # Определяем путь к конфигу
    if args.config:
        config_path = args.config
    else:
        # Ищем config рядом с файлом
        base_path = Path(args.file).with_suffix('')
        config_path = str(base_path) + '.config.json'
    
    # Загружаем параметры
    params = load_config_params(config_path)
    
    if params is None:
        print(_('❌ Конфиг не найден: {0}', config_path))
        print(_('💡 Создайте конфиг командой: morse_cli.py auto {0}', args.file))
        return 1
    
    print(_('📁 Декодирование: {0}', Path(args.file).name))
    print(_('⚙️  Параметры из: {0}', Path(config_path).name))
    print(f"   • Pulse Detection:  {params.get('pulse_percentile', 60)}")
    print(f"   • Dot-Dash Gap:     {params.get('gap_percentile_dot_dash', 60)}")
    print(f"   • Character Gap:    {params.get('gap_percentile_char', 75)}")
    print(f"   • Word Gap:         {params.get('gap_percentile_word', 90)}")
    print()
    
    # Создаем декодер с параметрами из конфига
    decoder = MorseDecoder(
        pulse_percentile=params.get('pulse_percentile', 60),
        gap_percentile_dot_dash=params.get('gap_percentile_dot_dash', 60),
        gap_percentile_char=params.get('gap_percentile_char', 75),
        gap_percentile_word=params.get('gap_percentile_word', 90),
        auto_frequency=params.get('auto_frequency', True)
    )
    
    # Обработка файла
    text_en, text_ru, stats = decoder.process_file(args.file, analyze_procedural=True, verbose=True)
    if stats.get('error'):
        return 1
    
    # Выбираем лучший вариант
    if text_en and text_ru:
        quality_en = 100 - (text_en.count('□') / len(text_en) * 100) if text_en else 0
        quality_ru = 100 - (text_ru.count('□') / len(text_ru) * 100) if text_ru else 0
        
        print(_('\n📊 Доля символов без □ (не точность распознавания):'))
        print(_('   🇬🇧 Английский: {0:.1f}%', quality_en))
        print(_('   🇷🇺 Русский:    {0:.1f}%', quality_ru))
        
    # Анализ процедурных кодов если запрошен
    if hasattr(args, 'analyze') and args.analyze:
        detector = ProceduralCodeDetector()
        best_text = text_en if len(text_en) >= len(text_ru) else text_ru
        codes = detector.detect_codes(best_text)
        
        print(_('\n🔍 Обнаружено:'))
        print(_('   📡 Позывные:      {0}', len(codes.get('callsigns', []))))
        print(_('   📟 Q-коды:        {0}', len(codes.get('q_codes', []))))
        print(f"   🔤 Prosigns:      {len(codes.get('prosigns', []))}")
        print(_('   📝 CW-сокращения: {0}', len(codes.get('cw_abbreviations', []))))
    
    print(_('\n✅ Декодирование завершено'))
    return 0





def cmd_experiment(args):
    """Экспериментальный режим с вариацией параметров"""
    if not os.path.exists(args.file):
        print(_('❌ Файл не найден: {0}', args.file))
        return 1
    
    print(_('🧪 ЭКСПЕРИМЕНТАЛЬНЫЙ РЕЖИМ'))
    print(_('📁 Файл: {0}', args.file))
    print(_('🔄 Итераций: {0}', args.iterations))
    print(_('🎯 Цель: поиск Q/Z-кодов, CW-сокращений, осмысленного текста\n'))
    
    best_results = []
    code_detector = ProceduralCodeDetector()
    
    # Экспериментальные диапазоны параметров
    pulse_percentile_range = [70, 75, 80, 85, 90]
    gap_dot_dash_range = [55, 60, 62, 65, 70]
    gap_char_range = [85, 88, 90, 92, 95]
    min_freq_range = [300, 400, 500, 600]
    max_freq_range = [1000, 1200, 1500, 2000]
    
    import itertools
    import random
    
    # Генерируем все комбинации и выбираем случайные
    all_combinations = list(itertools.product(
        pulse_percentile_range,
        gap_dot_dash_range,
        gap_char_range,
        min_freq_range,
        max_freq_range
    ))
    selected_combinations = random.sample(all_combinations, min(args.iterations, len(all_combinations)))
    
    print(_('🔬 Будет протестировано комбинаций: {0}\n', len(selected_combinations)))
    
    for idx, (pulse_perc, gap_dd, gap_char, min_f, max_f) in enumerate(selected_combinations, 1):
        print(f"[{idx}/{len(selected_combinations)}] Pulse={pulse_perc}, Gap_DD={gap_dd}, Gap_Char={gap_char}, Freq={min_f}-{max_f}")
        
        # Создаём декодер с этими параметрами
        decoder = MorseDecoder(
            pulse_percentile=pulse_perc,
            gap_percentile_dot_dash=gap_dd,
            gap_percentile_char=gap_char,
            auto_frequency=False,
            min_freq=min_f,
            max_freq=max_f
        )
        
        # Загружаем и обрабатываем
        audio, sample_rate = decoder.load_audio(args.file)
        filtered = decoder.bandpass_filter(audio, sample_rate)
        envelope = decoder.envelope_detection(filtered, sample_rate)
        pulses, gaps = decoder.detect_pulses(envelope, sample_rate)
        
        if not pulses:
            # Нет импульсов - пропускаем
            continue
        
        morse_letters = decoder.classify_morse(pulses, gaps)
        decoded_text = decoder.decode_morse(morse_letters, language='ru')
        
        # Ищем коды
        detected_codes = code_detector.detect_codes(decoded_text)
        
        # Подсчитываем метрики (нераспознанные символы обозначены как □)
        num_questions = decoded_text.count('□')
        text_length = len(decoded_text)
        error_rate = (num_questions / text_length * 100) if text_length > 0 else 100
        
        # Считаем найденные коды (теперь это списки словарей или списки строк)
        total_codes = (
            len(detected_codes.get('q_codes', [])) +
            len(detected_codes.get('z_codes', [])) +
            len(detected_codes.get('shch_codes', [])) +
            len(detected_codes.get('RU_PROCEDURAL_ABBR', [])) +
            len(detected_codes.get('cw_abbreviations', [])) +
            len(detected_codes.get('prosigns', [])) +
            len(detected_codes.get('callsigns', []))
        )
        
        # Оценка читаемости (простая метрика: длина без '?')
        readable_chars = text_length - num_questions
        readability_score = (readable_chars / text_length * 100) if text_length > 0 else 0
        
        quality_score = total_codes * 100 + readability_score - error_rate
        
        result = {
            'pulse_percentile': pulse_perc,
            'gap_dot_dash': gap_dd,
            'gap_char': gap_char,
            'min_freq': min_f,
            'max_freq': max_f,
            'text': decoded_text[:500],  # Первые 500 символов
            'codes': detected_codes,
            'total_codes': total_codes,
            'error_rate': error_rate,
            'readability': readability_score,
            'quality_score': quality_score,
            'text_length': text_length
        }
        
        best_results.append(result)
        
        if total_codes > 0:
            print(_('  ✨ Найдено кодов: {0} | Читаемость: {1:.1f}% | Ошибки: {2:.1f}%', total_codes, readability_score, error_rate))
        else:
            print(_('  ⚪ Коды не найдены | Читаемость: {0:.1f}% | Ошибки: {1:.1f}%', readability_score, error_rate))
    
    # Сортируем по качеству
    best_results.sort(key=lambda x: x['quality_score'], reverse=True)
    
    # Сохраняем результаты
    import json
    output_file = "experiment_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'file': args.file,
            'iterations': len(selected_combinations),
            'best_results': best_results[:20],  # Топ-20
            'summary': {
                'max_codes_found': max(r['total_codes'] for r in best_results),
                'best_readability': max(r['readability'] for r in best_results),
                'min_error_rate': min(r['error_rate'] for r in best_results)
            }
        }, f, ensure_ascii=False, indent=2)
    
    # Показываем лучшие результаты
    print(f"\n{'='*70}")
    print(_('🏆 ТОП-5 ЛУЧШИХ РЕЗУЛЬТАТОВ:'))
    print(f"{'='*70}\n")
    
    for idx, result in enumerate(best_results[:5], 1):
        print(_('#{0} | Качество: {1:.1f}', idx, result['quality_score']))
        print(f"    Pulse: {result['pulse_percentile']} | Gap_DD: {result['gap_dot_dash']} | Gap_Char: {result['gap_char']}")
        print(f"    Freq: {result['min_freq']}-{result['max_freq']} Hz")
        print(_('    Кодов найдено: {0}', result['total_codes']))
        print(_('    Читаемость: {0:.1f}% | Ошибки: {1:.1f}%', result['readability'], result['error_rate']))
        
        codes = result['codes']
        # Обрабатываем коды с учетом нового формата (могут быть списки dict или списки str)
        if codes.get('q_codes'):
            q_items = codes['q_codes']
            if q_items and isinstance(q_items[0], dict):
                q_list = [item['code'] for item in q_items[:5]]
            else:
                q_list = q_items[:5]
            print(_('    📻 Q-коды: {0}', ', '.join(q_list)))
        
        if codes.get('z_codes'):
            z_items = codes['z_codes']
            if z_items and isinstance(z_items[0], dict):
                z_list = [item['code'] for item in z_items[:5]]
            else:
                z_list = z_items[:5]
            print(_('    🔒 Z-коды: {0}', ', '.join(z_list)))
        
        if codes.get('cw_abbreviations'):
            cw_items = codes['cw_abbreviations']
            if cw_items and isinstance(cw_items[0], dict):
                cw_list = [item['code'] for item in cw_items[:5]]
            else:
                cw_list = cw_items[:5]
            print(f"    📝 CW: {', '.join(cw_list)}")
        
        if codes.get('prosigns'):
            ps_items = codes['prosigns']
            if ps_items and isinstance(ps_items[0], dict):
                ps_list = [item['code'] for item in ps_items[:5]]
            else:
                ps_list = ps_items[:5]
            print(f"    🔔 Prosigns: {', '.join(ps_list)}")
        
        if codes.get('RU_PROCEDURAL_ABBR'):
            ru_items = codes['RU_PROCEDURAL_ABBR']
            if ru_items and isinstance(ru_items[0], dict):
                ru_list = [item['code'] for item in ru_items[:5]]
            else:
                ru_list = ru_items[:5]
            print(f"    🇷🇺 RUS: {', '.join(ru_list)}")
        
        if codes.get('callsigns'):
            call_items = codes['callsigns']
            if call_items and isinstance(call_items[0], dict):
                call_list = [item['callsign'] for item in call_items[:5]]
            else:
                call_list = call_items[:5]
            print(_('    📡 Позывные: {0}', ', '.join(call_list)))
        
        # Показываем фрагмент текста
        preview = result['text'][:200].replace('\n', ' ')
        print(_('    Текст: {0}...', preview))
        print()
    
    print(_('✅ Результаты сохранены: {0}', output_file))
    
    return 0


def _main(argv):
    """Главная функция CLI"""
    parser = argparse.ArgumentParser(
        description=_('Morse Decoder - декодирование азбуки Морзе из WebSDR записей'),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_('\nПримеры использования:\n  \n  Автонастройка одного файла:\n    python morse_cli.py auto recording.wav\n    python morse_cli.py auto recording.wav --mode thorough\n    python morse_cli.py auto recording.wav --lookup-callsigns\n  \n  Пакетная обработка папки:\n    python morse_cli.py batch TrainingData\n    python morse_cli.py batch TrainingData --mode extreme\n    python morse_cli.py batch TrainingData --lookup-callsigns\n  \n  Декодирование нескольких параллельных сигналов:\n    python morse_cli.py multi recording.wav --auto-detect\n    python morse_cli.py multi recording.wav --bands "400-800,1000-1400,1500-1900"\n    python morse_cli.py multi recording.wav --speed-range "15-40"\n  \n  Экспериментальный поиск кодов:\n    python morse_cli.py experiment recording.wav --iterations 100\n\nРежимы обработки (--mode):\n  fast      - быстрая обработка (меньше вариантов параметров) [по умолчанию]\n  thorough  - тщательная обработка (средний баланс)\n  extreme   - максимальная точность (много времени)\n        ')
    )
    
    subparsers = parser.add_subparsers(dest='command', help=_('Доступные команды'))
    
    # Команда: auto
    parser_auto = subparsers.add_parser('auto', help=_('Автонастройка параметров для файла'))
    parser_auto.add_argument('file', help=_('Путь к аудиофайлу (WAV, MP3, OGG)'))
    parser_auto.add_argument('--mode', '-m', default='fast', 
                            choices=['fast', 'thorough', 'extreme'],
                            help=_('Режим обработки (по умолчанию: fast)'))
    parser_auto.add_argument('--lookup-callsigns', '--lookup', action='store_true',
                           help=_('Искать информацию о найденных позывных через API'))
    parser_auto.set_defaults(func=cmd_auto)
    
    # Команда: batch
    parser_batch = subparsers.add_parser('batch', help=_('Пакетная обработка папки'))
    parser_batch.add_argument('folder', help=_('Путь к папке с WAV-файлами'))
    parser_batch.add_argument('--mode', '-m', default='fast',
                             choices=['fast', 'thorough', 'extreme'],
                             help=_('Режим обработки (по умолчанию: fast)'))
    parser_batch.add_argument('--lookup-callsigns', '--lookup', action='store_true',
                            help=_('Искать информацию о найденных позывных через API'))
    parser_batch.add_argument('--workers', '-w', type=int, default=0,
                            help=_('Количество параллельных потоков (0=авто, 1=последовательно)'))
    parser_batch.set_defaults(func=cmd_batch)
    
    # Команда: decode (декодирование с параметрами из .config.json)
    parser_decode = subparsers.add_parser('decode', help=_('Декодирование с параметрами из .config.json'))
    parser_decode.add_argument('file', help=_('Путь к аудиофайлу (WAV, MP3, OGG)'))
    parser_decode.add_argument('--config', '-c', help=_('Путь к .config.json (по умолчанию: рядом с файлом)'))
    parser_decode.add_argument('--analyze', '-a', action='store_true',
                              help=_('Провести анализ процедурных кодов'))
    parser_decode.add_argument('--lookup-callsigns', '--lookup', action='store_true',
                              help=_('Искать информацию о найденных позывных через API'))
    parser_decode.set_defaults(func=cmd_decode)
    
    # Команда: multi (декодирование нескольких параллельных сигналов)
    parser_multi = subparsers.add_parser('multi', help=_('Декодирование нескольких параллельных сигналов'))
    parser_multi.add_argument('file', help=_('Путь к аудиофайлу (WAV, MP3, OGG)'))
    parser_multi.add_argument('--auto-detect', '-a', action='store_true', default=True,
                             help=_('Автоматически определять частотные диапазоны (по умолчанию)'))
    parser_multi.add_argument('--bands', '-b', type=str,
                             help=_('Частотные диапазоны вручную, например: "400-800,900-1300,1400-1800"'))
    parser_multi.add_argument('--max-signals', '-m', type=int, default=3,
                             help=_('Максимальное количество сигналов для обнаружения (по умолчанию: 3)'))
    parser_multi.add_argument('--speed-range', '-s', type=str, default="10-50",
                             help=_('Диапазон скоростей WPM для поиска (по умолчанию: 10-50)'))
    parser_multi.add_argument('--lookup-callsigns', '--lookup', action='store_true',
                             help=_('Искать информацию о найденных позывных через API'))
    parser_multi.set_defaults(func=cmd_multi)
    
    # Команда: experiment
    parser_exp = subparsers.add_parser('experiment', help=_('Экспериментальный поиск кодов'))
    parser_exp.add_argument('file', help=_('Путь к аудиофайлу (WAV, MP3, OGG)'))
    parser_exp.add_argument('--iterations', '-n', type=int, default=30,
                           help=_('Количество экспериментов (по умолчанию: 30)'))
    parser_exp.set_defaults(func=cmd_experiment)
    
    for command_parser in (parser, parser_auto, parser_batch, parser_decode, parser_multi, parser_exp):
        command_parser.add_argument('--ru', action='store_true', default=argparse.SUPPRESS,
                                    help=_('Выводить сообщения консоли на русском'))

    # Парсим аргументы
    args = parser.parse_args(argv)
    
    # Если команда не указана, показываем help
    if not args.command:
        parser.print_help()
        return 0
    
    # Выполняем команду
    try:
        return args.func(args)
    except AudioLoadError as e:
        print(_('❌ Ошибка: {0}', str(e)))
        return 1
    except KeyboardInterrupt:
        print(_('\n\n⚠️  Прервано пользователем'))
        return 130
    except Exception as e:
        print(_('\n❌ Ошибка: {0}', e))
        import traceback
        traceback.print_exc()
        return 1


def main(argv=None):
    """Select the console language before parsing, including --help output."""
    argv = list(sys.argv[1:] if argv is None else argv)
    # A token after -- is a positional value, even if it is named --ru.
    options = argv[:argv.index('--')] if '--' in argv else argv
    previous_language = get_console_language()
    set_console_language('ru' if '--ru' in options else 'en')
    try:
        return _main(argv)
    finally:
        set_console_language(previous_language)


if __name__ == '__main__':
    sys.exit(main())
