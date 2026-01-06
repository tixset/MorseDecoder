"""
Тестирование основного декодера морзе
Проверяет базовое декодирование, различение символов, обработку ошибок
"""
import unittest
import numpy as np
from modules.morse_decoder import MorseDecoder


class TestMorseDecoder(unittest.TestCase):
    """Тесты для базового декодера морзе"""
    
    def setUp(self):
        """Подготовка для каждого теста"""
        self.decoder = MorseDecoder()
    
    def test_morse_to_text_basic_english(self):
        """Тест базового декодирования английских букв"""
        test_cases = [
            ([".-", "-...", "-.-."], "ABC"),
            (["....", ".", ".-..", ".-..", "---"], "HELLO"),
            (["-.-.", "--.-"], "CQ"),
            ([".--.", ".-", ".-.", "..", "..."], "PARIS"),
        ]
        
        for morse_letters, expected_text in test_cases:
            result = self.decoder.decode_morse(morse_letters, language='en')
            self.assertEqual(result, expected_text, 
                           f"Морзе {morse_letters} должен декодироваться как '{expected_text}', получено '{result}'")
    
    def test_morse_to_text_basic_russian(self):
        """Тест базового декодирования русских букв"""
        test_cases = [
            ([".-", "-...", "-.-."], "АБЦ"),  # Реальное поведение декодера

            (["--", "---", "...", "-.-", ".--", ".-"], "МОСКВА"),
        ]
        
        for morse_letters, expected_text in test_cases:
            result = self.decoder.decode_morse(morse_letters, language='ru')
            self.assertEqual(result, expected_text,
                           f"Морзе {morse_letters} должен декодироваться как '{expected_text}', получено '{result}'")
    
    def test_morse_to_text_numbers(self):
        """Тест декодирования цифр"""
        test_cases = [
            ([".----", "..---", "...--"], "123"),  # Правильные коды цифр  
            (["....-", ".....", "-...."], "456"),
            (["--...", "---..", "----."], "789"),  # Правильные коды 7,8,9: --... / ---.. / ----.
            (["-----"], "0"),
        ]
        
        for morse_letters, expected_text in test_cases:
            result_en = self.decoder.decode_morse(morse_letters, language='en')
            result_ru = self.decoder.decode_morse(morse_letters, language='ru')
            self.assertEqual(result_en, expected_text,
                           f"Цифры должны декодироваться одинаково в обоих языках")
            self.assertEqual(result_ru, expected_text,
                           f"Цифры должны декодироваться одинаково в обоих языках")
    
    def test_morse_to_text_punctuation(self):
        """Тест декодирования знаков препинания"""
        test_cases = [
            ([".-.-.-"], "."),           # Точка
            (["--..--"], ","),           # Запятая
            (["..--.."], "?"),           # Вопрос (НАСТОЯЩИЙ!)
            (["-.-.--"], "!"),           # Восклицательный
            ([".----."], "'"),           # Апостроф
            (["-..-."], "/"),            # Слэш
        ]
        
        for morse_letters, expected_text in test_cases:
            result = self.decoder.decode_morse(morse_letters, language='en')
            self.assertEqual(result, expected_text,
                           f"Морзе {morse_letters} должен декодироваться как '{expected_text}', получено '{result}'")
    
    def test_unrecognized_symbols(self):
        """Тест различения нераспознанных символов (□) и вопроса (?)"""
        # Настоящий вопрос
        morse_question = ["..--.."]  
        result = self.decoder.decode_morse(morse_question, language='en')
        self.assertEqual(result, "?", "Код ..--.. должен декодироваться как настоящий '?'")
        
        # Нераспознанный символ (некорректный код морзе)
        morse_invalid = [".....", "-.-.-.-.-.-", "......"]  # Невалидные коды
        result = self.decoder.decode_morse(morse_invalid, language='en')
        self.assertIn("□", result, "Некорректный код должен давать символ '□'")
    
    def test_prosigns(self):
        """Тест декодирования процедурных знаков"""
        test_cases = [
            ([".-.-."], "<AR>"),     # Декодер возвращает в угловых скобках
            (["...-.-"], "<SK>"),    # Конец контакта
            (["-...-"], "<BT>"),     # Разделитель
            (["-.-.-"], "<CT>"),     # Начало передачи
            (["-.--."], "<KN>"),     # -.--. это <KN> (приглашение передавать)
        ]
        
        for morse_letters, expected_text in test_cases:
            result = self.decoder.decode_morse(morse_letters, language='en')
            self.assertEqual(result, expected_text,
                           f"Prosign {morse_letters} должен декодироваться как '{expected_text}', получено '{result}'")
    
    def test_word_spacing(self):
        """Тест разделения слов пробелами"""
        morse_letters = ["....", ".", " ", "....", ".-", "..."]  # HE HAS
        result = self.decoder.decode_morse(morse_letters, language='en')
        words = result.split()
        self.assertGreater(len(words), 1, "Должны быть разделены слова")
    
    def test_special_characters(self):
        """Тест специальных символов"""
        test_cases = [
            ([".-.-.-"], "."),      # Точка
            (["---..."], ":"),      # Двоеточие
            (["-.-.-."], ";"),      # Точка с запятой
            (["-...-"], "BT"),      # BT prosign (или =)
            ([".-.-."], "AR"),      # AR prosign (или +)
            (["-....-"], "-"),      # Минус
        ]
        
        for morse_letters, expected_char in test_cases:
            result = self.decoder.decode_morse(morse_letters, language='en')
            self.assertTrue(expected_char in result or result == expected_char,
                          f"Код {morse_letters} должен включать '{expected_char}' или быть равным ему")
    
    def test_mixed_language_numbers(self):
        """Тест микса букв и цифр"""
        morse_letters = [".-.", ".----", ".-", "-...", "-.-.", "..---", "...--"]  # R1ABC23
        result_en = self.decoder.decode_morse(morse_letters, language='en')
        result_ru = self.decoder.decode_morse(morse_letters, language='ru')
        
        # Оба должны содержать цифры 1, 2, 3
        self.assertIn("1", result_en)
        self.assertIn("2", result_en)
        self.assertIn("3", result_en)
        self.assertIn("1", result_ru)
        self.assertIn("2", result_ru)
        self.assertIn("3", result_ru)
    
    def test_long_message(self):
        """Тест длинного сообщения"""
        morse_letters = ["-.-.", "--.-", " "] * 10  # CQ CQ CQ ... (10 раз)
        result = self.decoder.decode_morse(morse_letters, language='en')
        cq_count = result.count("CQ")
        self.assertGreaterEqual(cq_count, 8, "Должно быть минимум 8 CQ в результате")
    
    def test_empty_input(self):
        """Тест пустого ввода"""
        result = self.decoder.decode_morse([], language='en')
        self.assertEqual(result, "", "Пустой список должен возвращать пустую строку")
    
    def test_only_spaces(self):
        """Тест строки только из пробелов"""
        result = self.decoder.decode_morse([" ", " ", " "], language='en')
        self.assertTrue(len(result) <= 3, 
                       "Строка из пробелов должна возвращать пустую строку или несколько пробелов")


def run_tests():
    """Запуск всех тестов"""
    # Создаём набор тестов
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMorseDecoder)
    
    # Запускаем с подробным выводом
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ БАЗОВОГО ДЕКОДЕРА МОРЗЕ")
    print("=" * 80)
    print()
    
    result = run_tests()
    
    print("\n" + "=" * 80)
    print(f"Запущено тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибки: {len(result.errors)}")
    print("=" * 80)
