"""
Комплексное тестирование военных кодов
Включает тестирование процедурных знаков, Q/Z-кодов и российских военных кодов
"""
from modules.procedural_codes import ProceduralCodeDetector


def test_prosigns():
    """Тестирование процедурных знаков и полей CHECK/NR"""
    
    test_messages = [
        # Пример 1: Полная радиограмма с CHECK и NR
        "NR 15 DE R2AA ZUG QTC 3 CHECK 8 BT MSG TEXT HERE AR K",
        
        # Пример 2: Короткое сообщение с prosigns
        "DE R2AA BT QSL QRU AR SK",
        
        # Пример 3: Начало связи
        "CQ CQ CQ DE RA3AA RA3AA RA3AA K",
        
        # Пример 4: Сообщение с ошибкой
        "DE R2AA BT MSG TEXT HH HH RPT AR",
        
        # Пример 5: Радиограмма с номером и CHECK
        "NR 42 CHECK 12 BT URGENT MSG AR",
        
        # Пример 6: Q-коды и prosigns
        "QRZ DE R1AA QTH MOSCOW QSL AR SK",
        
        # Пример 7: Военные коды
        "ZAA ZUG NR 7 CHECK 5 BT ALERT AS K",
    ]
    
    detector = ProceduralCodeDetector()
    
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ ПРОЦЕДУРНЫХ ЗНАКОВ И ПОЛЕЙ CHECK/NR")
    print("=" * 80)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'─' * 80}")
        print(f"ТЕСТ #{i}")
        print(f"{'─' * 80}")
        print(f"\n📻 Исходное сообщение:")
        print(f"   {message}")
        
        # Анализ
        detected = detector.detect_codes(message)
        
        # Проверка результатов
        print(f"\n🔍 Результаты анализа:")
        print(f"   • Позывные: {len(detected['callsigns'])}")
        print(f"   • Q-коды: {len(detected['q_codes'])}")
        print(f"   • Z-коды: {len(detected['z_codes'])}")
        print(f"   • Prosigns: {len(detected['prosigns'])}")
        print(f"   • Номер сообщения: {detected['message_number']}")
        print(f"   • CHECK: {detected['check_field']}")
        
        # Форматированный вывод
        print(detector.format_analysis(detected))


def test_russian_codes():
    """Тестирование российских военных кодов (Щ-коды и сокращения)"""
    
    test_messages = [
        # Пример 1: Реальная российская радиограмма
        "2ДКП 121 40 8 1315 121 = АДРЕС = = ТЕКСТ К",
        
        # Пример 2: Установочный вызов
        "КВМЗ ДЕ ЛДНП К",
        
        # Пример 3: Подтверждение приёма
        "КВМЗ Р 121 К",
        
        # Пример 4: Запрос повторения
        "08196 РПТ АЛ К",
        
        # Пример 5: С Щ-кодами
        "ЩРТ ЩРЩ ЩСА К",
        
        # Пример 6: Сложное сообщение
        "ЛДНП ДЕ 2ДКП НВ 121 40 РПТ АЛ К",
        
        # Пример 7: С prosigns и российскими кодами
        "ДЕ R2AA BT РПТ АС 5 НВ AR",
        
        # Пример 8: Подтверждение с "Ц"
        "ЛДНП Ц К",
    ]
    
    detector = ProceduralCodeDetector()
    
    print("\n\n" + "=" * 80)
    print("ТЕСТИРОВАНИЕ РОССИЙСКИХ ВОЕННЫХ КОДОВ")
    print("=" * 80)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'─' * 80}")
        print(f"ТЕСТ #{i}")
        print(f"{'─' * 80}")
        print(f"\n📻 Радиограмма:")
        print(f"   {message}")
        
        # Анализ
        detected = detector.detect_codes(message)
        
        # Проверка результатов
        print(f"\n🔍 Обнаружено:")
        if detected['message_number']:
            print(f"   • Номер сообщения: {detected['message_number']}")
        if detected['check_field']:
            print(f"   • CHECK: {detected['check_field']} групп")
        if detected['shch_codes']:
            print(f"   • Щ-коды: {len(detected['shch_codes'])}")
        if detected['ru_procedural_abbr']:
            print(f"   • Российские сокращения: {len(detected['ru_procedural_abbr'])}")
        if detected['prosigns']:
            print(f"   • Prosigns: {len(detected['prosigns'])}")
        if detected['callsigns']:
            print(f"   • Позывные: {', '.join(detected['callsigns'])}")
        
        # Форматированный вывод
        print(detector.format_analysis(detected))


def test_q_codes():
    """Тестирование Q-кодов"""
    
    test_messages = [
        "QRZ DE R1ABC K",
        "QTH MOSCOW QSL",
        "QRM QRN QSB K",
        "QRL QRV QRX K",
        "QSA5 QRK5 K",
        "QTR QTC 5 K",
    ]
    
    detector = ProceduralCodeDetector()
    
    print("\n\n" + "=" * 80)
    print("ТЕСТИРОВАНИЕ Q-КОДОВ")
    print("=" * 80)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'─' * 80}")
        print(f"ТЕСТ #{i}: {message}")
        print(f"{'─' * 80}")
        
        detected = detector.detect_codes(message)
        
        print(f"Q-коды: {detected['q_codes']}")
        print(f"Позывные: {detected['callsigns']}")
        
        assert len(detected['q_codes']) > 0, f"Должны быть обнаружены Q-коды в '{message}'"


