"""
Конвертация MP3 файлов в WAV и анализ
"""
import os
from pathlib import Path
import subprocess

def convert_mp3_to_wav(mp3_file, wav_file, target_rate=8000):
    """
    Конвертация MP3 в WAV 8kHz mono
    
    Args:
        mp3_file: путь к MP3
        wav_file: путь для WAV
        target_rate: целевая частота дискретизации
    """
    try:
        # Необязательный импорт: при его ошибке доступен FFmpeg.
        from pydub import AudioSegment
        # Попытка через pydub
        audio = AudioSegment.from_mp3(mp3_file)
        audio = audio.set_channels(1)  # mono
        audio = audio.set_frame_rate(target_rate)  # 8kHz
        audio.export(wav_file, format='wav')
        return True
    except Exception as e:
        print(f"⚠️  pydub error: {e}")
        # Попытка через ffmpeg напрямую
        try:
            cmd = [
                'ffmpeg', '-i', mp3_file,
                '-ar', str(target_rate),
                '-ac', '1',
                '-y',  # overwrite
                wav_file
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except Exception as e2:
            print(f"❌ ffmpeg error: {e2}")
            return False


def batch_convert_mp3_to_wav(folder="TrainingData", output_folder=None, max_files=None):
    """
    Пакетная конвертация всех MP3 в WAV
    
    Args:
        folder: папка с MP3
        output_folder: папка для WAV (если None, то та же)
        max_files: максимум файлов (None = все)
    """
    if output_folder is None:
        output_folder = folder
    
    folder_path = Path(folder)
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)
    
    mp3_files = sorted(folder_path.glob("*.mp3"))
    
    if max_files:
        mp3_files = mp3_files[:max_files]
    
    print(f"\n{'='*80}")
    print(f"🎵 КОНВЕРТАЦИЯ MP3 → WAV")
    print(f"{'='*80}")
    print(f"Найдено MP3 файлов: {len(mp3_files)}")
    print(f"Целевая частота: 8000 Гц, mono\n")
    
    successful = 0
    failed = []
    
    for i, mp3_file in enumerate(mp3_files, 1):
        wav_file = output_path / (mp3_file.stem + '.wav')
        
        # Пропуск если уже существует
        if wav_file.exists():
            print(f"[{i}/{len(mp3_files)}] ⏭️  {mp3_file.name} (уже существует)")
            successful += 1
            continue
        
        print(f"[{i}/{len(mp3_files)}] 🔄 {mp3_file.name} → {wav_file.name}")
        
        if convert_mp3_to_wav(str(mp3_file), str(wav_file)):
            print(f"           ✅ Успешно")
            successful += 1
        else:
            print(f"           ❌ Ошибка")
            failed.append(mp3_file.name)
    
    print(f"\n{'='*80}")
    print(f"📊 РЕЗУЛЬТАТЫ КОНВЕРТАЦИИ")
    print(f"{'='*80}")
    print(f"Успешно: {successful}/{len(mp3_files)}")
    if failed:
        print(f"Ошибки: {len(failed)}")
        for f in failed:
            print(f"  - {f}")
    
    return successful, failed


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Конвертация MP3 → WAV")
    parser.add_argument('folder', nargs='?', default='TrainingData', help='Папка с MP3')
    parser.add_argument('--output', help='Папка для WAV (по умолчанию та же)')
    parser.add_argument('--max-files', type=int, help='Максимум файлов')
    
    args = parser.parse_args()
    
    # Проверка наличия ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ ffmpeg найден")
    except:
        print("⚠️  ffmpeg не найден. Установите: https://ffmpeg.org/download.html")
        print("   Для чтения MP3 через pydub также требуется FFmpeg.")
    
    batch_convert_mp3_to_wav(
        folder=args.folder,
        output_folder=args.output,
        max_files=args.max_files
    )
