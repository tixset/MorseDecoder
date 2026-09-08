"""
Запуск всех тестов и генерация отчёта
Результаты сохраняются в reports/test_results_<timestamp>.txt и test_results_latest.txt

Автор: Антон Зеленов (tixset@gmail.com)
GitHub: https://github.com/tixset/MorseDecoder
Лицензия: MIT
"""
import os
import sys
import unittest
import time
from datetime import datetime
from io import StringIO


def run_all_tests():
    """Запуск всех тестов из папки tests/"""
    
    # Добавляем текущую директорию в путь
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # discovery включает новые модули и учитывает ошибки импорта как ошибки тестов.
    root = os.path.dirname(os.path.abspath(__file__))
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.join(root, 'tests'), top_level_dir=root)

    # Запускаем тесты с перехватом вывода
    print("\n" + "=" * 80)
    print("ЗАПУСК ВСЕХ ТЕСТОВ")
    print("=" * 80)
    print()
    
    # Создаём буфер для захвата вывода
    output_buffer = StringIO()
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(stream=output_buffer, verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    duration = time.time() - start_time
    
    # Получаем вывод
    test_output = output_buffer.getvalue()
    
    # Выводим на экран
    print(test_output)
    
    # Формируем итоговый отчёт
    report = generate_report(result, duration, test_output)
    
    # Сохраняем в файл
    save_report(report)
    
    return result, report


def generate_report(result, duration, test_output):
    """Генерация текстового отчёта"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = []
    report.append("=" * 80)
    report.append("ОТЧЁТ О ТЕСТИРОВАНИИ MORSE DECODER")
    report.append("=" * 80)
    report.append(f"Дата: {timestamp}")
    report.append(f"Время выполнения: {duration:.2f} секунд")
    report.append("")
    
    # Пропуски и ожидаемые/неожиданные исходы не считаются обычным успехом.
    passed = (result.testsRun - len(result.failures) - len(result.errors)
              - len(result.skipped) - len(result.expectedFailures)
              - len(result.unexpectedSuccesses))
    # Общая статистика
    report.append("ОБЩАЯ СТАТИСТИКА")
    report.append("-" * 80)
    report.append(f"Всего тестов:     {result.testsRun}")
    report.append(f"Успешно:          {passed}")
    report.append(f"Провалено:        {len(result.failures)}")
    report.append(f"Ошибки:           {len(result.errors)}")
    report.append(f"Пропущено:        {len(result.skipped)}")
    
    # Процент успеха
    if result.testsRun > 0:
        success_rate = ((passed) / result.testsRun) * 100
        report.append(f"Процент успеха:   {success_rate:.1f}%")
    
    report.append("")
    
    # Детали провалов
    if result.failures:
        report.append("ПРОВАЛЕННЫЕ ТЕСТЫ")
        report.append("-" * 80)
        for test, traceback in result.failures:
            report.append(f"\n✗ {test}")
            report.append(traceback)
        report.append("")
    
    # Детали ошибок
    if result.errors:
        report.append("ОШИБКИ В ТЕСТАХ")
        report.append("-" * 80)
        for test, traceback in result.errors:
            report.append(f"\n✗ {test}")
            report.append(traceback)
        report.append("")
    
    # Полный вывод тестов
    report.append("ПОЛНЫЙ ВЫВОД ТЕСТОВ")
    report.append("-" * 80)
    report.append(test_output)
    
    report.append("")
    report.append("=" * 80)
    report.append("КОНЕЦ ОТЧЁТА")
    report.append("=" * 80)
    
    return "\n".join(report)


def save_report(report):
    """Сохранение отчёта в файл"""
    
    # Создаём папку reports если её нет
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    # Имя файла с временной меткой
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.txt"
    filepath = os.path.join(reports_dir, filename)
    
    # Сохраняем
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✓ Отчёт сохранён: {filepath}")
    
    # Также сохраняем копию последнего результата
    latest_filepath = os.path.join(reports_dir, "test_results_latest.txt")
    try:
        if os.path.exists(latest_filepath):
            os.remove(latest_filepath)
        with open(latest_filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✓ Последний результат: {latest_filepath}")
    except Exception as e:
        print(f"⚠ Не удалось создать файл latest: {e}")


def print_summary(result):
    """Вывод краткой сводки"""
    
    print("\n" + "=" * 80)
    print("КРАТКАЯ СВОДКА")
    print("=" * 80)
    
    if result.wasSuccessful():
        print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО! 🎉")
    else:
        print("✗ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ")
        print(f"  Провалено: {len(result.failures)}")
        print(f"  Ошибки: {len(result.errors)}")
    
    print("=" * 80)


if __name__ == '__main__':
    result, report = run_all_tests()
    print_summary(result)
    
    # Возвращаем код выхода
    sys.exit(0 if result.wasSuccessful() else 1)
