"""
Декодер азбуки Морзе из аудио файлов
Поддержка английского и русского языков
С анализом военных кодов и команд
"""

import numpy as np
import scipy.io.wavfile as wavfile
from scipy import signal
from pathlib import Path
import warnings
import hashlib
import json
from functools import lru_cache
warnings.filterwarnings('ignore')

# Опциональный импорт модуля военных кодов
try:
    from .procedural_codes import ProceduralCodeDetector
    HAS_PROCEDURAL_CODES = True
except ImportError:
    HAS_PROCEDURAL_CODES = False

# Опциональный импорт модуля аналитики сигналов
try:
    from .signal_analyzer import SignalAnalyzer
    HAS_SIGNAL_ANALYZER = True
except ImportError:
    HAS_SIGNAL_ANALYZER = False

# Prosigns - слитные комбинации, передаваемые БЕЗ пробела между символами
# ВАЖНО: Проверяются ПЕРВЫМИ, до обычных символов, т.к. имеют конфликты
# Например: AR (.-.-.) = A+R слитно, но в обычном словаре .-.-. = '+'
PROSIGNS_MORSE = {
    '.-.-.'  : '<AR>',   # Конец передачи (A+R)
    '...-.-' : '<SK>',   # Конец контакта (S+K)
    '-...-'  : '<BT>',   # Разделитель (B+T)
    '-.-.-'  : '<CT>',   # Начало передачи (K+A или C+T)
    '-.--.'  : '<KN>',   # Только вам (K+N)
    '.-...'  : '<AS>',   # Ожидайте (A+S)
    '........': '<HH>',  # Ошибка (8 точек)
    '...-.'  : '<SN>',   # Понял (S+N)
    '..-.'   : '<INT>',  # Вопрос (не путать с F)
}

# Словарь Морзе для английского языка
MORSE_CODE_DICT_EN = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z',
    '-----': '0', '.----': '1', '..---': '2', '...--': '3',
    '....-': '4', '.....': '5', '-....': '6', '--...': '7',
    '---..': '8', '----.': '9',
    '.-.-.-': '.', '--..--': ',', '..--..': '?', '.----.': "'",
    '-.-.--': '!', '-..-.': '/', '-.--.': '(', '-.--.-': ')',
    '.-...': '&', '---...': ':', '-.-.-.': ';', '-...-': '=',
    '.-.-.': '+', '-....-': '-', '..--.-': '_', '.-..-.': '"',
    '...-..-': '$', '.--.-.': '@'
}

# Словарь Морзе для русского языка
MORSE_CODE_DICT_RU = {
    '.-': 'А', '-...': 'Б', '.--': 'В', '--.': 'Г', '-..': 'Д',
    '.': 'Е', '...-': 'Ж', '--..': 'З', '..': 'И', '.---': 'Й',
    '-.-': 'К', '.-..': 'Л', '--': 'М', '-.': 'Н', '---': 'О',
    '.--.': 'П', '.-.': 'Р', '...': 'С', '-': 'Т', '..-': 'У',
    '..-.': 'Ф', '....': 'Х', '-.-.': 'Ц', '---.': 'Ч', '----': 'Ш',
    '--.-': 'Щ', '-.--': 'Ы', '-..-': 'Ь', '..-.': 'Э', '..--': 'Ю',
    '.-.-': 'Я',
    '-----': '0', '.----': '1', '..---': '2', '...--': '3',
    '....-': '4', '.....': '5', '-....': '6', '--...': '7',
    '---..': '8', '----.': '9',
    '.-.-.-': '.', '--..--': ',', '..--..': '?', '.----.': "'",
    '-.-.--': '!', '-..-.': '/', '-.--.': '(', '-.--.-': ')',
    '---...': ':', '-.-.-.': ';', '-...-': '='
}

# Кеш для результатов декодирования
_DECODE_CACHE = {}
_CACHE_MAX_SIZE = 100  # Максимум 100 закешированных результатов

def _get_file_params_hash(filepath, params_dict):
    """
    Вычисляет хеш файла и параметров для кеширования
    """
    filepath_obj = Path(filepath)
    
    # Используем mtime и size файла для быстрой проверки
    try:
        stat = filepath_obj.stat()
        file_key = f"{filepath_obj.name}:{stat.st_size}:{stat.st_mtime_ns}"
    except:
        # Файл не существует, используем только имя
        file_key = str(filepath_obj)
    
    # Добавляем параметры декодера
    params_key = json.dumps(params_dict, sort_keys=True)
    
    # Хешируем
    combined = f"{file_key}:{params_key}"
    return hashlib.md5(combined.encode()).hexdigest()


