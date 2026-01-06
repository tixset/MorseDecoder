"""
Тестирование анализатора сигналов
Проверяет определение типа модуляции, чистоты сигнала, мастерства оператора
"""
import unittest
import numpy as np
from modules.signal_analyzer import SignalAnalyzer


class TestSignalAnalyzer(unittest.TestCase):
    """Тесты для анализатора сигналов"""
    
    def setUp(self):
        """Подготовка для каждого теста"""
        self.analyzer = SignalAnalyzer()
    
    def test_analyzer_creation(self):
        """Тест создания анализатора"""
        self.assertIsNotNone(self.analyzer)
        self.assertIsInstance(self.analyzer, SignalAnalyzer)
    
    def test_detect_modulation_type_structure(self):
        """Тест структуры результата определения модуляции"""
        # Создаём простой тестовый сигнал
        sample_rate = 8000
        duration = 1
        audio_data = np.sin(2 * np.pi * 600 * np.linspace(0, duration, sample_rate * duration))
        audio_data = (audio_data * 10000).astype(np.float64)
        
        result = self.analyzer.detect_modulation_type(audio_data, sample_rate)
        
        # Проверяем наличие основных полей
        expected_fields = ['type', 'confidence', 'characteristics']
        
        for field in expected_fields:
            self.assertIn(field, result, f"Результат должен содержать поле '{field}'")
    
    def test_modulation_type_values(self):
        """Тест допустимых значений типа модуляции"""
        sample_rate = 8000
        audio_data = np.random.rand(sample_rate) * 10000
        
        result = self.analyzer.detect_modulation_type(audio_data, sample_rate)
        
        valid_types = ['CW', 'PSK31', 'RTTY', 'UNKNOWN']
        self.assertIn(result['type'], valid_types,
                     f"Тип модуляции должен быть одним из {valid_types}")
    
    def test_confidence_range(self):
        """Тест диапазона уверенности"""
        sample_rate = 8000
        audio_data = np.random.rand(sample_rate) * 10000
        
        result = self.analyzer.detect_modulation_type(audio_data, sample_rate)
        
        confidence = result['confidence']
        self.assertTrue(0 <= confidence <= 100,
                       f"Уверенность должна быть в диапазоне 0-100, получено {confidence}")
    
    def test_signal_purity_fields(self):
        """Тест полей качества сигнала"""
        sample_rate = 8000
        audio_data = np.random.rand(sample_rate) * 10000
        envelope = np.abs(audio_data)
        
        result = self.analyzer.analyze_signal_purity(audio_data, envelope, sample_rate)
        
        expected_quality_fields = ['chirp', 'clicks', 'noise_level', 'snr_estimate', 'qrm_detected', 'purity_score']
        
        for field in expected_quality_fields:
            self.assertIn(field, result, f"signal_purity должно содержать поле '{field}'")
    
    def test_operator_skill_fields(self):
        """Тест полей мастерства оператора"""
        # Создаём тестовые импульсы и паузы
        pulses = [100, 150, 200, 300, 400]
        gaps = [50, 75, 100, 150, 200]
        
        result = self.analyzer.analyze_operator_skill(pulses, gaps)
        
        expected_skill_fields = ['timing_stability', 'rhythm_consistency', 'dot_dash_ratio']
        
        for field in expected_skill_fields:
            self.assertIn(field, result, f"operator_skill должно содержать поле '{field}'")
    
    def test_clean_cw_signal(self):
        """Тест анализа чистого CW сигнала"""
        sample_rate = 8000
        duration = 1
        frequency = 600  # Типичная частота для CW
        
        # Создаём чистый синусоидальный сигнал (идеальный CW)
        t = np.linspace(0, duration, sample_rate * duration)
        audio_data = np.sin(2 * np.pi * frequency * t) * 10000
        
        result = self.analyzer.detect_modulation_type(audio_data, sample_rate)
        
        # Для чистого сигнала ожидаем высокое качество
        self.assertEqual(result['type'], 'CW',
                        "Чистый синусоидальный сигнал должен определяться как CW")
        self.assertGreater(result['confidence'], 50,
                          "Уверенность для чистого CW должна быть выше 50%")
    
    def test_noisy_signal_purity(self):
        """Тест анализа зашумленного сигнала"""
        sample_rate = 8000
        duration = 1
        
        # Создаём шумный сигнал
        noise = np.random.rand(sample_rate * duration) * 10000
        envelope = np.abs(noise)
        
        result = self.analyzer.analyze_signal_purity(noise, envelope, sample_rate)
        
        # Для шумного сигнала ожидаем низкое SNR
        snr = result['snr_estimate']
        self.assertIsInstance(snr, (int, float), "SNR должно быть числом")
    
    def test_empty_pulses(self):
        """Тест анализа с пустым списком импульсов"""
        result = self.analyzer.analyze_operator_skill([], [])
        
        # Должен корректно обработать пустые данные
        self.assertIsNotNone(result)
        self.assertIn('timing_stability', result)
    
    def test_few_pulses(self):
        """Тест анализа с малым количеством импульсов"""
        pulses = [100, 150]
        gaps = [50]
        
        result = self.analyzer.analyze_operator_skill(pulses, gaps)
        
        # Должен корректно обработать малое количество данных
        self.assertIsNotNone(result)
        self.assertIn('skill_level', result)
    
    def test_timing_stability_range(self):
        """Тест диапазона стабильности тайминга"""
        pulses = [{'duration': 100} for _ in range(20)]  # Список dict с duration
        gaps = [50] * 19
        
        result = self.analyzer.analyze_operator_skill(pulses, gaps)
        
        timing = result['timing_stability']
        self.assertTrue(0 <= timing <= 100,
                       f"timing_stability должен быть в диапазоне 0-100, получено {timing}")
        
        # Для идеально стабильных импульсов должна быть высокая стабильность
        self.assertGreater(timing, 80, "Для стабильных импульсов timing_stability должен быть высоким")
    
    def test_rhythm_consistency_range(self):
        """Тест диапазона ритмической консистентности"""
        pulses = [{'duration': d} for d in [100, 150, 200] * 10]  # Список dict
        gaps = [50, 75, 100] * 10
        
        result = self.analyzer.analyze_operator_skill(pulses, gaps)
        
        rhythm = result['rhythm_consistency']
        self.assertTrue(0 <= rhythm <= 100,
                       f"rhythm_consistency должен быть в диапазоне 0-100, получено {rhythm}")
    
    def test_dot_dash_ratio_positive(self):
        """Тест что соотношение точка/тире положительное"""
        pulses = [100, 300, 100, 300]  # Чередование точек и тире
        gaps = [50, 50, 50]
        
        result = self.analyzer.analyze_operator_skill(pulses, gaps)
        
        ratio = result['dot_dash_ratio']
        self.assertGreaterEqual(ratio, 0, "dot_dash_ratio должно быть неотрицательным")
    
    def test_purity_score_range(self):
        """Тест диапазона оценки чистоты"""
        sample_rate = 8000
        audio_data = np.random.rand(sample_rate) * 10000
        envelope = np.abs(audio_data)
        
        result = self.analyzer.analyze_signal_purity(audio_data, envelope, sample_rate)
        
        purity = result['purity_score']
        self.assertTrue(0 <= purity <= 100,
                       f"purity_score должен быть в диапазоне 0-100, получено {purity}")


def run_tests():
    """Запуск всех тестов"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSignalAnalyzer)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


if __name__ == '__main__':
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ АНАЛИЗАТОРА СИГНАЛОВ")
    print("=" * 80)
    print()
    
    result = run_tests()
    
    print("\n" + "=" * 80)
    print(f"Запущено тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибки: {len(result.errors)}")
    print("=" * 80)
