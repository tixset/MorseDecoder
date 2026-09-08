"""Prepare compressed audio for the WAV-based signal processing pipeline."""

from contextlib import contextmanager
from pathlib import Path
import subprocess
import tempfile

from .console_i18n import console_text as _


class AudioLoadError(ValueError):
    """An input file cannot be decoded or contains no usable audio."""


@contextmanager
def prepared_audio(filepath, sample_rate=8000):
    """Yield a WAV path, removing any converted file when processing finishes."""
    source = Path(filepath).resolve()
    if not source.is_file():
        raise AudioLoadError(_('Файл не найден: {0}', str(filepath)))
    if source.suffix.lower() == '.wav':
        yield source
        return
    if source.suffix.lower() not in ('.mp3', '.ogg'):
        raise AudioLoadError(_('Неподдерживаемый формат аудио: {0}. Используйте WAV, MP3 или OGG.', source.suffix))

    with tempfile.TemporaryDirectory(prefix='morse-audio-') as directory:
        converted = Path(directory) / 'audio.wav'
        try:
            result = subprocess.run(
                ['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error',
                 '-i', str(source), '-map', '0:a:0', '-vn', '-ac', '1',
                 '-ar', str(sample_rate), '-c:a', 'pcm_s16le', str(converted)],
                capture_output=True, check=False,
            )
        except FileNotFoundError as exc:
            raise AudioLoadError(_('Для чтения MP3/OGG требуется FFmpeg. Установите ffmpeg и добавьте его в PATH.')) from exc
        except OSError as exc:
            raise AudioLoadError(_('Не удалось запустить FFmpeg: {0}', str(exc))) from exc
        if result.returncode:
            detail = result.stderr.decode('utf-8', errors='replace').strip()
            raise AudioLoadError(_('Не удалось прочитать аудиофайл {0}: {1}', source.name, detail))
        yield converted
