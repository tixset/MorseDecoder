"""
Анализ всех обнаруженных процедурных кодов в расшифровках
"""
import json
from pathlib import Path
from .procedural_codes import ProceduralCodeDetector

def analyze_all_decodings():
    """
    Анализирует все .txt файлы и ищет процедурные коды
    """
    detector = ProceduralCodeDetector()
    training_data = Path("TrainingData")
    
    all_findings = {
        'q_codes': {},
        'z_codes': {},
        'shch_codes': {},
        'ru_procedural': {},
        'cw_abbreviations': {},
        'prosigns': {},
        'callsigns_by_file': {},
        'total_files': 0,
        'files_with_codes': 0
    }
    
    # Обработка всех .txt файлов
    for txt_file in sorted(training_data.glob("*.txt")):
        all_findings['total_files'] += 1
        print(f"\n📄 Анализ: {txt_file.name}")
        
        # Чтение текста
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Извлечение расшифрованного текста (между маркерами)
        if "📝 Расшифрованный текст:" in content:
            parts = content.split("📝 Расшифрованный текст:")
            if len(parts) > 1:
                text_section = parts[1].split("="*80)[1] if "="*80 in parts[1] else parts[1]
                # Берем до следующей секции
                text_section = text_section.split("📡 Обнаруженные позывные")[0]
                text_section = text_section.strip()
                
                # Анализ
                detected = detector.detect_codes(text_section)
                
                file_has_codes = False
                
                # Q-коды
                if detected['q_codes']:
                    file_has_codes = True
                    print(f"  ✅ Q-коды: {len(detected['q_codes'])}")
                    for item in detected['q_codes']:
                        code = item['code']
                        if code not in all_findings['q_codes']:
                            all_findings['q_codes'][code] = {
                                'meaning': item['meaning'],
                                'count': 0,
                                'files': []
                            }
                        all_findings['q_codes'][code]['count'] += 1
                        all_findings['q_codes'][code]['files'].append(txt_file.name)
                
                # Z-коды
                if detected['z_codes']:
                    file_has_codes = True
                    print(f"  ✅ Z-коды: {len(detected['z_codes'])}")
                    for item in detected['z_codes']:
                        code = item['code']
                        if code not in all_findings['z_codes']:
                            all_findings['z_codes'][code] = {
                                'meaning': item['meaning'],
                                'count': 0,
                                'files': []
                            }
                        all_findings['z_codes'][code]['count'] += 1
                        all_findings['z_codes'][code]['files'].append(txt_file.name)
                
                # Щ-коды
                if detected['shch_codes']:
                    file_has_codes = True
                    print(f"  ✅ Щ-коды: {len(detected['shch_codes'])}")
                    for item in detected['shch_codes']:
                        code = item['code']
                        if code not in all_findings['shch_codes']:
                            all_findings['shch_codes'][code] = {
                                'meaning': item['meaning'],
                                'count': 0,
                                'files': []
                            }
                        all_findings['shch_codes'][code]['count'] += 1
                        all_findings['shch_codes'][code]['files'].append(txt_file.name)
                
                # Российские процедурные
                if detected['RU_PROCEDURAL_ABBR']:
                    file_has_codes = True
                    print(f"  ✅ RU процедурные: {len(detected['RU_PROCEDURAL_ABBR'])}")
                    for item in detected['RU_PROCEDURAL_ABBR']:
                        code = item['code']
                        if code not in all_findings['ru_procedural']:
                            all_findings['ru_procedural'][code] = {
                                'meaning': item['meaning'],
                                'count': 0,
                                'files': []
                            }
                        all_findings['ru_procedural'][code]['count'] += 1
                        all_findings['ru_procedural'][code]['files'].append(txt_file.name)
                
                # CW-сокращения
                if detected['cw_abbreviations']:
                    file_has_codes = True
                    print(f"  ✅ CW-сокращения: {len(detected['cw_abbreviations'])}")
                    for item in detected['cw_abbreviations']:
                        code = item['code']
                        if code not in all_findings['cw_abbreviations']:
                            all_findings['cw_abbreviations'][code] = {
                                'meaning': item['meaning'],
                                'count': 0,
                                'files': []
                            }
                        all_findings['cw_abbreviations'][code]['count'] += 1
                        all_findings['cw_abbreviations'][code]['files'].append(txt_file.name)
                
                # Prosigns
                if detected['prosigns']:
                    file_has_codes = True
                    print(f"  ✅ Prosigns: {len(detected['prosigns'])}")
                    for item in detected['prosigns']:
                        code = item['code']
                        if code not in all_findings['prosigns']:
                            all_findings['prosigns'][code] = {
                                'meaning': item['meaning'],
                                'count': 0,
                                'files': []
                            }
                        all_findings['prosigns'][code]['count'] += 1
                        all_findings['prosigns'][code]['files'].append(txt_file.name)
                
                # Позывные
                if detected['callsigns']:
                    all_findings['callsigns_by_file'][txt_file.name] = detected['callsigns']
                    print(f"  📡 Позывных: {len(detected['callsigns'])}")
                
                if file_has_codes:
                    all_findings['files_with_codes'] += 1
                
                if not file_has_codes and not detected['callsigns']:
                    print(f"  ⚠️  Коды не обнаружены")
    
    # Вывод итоговой статистики
    print("\n" + "="*80)
    print("📊 ИТОГОВАЯ СТАТИСТИКА ПО ВСЕМ ФАЙЛАМ")
    print("="*80)
    
    print(f"\n📄 Обработано файлов: {all_findings['total_files']}")
    print(f"✅ Файлов с кодами: {all_findings['files_with_codes']}")
    
    if all_findings['q_codes']:
        print(f"\n📻 Q-КОДЫ (найдено уникальных: {len(all_findings['q_codes'])})")
        for code, data in sorted(all_findings['q_codes'].items()):
            print(f"  • {code}: {data['meaning']} (встречается {data['count']}×)")
    else:
        print(f"\n📻 Q-КОДЫ: не обнаружены")
    
    if all_findings['z_codes']:
        print(f"\n🔒 Z-КОДЫ (найдено уникальных: {len(all_findings['z_codes'])})")
        for code, data in sorted(all_findings['z_codes'].items()):
            print(f"  • {code}: {data['meaning']} (встречается {data['count']}×)")
    else:
        print(f"\n🔒 Z-КОДЫ: не обнаружены")
    
    if all_findings['shch_codes']:
        print(f"\n🇷🇺 Щ-КОДЫ (найдено уникальных: {len(all_findings['shch_codes'])})")
        for code, data in sorted(all_findings['shch_codes'].items()):
            print(f"  • {code}: {data['meaning']} (встречается {data['count']}×)")
    else:
        print(f"\n🇷🇺 Щ-КОДЫ: не обнаружены")
    
    if all_findings['ru_procedural']:
        print(f"\n🇷🇺 РОССИЙСКИЕ ПРОЦЕДУРНЫЕ (найдено уникальных: {len(all_findings['ru_procedural'])})")
        for code, data in sorted(all_findings['ru_procedural'].items()):
            print(f"  • {code}: {data['meaning']} (встречается {data['count']}×)")
    else:
        print(f"\n🇷🇺 РОССИЙСКИЕ ПРОЦЕДУРНЫЕ: не обнаружены")
    
    if all_findings['cw_abbreviations']:
        print(f"\n📝 CW-СОКРАЩЕНИЯ (найдено уникальных: {len(all_findings['cw_abbreviations'])})")
        for code, data in sorted(all_findings['cw_abbreviations'].items()):
            print(f"  • {code}: {data['meaning']} (встречается {data['count']}×)")
    else:
        print(f"\n📝 CW-СОКРАЩЕНИЯ: не обнаружены")
    
    if all_findings['prosigns']:
        print(f"\n🔔 PROSIGNS (найдено уникальных: {len(all_findings['prosigns'])})")
        for code, data in sorted(all_findings['prosigns'].items()):
            print(f"  • {code}: {data['meaning']} (встречается {data['count']}×)")
    else:
        print(f"\n🔔 PROSIGNS: не обнаружены")
    
    # Позывные
    total_callsigns = sum(len(calls) for calls in all_findings['callsigns_by_file'].values())
    print(f"\n📡 ПОЗЫВНЫЕ: всего обнаружено {total_callsigns} в {len(all_findings['callsigns_by_file'])} файлах")
    
    # Сохранение в JSON
    with open('code_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_findings, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в: code_analysis_results.json")
    print("="*80)
    
    return all_findings

if __name__ == "__main__":
    analyze_all_decodings()
