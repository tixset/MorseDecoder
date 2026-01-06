"""
Асинхронный модуль для быстрого поиска информации о позывных
Использует aiohttp для параллельных HTTP-запросов
"""
import asyncio
import aiohttp
import json
from pathlib import Path
import time
import re
from typing import List, Dict, Optional

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

# DXCC префиксы → названия стран (импортируем из общего модуля)
from .code_dictionaries import DXCC_PREFIX_MAP


class AsyncCallsignLookup:
    """Асинхронный поиск информации о позывных"""
    
    def __init__(self, cache_dir="callsign_cache", timeout=5, max_concurrent=10):
        """
        Инициализация
        
        Args:
            cache_dir: папка для кэширования результатов
            timeout: таймаут для HTTP-запросов (секунды)
            max_concurrent: максимальное количество одновременных запросов
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.user_agent = 'MorseDecoder/1.0 (async)'
    
    def is_valid_callsign(self, callsign: str) -> bool:
        """Проверка валидности позывного"""
        clean = callsign.replace('?', '').replace('Ш', '').replace('0', 'O')
        pattern = r'^[A-Z]{1,2}\d[A-Z]{1,4}$'
        return bool(re.match(pattern, clean)) and len(clean) >= 4
    
    def get_cached(self, callsign: str) -> Optional[Dict]:
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
    
    def save_cache(self, callsign: str, data: Dict):
        """Сохранить данные в кэш"""
        cache_file = self.cache_dir / f"{callsign}.json"
        data['cached_at'] = time.time()
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    async def lookup_hamqth(self, session: aiohttp.ClientSession, callsign: str) -> Optional[Dict]:
        """Асинхронный поиск через HamQTH.com"""
        try:
            async with self.semaphore:
                url = f"https://www.hamqth.com/dxcc_json.php?callsign={callsign}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('callsign'):
                            country = data.get('country') or data.get('name', '')
                            prefix = data.get('adif', '')
                            
                            if not country or country == 'Unknown':
                                if prefix in DXCC_PREFIX_MAP:
                                    country = DXCC_PREFIX_MAP[prefix]
                            
                            return {
                                'source': 'HamQTH',
                                'callsign': data.get('callsign', callsign),
                                'country': country or 'Unknown',
                                'prefix': prefix,
                                'cq_zone': data.get('waz', ''),
                                'itu_zone': data.get('itu', ''),
                                'continent': data.get('cont', ''),
                                'latitude': data.get('lat', ''),
                                'longitude': data.get('lng', ''),
                                'details': data.get('details', ''),
                                'found': True
                            }
        except:
            pass
        return None
    
    async def lookup_radioqth(self, session: aiohttp.ClientSession, callsign: str) -> Optional[Dict]:
        """Асинхронный поиск через RadioQTH.com"""
        try:
            async with self.semaphore:
                url = f"https://www.radioqth.net/dxcinfo/{callsign}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
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
    
    async def lookup_aprs_fi(self, session: aiohttp.ClientSession, callsign: str) -> Optional[Dict]:
        """Асинхронный поиск через APRS.fi"""
        try:
            async with self.semaphore:
                url = f"https://api.aprs.fi/api/get?name={callsign}&what=loc&apikey=demo&format=json"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
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
    
    async def lookup_single(self, session: aiohttp.ClientSession, callsign: str) -> Dict:
        """
        Асинхронный поиск информации о позывном
        
        Args:
            session: aiohttp ClientSession
            callsign: позывной радиостанции
            
        Returns:
            dict с информацией
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
        
        # Параллельный поиск в разных источниках
        tasks = [
            self.lookup_hamqth(session, callsign),
            self.lookup_radioqth(session, callsign),
            self.lookup_aprs_fi(session, callsign),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Выбираем первый успешный результат
        for result in results:
            if isinstance(result, dict) and result.get('found'):
                self.save_cache(callsign, result)
                return result
        
        # Если ничего не найдено
        result = {
            'callsign': callsign,
            'found': False,
            'error': 'Not found in any database'
        }
        
        self.save_cache(callsign, result)
        return result
    
    async def lookup_batch(self, callsigns: List[str]) -> List[Dict]:
        """
        Асинхронный массовый поиск информации о позывных
        
        Args:
            callsigns: список позывных
            
        Returns:
            список словарей с информацией
        """
        async with aiohttp.ClientSession(
            timeout=self.timeout,
            headers={'User-Agent': self.user_agent}
        ) as session:
            tasks = [self.lookup_single(session, cs) for cs in callsigns]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Обработка исключений
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        'callsign': callsigns[i],
                        'found': False,
                        'error': str(result)
                    })
                else:
                    processed_results.append(result)
            
            return processed_results


def batch_lookup_callsigns_async(callsigns: List[str], output_file: str = "callsigns_info.txt") -> Dict:
    """
    Синхронная обёртка для асинхронного массового поиска
    
    Args:
        callsigns: список позывных
        output_file: файл для сохранения результатов
        
    Returns:
        статистика поиска
    """
    lookup = AsyncCallsignLookup()
    
    # Очистка файла
    Path(output_file).write_text("", encoding='utf-8')
    
    print(f"\n🔍 Асинхронный поиск информации о {len(callsigns)} позывных...")
    print(f"💾 Результаты будут сохранены в: {output_file}\n")
    
    start_time = time.time()
    
    # Запуск асинхронной задачи
    results = asyncio.run(lookup.lookup_batch(callsigns))
    
    elapsed = time.time() - start_time
    
    # Сохранение результатов
    found_count = 0
    with open(output_file, 'a', encoding='utf-8') as f:
        for callsign, info in zip(callsigns, results):
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
                
                if info.get('from_cache'):
                    f.write(f"\n(Данные из кэша)\n")
                
                found_count += 1
                print(f"✅ {callsign}: {info.get('country', 'Unknown')}")
            else:
                f.write(f"Статус: Не найден\n")
                if info.get('error'):
                    f.write(f"Причина: {info['error']}\n")
                print(f"❌ {callsign}: Не найден")
            
            f.write("\n")
    
    stats = {
        'total': len(callsigns),
        'found': found_count,
        'not_found': len(callsigns) - found_count,
        'success_rate': found_count / len(callsigns) * 100 if callsigns else 0,
        'elapsed_time': elapsed,
        'avg_time_per_callsign': elapsed / len(callsigns) if callsigns else 0
    }
    
    print(f"\n✅ Обработано: {stats['total']}")
    print(f"📡 Найдено: {stats['found']} ({stats['success_rate']:.1f}%)")
    print(f"⏱️  Время: {elapsed:.2f}s ({stats['avg_time_per_callsign']:.3f}s на позывной)")
    print(f"💾 Результаты: {output_file}")
    
    return stats
