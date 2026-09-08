"""Compressed input, conversion cleanup, and CLI failure regression tests."""

from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from scipy.io import wavfile

import morse_cli
from modules.audio_input import AudioLoadError, prepared_audio
from modules.auto_tune import auto_tune_parameters
from modules.console_i18n import get_console_language, set_console_language
from modules.morse_decoder import MorseDecoder


class AudioInputTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.folder = Path(self.directory.name)
        self.wav = self.folder / 'recording.wav'
        rate = 8000
        dot = np.sin(2 * np.pi * 600 * np.arange(480) / rate)
        letter = np.concatenate([dot, np.zeros(480), dot, np.zeros(480), dot, np.zeros(1440)])
        wavfile.write(self.wav, rate, (np.tile(letter, 8) * 16000).astype(np.int16))
        previous = get_console_language()
        self.addCleanup(set_console_language, previous)
        set_console_language('en')

    def encode(self, extension):
        if not shutil.which('ffmpeg'):
            self.skipTest('FFmpeg is required for compressed audio integration tests')
        target = self.folder / ('Запись с пробелами.' + extension)
        subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-i', str(self.wav), str(target)],
                       check=True, capture_output=True)
        return target

    def test_mp3_and_ogg_load_as_finite_mono_audio(self):
        for extension in ('mp3', 'ogg'):
            with self.subTest(extension=extension):
                source = self.encode(extension)
                audio, rate = MorseDecoder().load_audio(source)
                self.assertEqual(rate, 8000)
                self.assertEqual(audio.ndim, 1)
                self.assertTrue(np.isfinite(audio).all())
                self.assertGreater(np.max(np.abs(audio)), 0.9)
                self.assertAlmostEqual(len(audio) / rate, 3.84, delta=0.1)

    def test_conversion_cleanup_and_existing_wav_are_preserved(self):
        source = self.encode('mp3')
        existing = source.with_suffix('.wav')
        existing.write_bytes(b'user file')
        with prepared_audio(source) as temporary:
            self.assertTrue(temporary.is_file())
            self.assertNotEqual(temporary, existing)
        self.assertFalse(temporary.exists())
        self.assertEqual(existing.read_bytes(), b'user file')
        with self.assertRaisesRegex(RuntimeError, 'processing failed'):
            with prepared_audio(source) as temporary:
                raise RuntimeError('processing failed')
        self.assertFalse(temporary.exists())

    def test_auto_converts_once_and_saves_beside_original(self):
        source = self.encode('mp3')
        original = source.read_bytes()
        stdout = StringIO()
        with patch('modules.audio_input.subprocess.run', wraps=subprocess.run) as convert:
            with redirect_stdout(stdout), redirect_stderr(StringIO()):
                result = auto_tune_parameters(source)
        self.assertIsNotNone(result)
        self.assertEqual(convert.call_count, 1)
        self.assertTrue(source.with_suffix('.txt').is_file())
        self.assertTrue(source.with_suffix('.config.json').is_file())
        self.assertFalse(source.with_suffix('.wav').exists())
        self.assertEqual(source.read_bytes(), original)
        self.assertIn('BEST PARAMETERS AMONG TESTED COMBINATIONS', stdout.getvalue())
        self.assertNotIn('Traceback', stdout.getvalue())

    def test_missing_ffmpeg_stops_before_parameter_search_in_both_languages(self):
        source = self.folder / 'recording.mp3'
        source.write_bytes(b'compressed data')
        for flags, expected in (([], 'FFmpeg is required'), (['--ru'], 'требуется FFmpeg')):
            with self.subTest(flags=flags):
                stdout, stderr = StringIO(), StringIO()
                with patch('modules.audio_input.subprocess.run', side_effect=FileNotFoundError) as convert:
                    with redirect_stdout(stdout), redirect_stderr(stderr):
                        code = morse_cli.main(['auto', str(source)] + flags)
                self.assertEqual(code, 1)
                self.assertEqual(convert.call_count, 1)
                self.assertIn(expected, stdout.getvalue())
                self.assertNotIn('Progress:', stdout.getvalue())
                self.assertNotIn('BEST PARAMETERS AMONG TESTED COMBINATIONS', stdout.getvalue())
                self.assertNotIn('Traceback', stderr.getvalue())

    def test_corrupt_wav_and_mp3_do_not_start_search(self):
        for extension in ('wav', 'mp3'):
            source = self.folder / ('broken.' + extension)
            source.write_bytes(b'not audio')
            stdout, stderr = StringIO(), StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = morse_cli.main(['auto', str(source)])
            self.assertEqual(code, 1)
            self.assertNotIn('Progress:', stdout.getvalue())
            self.assertNotIn('Traceback', stderr.getvalue())
            self.assertFalse(source.with_suffix('.config.json').exists())

    def test_empty_audio_is_rejected_and_silence_stays_finite(self):
        wavfile.write(self.wav, 8000, np.array([], dtype=np.int16))
        with self.assertRaises(AudioLoadError):
            MorseDecoder().load_audio(self.wav)
        wavfile.write(self.wav, 8000, np.zeros(8000, dtype=np.int16))
        audio, _ = MorseDecoder().load_audio(self.wav)
        self.assertTrue(np.isfinite(audio).all())
        self.assertTrue((audio == 0).all())

    def test_unsuccessful_search_does_not_announce_success(self):
        stdout = StringIO()
        with patch('modules.auto_tune._test_params_wrapper', return_value=None):
            with redirect_stdout(stdout), redirect_stderr(StringIO()):
                result = auto_tune_parameters(self.wav)
        self.assertIsNone(result)
        self.assertNotIn('BEST PARAMETERS AMONG TESTED COMBINATIONS', stdout.getvalue())
        self.assertIn('Could not find suitable parameters', stdout.getvalue())

    def test_decode_input_failure_returns_nonzero(self):
        self.wav.write_bytes(b'broken WAV')
        self.wav.with_suffix('.config.json').write_text('{"parameters": {}}')
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = morse_cli.main(['decode', str(self.wav), '--analyze'])
        self.assertEqual(code, 1)
        self.assertNotIn('Decoding complete', stdout.getvalue())
        self.assertNotIn('Traceback', stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
