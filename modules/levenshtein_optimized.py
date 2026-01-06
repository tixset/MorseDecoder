"""
Оптимизация расстояния Левенштейна с использованием Numba JIT
Значительное ускорение для больших объёмов вычислений
"""
try:
    from numba import jit
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False
    # Заглушка-декоратор если numba не установлена
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


@jit(nopython=True, cache=True)
def levenshtein_distance_numba(s1, s2):
    """
    Вычисление расстояния Левенштейна с Numba JIT компиляцией
    Работает в 10-100x быстрее обычной Python версии
    
    Args:
        s1, s2: строки для сравнения (будут преобразованы в байты)
    
    Returns:
        int: расстояние Левенштейна
    """
    len1 = len(s1)
    len2 = len(s2)
    
    # Оптимизация: если одна строка пустая
    if len1 == 0:
        return len2
    if len2 == 0:
        return len1
    
    # Оптимизация: меняем местами для использования меньше памяти
    if len1 < len2:
        s1, s2 = s2, s1
        len1, len2 = len2, len1
    
    # Используем только одну строку памяти вместо матрицы
    previous_row = list(range(len2 + 1))
    
    for i in range(len1):
        current_row = [i + 1]
        for j in range(len2):
            # Стоимость операций
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (0 if s1[i] == s2[j] else 1)
            
            current_row.append(min(insertions, deletions, substitutions))
        
        previous_row = current_row
    
    return previous_row[-1]


def get_levenshtein_function():
    """
    Возвращает оптимальную функцию для вычисления расстояния Левенштейна
    
    Returns:
        function: numba-версия если доступна, иначе обычная Python версия
    """
    if HAS_NUMBA:
        # Оборачиваем для работы со строками (numba требует байты)
        def optimized_levenshtein(s1, s2):
            # Преобразуем строки в байты для numba
            b1 = s1.encode('utf-8') if isinstance(s1, str) else s1
            b2 = s2.encode('utf-8') if isinstance(s2, str) else s2
            return levenshtein_distance_numba(b1, b2)
        
        return optimized_levenshtein
    else:
        # Fallback на обычную Python версию
        def python_levenshtein(s1, s2):
            if len(s1) < len(s2):
                return python_levenshtein(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        return python_levenshtein


# Экспортируем оптимизированную версию
levenshtein_fast = get_levenshtein_function()


if __name__ == "__main__":
    """Тест производительности"""
    import time
    
    # Тестовые данные
    test_pairs = [
        ("KITTEN", "SITTING"),
        ("SATURDAY", "SUNDAY"),
        ("R3DC", "R3DС"),  # Кириллица С vs латиница C
        ("QRZ", "QRZ"),
        ("UA3ABC", "UA3ABD"),
        ("K1ABC", "W1ABC"),
    ]
    
    # Прогрев JIT (если numba доступна)
    for s1, s2 in test_pairs[:2]:
        _ = levenshtein_fast(s1, s2)
    
    # Benchmark
    iterations = 10000
    
    print("🔥 Benchmark расстояния Левенштейна")
    print(f"Итераций: {iterations}\n")
    
    start = time.perf_counter()
    for _ in range(iterations):
        for s1, s2 in test_pairs:
            _ = levenshtein_fast(s1, s2)
    elapsed = time.perf_counter() - start
    
    print(f"{'Режим:':<20} {'Numba JIT' if HAS_NUMBA else 'Python fallback'}")
    print(f"{'Время:':<20} {elapsed:.4f}s")
    print(f"{'Операций в сек:':<20} {iterations * len(test_pairs) / elapsed:.0f}")
    print(f"{'Время на операцию:':<20} {elapsed / (iterations * len(test_pairs)) * 1000:.3f}ms")
    
    # Проверка результатов
    print("\nПроверка результатов:")
    for s1, s2 in test_pairs:
        dist = levenshtein_fast(s1, s2)
        print(f"  {s1:<10} ↔ {s2:<10} = {dist}")
