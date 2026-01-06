"""
Тестирование автонастройки параметров
Проверяет корректность работы auto_tune модуля
"""
import unittest
import os
import numpy as np
from scipy.io import wavfile
from modules.auto_tune import auto_tune_parameters, calculate_quality_score, test_parameter_combination
import tempfile


class TestAutoTune(unittest.TestCase):
    """Тесты для модуля автонастройки"""
    
    @classmethod
    def setUpClass(cls):
        """Создание тестового WAV файла"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_wav = os.path.join(cls.temp_dir, "test.wav")
        
        # Создаём простой тестовый WAV файл (1 секунда, 8kHz)
        sample_rate = 8000
        duration = 1
        audio_data = np.random.randint(-1000, 1000, sample_rate * duration, dtype=np.int16)
        wavfile.write(cls.test_wav, sample_rate, audio_data)
    
    @classmethod
    def tearDownClass(cls):
        """Удаление тестового файла"""
        if os.path.exists(cls.test_wav):
            os.remove(cls.test_wav)
        os.rmdir(cls.temp_dir)
    
    def test_auto_tune_modes(self):
        """Тест доступности всех режимов"""
        modes = ['fast', 'thorough', 'extreme']
        
        for mode in modes:
            try:
                # Запускаем auto_tune
                result = auto_tune_parameters(self.test_wav, mode=mode)
                
                # Проверяем что результат содержит ожидаемые поля
                self.assertIsNotNone(result)
                self.assertIn('params', result)  # Реальное поле вместо best_params
                self.assertIn('score', result)   # Реальное поле вместо best_quality
                self.assertIn('text', result)
                
                print(f"✓ Режим '{mode}' работает корректно")
                
            except Exception as e:
                self.fail(f"Режим '{mode}' выдал ошибку: {e}")
    
    def test_auto_tune_parameter_ranges(self):
        """Тест что параметры находятся в допустимых диапазонах"""
        result = auto_tune_parameters(self.test_wav, mode='fast')
        
        if result and 'params' in result:
            params = result['params']
            
            # Проверяем диапазоны параметров (реальные ключи: pulse, dot_dash, char, word)
            if 'pulse' in params:
                self.assertTrue(40 <= params['pulse'] <= 95,
                              f"pulse должен быть в диапазоне 40-95, получено {params['pulse']}")
            
            if 'gap_percentile_dot_dash' in params:
                self.assertTrue(50 <= params['gap_percentile_dot_dash'] <= 70,
                              f"gap_percentile_dot_dash должен быть в диапазоне 50-70")
            
            if 'gap_percentile_char' in params:
                self.assertTrue(85 <= params['gap_percentile_char'] <= 95,
                              f"gap_percentile_char должен быть в диапазоне 85-95")
            
            if 'gap_percentile_word' in params:
                self.assertTrue(90 <= params['gap_percentile_word'] <= 98,
                              f"gap_percentile_word должен быть в диапазоне 90-98")
    
    def test_quality_score_calculation(self):
        """Тест функции оценки качества"""
        # Хороший текст (мало ошибок)
        good_text = "HELLO WORLD QRZ DE R1ABC K"
        good_stats = {'wpm': 20, 'total_pulses': 100, 'dots': 50, 'dashes': 50}
        good_codes = {'q_codes': ['QRZ'], 'callsigns': ['R1ABC']}
        quality_good = calculate_quality_score(good_text, good_stats, good_codes)
        
        # Плохой текст (много □)
        bad_text = "□□□ H□LL□ □□□□□ W□RLD □□□"
        bad_stats = {'wpm': 20, 'total_pulses': 100, 'dots': 50, 'dashes': 50}
        bad_codes = {'q_codes': [], 'callsigns': []}
        quality_bad = calculate_quality_score(bad_text, bad_stats, bad_codes)
        
        # Хороший текст должен иметь более высокое качество
        self.assertGreater(quality_good, quality_bad,
                          "Текст с меньшим количеством ошибок должен иметь более высокое качество")
        
        # Score может быть отрицательным для плохих результатов
        self.assertIsInstance(quality_good, (int, float), "Качество должно быть числом")
        self.assertIsInstance(quality_bad, (int, float), "Качество должно быть числом")
    
    def test_fast_mode_exists(self):
        """Тест что fast режим существует и работает"""
        result = auto_tune_parameters(self.test_wav, mode='fast')
        self.assertIsNotNone(result)
        self.assertIn('score', result)  # Реальное поле вместо best_quality
        self.assertIn('params', result)  # Реальное поле вместо best_params
    
    def test_thorough_mode_exists(self):
        """Тест что thorough режим существует и работает"""
        result = auto_tune_parameters(self.test_wav, mode='thorough')
        self.assertIsNotNone(result)
        self.assertIn('score', result)  # Реальное поле вместо best_quality
        self.assertIn('params', result)  # Реальное поле вместо best_params
    
    def test_extreme_mode_exists(self):
        """Тест что extreme режим существует и работает"""
        result = auto_tune_parameters(self.test_wav, mode='extreme')
        self.assertIsNotNone(result)
        self.assertIn('score', result)  # Реальное поле вместо best_quality
        self.assertIn('params', result)  # Реальное поле вместо best_params
    
    def test_invalid_mode(self):
        """Тест обработки некорректного режима"""
        # Должен использовать режим по умолчанию или выдать ошибку
        try:
            result = auto_tune_parameters(self.test_wav, mode='invalid_mode')
            # Если не выдал ошибку, должен вернуть результат
            self.assertIsNotNone(result)
        except ValueError:
            # Или выдать ValueError
            pass
    
    def test_result_structure(self):
        """Тест структуры возвращаемого результата"""
        result = auto_tune_parameters(self.test_wav, mode='fast')
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        
        # Основные поля (реальные поля API)
        expected_fields = ['score', 'params', 'text']
        for field in expected_fields:
            self.assertIn(field, result, f"Результат должен содержать поле '{field}'")


def run_tests():
    """Запуск всех тестов"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAutoTune)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


if __name__ == '__main__':
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ МОДУЛЯ АВТОНАСТРОЙКИ")
    print("=" * 80)
    print()
    
    result = run_tests()
    
    print("\n" + "=" * 80)
    print(f"Запущено тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибки: {len(result.errors)}")
    print("=" * 80)
