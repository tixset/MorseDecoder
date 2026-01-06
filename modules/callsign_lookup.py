"""
Модуль для поиска информации о радиолюбительских позывных
Использует API различных сервисов для получения данных о станциях
"""
import requests
import json
from pathlib import Path
import time
import re

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

# DXCC префиксы → названия стран (импорт из общего модуля)
from .code_dictionaries import DXCC_PREFIX_MAP

# Backwards compatibility (оставляем для совместимости)
# TODO: Удалить после обновления всех ссылок
# DXCC_PREFIX_MAP остается доступным через импорт из code_dictionaries

class CallsignLookup:
    """Поиск информации о позывных"""
    
    def __init__(self, cache_dir="callsign_cache"):
        """
        Инициализация
        
        Args:
            cache_dir: папка для кэширования результатов
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MorseDecoder/1.0'
        })
    
    def is_valid_callsign(self, callsign):
        """
        Проверка валидности позывного
        
        Формат: 1-2 буквы (префикс) + цифра + 1-4 буквы (суффикс)
        Примеры: R2AA, UA3ABC, K1ABC, G0XYZ
        """
        # Удаляем символы вопроса и другой мусор
        clean = callsign.replace('?', '').replace('Ш', '').replace('0', 'O')
        
        # Паттерн позывного: префикс (1-2 буквы) + цифра + суффикс (1-4 буквы)
        pattern = r'^[A-Z]{1,2}\d[A-Z]{1,4}$'
        
        return bool(re.match(pattern, clean)) and len(clean) >= 4
    
    def get_cached(self, callsign):
        """Получить данные из кэша"""
        cache_file = self.cache_dir / f"{callsign}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Кэш действителен 7 дней
                    if time.time() - data.get('cached_at', 0) < 7 * 24 * 3600:
                        return data
            except:
                pass
        return None
    
    def save_cache(self, callsign, data):
        """Сохранить данные в кэш"""
        cache_file = self.cache_dir / f"{callsign}.json"
        data['cached_at'] = time.time()
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def lookup_hamqth(self, callsign):
        """
        Поиск через HamQTH.com (бесплатный API, не требует регистрации)
        """
        try:
            url = f"https://www.hamqth.com/dxcc_json.php?callsign={callsign}"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('callsign'):
                    # HamQTH возвращает страну в поле 'name', а не 'country'
                    country = data.get('country') or data.get('name', '')
                    prefix = data.get('adif', '')
                    
                    # Если country пустая, пробуем получить из DXCC префикса
                    if not country or country == 'Unknown':
                        if prefix in DXCC_PREFIX_MAP:
                            country = DXCC_PREFIX_MAP[prefix]
                    
                    return {
                        'source': 'HamQTH',
                        'callsign': data.get('callsign', callsign),
                        'country': country or 'Unknown',
                        'prefix': prefix,
                        'cq_zone': data.get('waz', ''),  # HamQTH использует 'waz' вместо 'cq'
                        'itu_zone': data.get('itu', ''),
                        'continent': data.get('cont', ''),
                        'latitude': data.get('lat', ''),
                        'longitude': data.get('lng', ''),
                        'details': data.get('details', ''),  # Дополнительная информация
                        'found': True
                    }
        except:
            pass
        
        return None
    
    def lookup_radioqth(self, callsign):
        """
        Поиск через RadioQTH.com (бесплатный API, не требует регистрации)
        """
        try:
            url = f"https://www.radioqth.net/dxcinfo/{callsign}"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK':
                    return {
                        'source': 'RadioQTH',
                        'callsign': callsign,
                        'country': data.get('country', 'Unknown'),
                        'dxcc': data.get('dxcc', ''),
                        'cq_zone': data.get('cq', ''),
                        'itu_zone': data.get('itu', ''),
                        'continent': data.get('cont', ''),
                        'found': True
                    }
        except:
            pass
        
        return None
    
    def lookup_aprs_fi(self, callsign):
        """
        Поиск через APRS.fi (бесплатный API для APRS-активных станций)
        Требует API key, но его можно получить бесплатно на aprs.fi
        """
        try:
            # API key можно получить на https://aprs.fi/page/api
            # Здесь используем публичный endpoint без ключа (ограниченный)
            url = f"https://api.aprs.fi/api/get?name={callsign}&what=loc&apikey=demo&format=json"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('result') == 'ok' and data.get('entries'):
                    entry = data['entries'][0]
                    return {
                        'source': 'APRS.fi',
                        'callsign': entry.get('name', callsign),
                        'latitude': entry.get('lat', ''),
                        'longitude': entry.get('lng', ''),
                        'last_seen': entry.get('lasttime', ''),
                        'comment': entry.get('comment', ''),
                        'found': True
                    }
        except:
            pass
        
        return None
    
    def lookup_qrz_ru(self, callsign):
        """
        Поиск через QRZ.RU (для российских позывных)
        Использует BeautifulSoup для детального парсинга
        """
        try:
            url = f"https://www.qrz.ru/db/{callsign}"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200 and 'Позывной не найден' not in response.text:
                info = {
                    'source': 'QRZ.RU',
                    'callsign': callsign,
                    'url': url,
                    'country': 'Russia',  # QRZ.RU - только российские
                    'found': True
                }
                
                # Парсинг с BeautifulSoup если доступен
                if HAS_BS4:
                    try:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Ищем таблицу с данными (структура QRZ.RU)
                        # Обычно данные в таблице с классом или в div
                        content = response.text
                        
                        # Извлечение имени (обычно после "Имя:" или "ФИО:")
                        name_match = re.search(r'(?:Имя|ФИО|Оператор)[:\s]+([А-Яа-яA-Za-z\s]+)', content)
                        if name_match:
                            info['name'] = name_match.group(1).strip()
                        
                        # Извлечение QTH (локатор/город)
                        qth_match = re.search(r'(?:QTH|Локатор|Город)[:\s]+([А-Яа-яA-Za-z0-9\s\-,]+)', content)
                        if qth_match:
                            info['qth'] = qth_match.group(1).strip()
                        
                        # Извлечение региона
                        region_match = re.search(r'(?:Регион|Область)[:\s]+([А-Яа-яA-Za-z\s]+)', content)
                        if region_match:
                            info['region'] = region_match.group(1).strip()
                        
                        # Извлечение email
                        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', content)
                        if email_match:
                            info['email'] = email_match.group(1)
                            
                    except Exception as e:
                        # Если BeautifulSoup не сработал, используем простой парсинг
                        pass
                else:
                    # Простой парсинг без BeautifulSoup
                    html = response.text
                    if 'Россия' in html or 'Russia' in html:
                        info['country'] = 'Russia'
                
                return info
        except:
            pass
        
        return None
    
    def lookup(self, callsign):
        """
        Поиск информации о позывном
        
        Args:
            callsign: позывной радиостанции
            
        Returns:
            dict с информацией или None
        """
        # Очистка позывного
        callsign = callsign.upper().replace('?', '').strip()
        
        # Проверка валидности
        if not self.is_valid_callsign(callsign):
            return {
                'callsign': callsign,
                'found': False,
                'error': 'Invalid callsign format'
            }
        
        # Проверка кэша
        cached = self.get_cached(callsign)
        if cached:
            cached['from_cache'] = True
            return cached
        
        # Поиск в разных источниках
        result = None
        
        # 1. HamQTH (работает для всех позывных)
        result = self.lookup_hamqth(callsign)
        
        # 2. RadioQTH (альтернативный бесплатный API)
        if not result:
            result = self.lookup_radioqth(callsign)
        
        # 3. QRZ.RU (для российских позывных)
        if not result and (callsign.startswith('R') or callsign.startswith('U')):
            result = self.lookup_qrz_ru(callsign)
        
        # 4. APRS.fi (для APRS-активных станций)
        if not result:
            result = self.lookup_aprs_fi(callsign)
        
        # Если ничего не найдено
        if not result:
            result = {
                'callsign': callsign,
                'found': False,
                'error': 'Not found in any database'
            }
        
        # Сохранение в кэш
        self.save_cache(callsign, result)
        
        return result
    
    def save_callsign_info(self, callsign, info, output_file):
        """
        Сохранить информацию о позывном в файл
        
        Args:
            callsign: позывной
            info: словарь с информацией
            output_file: путь к файлу для сохранения
        """
        output_path = Path(output_file)
        
        try:
            with open(output_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"ПОЗЫВНОЙ: {callsign}\n")
                f.write(f"{'='*80}\n")
                
                if info.get('found'):
                    f.write(f"Источник: {info.get('source', 'Unknown')}\n")
                    f.write(f"Страна: {info.get('country', 'Unknown')}\n")
                    
                    if info.get('prefix'):
                        f.write(f"DXCC Prefix: {info['prefix']}\n")
                    if info.get('continent'):
                        f.write(f"Континент: {info['continent']}\n")
                    if info.get('cq_zone'):
                        f.write(f"CQ Zone: {info['cq_zone']}\n")
                    if info.get('itu_zone'):
                        f.write(f"ITU Zone: {info['itu_zone']}\n")
                    if info.get('latitude') and info.get('longitude'):
                        f.write(f"Координаты: {info['latitude']}, {info['longitude']}\n")
                    if info.get('url'):
                        f.write(f"URL: {info['url']}\n")
                    
                    if info.get('from_cache'):
                        f.write(f"\n(Данные из кэша)\n")
                else:
                    f.write(f"Статус: Не найден\n")
                    if info.get('error'):
                        f.write(f"Причина: {info['error']}\n")
                
                f.write("\n")
                
        except Exception as e:
            print(f"⚠️  Ошибка сохранения информации о {callsign}: {e}")


def batch_lookup_callsigns(callsigns, output_file="callsigns_info.txt", delay=1.0):
    """
    Массовый поиск информации о позывных
    
    Args:
        callsigns: список позывных
        output_file: файл для сохранения результатов
        delay: задержка между запросами (секунды)
    """
    lookup = CallsignLookup()
    
    # Очистка файла
    Path(output_file).write_text("", encoding='utf-8')
    
    print(f"\n🔍 Поиск информации о {len(callsigns)} позывных...")
    print(f"💾 Результаты будут сохранены в: {output_file}\n")
    
    found_count = 0
    for idx, callsign in enumerate(callsigns, 1):
        print(f"[{idx}/{len(callsigns)}] {callsign}...", end=' ')
        
        info = lookup.lookup(callsign)
        lookup.save_callsign_info(callsign, info, output_file)
        
        if info.get('found'):
            print(f"✅ {info.get('country', 'Unknown')}")
            found_count += 1
        else:
            print("❌ Не найден")
        
        # Задержка между запросами (чтобы не перегружать API)
        if idx < len(callsigns) and not info.get('from_cache'):
            time.sleep(delay)
    
    print(f"\n✅ Обработано: {len(callsigns)}")
    print(f"📡 Найдено: {found_count} ({found_count/len(callsigns)*100:.1f}%)")
    print(f"💾 Результаты: {output_file}")
