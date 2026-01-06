"""
Модуль расширенной аналитики сигналов
Анализ качества, чистоты и характеристик морзе-сигналов
"""

import numpy as np
from scipy import signal as scipy_signal
from scipy.fft import fft, fftfreq


class SignalAnalyzer:
    """
    Анализатор качества и характеристик сигнала
    """
    
    def __init__(self, sample_rate=8000):
        self.sample_rate = sample_rate
    
    def detect_modulation_type(self, audio, sample_rate):
        """
        Определение типа модуляции
        
        Returns:
            dict: {
                'type': 'CW' | 'PSK31' | 'RTTY' | 'UNKNOWN',
                'confidence': 0-100,
                'characteristics': {...}
            }
        """
        # Анализируем частотный спектр
        n = len(audio)
        freqs = fftfreq(n, 1/sample_rate)
        fft_vals = np.abs(fft(audio))
        
        # Берем только положительные частоты
        pos_mask = freqs > 0
        freqs_pos = freqs[pos_mask]
        fft_pos = fft_vals[pos_mask]
        
        # CW характеристики: одна доминирующая частота
        # PSK31: узкая полоса ~31 Hz, характерные биения
        # RTTY: две частоты (mark/space), обычно 170 Hz разница
        
        # Ищем доминирующую частоту
        peak_idx = np.argmax(fft_pos)
        dominant_freq = freqs_pos[peak_idx]
        
        # Анализ ширины спектра
        threshold = np.max(fft_pos) * 0.1
        significant_freqs = freqs_pos[fft_pos > threshold]
        bandwidth = np.max(significant_freqs) - np.min(significant_freqs) if len(significant_freqs) > 0 else 0
        
        # Поиск множественных пиков (для RTTY)
        peaks, properties = scipy_signal.find_peaks(fft_pos, height=np.max(fft_pos) * 0.3, distance=50)
        
        modulation_type = 'CW'
        confidence = 80
        characteristics = {
            'dominant_frequency': float(dominant_freq),
            'bandwidth': float(bandwidth),
            'num_peaks': len(peaks)
        }
        
        if len(peaks) >= 2:
            # Проверяем расстояние между пиками
            peak_freqs = freqs_pos[peaks]
            freq_distances = np.diff(sorted(peak_freqs))
            
            # RTTY обычно имеет разницу 170 или 450 Hz
            if any(150 < d < 200 for d in freq_distances) or any(400 < d < 500 for d in freq_distances):
                modulation_type = 'RTTY'
                confidence = 70
                characteristics['mark_space_shift'] = float(freq_distances[0])
        elif bandwidth < 50:
            # Очень узкая полоса может быть PSK31 (~31 Hz)
            if 20 < bandwidth < 60:
                modulation_type = 'PSK31'
                confidence = 60
        
        return {
            'type': modulation_type,
            'confidence': confidence,
            'characteristics': characteristics
        }
    
    def analyze_signal_purity(self, audio, envelope, sample_rate):
        """
        Анализ чистоты сигнала
        
        Returns:
            dict: {
                'chirp': float,  # 0-100, дрейф частоты
                'clicks': int,   # количество резких скачков
                'noise_level': float,  # 0-100, уровень шума
                'snr_estimate': float,  # оценка SNR в dB
                'qrm_detected': bool,  # помехи от других станций
                'purity_score': float  # общая оценка 0-100
            }
        """
        # 1. Анализ chirp (дрейф частоты)
        chirp_score = self._detect_frequency_drift(audio, sample_rate)
        
        # 2. Детектирование clicks (резкие скачки)
        clicks_count = self._detect_clicks(envelope, sample_rate)
        
        # 3. Оценка уровня шума
        noise_level = self._estimate_noise_level(envelope)
        
        # 4. Оценка SNR
        snr_db = self._estimate_snr(envelope)
        
        # 5. Детектирование QRM (помехи от других станций)
        qrm_detected = self._detect_qrm(audio, sample_rate)
        
        # Общая оценка чистоты (0-100, выше = чище)
        purity_score = 100
        purity_score -= chirp_score * 0.3  # штраф за дрейф
        purity_score -= min(clicks_count * 5, 30)  # штраф за клики
        purity_score -= noise_level * 0.5  # штраф за шум
        purity_score = max(0, min(100, purity_score))
        
        return {
            'chirp': float(chirp_score),
            'clicks': int(clicks_count),
            'noise_level': float(noise_level),
            'snr_estimate': float(snr_db),
            'qrm_detected': bool(qrm_detected),
            'purity_score': float(purity_score)
        }
    
    def analyze_operator_skill(self, pulses, gaps):
        """
        Анализ мастерства оператора
        
        Returns:
            dict: {
                'timing_stability': float,  # 0-100, стабильность тайминга
                'rhythm_consistency': float,  # 0-100, консистентность ритма
                'dot_dash_ratio': float,  # идеал = 3.0
                'variance_score': float,  # вариация длительностей
                'skill_level': str,  # 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | 'EXPERT'
                'skill_score': float  # общая оценка 0-100
            }
        """
        if not pulses or len(pulses) < 10:
            return {
                'timing_stability': 0,
                'rhythm_consistency': 0,
                'dot_dash_ratio': 0,
                'variance_score': 0,
                'skill_level': 'UNKNOWN',
                'skill_score': 0
            }
        
        # Извлекаем длительности импульсов
        durations = np.array([p['duration'] for p in pulses])
        
        # 1. Timing stability - стабильность длительностей
        timing_stability = self._calculate_timing_stability(durations)
        
        # 2. Rhythm consistency - консистентность ритма
        rhythm_consistency = self._calculate_rhythm_consistency(durations, gaps)
        
        # 3. Dot-dash ratio (должно быть ~3.0 для правильной морзянки)
        dot_dash_ratio = self._calculate_dot_dash_ratio(durations)
        
        # 4. Variance score - низкая вариация = лучше
        variance_score = self._calculate_variance_score(durations)
        
        # Общая оценка мастерства
        skill_score = (timing_stability + rhythm_consistency + variance_score) / 3
        
        # Определяем уровень мастерства
        if skill_score >= 80:
            skill_level = 'EXPERT'
        elif skill_score >= 60:
            skill_level = 'ADVANCED'
        elif skill_score >= 40:
            skill_level = 'INTERMEDIATE'
        else:
            skill_level = 'BEGINNER'
        
        return {
            'timing_stability': float(timing_stability),
            'rhythm_consistency': float(rhythm_consistency),
            'dot_dash_ratio': float(dot_dash_ratio),
            'variance_score': float(variance_score),
            'skill_level': skill_level,
            'skill_score': float(skill_score)
        }
    
    # === Вспомогательные методы ===
    
    def _detect_frequency_drift(self, audio, sample_rate):
        """Детектирование дрейфа частоты (chirp)"""
        # Разбиваем сигнал на сегменты и анализируем изменение частоты
        segment_length = int(0.5 * sample_rate)  # 500 мс сегменты
        num_segments = len(audio) // segment_length
        
        if num_segments < 2:
            return 0
        
        peak_freqs = []
        for i in range(num_segments):
            start = i * segment_length
            end = start + segment_length
            segment = audio[start:end]
            
            # FFT сегмента
            freqs = fftfreq(len(segment), 1/sample_rate)
            fft_vals = np.abs(fft(segment))
            
            # Находим пиковую частоту
            pos_mask = (freqs > 0) & (freqs < 3000)
            if np.any(pos_mask):
                peak_idx = np.argmax(fft_vals[pos_mask])
                peak_freq = freqs[pos_mask][peak_idx]
                peak_freqs.append(peak_freq)
        
        if len(peak_freqs) < 2:
            return 0
        
        # Оценка дрейфа как вариация частоты
        freq_std = np.std(peak_freqs)
        freq_range = np.max(peak_freqs) - np.min(peak_freqs)
        
        # Нормализуем к шкале 0-100
        chirp_score = min(100, (freq_range / 10))  # 10 Hz дрейфа = 1 балл
        
        return chirp_score
    
    def _detect_clicks(self, envelope, sample_rate):
        """Детектирование резких скачков (clicks)"""
        # Вычисляем производную огибающей
        diff = np.diff(envelope)
        
        # Находим резкие скачки (больше 3 стандартных отклонений)
        threshold = np.std(diff) * 3
        clicks = np.sum(np.abs(diff) > threshold)
        
        return clicks
    
    def _estimate_noise_level(self, envelope):
        """Оценка уровня шума (0-100)"""
        # Берем нижний перцентиль огибающей как уровень шума
        noise_floor = np.percentile(envelope, 10)
        signal_peak = np.max(envelope)
        
        if signal_peak == 0:
            return 100
        
        noise_ratio = noise_floor / signal_peak
        noise_level = noise_ratio * 100
        
        return min(100, noise_level)
    
    def _estimate_snr(self, envelope):
        """Оценка SNR в децибелах"""
        signal_power = np.mean(envelope[envelope > np.percentile(envelope, 50)] ** 2)
        noise_power = np.mean(envelope[envelope < np.percentile(envelope, 25)] ** 2)
        
        if noise_power == 0:
            return 40  # максимальное значение
        
        snr = 10 * np.log10(signal_power / noise_power)
        return max(0, min(40, snr))
    
    def _detect_qrm(self, audio, sample_rate):
        """Детектирование помех от других станций (QRM)"""
        # Ищем множественные частотные компоненты
        freqs = fftfreq(len(audio), 1/sample_rate)
        fft_vals = np.abs(fft(audio))
        
        pos_mask = (freqs > 0) & (freqs < 3000)
        peaks, _ = scipy_signal.find_peaks(
            fft_vals[pos_mask], 
            height=np.max(fft_vals[pos_mask]) * 0.2,
            distance=100
        )
        
        # Если больше 3 значительных пиков - вероятно QRM
        return len(peaks) > 3
    
    def _calculate_timing_stability(self, durations):
        """Стабильность тайминга (0-100)"""
        # Коэффициент вариации (CV)
        mean_dur = np.mean(durations)
        std_dur = np.std(durations)
        
        if mean_dur == 0:
            return 0
        
        cv = std_dur / mean_dur
        
        # Низкий CV = высокая стабильность
        stability = max(0, 100 - (cv * 200))
        return stability
    
    def _calculate_rhythm_consistency(self, durations, gaps):
        """Консистентность ритма (0-100)"""
        if not gaps or len(gaps) < 5:
            return 50  # недостаточно данных
        
        gap_durations = np.array(gaps)
        
        # Анализируем вариацию пауз
        gap_cv = np.std(gap_durations) / np.mean(gap_durations) if np.mean(gap_durations) > 0 else 1
        
        # Низкая вариация = высокая консистентность
        consistency = max(0, 100 - (gap_cv * 150))
        return consistency
    
    def _calculate_dot_dash_ratio(self, durations):
        """Соотношение длительностей точка/тире (идеал = 3.0)"""
        # Разделяем на короткие (точки) и длинные (тире) импульсы
        threshold = np.median(durations)
        dots = durations[durations < threshold]
        dashes = durations[durations >= threshold]
        
        if len(dots) == 0 or len(dashes) == 0:
            return 0
        
        avg_dot = np.mean(dots)
        avg_dash = np.mean(dashes)
        
        if avg_dot == 0:
            return 0
        
        ratio = avg_dash / avg_dot
        return ratio
    
    def _calculate_variance_score(self, durations):
        """Оценка вариации (0-100, выше = меньше вариации)"""
        # Нормализованная вариация
        variance = np.var(durations)
        mean = np.mean(durations)
        
        if mean == 0:
            return 0
        
        normalized_variance = variance / (mean ** 2)
        
        # Преобразуем в оценку (меньше вариация = выше оценка)
        score = max(0, 100 - (normalized_variance * 500))
        return score
