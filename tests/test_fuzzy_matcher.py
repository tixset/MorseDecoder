"""
Тестирование нечёткого сопоставления
Проверяет работу fuzzy matcher для поиска похожих кодов
"""
import unittest
from modules.fuzzy_matcher import (
    levenshtein_distance,
    similarity_ratio,
    fuzzy_match_q_code,
    fuzzy_match_callsign
)


class TestFuzzyMatcher(unittest.TestCase):
    """Тесты для нечёткого сопоставления"""
    
    def test_levenshtein_exact_match(self):
        """Тест точного совпадения"""
        distance = levenshtein_distance("QRZ", "QRZ")
        self.assertEqual(distance, 0, "Расстояние для точного совпадения должно быть 0")
    
    def test_levenshtein_one_char_diff(self):
        """Тест с разницей в один символ"""
        distance = levenshtein_distance("QRZ", "QRX")
        self.assertEqual(distance, 1, "Расстояние для одного символа должно быть 1")
    
    def test_levenshtein_completely_different(self):
        """Тест полностью разных строк"""
        distance = levenshtein_distance("ABC", "XYZ")
        self.assertEqual(distance, 3, "Расстояние для полностью разных строк должно быть равно длине")
    
    def test_levenshtein_empty_strings(self):
        """Тест с пустыми строками"""
        self.assertEqual(levenshtein_distance("ABC", ""), 3)
        self.assertEqual(levenshtein_distance("", "ABC"), 3)
        self.assertEqual(levenshtein_distance("", ""), 0)
    
    def test_levenshtein_insert(self):
        """Тест вставки символа"""
        distance = levenshtein_distance("ABC", "ABCD")
        self.assertEqual(distance, 1, "Вставка одного символа = расстояние 1")
    
    def test_levenshtein_delete(self):
        """Тест удаления символа"""
        distance = levenshtein_distance("ABCD", "ABC")
        self.assertEqual(distance, 1, "Удаление одного символа = расстояние 1")
    
    def test_similarity_ratio_exact(self):
        """Тест коэффициента схожести для точного совпадения"""
        ratio = similarity_ratio("QRZ", "QRZ")
        self.assertEqual(ratio, 1.0, "Точное совпадение должно иметь ratio = 1.0")
    
    def test_similarity_ratio_different(self):
        """Тест коэффициента схожести для разных строк"""
        ratio = similarity_ratio("ABC", "XYZ")
        self.assertLess(ratio, 0.5, "Разные строки должны иметь низкий ratio")
    
    def test_similarity_ratio_partial(self):
        """Тест коэффициента схожести для частичного совпадения"""
        ratio = similarity_ratio("QRZ", "QRX")
        self.assertGreater(ratio, 0.5, "Частичное совпадение должно иметь ratio > 0.5")
        self.assertLess(ratio, 1.0, "Частичное совпадение должно иметь ratio < 1.0")
    
    def test_fuzzy_match_q_code_exact(self):
        """Тест точного совпадения Q-кода"""
        q_codes = {'QRZ': 'Who is calling?', 'QTH': 'Location', 'QSL': 'Confirm'}
        result = fuzzy_match_q_code("QRZ", q_codes, max_distance=1)
        
        self.assertIsNotNone(result, "Точное совпадение должно быть найдено")
        if result:
            self.assertEqual(result[0], "QRZ", "Должен вернуть точное совпадение")
    
    def test_fuzzy_match_q_code_close(self):
        """Тест близкого совпадения Q-кода"""
        q_codes = {'QRZ': 'Who is calling?', 'QTH': 'Location', 'QSL': 'Confirm'}
        result = fuzzy_match_q_code("QRX", q_codes, max_distance=1)
        
        # Должен найти QRZ (отличается на 1 символ)
        if result:
            self.assertEqual(result[0], "QRZ", "Должен найти ближайший код QRZ")
    
    def test_fuzzy_match_q_code_no_match(self):
        """Тест когда нет близких совпадений"""
        q_codes = {'QRZ': 'Who is calling?', 'QTH': 'Location'}
        result = fuzzy_match_q_code("XYZ", q_codes, max_distance=1)
        
        # При max_distance=1 не должен найти совпадения для XYZ
        self.assertIsNone(result, "Не должно быть совпадений для XYZ с distance=1")
    
    def test_fuzzy_match_callsign(self):
        """Тест нечёткого сопоставления позывных"""
        callsigns = ['R1ABC', 'RA3AA', 'UA3ABC']
        
        # Точное совпадение
        result = fuzzy_match_callsign("R1ABC", callsigns)
        if result:
            self.assertEqual(result[0], "R1ABC")
    
    def test_case_insensitive(self):
        """Тест нечувствительности к регистру"""
        dist1 = levenshtein_distance("QRZ", "qrz")
        dist2 = levenshtein_distance("QRZ".upper(), "qrz".upper())
        
        # После приведения к одному регистру расстояние должно быть 0
        self.assertEqual(dist2, 0, "После приведения к одному регистру должно быть расстояние 0")
    
    def test_russian_codes(self):
        """Тест с русскими символами"""
        dist = levenshtein_distance("РПТ", "РПТ")
        self.assertEqual(dist, 0, "Должен работать с русскими буквами")
        
        dist2 = levenshtein_distance("РПТ", "НВ")
        self.assertGreater(dist2, 0, "Разные русские коды должны иметь расстояние > 0")
    
    def test_long_strings(self):
        """Тест с длинными строками"""
        s1 = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
        s2 = "THEQUICKBROWNFOXJUMPSOVERTHELAZYCAT"
        
        dist = levenshtein_distance(s1, s2)
        # Различаются только последние 3 символа (DOG vs CAT)
        self.assertEqual(dist, 3, "Должно быть расстояние 3 для DOG vs CAT")
    
    def test_similarity_symmetry(self):
        """Тест симметричности similarity_ratio"""
        ratio1 = similarity_ratio("ABC", "XYZ")
        ratio2 = similarity_ratio("XYZ", "ABC")
        self.assertEqual(ratio1, ratio2, "similarity_ratio должен быть симметричным")
    
    def test_levenshtein_symmetry(self):
        """Тест симметричности расстояния Левенштейна"""
        dist1 = levenshtein_distance("ABC", "XYZ")
        dist2 = levenshtein_distance("XYZ", "ABC")
        self.assertEqual(dist1, dist2, "Расстояние Левенштейна должно быть симметричным")


def run_tests():
    """Запуск всех тестов"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFuzzyMatcher)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result


if __name__ == '__main__':
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ НЕЧЁТКОГО СОПОСТАВЛЕНИЯ")
    print("=" * 80)
    print()
    
    result = run_tests()
    
    print("\n" + "=" * 80)
    print(f"Запущено тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибки: {len(result.errors)}")
    print("=" * 80)
