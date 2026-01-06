"""
GUI для настройки параметров декодера Морзе в реальном времени
Позволяет экспериментировать с percentile порогами без изменения кода

Автор: Антон Зеленов (tixset@gmail.com)
GitHub: https://github.com/tixset/MorseDecoder
Лицензия: MIT
"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from pathlib import Path
import threading
from modules.morse_decoder import MorseDecoder
import subprocess


class MorseTunerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Morse Decoder Tuner 🎛️")
        self.root.geometry("900x700")
        
        self.current_file = None
        self.current_wav = None
        self.decoder = None
        
        # Создание интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # === ПАНЕЛЬ ВЫБОРА ФАЙЛА ===
        file_frame = ttk.LabelFrame(self.root, text="📁 Выбор файла", padding=10)
        file_frame.pack(fill='x', padx=10, pady=5)
        
        self.file_label = ttk.Label(file_frame, text="Файл не выбран", foreground='gray')
        self.file_label.pack(side='left', padx=5)
        
        ttk.Button(file_frame, text="Открыть MP3/OGG/WAV", 
                  command=self.select_file).pack(side='right', padx=5)
        
        # === ПАНЕЛЬ ПАРАМЕТРОВ ===
        params_frame = ttk.LabelFrame(self.root, text="⚙️ Параметры Percentile", padding=10)
        params_frame.pack(fill='x', padx=10, pady=5)
        
        # Pulse Detection Percentile (70-95)
        self.create_slider(params_frame, "Импульсы (Pulse Detection)", 
                          70, 95, 85, 0, 'pulse_percentile')
        
        # Gap Dot-Dash Percentile (50-70)
        self.create_slider(params_frame, "Точка/Тире (Dot-Dash Gap)", 
                          50, 70, 62, 1, 'gap_percentile_dot_dash')
        
        # Gap Character Percentile (85-95)
        self.create_slider(params_frame, "Символ (Character Gap)", 
                          85, 95, 90, 2, 'gap_percentile_char')
        
        # Gap Word Percentile (90-98)
        self.create_slider(params_frame, "Слово (Word Gap)", 
                          90, 98, 92, 3, 'gap_percentile_word')
        
        # === КНОПКИ УПРАВЛЕНИЯ ===
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill='x', padx=10)
        
        self.decode_btn = ttk.Button(control_frame, text="🔄 Декодировать", 
                                     command=self.decode_file, state='disabled')
        self.decode_btn.pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="🔃 Сбросить", 
                  command=self.reset_defaults).pack(side='left', padx=5)
        
        self.status_label = ttk.Label(control_frame, text="Готов к работе", foreground='green')
        self.status_label.pack(side='right', padx=5)
        
        # === СТАТИСТИКА ===
        stats_frame = ttk.LabelFrame(self.root, text="📊 Статистика", padding=10)
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        self.stats_text = ttk.Label(stats_frame, text="—", font=('Consolas', 9))
        self.stats_text.pack()
        
        # === ВЫВОД РЕЗУЛЬТАТА ===
        output_frame = ttk.LabelFrame(self.root, text="📝 Результат декодирования", padding=10)
        output_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Английский
        ttk.Label(output_frame, text="🇬🇧 Английский:", font=('Arial', 9, 'bold')).pack(anchor='w')
        self.output_en = scrolledtext.ScrolledText(output_frame, height=8, font=('Consolas', 10))
        self.output_en.pack(fill='both', expand=True, pady=(0, 10))
        
        # Русский
        ttk.Label(output_frame, text="🇷🇺 Русский:", font=('Arial', 9, 'bold')).pack(anchor='w')
        self.output_ru = scrolledtext.ScrolledText(output_frame, height=8, font=('Consolas', 10))
        self.output_ru.pack(fill='both', expand=True)
        
    def create_slider(self, parent, label, min_val, max_val, default, row, var_name):
        """Создание ползунка с подписями"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky='ew', pady=5)
        parent.columnconfigure(0, weight=1)
        
        # Заголовок
        title_label = ttk.Label(frame, text=label, width=25, anchor='w')
        title_label.pack(side='left', padx=(0, 10))
        
        # Значение
        value_var = tk.IntVar(value=default)
        setattr(self, var_name, value_var)
        
        value_label = ttk.Label(frame, textvariable=value_var, width=3, 
                               font=('Consolas', 10, 'bold'))
        value_label.pack(side='right', padx=(10, 0))
        
        # Ползунок
        slider = ttk.Scale(frame, from_=min_val, to=max_val, 
                          orient='horizontal', variable=value_var,
                          command=lambda v: value_var.set(int(float(v))))
        slider.pack(side='left', fill='x', expand=True)
        
    def select_file(self):
        """Выбор аудио файла"""
        filetypes = [
            ('Аудио файлы', '*.mp3 *.ogg *.wav'),
            ('MP3 файлы', '*.mp3'),
            ('OGG файлы', '*.ogg'),
            ('WAV файлы', '*.wav'),
            ('Все файлы', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="Выбор аудио файла",
            filetypes=filetypes,
            initialdir=Path('TrainingData') if Path('TrainingData').exists() else Path.cwd()
        )
        
        if filename:
            self.current_file = Path(filename)
            self.file_label.config(text=self.current_file.name, foreground='black')
            self.decode_btn.config(state='normal')
            self.status_label.config(text="Файл загружен, нажмите Декодировать", foreground='blue')
            
            # Очистка предыдущих результатов
            self.output_en.delete(1.0, tk.END)
            self.output_ru.delete(1.0, tk.END)
            self.stats_text.config(text="—")
    
    def convert_to_wav(self, audio_path):
        """Конвертация в WAV если нужно"""
        if audio_path.suffix.lower() == '.wav':
            return audio_path
        
        wav_path = audio_path.with_suffix('.wav')
        
        if wav_path.exists():
            return wav_path
        
        try:
            cmd = [
                'ffmpeg', '-i', str(audio_path),
                '-ar', '8000', '-ac', '1', '-y',
                str(wav_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return wav_path
            else:
                raise Exception("FFmpeg конвертация не удалась")
        except FileNotFoundError:
            raise Exception("FFmpeg не установлен")
    
    def decode_file(self):
        """Декодирование файла с текущими параметрами"""
        if not self.current_file:
            return
        
        # Запуск в отдельном потоке
        thread = threading.Thread(target=self._decode_thread)
        thread.daemon = True
        thread.start()
    
    def _decode_thread(self):
        """Декодирование в отдельном потоке"""
        try:
            self.status_label.config(text="⏳ Декодирование...", foreground='orange')
            self.decode_btn.config(state='disabled')
            
            # Конвертация в WAV
            self.current_wav = self.convert_to_wav(self.current_file)
            
            # Создание декодера с текущими параметрами
            self.decoder = MorseDecoder(
                pulse_percentile=self.pulse_percentile.get(),
                gap_percentile_dot_dash=self.gap_percentile_dot_dash.get(),
                gap_percentile_char=self.gap_percentile_char.get(),
                gap_percentile_word=self.gap_percentile_word.get()
            )
            
            # Обработка
            text_en, text_ru, stats = self.decoder.process_file(str(self.current_wav))
            
            # Обновление GUI в главном потоке
            self.root.after(0, self._update_results, text_en, text_ru, stats)
            
        except Exception as e:
            error_msg = f"Ошибка: {type(e).__name__}: {str(e)}"
            self.root.after(0, self._show_error, error_msg)
    
    def _update_results(self, text_en, text_ru, stats):
        """Обновление результатов в GUI"""
        # Вывод текста
        self.output_en.delete(1.0, tk.END)
        self.output_en.insert(1.0, text_en if text_en else "(нет данных)")
        
        self.output_ru.delete(1.0, tk.END)
        self.output_ru.insert(1.0, text_ru if text_ru else "(нет данных)")
        
        # Статистика
        if stats:
            stats_str = (
                f"⚡ WPM: {stats.get('wpm', 0)} | "
                f"📊 Импульсов: {stats.get('pulses', 0)} | "
                f"⏱️ Длительность: {stats.get('duration', 0):.1f}с | "
                f"🎯 Символов: {len(text_en)}"
            )
            self.stats_text.config(text=stats_str)
        
        self.status_label.config(text="✅ Декодирование завершено", foreground='green')
        self.decode_btn.config(state='normal')
    
    def _show_error(self, error_msg):
        """Отображение ошибки"""
        self.output_en.delete(1.0, tk.END)
        self.output_en.insert(1.0, error_msg)
        
        self.status_label.config(text="❌ Ошибка", foreground='red')
        self.decode_btn.config(state='normal')
    
    def reset_defaults(self):
        """Сброс параметров к значениям по умолчанию"""
        self.pulse_percentile.set(85)
        self.gap_percentile_dot_dash.set(62)
        self.gap_percentile_char.set(90)
        self.gap_percentile_word.set(92)
        
        self.status_label.config(text="Параметры сброшены", foreground='blue')


def main():
    root = tk.Tk()
    app = MorseTunerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