def test_z_codes():
    """Тестирование Z-кодов (ACP-131)"""
    
    test_messages = [
        "ZAA ZAB K",
        "ZAG ZAK K",
        "ZRP ZUG K",
        "ZBW2 K",
    ]
    
    detector = ProceduralCodeDetector()
    
    print("\n\n" + "=" * 80)
    print("ТЕСТИРОВАНИЕ Z-КОДОВ")
    print("=" * 80)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'─' * 80}")
        print(f"ТЕСТ #{i}: {message}")
        print(f"{'─' * 80}")
        
        detected = detector.detect_codes(message)
        
        print(f"Z-коды: {detected['z_codes']}")
        
        assert len(detected['z_codes']) > 0, f"Должны быть обнаружены Z-коды в '{message}'"


def test_callsigns():
    """Тестирование детектирования позывных"""
    
    test_messages = [
        "DE R1ABC K",
        "CQ CQ DE RA3AA K",
        "DE IM4TET K",
        "W1AW DE K1ABC K",
        "UA3ABC DE R2AA K",
    ]
    
    detector = ProceduralCodeDetector()
    
    print("\n\n" + "=" * 80)
    print("ТЕСТИРОВАНИЕ ДЕТЕКТИРОВАНИЯ ПОЗЫВНЫХ")
    print("=" * 80)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'─' * 80}")
        print(f"ТЕСТ #{i}: {message}")
        print(f"{'─' * 80}")
        
        detected = detector.detect_codes(message)
        
        print(f"Позывные: {detected['callsigns']}")
        
        assert len(detected['callsigns']) > 0, f"Должны быть обнаружены позывные в '{message}'"


def test_check_and_nr_extraction():
    """Тестирование извлечения полей CHECK и NR"""
    
    test_cases = [
        ("NR 15 CHECK 8 K", 15, 8),
        ("NR 42 K", 42, None),
        ("CHECK 12 K", None, 12),
        ("NR 7 CHECK 5 BT MSG K", 7, 5),
    ]
    
    detector = ProceduralCodeDetector()
    
    print("\n\n" + "=" * 80)
    print("ТЕСТИРОВАНИЕ ИЗВЛЕЧЕНИЯ CHECK И NR")
    print("=" * 80)
    
    for i, (message, expected_nr, expected_check) in enumerate(test_cases, 1):
        print(f"\n{'─' * 80}")
        print(f"ТЕСТ #{i}: {message}")
        print(f"{'─' * 80}")
        
        detected = detector.detect_codes(message)
        
        print(f"NR: {detected['message_number']} (ожидается: {expected_nr})")
        print(f"CHECK: {detected['check_field']} (ожидается: {expected_check})")
        
        assert detected['message_number'] == expected_nr, \
            f"NR должен быть {expected_nr}, получено {detected['message_number']}"
        assert detected['check_field'] == expected_check, \
            f"CHECK должен быть {expected_check}, получено {detected['check_field']}"


def test_mixed_codes():
    """Тестирование смеси различных кодов"""
    
    test_messages = [
        "CQ CQ DE R1ABC QTH MOSCOW QRZ K",
        "NR 15 ZUG QTC 3 CHECK 8 BT AR K",
        "QRZ DE RA3AA РПТ АЛ K",
        "DE R2AA BT QSL ДЕ НВ AR SK",
    ]
    
    detector = ProceduralCodeDetector()
    
    print("\n\n" + "=" * 80)
    print("ТЕСТИРОВАНИЕ СМЕШАННЫХ КОДОВ")
    print("=" * 80)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'─' * 80}")
        print(f"ТЕСТ #{i}: {message}")
        print(f"{'─' * 80}")
        
        detected = detector.detect_codes(message)
        
        total_codes = (len(detected['q_codes']) + len(detected['z_codes']) + 
                      len(detected['prosigns']) + len(detected['callsigns']) +
                      len(detected['ru_procedural_abbr']))
        
        print(f"Всего кодов/знаков: {total_codes}")
        print(detector.format_analysis(detected))
        
        assert total_codes > 0, f"Должны быть обнаружены коды в '{message}'"


def test_urgency_detection():
    """Тестирование определения уровня срочности"""
    
    test_cases = [
        ("NR 15 DE R2AA BT MSG K", "normal"),
        ("PRIORITY NR 15 K", "priority"),
        ("URGENT MSG K", "urgent"),
        ("FLASH MSG K", "flash"),
    ]
    
    detector = ProceduralCodeDetector()
    
    print("\n\n" + "=" * 80)
    print("ТЕСТИРОВАНИЕ ОПРЕДЕЛЕНИЯ УРОВНЯ СРОЧНОСТИ")
    print("=" * 80)
    
    for i, (message, expected_urgency) in enumerate(test_cases, 1):
        print(f"\n{'─' * 80}")
        print(f"ТЕСТ #{i}: {message}")
        print(f"{'─' * 80}")
        
        detected = detector.detect_codes(message)
        
        print(f"Уровень срочности: {detected.get('urgency', 'normal')} (ожидается: {expected_urgency})")


def run_all_tests():
    """Запуск всех тестов"""
    test_prosigns()
    test_russian_codes()
    test_q_codes()
    test_z_codes()
    test_callsigns()
    test_check_and_nr_extraction()
    test_mixed_codes()
    test_urgency_detection()
    
    print(f"\n\n{'=' * 80}")
    print("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
    print(f"{'=' * 80}\n")


if __name__ == '__main__':
    run_all_tests()
