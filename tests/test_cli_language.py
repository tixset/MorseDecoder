"""Regression tests for CLI language selection and preservation of decoded data."""

from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import json
import multiprocessing
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from scipy.io import wavfile

import morse_cli
from modules.console_i18n import (
    console_text, console_signal_warning, get_console_language, set_console_language,
)
from modules.procedural_codes import ProceduralCodeDetector


class CLILanguageTests(unittest.TestCase):
    def invoke(self, argv):
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                code = morse_cli.main(argv)
            except SystemExit as exc:
                code = exc.code
        return code, stdout.getvalue(), stderr.getvalue()

    def test_help_for_every_command_in_both_languages(self):
        for command in ([], ['auto'], ['batch'], ['decode'], ['multi'], ['experiment']):
            for ru in (False, True):
                with self.subTest(command=command, ru=ru):
                    flags = ['--ru'] if ru else []
                    code, output, _ = self.invoke(command + ['--help'] + flags)
                    self.assertEqual(code, 0)
                    self.assertIn('--ru', output)
                    if ru:
                        self.assertIn('Выводить сообщения', output)
                    else:
                        self.assertIn('Display console messages', output)
                        self.assertNotRegex(output, '[А-Яа-яЁё]')

    def test_missing_files_and_flag_positions(self):
        for command in ('auto', 'batch', 'decode', 'multi', 'experiment'):
            for before in (True, False):
                with self.subTest(command=command, before=before):
                    args = [command, '/nonexistent/Запись.wav']
                    ru_args = ['--ru'] + args if before else args + ['--ru']
                    code, output, _ = self.invoke(ru_args)
                    self.assertEqual(code, 1)
                    self.assertIn('не найден', output)
                    code, output, _ = self.invoke(args)
                    self.assertEqual(code, 1)
                    self.assertIn('not found', output)
                    self.assertIn('Запись.wav', output)

    def test_language_is_restored_after_help_and_errors(self):
        previous = get_console_language()
        self.invoke(['--help'])
        self.assertEqual(get_console_language(), previous)
        code, _, error = self.invoke(['auto', '--invalid'])
        self.assertEqual(code, 2)
        self.assertIn('error:', error)
        self.assertEqual(get_console_language(), previous)
        self.invoke(['--ru', 'auto', '/nonexistent.wav'])
        _, output, _ = self.invoke(['auto', '/nonexistent.wav'])
        self.assertIn('File not found', output)

    def test_double_dash_preserves_ru_as_filename(self):
        code, output, _ = self.invoke(['auto', '--', '--ru'])
        self.assertEqual(code, 1)
        self.assertIn('File not found: --ru', output)

    def test_translations_preserve_interpolated_data(self):
        text = 'Ошибка: Русский {file} QSL'
        self.assertEqual(console_text('❌ Файл не найден: {0}', text, language='en'),
                         '❌ File not found: ' + text)
        self.assertEqual(console_text('❌ Файл не найден: {0}', text, language='ru'),
                         '❌ Файл не найден: ' + text)

    def test_procedural_analysis_keeps_russian_report_default(self):
        detector = ProceduralCodeDetector()
        codes = detector.detect_codes('QSL QTH DE R1ABC AR')
        original = detector.format_analysis(codes)
        english = detector.format_analysis(codes, language='en')
        self.assertIn('АНАЛИЗ ПРОЦЕДУРНЫХ', original)
        self.assertIn('PROCEDURAL CODE', english)
        self.assertIn('Reception confirmed', english)
        self.assertNotRegex(english, '[А-Яа-яЁё]')
        self.assertEqual(detector.format_analysis(codes), original)

    def test_spawn_workers_receive_language(self):
        context = multiprocessing.get_context('spawn')
        for language, expected in (('en', 'File: sample.wav'), ('ru', 'Файл: sample.wav')):
            with context.Pool(1, initializer=set_console_language, initargs=(language,)) as pool:
                self.assertEqual(pool.apply(console_text, ('Файл: {0}', 'sample.wav')), expected)

    def test_signal_warning_preserves_measurements(self):
        previous = get_console_language()
        try:
            set_console_language('en')
            warning = 'Все 3 пика находятся в узком диапазоне (450 Hz) - вероятно это один сигнал'
            self.assertEqual(console_signal_warning(warning),
                             'All 3 peaks are in a narrow range (450 Hz) - this is probably one signal')
            set_console_language('ru')
            self.assertEqual(console_signal_warning(warning), warning)
        finally:
            set_console_language(previous)

    def test_decode_with_real_audio_in_both_languages(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.wav'
            sample_rate = 8000
            dot = np.sin(2 * np.pi * 600 * np.arange(480) / sample_rate)
            silence = np.zeros(480)
            audio = np.concatenate([silence] + [part for _ in range(8)
                                               for part in (dot, silence, dot, silence, dot,
                                                            np.zeros(1440))])
            wavfile.write(path, sample_rate, (audio * 16000).astype(np.int16))
            config = path.with_suffix('.config.json')
            config.write_text(json.dumps({'parameters': {}}))
            for ru in (False, True):
                # Avoid the existing result cache so both runs exercise detailed output.
                with patch.dict('modules.morse_decoder._DECODE_CACHE', clear=True):
                    code, output, error = self.invoke(['decode', str(path)] + (['--ru'] if ru else []))
                self.assertEqual(code, 0, error)
                self.assertIn('Декодирование завершено' if ru else 'Decoding complete', output)
                self.assertIn('Обработка:' if ru else 'Processing:', output)
                if not ru:
                    self.assertNotIn('Загружено:', output)
                    self.assertNotIn('Определена скорость:', output)


if __name__ == '__main__':
    unittest.main()