class MorseDecoder:
    def __init__(self, sample_rate=8000, min_freq=400, max_freq=1200,
                 pulse_percentile=85, gap_percentile_dot_dash=62,
                 gap_percentile_char=90, gap_percentile_word=92,
                 use_cache=True):
        """
        Инициализация декодера
        
        Args:
            sample_rate: частота дискретизации для обработки
            min_freq: минимальная частота фильтра (Гц)
            max_freq: максимальная частота фильтра (Гц)
            pulse_percentile: percentile порог для обнаружения импульсов (70-95)
            gap_percentile_dot_dash: percentile для разделения точек/тире (50-70)
            gap_percentile_char: percentile для разделения символов (85-95)
            gap_percentile_word: percentile для разделения слов (90-98)
            use_cache: использовать кеширование результатов (по умолчанию True)
        """
        self.target_sample_rate = sample_rate
        self.min_freq = min_freq
        self.max_freq = max_freq
        self.pulse_percentile = pulse_percentile
        self.gap_percentile_dot_dash = gap_percentile_dot_dash
        self.gap_percentile_char = gap_percentile_char
        self.gap_percentile_word = gap_percentile_word
        self.use_cache = use_cache
        
        # Предкомпиляция фильтра Butterworth для производительности
        self._filter_coefficients = None
        self._compile_filter()
    
    def _compile_filter(self):
        """Предварительная компиляция коэффициентов фильтра"""
        nyquist = self.target_sample_rate / 2
        low = self.min_freq / nyquist
        high = self.max_freq / nyquist
        
        # Butterworth фильтр 4-го порядка
        self._filter_coefficients = signal.butter(4, [low, high], btype='band')
    
    def load_audio(self, filepath):
        """Загрузка и предобработка аудио файла"""
        # Загрузка аудио
        sample_rate, audio = wavfile.read(filepath)
        
        # Конвертация в моно если стерео
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)
        
        # Нормализация
        audio = audio.astype(np.float32)
        audio = audio / np.max(np.abs(audio))
        
        # Ресэмплинг если нужно
        if sample_rate != self.target_sample_rate:
            num_samples = int(len(audio) * self.target_sample_rate / sample_rate)
            audio = signal.resample(audio, num_samples)
            sample_rate = self.target_sample_rate
        
        return audio, sample_rate
    
    def bandpass_filter(self, audio, sample_rate):
        """Полосовой фильтр для выделения сигнала Морзе"""
        # Используем предкомпилированные коэффициенты
        if self._filter_coefficients is None:
            self._compile_filter()
        
        b, a = self._filter_coefficients
        filtered = signal.filtfilt(b, a, audio)
        
        return filtered
    
    def envelope_detection(self, audio, sample_rate):
        """Детектирование огибающей сигнала"""
        # Получение амплитуды через преобразование Гильберта
        analytic_signal = signal.hilbert(audio)
        envelope = np.abs(analytic_signal)
        
        # Сглаживание огибающей
        window_size = int(sample_rate * 0.01)  # 10 мс окно
        if window_size % 2 == 0:
            window_size += 1
        envelope = signal.medfilt(envelope, window_size)
        
        return envelope
    
    def detect_pulses(self, envelope, sample_rate):
        """Детектирование импульсов (точек и тире)"""
        # Адаптивный порог на основе перцентилей
        # Для импульсных сигналов (CW) большую часть времени сигнал выключен,
        # поэтому используем высокий перцентиль как порог
        threshold = np.percentile(envelope, self.pulse_percentile)
        
        # Бинаризация сигнала
        binary = (envelope > threshold).astype(int)
        
        # Поиск переходов
        diff = np.diff(np.concatenate(([0], binary, [0])))
        starts = np.where(diff == 1)[0]
        ends = np.where(diff == -1)[0]
        
        # Векторизованное создание массива импульсов
        start_times = starts / sample_rate
        end_times = ends / sample_rate
        durations = (ends - starts) / sample_rate
        
        pulses = [
            {'start': float(s), 'end': float(e), 'duration': float(d)}
            for s, e, d in zip(start_times, end_times, durations)
        ]
        
        # Векторизованное создание массива пауз
        if len(pulses) > 1:
            gaps = (start_times[1:] - end_times[:-1]).tolist()
        else:
            gaps = []
        
        return pulses, gaps
    
    def estimate_wpm(self, pulses):
        """Оценка скорости передачи в словах в минуту (WPM)"""
        if not pulses:
            return 0
        
        # Определяем минимальную длительность импульса (точка)
        durations = [p['duration'] for p in pulses]
        unit_time = np.median(durations)  # Используем медиану вместо минимума для устойчивости
        
        # По стандарту CODEX/PARIS: слово "PARIS" = 50 единичных элементов
        # WPM = 60 / (50 * unit_time) = 1.2 / unit_time
        wpm = 1.2 / unit_time if unit_time > 0 else 0
        
        # Ограничиваем разумными пределами (10-100 WPM для большинства случаев)
        wpm = max(10, min(100, wpm))
        
        return round(wpm)
    
    def classify_morse(self, pulses, gaps, verbose=True):
        """Классификация импульсов на точки и тире"""
        if not pulses:
            return ""
        
        # Определение базовой единицы времени (точка)
        durations = [p['duration'] for p in pulses]
        
        # Используем кластеризацию для определения точек и тире
        durations_sorted = sorted(durations)
        
        if len(durations_sorted) < 2:
            # Если только один тип импульсов
            unit_time = durations_sorted[0]
        else:
            # Находим разделение между точками и тире
            # Предполагаем, что тире в 3 раза длиннее точки
            median_duration = np.median(durations)
            unit_time = median_duration / 1.5  # примерная оценка
        
        # Классификация импульсов
        morse_symbols = []
        for i, pulse in enumerate(pulses):
            if pulse['duration'] < unit_time * 2:
                morse_symbols.append('.')
            else:
                morse_symbols.append('-')
        
        # Оценка скорости передачи
        wpm = self.estimate_wpm(pulses)
        if wpm > 0 and verbose:
            print(f"⚡ Определена скорость: ~{wpm} WPM")
        
        # Группировка в символы и слова
        morse_code = self.group_morse_symbols(morse_symbols, gaps, unit_time)
        
        return morse_code
    
    def group_morse_symbols(self, symbols, gaps, unit_time):
        """Группировка морзе-символов в буквы и слова"""
        if not symbols:
            return ""
        
        # Адаптивное определение порогов на основе распределения пауз
        median_gap = np.median(gaps)
        # Используем анализ распределения пауз для определения порогов
        # Есть 3 группы: внутрибуквенные, межбуквенные, межсловные
        gaps_sorted = np.sort(gaps)
        
        # Находим значительные разрывы в распределении пауз
        # Оптимизация: один вызов вместо трёх
        p62, p90, p92 = np.percentile(gaps_sorted, [self.gap_percentile_dot_dash, 
                                                     self.gap_percentile_char, 
                                                     self.gap_percentile_word])
        
        # Порог между внутрибуквенными и межбуквенными:
        # берём середину между концом первого кластера и началом второго
        letter_threshold = p62 * 1.5  # чуть выше максимума первого кластера
        
        # Порог между межбуквенными и межсловными:
        # берём середину между концом второго и началом третьего кластера
        word_threshold = (p90 + p92) / 2
        
        morse_letters = []
        current_letter = symbols[0]
        
        for i, gap in enumerate(gaps):
            if i + 1 >= len(symbols):
                break
            
            if gap < letter_threshold:  # элементы одной буквы
                current_letter += symbols[i + 1]
            elif gap < word_threshold:  # конец буквы
                morse_letters.append(current_letter)
                current_letter = symbols[i + 1]
            else:  # конец слова
                morse_letters.append(current_letter)
                morse_letters.append(' ')
                current_letter = symbols[i + 1]
        
        # Добавляем последнюю букву
        morse_letters.append(current_letter)
        
        return morse_letters
    
    def decode_morse(self, morse_letters, language='en'):
        """Декодирование морзе в текст"""
        morse_dict = MORSE_CODE_DICT_EN if language == 'en' else MORSE_CODE_DICT_RU
        
        decoded_text = []
        for i, letter in enumerate(morse_letters):
            if letter == ' ':
                # Только один пробел между словами, не добавляем пробелы вокруг него
                if decoded_text and decoded_text[-1] != ' ':
                    decoded_text.append(' ')
            elif letter in PROSIGNS_MORSE:
                # ПРИОРИТЕТ: Сначала проверяем prosigns (слитные комбинации)
                decoded_text.append(PROSIGNS_MORSE[letter])
            elif letter in morse_dict:
                decoded_text.append(morse_dict[letter])
            else:
                decoded_text.append('□')  # неизвестный/нераспознанный символ
        
        # Объединяем без дополнительных пробелов
        return ''.join(decoded_text)
    
    def process_file(self, filepath, language='en', analyze_procedural=True, verbose=True):
        """Полная обработка аудио файла"""
        
        # Проверка кеша
        if self.use_cache:
            params_dict = {
                'pulse_percentile': self.pulse_percentile,
                'gap_percentile_dot_dash': self.gap_percentile_dot_dash,
                'gap_percentile_char': self.gap_percentile_char,
                'gap_percentile_word': self.gap_percentile_word,
                'language': language,
                'analyze_procedural': analyze_procedural
            }
            cache_key = _get_file_params_hash(filepath, params_dict)
            
            if cache_key in _DECODE_CACHE:
                if verbose:
                    print(f"\n{'='*60}")
                    print(f"⚡ Используется кешированный результат: {Path(filepath).name}")
                    print(f"{'='*60}")
                return _DECODE_CACHE[cache_key]
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Обработка: {Path(filepath).name}")
            print(f"{'='*60}")
        
        try:
            # Загрузка аудио
            audio, sample_rate = self.load_audio(filepath)
            if verbose:
                print(f"✓ Загружено: {len(audio)/sample_rate:.2f} сек, {sample_rate} Гц")
            
            # Фильтрация
            filtered = self.bandpass_filter(audio, sample_rate)
            if verbose:
                print(f"✓ Применен полосовой фильтр: {self.min_freq}-{self.max_freq} Гц")
            
            # Детектирование огибающей
            envelope = self.envelope_detection(filtered, sample_rate)
            if verbose:
                print(f"✓ Детектирована огибающая сигнала")
            
            # Детектирование импульсов
            pulses, gaps = self.detect_pulses(envelope, sample_rate)
            if verbose:
                print(f"✓ Обнаружено импульсов: {len(pulses)}")
            
            if not pulses:
                if verbose:
                    print("✗ Импульсы не обнаружены")
                duration = len(audio) / sample_rate
                stats = {
                    'wpm': 0,
                    'pulses': 0,
                    'duration': round(duration, 2),
                    'pulse_threshold': self.pulse_percentile,
                    'error': 'No pulses detected'
                }
                return None, None, stats
            
            # Классификация
            morse_letters = self.classify_morse(pulses, gaps, verbose=verbose)
            if verbose:
                print(f"✓ Распознано морзе-символов: {len([m for m in morse_letters if m != ' '])}")
            
            # Сохраняем морзе-код
            morse_code_str = ' '.join(morse_letters)
            
            # Декодирование
            text_en = self.decode_morse(morse_letters, 'en')
            text_ru = self.decode_morse(morse_letters, 'ru')
            
            if verbose:
                print(f"\n📝 Морзе-код: {morse_code_str}")
                print(f"\n🇬🇧 Английский: {text_en}")
                print(f"🇷🇺 Русский: {text_ru}")
            
            # Анализ процедурных кодов
            if analyze_procedural and HAS_PROCEDURAL_CODES:
                detector = ProceduralCodeDetector()
                
                # Анализируем оба варианта
                detected_en = detector.detect_codes(text_en)
                detected_ru = detector.detect_codes(text_ru)
                
                # Выбираем более релевантный анализ
                total_codes_en = (len(detected_en['q_codes']) + 
                                 len(detected_en['z_codes']) + 
                                 len(detected_en['cw_abbreviations']))
                total_codes_ru = (len(detected_ru['q_codes']) + 
                                 len(detected_ru['z_codes']) + 
                                 len(detected_ru['cw_abbreviations']))
                
                if total_codes_en > 0 or total_codes_ru > 0:
                    # Показываем анализ для варианта с большим количеством кодов
                    if verbose:
                        if total_codes_en >= total_codes_ru:
                            print(detector.format_analysis(detected_en))
                        else:
                            print(detector.format_analysis(detected_ru))
            
            # Вычисление статистики
            duration = len(audio) / sample_rate
            # WPM расчет по стандарту PARIS (50 дитов на слово)
            total_dits = sum(len(m) for m in morse_letters if m != ' ')
            if total_dits > 0 and duration > 0:
                wpm = (total_dits / 50) / (duration / 60)
            else:
                wpm = 0
            
            stats = {
                'wpm': round(wpm, 1),
                'pulses': len(pulses),
                'duration': round(duration, 2),
                'pulse_threshold': self.pulse_percentile,
                'morse_code': morse_code_str
            }
            
            # Расширенная аналитика сигналов
            if HAS_SIGNAL_ANALYZER:
                analyzer = SignalAnalyzer(sample_rate)
                
                # Определение типа модуляции
                modulation = analyzer.detect_modulation_type(filtered, sample_rate)
                
                # Анализ чистоты сигнала
                purity = analyzer.analyze_signal_purity(filtered, envelope, sample_rate)
                
                # Анализ мастерства оператора
                skill = analyzer.analyze_operator_skill(pulses, gaps)
                
                # Добавляем в статистику
                stats['signal_analysis'] = {
                    'modulation': modulation,
                    'purity': purity,
                    'operator_skill': skill
                }
                
                if verbose:
                    print(f"\n📊 РАСШИРЕННАЯ АНАЛИТИКА")
                    print(f"{'='*60}")
                    print(f"\n🔊 Тип модуляции: {modulation['type']} (уверенность: {modulation['confidence']}%)")
                    print(f"\n✨ Чистота сигнала:")
                    print(f"   Общая оценка:     {purity['purity_score']:.1f}/100")
                    print(f"   Дрейф частоты:    {purity['chirp']:.1f}")
                    print(f"   Щелчки/клики:     {purity['clicks']}")
                    print(f"   Уровень шума:     {purity['noise_level']:.1f}%")
                    print(f"   SNR (оценка):     {purity['snr_estimate']:.1f} dB")
                    print(f"   QRM (помехи):     {'Да' if purity['qrm_detected'] else 'Нет'}")
                    print(f"\n👤 Мастерство оператора:")
                    print(f"   Уровень:          {skill['skill_level']}")
                    print(f"   Общая оценка:     {skill['skill_score']:.1f}/100")
                    print(f"   Стабильность:     {skill['timing_stability']:.1f}/100")
                    print(f"   Консистентность:  {skill['rhythm_consistency']:.1f}/100")
                    print(f"   Точка/Тире:       {skill['dot_dash_ratio']:.2f} (идеал: 3.0)")
            
            # Сохранение результата в кеш
            result = (text_en, text_ru, stats)
            if self.use_cache:
                # Управление размером кеша (простой LRU)
                if len(_DECODE_CACHE) >= _CACHE_MAX_SIZE:
                    # Удаляем первый элемент (самый старый)
                    first_key = next(iter(_DECODE_CACHE))
                    del _DECODE_CACHE[first_key]
                
                _DECODE_CACHE[cache_key] = result
            
            return result
            
        except FileNotFoundError:
            print(f"❌ Файл не найден: {filepath}")
            return None, None, {'wpm': 0, 'pulses': 0, 'duration': 0, 'error': 'File not found'}
        except Exception as e:
            print(f"❌ Ошибка обработки: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, None, {'wpm': 0, 'pulses': 0, 'duration': 0, 'error': str(e)}


def process_directory(directory_path, output_file='results.txt'):
    """Обработка всех WAV файлов в директории"""
    decoder = MorseDecoder()
    directory = Path(directory_path)
    
    # Поиск всех WAV файлов
    wav_files = list(directory.glob('*.wav'))
    
    if not wav_files:
        print("WAV файлы не найдены")
        return
    
    print(f"\n🎵 Найдено {len(wav_files)} WAV файлов\n")
    
    results = []
    
    for wav_file in wav_files:
        text_en, text_ru = decoder.process_file(str(wav_file))
        
        if text_en or text_ru:
            results.append({
                'file': wav_file.name,
                'english': text_en,
                'russian': text_ru
            })
    
    # Сохранение результатов
    if results:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("РЕЗУЛЬТАТЫ ДЕКОДИРОВАНИЯ АЗБУКИ МОРЗЕ\n")
            f.write("="*70 + "\n\n")
            
            for i, result in enumerate(results, 1):
                f.write(f"{i}. Файл: {result['file']}\n")
                f.write(f"   Английский: {result['english']}\n")
                f.write(f"   Русский: {result['russian']}\n")
                f.write("-"*70 + "\n\n")
        
        print(f"\n✓ Результаты сохранены в {output_file}")
    
    return results


if __name__ == "__main__":
    # Обработка всех файлов из папки TrainingData
    training_data_path = Path(__file__).parent / "TrainingData"
    
    if training_data_path.exists():
        results = process_directory(training_data_path)
    else:
        print(f"Папка {training_data_path} не найдена")
        
        # Пример обработки одного файла
        print("\nПример использования:")
        print("decoder = MorseDecoder()")
        print("text_en, text_ru = decoder.process_file('path/to/file.wav')")
