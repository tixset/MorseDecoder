#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для декодирования нескольких параллельных морзе-сигналов на одной записи.

Поддерживает разделение сигналов по:
- Частоте (тональности)
- Скорости передачи (WPM)
- Амплитуде (громкости)
"""

from .console_i18n import console_text as _, console_signal_warning

import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
from .morse_decoder import MorseDecoder
from .auto_tune import test_parameter_combination
import warnings
import itertools

warnings.filterwarnings('ignore')

# Опциональный импорт signal_analyzer
try:
    from .signal_analyzer import SignalAnalyzer
    HAS_SIGNAL_ANALYZER = True
except ImportError:
    HAS_SIGNAL_ANALYZER = False


class MultiSignalDecoder:
    """
    Декодер для обработки нескольких параллельных морзе-сигналов
    """
    
    def __init__(self, sample_rate=8000, frequency_bands=None, auto_detect=True, num_peaks=3):
        """
        Инициализация мульти-сигнального декодера
        
        Args:
            sample_rate: частота дискретизации
            frequency_bands: список частотных диапазонов [(min1, max1), (min2, max2), ...]
                           Если None, будет автоматическое определение
            auto_detect: автоматически определять частотные диапазоны сигналов
            num_peaks: максимальное количество сигналов для автоопределения (по умолчанию 3)
        """
        self.sample_rate = sample_rate
        self.frequency_bands = frequency_bands
        self.auto_detect = auto_detect
        self.num_peaks = num_peaks
        
    def detect_frequency_peaks(self, audio, sample_rate, min_freq=300, max_freq=1500, 
                               num_peaks=3, peak_threshold=0.1):
        """
        Автоматическое определение частотных пиков в спектре
        
        Args:
            audio: аудио сигнал
            sample_rate: частота дискретизации
            min_freq: минимальная частота для поиска
            max_freq: максимальная частота для поиска
            num_peaks: максимальное количество пиков для поиска
            peak_threshold: минимальная относительная амплитуда пика (0-1)
            
        Returns:
            кортеж: (список частотных диапазонов, информация о пиках)
            bands: [(min1, max1), (min2, max2), ...]
            peak_info: {'count': N, 'frequencies': [...], 'amplitudes': [...], 'is_single_signal': bool}
        """
        # Вычисляем FFT для всего сигнала
        n = len(audio)
        freqs = fftfreq(n, 1/sample_rate)
        fft_vals = np.abs(fft(audio))
        
        # Берем только положительные частоты
        pos_mask = (freqs >= min_freq) & (freqs <= max_freq)
        freqs_pos = freqs[pos_mask]
        fft_pos = fft_vals[pos_mask]
        
        # Нормализуем спектр
        fft_normalized = fft_pos / np.max(fft_pos)
        
        # Ищем пики
        # Используем scipy.signal.find_peaks с минимальной высотой и дистанцией
        peaks, properties = signal.find_peaks(
            fft_normalized, 
            height=peak_threshold,
            distance=int(100 * len(fft_normalized) / (max_freq - min_freq))  # минимум 100 Гц между пиками
        )
        
        if len(peaks) == 0:
            # Если пики не найдены, возвращаем весь диапазон
            peak_info = {
                'count': 0,
                'frequencies': [],
                'amplitudes': [],
                'is_single_signal': True,
                'warning': 'Частотные пики не обнаружены'
            }
            return [(min_freq, max_freq)], peak_info
        
        # Сортируем пики по амплитуде
        peak_heights = properties['peak_heights']
        sorted_indices = np.argsort(peak_heights)[::-1]  # от большего к меньшему
        
        # Берем топ num_peaks пиков
        top_peaks = sorted(peaks[sorted_indices[:min(num_peaks, len(peaks))]])
        
        # Анализируем пики для определения количества реальных сигналов
        peak_freqs = [freqs_pos[p] for p in top_peaks]
        peak_amps = [peak_heights[np.where(peaks == p)[0][0]] for p in top_peaks]
        
        # Определяем, один это сигнал или несколько
        is_single_signal = False
        warning = None
        
        if len(top_peaks) == 1:
            is_single_signal = True
            warning = 'Обнаружен только один частотный пик - возможно это одиночный сигнал'
        elif len(top_peaks) == 2:
            # Проверяем расстояние между пиками
            freq_distance = abs(peak_freqs[1] - peak_freqs[0])
            if freq_distance < 300:
                is_single_signal = True
                warning = f'Пики слишком близко ({freq_distance:.0f} Hz) - возможно это один сигнал с гармониками'
            # Проверяем соотношение амплитуд
            amp_ratio = min(peak_amps) / max(peak_amps)
            if amp_ratio > 0.7:
                # Если амплитуды очень близки, это может быть один широкий сигнал
                if freq_distance < 500:
                    is_single_signal = True
                    warning = f'Близкие амплитуды ({amp_ratio:.2f}) и частоты - возможно один широкополосный сигнал'
        elif len(top_peaks) >= 3:
            # Проверяем разброс частот - если все пики в узком диапазоне, это один сигнал
            freq_range = max(peak_freqs) - min(peak_freqs)
            if freq_range < 800:  # все пики в пределах 800 Hz
                is_single_signal = True
                warning = f'Все {len(top_peaks)} пика находятся в узком диапазоне ({freq_range:.0f} Hz) - вероятно это один сигнал'
            else:
                # Проверяем среднее расстояние между соседними пиками
                sorted_freqs = sorted(peak_freqs)
                avg_distance = sum(sorted_freqs[i+1] - sorted_freqs[i] for i in range(len(sorted_freqs)-1)) / (len(sorted_freqs)-1)
                if avg_distance < 400:
                    is_single_signal = True
                    warning = f'Малое расстояние между пиками (среднее {avg_distance:.0f} Hz) - вероятно это один сигнал'
        
        peak_info = {
            'count': len(top_peaks),
            'frequencies': peak_freqs,
            'amplitudes': peak_amps,
            'is_single_signal': is_single_signal,
            'warning': warning
        }
        
        # Определяем частотные диапазоны вокруг пиков
        bands = []
        bandwidth = 400  # ширина полосы в Гц (±200 Гц от центра)
        
        for peak_idx in top_peaks:
            center_freq = freqs_pos[peak_idx]
            band_min = max(min_freq, center_freq - bandwidth/2)
            band_max = min(max_freq, center_freq + bandwidth/2)
            bands.append((int(band_min), int(band_max)))
            
        return bands, peak_info
    
    def decode_multi_signal(self, filepath, pulse_percentile=85, 
                           gap_dd=62, gap_char=90, gap_word=92,
                           verbose=True, use_auto_tune=True):
        """
        Декодирование нескольких параллельных сигналов
        
        Args:
            filepath: путь к аудиофайлу
            pulse_percentile: порог детектирования импульсов (если use_auto_tune=False)
            gap_dd: порог разделения точка/тире (если use_auto_tune=False)
            gap_char: порог разделения символов (если use_auto_tune=False)
            gap_word: порог разделения слов (если use_auto_tune=False)
            verbose: выводить отладочную информацию
            use_auto_tune: использовать автоподбор параметров для каждого сигнала
            
        Returns:
            список результатов для каждого обнаруженного сигнала
            [
                {
                    'frequency_band': (min_freq, max_freq),
                    'center_frequency': freq,
                    'text': decoded_text,
                    'wpm': speed,
                    'quality': quality_score,
                    'signal_strength': amplitude
                },
                ...
            ]
        """
        # Загружаем аудио с базовым декодером
        base_decoder = MorseDecoder(auto_frequency=False, sample_rate=self.sample_rate)
        audio, sample_rate = base_decoder.load_audio(filepath)
        
        # Автоматически определяем частотные диапазоны если нужно
        peak_info = None
        if self.auto_detect and self.frequency_bands is None:
            if verbose:
                print(_('🔍 Автоматическое определение частотных диапазонов...'))
            bands, peak_info = self.detect_frequency_peaks(audio, sample_rate, num_peaks=self.num_peaks)
            if verbose:
                print(_('   Найдено частотных диапазонов: {0}', len(bands)))
                for i, (min_f, max_f) in enumerate(bands, 1):
                    print(_('   {0}. {1}-{2} Hz (центр: {3:.0f} Hz)', i, min_f, max_f, (min_f + max_f) / 2))
                
                # Выводим предупреждение если это похоже на одиночный сигнал
                if peak_info and peak_info.get('is_single_signal'):
                    print(_('\n⚠️  {0}', console_signal_warning(peak_info.get('warning') or 'Возможно это одиночный сигнал')))
                    print(_('   💡 Рекомендуется использовать обычное декодирование: morse_cli.py auto <file>'))
        else:
            bands = self.frequency_bands or [(400, 1200)]
            peak_info = None
            
        # Декодируем каждый частотный диапазон отдельно
        results = []
        
        for band_idx, (min_freq, max_freq) in enumerate(bands, 1):
            if verbose:
                print(_('\n📡 Обработка сигнала #{0}: {1}-{2} Hz', band_idx, min_freq, max_freq))
            
            try:
                if use_auto_tune:
                    # Используем auto-tune для подбора оптимальных параметров
                    if verbose:
                        print(_('   🎛️  Автоподбор параметров...'))
                    
                    # Быстрый режим: тестируем 12 комбинаций
                    pulse_range = [60, 70, 80]
                    dot_dash_range = [55, 60]
                    char_range = [75, 85]
                    word_range = [90]
                    
                    combinations = list(itertools.product(
                        pulse_range, dot_dash_range, char_range, word_range
                    ))
                    
                    best_score = -float('inf')
                    best_params = None
                    best_decoder_result = None
                    
                    for pulse_p, dot_dash_p, char_p, word_p in combinations:
                        # Создаем декодер с этими параметрами
                        decoder = MorseDecoder(auto_frequency=False,
                            sample_rate=sample_rate,
                            min_freq=min_freq,
                            max_freq=max_freq,
                            pulse_percentile=pulse_p,
                            gap_percentile_dot_dash=dot_dash_p,
                            gap_percentile_char=char_p,
                            gap_percentile_word=word_p
                        )
                        
                        try:
                            # Фильтруем и декодируем
                            filtered = decoder.bandpass_filter(audio, sample_rate)
                            envelope = decoder.envelope_detection(filtered, sample_rate)
                            pulses_temp, gaps_temp = decoder.detect_pulses(envelope, sample_rate)
                            
                            if not pulses_temp or len(pulses_temp) < 5:
                                continue
                            
                            # Декодируем
                            morse_code = decoder.classify_morse(pulses_temp, gaps_temp, verbose=False)
                            text_temp = decoder.decode_morse(morse_code)
                            
                            if not text_temp or len(text_temp.strip()) < 3:
                                continue
                            
                            # Оцениваем качество
                            error_chars = text_temp.count('□')
                            total_chars = len(text_temp.replace(' ', ''))
                            if total_chars == 0:
                                continue
                            
                            question_ratio = error_chars / total_chars
                            score = (1 - question_ratio) * 100 + len(text_temp) * 0.1
                            
                            if score > best_score:
                                best_score = score
                                best_params = (pulse_p, dot_dash_p, char_p, word_p)
                                best_decoder_result = {
                                    'text': text_temp,
                                    'pulses': pulses_temp,
                                    'gaps': gaps_temp,
                                    'envelope': envelope,
                                    'question_ratio': question_ratio
                                }
                        except:
                            continue
                    
                    if best_params is None or best_decoder_result is None:
                        if verbose:
                            print(_('   ⚠️  Не удалось подобрать параметры'))
                        continue
                    
                    pulse_percentile, gap_dd, gap_char, gap_word = best_params
                    text = best_decoder_result['text']
                    pulses = best_decoder_result['pulses']
                    envelope = best_decoder_result['envelope']
                    
                    if verbose:
                        print(_('   ⚙️  Параметры: pulse={0}, dd={1}, char={2}, word={3}', pulse_percentile, gap_dd, gap_char, gap_word))
                    
                else:
                    # Используем заданные параметры
                    decoder = MorseDecoder(auto_frequency=False,
                        sample_rate=sample_rate,
                        min_freq=min_freq,
                        max_freq=max_freq,
                        pulse_percentile=pulse_percentile,
                        gap_percentile_dot_dash=gap_dd,
                        gap_percentile_char=gap_char,
                        gap_percentile_word=gap_word
                    )
                    
                    # Фильтруем и декодируем
                    filtered = decoder.bandpass_filter(audio, sample_rate)
                    envelope = decoder.envelope_detection(filtered, sample_rate)
                    pulses, gaps = decoder.detect_pulses(envelope, sample_rate)
                    
                    if not pulses:
                        if verbose:
                            print(_('   ⚠️  Импульсы не обнаружены'))
                        continue
                    
                    # Декодируем
                    morse_code = decoder.classify_morse(pulses, gaps, verbose=False)
                    text = decoder.decode_morse(morse_code)
                    
                    if not text or len(text.strip()) < 3:
                        if verbose:
                            print(_('   ⚠️  Текст слишком короткий'))
                        continue
                
                # Оцениваем силу сигнала
                signal_strength = np.max(envelope)
                
                # Создаем финальный декодер для оценки WPM
                final_decoder = MorseDecoder(auto_frequency=False,
                    sample_rate=sample_rate,
                    min_freq=min_freq,
                    max_freq=max_freq,
                    pulse_percentile=pulse_percentile,
                    gap_percentile_dot_dash=gap_dd,
                    gap_percentile_char=gap_char,
                    gap_percentile_word=gap_word
                )
                
                # Оцениваем скорость
                wpm = final_decoder.estimate_wpm(pulses)
                
                # Расширенная аналитика сигнала (если доступна)
                signal_analysis = None
                if HAS_SIGNAL_ANALYZER:
                    try:
                        analyzer = SignalAnalyzer(sample_rate)
                        filtered = final_decoder.bandpass_filter(audio, sample_rate)
                        
                        modulation = analyzer.detect_modulation_type(filtered, sample_rate)
                        purity = analyzer.analyze_signal_purity(filtered, envelope, sample_rate)
                        skill = analyzer.analyze_operator_skill(pulses, gaps if 'gaps' in locals() else best_decoder_result.get('gaps', []))
                        
                        signal_analysis = {
                            'modulation': modulation,
                            'purity': purity,
                            'operator_skill': skill
                        }
                        
                        if verbose:
                            print(_('   🔊 Модуляция: {0} ({1:.1f}% уверенность)', modulation['type'], modulation['confidence']))
                            print(_('   ✨ Чистота: {0:.1f}/100, SNR: {1:.1f} dB', purity['purity_score'], purity['snr_estimate']))
                            print(_('   👤 Оператор: {0} ({1:.1f}/100)', skill['skill_level'], skill['skill_score']))
                    except Exception as e:
                        if verbose:
                            print(_('   ⚠️  Аналитика недоступна: {0}', e))
                
                if not text or len(text.strip()) < 3:
                    if verbose:
                        print(_('   ⚠️  Текст слишком короткий'))
                    continue
                
                # Оцениваем качество (процент не-ошибочных символов)
                error_chars = text.count('□')
                total_chars = len(text.replace(' ', ''))
                quality = (1 - error_chars / total_chars) * 100 if total_chars > 0 else 0
                
                result = {
                    'frequency_band': (min_freq, max_freq),
                    'center_frequency': (min_freq + max_freq) / 2,
                    'text': text,
                    'wpm': wpm,
                    'quality': quality,
                    'signal_strength': float(signal_strength),
                    'pulses': len(pulses),
                    'signal_analysis': signal_analysis
                }
                
                results.append(result)
                
                if verbose:
                    print(_('   ✅ WPM: {0}, Качество: {1:.1f}%, Импульсов: {2}', wpm, quality, len(pulses)))
                    print(f"   📝 {text[:100]}{'...' if len(text) > 100 else ''}")
                    
            except Exception as e:
                if verbose:
                    print(_('   ❌ Ошибка: {0}', e))
                continue
        
        # Сортируем результаты по качеству
        results.sort(key=lambda x: x['quality'], reverse=True)
        
        # Возвращаем результаты вместе с информацией о пиках
        return {
            'signals': results,
            'peak_info': peak_info
        }
    
    def decode_with_multiple_speeds(self, filepath, frequency_band=(400, 1200),
                                    wpm_range=(10, 50), wpm_step=5,
                                    verbose=True):
        """
        Декодирование с перебором разных скоростей (для сигналов с разной скоростью)
        
        Args:
            filepath: путь к аудиофайлу
            frequency_band: частотный диапазон (min, max)
            wpm_range: диапазон скоростей (min_wpm, max_wpm)
            wpm_step: шаг перебора скоростей
            verbose: выводить информацию
            
        Returns:
            список результатов для разных скоростей
        """
        min_freq, max_freq = frequency_band
        min_wpm, max_wpm = wpm_range
        
        if verbose:
            print(_('🔍 Поиск сигналов со скоростью {0}-{1} WPM', min_wpm, max_wpm))
            print(_('   Частотный диапазон: {0}-{1} Hz', min_freq, max_freq))
        
        # Загружаем аудио
        decoder = MorseDecoder(auto_frequency=False, sample_rate=self.sample_rate, min_freq=min_freq, max_freq=max_freq)
        audio, sample_rate = decoder.load_audio(filepath)
        
        results = []
        
        # Перебираем разные параметры, соответствующие разным скоростям
        # Для разных WPM нужны разные пороги gap detection
        for target_wpm in range(min_wpm, max_wpm + 1, wpm_step):
            # Адаптируем параметры под целевую скорость
            # Более быстрые сигналы требуют более жестких порогов
            gap_dd = 55 + (target_wpm - min_wpm) / (max_wpm - min_wpm) * 15
            gap_char = 80 + (target_wpm - min_wpm) / (max_wpm - min_wpm) * 15
            
            try:
                test_decoder = MorseDecoder(auto_frequency=False,
                    sample_rate=sample_rate,
                    min_freq=min_freq,
                    max_freq=max_freq,
                    pulse_percentile=85,
                    gap_percentile_dot_dash=int(gap_dd),
                    gap_percentile_char=int(gap_char),
                    gap_percentile_word=92
                )
                
                filtered = test_decoder.bandpass_filter(audio, sample_rate)
                envelope = test_decoder.envelope_detection(filtered, sample_rate)
                pulses, gaps = test_decoder.detect_pulses(envelope, sample_rate)
                
                if pulses:
                    actual_wpm = test_decoder.estimate_wpm(pulses)
                    
                    # Проверяем, близка ли скорость к целевой
                    if abs(actual_wpm - target_wpm) < wpm_step * 2:
                        morse_code = test_decoder.classify_morse(pulses, gaps, verbose=False)
                        text = test_decoder.decode_morse(morse_code)
                        
                        if text and len(text.strip()) >= 3:
                            error_chars = text.count('?')
                            total_chars = len(text.replace(' ', ''))
                            quality = (1 - error_chars / total_chars) * 100 if total_chars > 0 else 0
                            
                            results.append({
                                'target_wpm': target_wpm,
                                'actual_wpm': actual_wpm,
                                'text': text,
                                'quality': quality,
                                'pulses': len(pulses)
                            })
            except:
                continue
        
        # Удаляем дубликаты (очень похожие результаты)
        unique_results = []
        for r in results:
            is_duplicate = False
            for ur in unique_results:
                # Если тексты очень похожи, это дубликат
                if r['text'][:50] == ur['text'][:50]:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_results.append(r)
        
        # Сортируем по качеству
        unique_results.sort(key=lambda x: x['quality'], reverse=True)
        
        if verbose and unique_results:
            print(_('\n✅ Найдено уникальных сигналов: {0}', len(unique_results)))
            for i, r in enumerate(unique_results[:3], 1):
                print(_('   {0}. WPM: {1}, Качество: {2:.1f}%', i, r['actual_wpm'], r['quality']))
                print(f"      {r['text'][:80]}...")
        
        return unique_results
