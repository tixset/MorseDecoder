"""Regression coverage for the user-provided extended code reference."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from modules import code_dictionaries as dictionaries
from modules.procedural_codes import ProceduralCodeDetector
from modules.morse_decoder import MorseDecoder
from modules.console_i18n import console_text
from modules.auto_tune import auto_tune_parameters, save_results
import shutil


class ExtendedCodeTests(unittest.TestCase):
    def test_reference_inventory_is_reachable_in_both_modes(self):
        # Counts from the supplied reference, not derived from implementation.
        groups = [('ARRL_QN_CODES', 'arrl_qn_codes', 26),
                  ('RU_Z_CODES', 'ru_z_codes', 4),
                  ('SHCH_CODES', 'shch_codes', 22),
                  ('RU_PROCEDURAL_ABBR', 'ru_procedural_abbr', 169),
                  ('CW_ABBREVIATIONS', 'cw_abbreviations', 55)]
        for fuzzy in (False, True):
            detector = ProceduralCodeDetector(use_fuzzy_matching=fuzzy)
            for name, field, count in groups:
                dictionary = getattr(dictionaries, name)
                self.assertEqual(len(dictionary), count)
                for code, meaning in dictionary.items():
                    with self.subTest(fuzzy=fuzzy, category=name, code=code):
                        matches = detector.detect_codes(code)[field]
                        self.assertTrue(any(m['code'] == code and m['meaning'] == meaning
                                            for m in matches))
                        self.assertNotRegex(console_text(meaning, language='en'), '[А-Яа-яЁё]')

    def test_conflicting_systems_and_profiles(self):
        all_codes = ProceduralCodeDetector().detect_codes('QNH ЗАН ZAN AA')
        self.assertNotEqual(all_codes['q_codes'][0]['meaning'],
                            all_codes['arrl_qn_codes'][0]['meaning'])
        self.assertEqual(all_codes['ru_z_codes'][0]['code'], 'ЗАН')
        self.assertEqual(all_codes['z_codes'][0]['code'], 'ZAN')
        self.assertEqual(all_codes['ru_z_codes'][0]['code_system'], 'soviet_z')
        self.assertIn('1982', all_codes['ru_z_codes'][0]['source'])
        for profile, kept, empty in [('ham_cw', 'q_codes', 'arrl_qn_codes'),
                                      ('arrl_traffic', 'arrl_qn_codes', 'q_codes')]:
            result = ProceduralCodeDetector(profile=profile).detect_codes('QNH')
            self.assertEqual(len(result[kept]), 1)
            self.assertEqual(result[empty], [])
        result = ProceduralCodeDetector(profile='ru_soviet').detect_codes('К Р Ц У В З Щ Ь')
        self.assertEqual(len(result['ru_procedural_abbr']), 8)
        result = ProceduralCodeDetector(profile='ham_cw').detect_codes('К Р Ц У В З Щ Ь')
        self.assertEqual(result['ru_procedural_abbr'], [])
        with self.assertRaises(ValueError):
            ProceduralCodeDetector(profile='invalid')

    def test_question_mark_and_word_boundaries(self):
        for fuzzy in (False, True):
            result = ProceduralCodeDetector(use_fuzzy_matching=fuzzy).detect_codes(
                'ЩРЖ? ЩРЖ QNH? QNH (РПТ), НЕИЗВЕСТНО xЩРЖx')
            self.assertEqual([m['is_question'] for m in result['shch_codes']], [True, False])
            self.assertEqual([m['is_question'] for m in result['arrl_qn_codes']], [True, False])
            self.assertEqual([m['code'] for m in result['ru_procedural_abbr']], ['РПТ'])

    def test_phrases_priority_and_rst(self):
        result = ProceduralCodeDetector().detect_codes(
            'НЕ ПНЛ ПНЛ PAN PAN SECURITE SÉCURITÉ ЬЬЬ ШТОРМ МЕДПОМОЩЬ МОЛНИЯ ЛЕСАВИА RST 599 RST 699 599')
        self.assertEqual([m['code'] for m in result['soviet_codes']].count('ПНЛ'), 1)
        self.assertIn('НЕ ПНЛ', [m['code'] for m in result['soviet_codes']])
        signals = [m['signal'] for m in result['service_signals']]
        for value in ('PAN PAN', 'SECURITE', 'SÉCURITÉ', 'ЬЬЬ'):
            self.assertIn(value, signals)
        self.assertEqual(len(result['soviet_urgency_levels']), 4)
        self.assertEqual(result['rst_reports'], [dict(code='RST', value='599', readability=5,
                                                    strength=9, tone=9)])

    def test_audio_symbols_and_joined_prosigns(self):
        decoder = MorseDecoder()
        patterns = ['..-.', ' ', '..-..', ' ', '..--..', ' ', '-.-', ' ', '...---...', ' ', '-.-..-..']
        self.assertEqual(decoder.decode_morse(patterns, language='ru'), 'Ф Э ? К <SOS> <CL>')
        self.assertEqual(decoder.decode_morse(['..-.'], language='en'), 'F')
        result = ProceduralCodeDetector().detect_codes('AR <AR> SK <SK> <SOS> <CL> <IMI> <K>')
        self.assertEqual([m['code'] for m in result['prosigns']], ['AR', 'SK', 'SOS', 'CL', 'IMI', 'K'])
        self.assertTrue(all(m['is_prosign'] for m in result['prosigns']))
        fuzzy = ProceduralCodeDetector(use_fuzzy_matching=True).detect_codes('AR <SOS>')
        self.assertTrue(any(m['code'] == 'SOS' and m['is_prosign'] for m in fuzzy['prosigns']))
        self.assertTrue(any(m['code'] == 'AR' and not m['is_prosign'] for m in fuzzy['prosigns']))

    def test_extended_report_contains_new_families_and_translations(self):
        detector = ProceduralCodeDetector()
        result = detector.detect_codes('QNI ЗАН ЩРЖ? РПТ ГР ШТОРМ SECURITE RST 599')
        for lang in ('ru', 'en'):
            report = detector.format_analysis(result, language=lang)
            for code in ('QNI', 'ЗАН', 'ЩРЖ?', 'РПТ', 'ГР', 'ШТОРМ', 'SECURITE', 'RST 599'):
                self.assertIn(code, report)
            self.assertNotIn('Обычное сообщение', report)
        english = detector.format_analysis(result, language='en')
        self.assertIn('Reception is absolutely impossible', english)
        self.assertIn('Group(s)', english)

    def test_soviet_alias_preserves_public_api(self):
        self.assertIs(dictionaries.SOVIET_CODES_LEGACY, dictionaries.SOVIET_CODES)
        self.assertEqual(dictionaries.RUSSIAN_PHONETIC['А'], 'Анна')


@unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg required')
class ExtendedReportTests(unittest.TestCase):
    def test_auto_report_keeps_complete_russian_analysis(self):
        with tempfile.TemporaryDirectory() as directory:
            audio = Path(directory) / 'sample.mp3'
            shutil.copyfile(Path(__file__).parent / 'fixtures' / 'noisy_cw.mp3', audio)
            with redirect_stdout(StringIO()):
                result = auto_tune_parameters(str(audio), mode='fast')
            self.assertIsNotNone(result)
            report = audio.with_suffix('.txt').read_text()
            self.assertIn('RU:', report)
            self.assertIn('РОССИЙСКИЕ ПРОЦЕДУРНЫЕ СОКРАЩЕНИЯ', report)
            self.assertIn('РПТ — Повторите / я повторяю', report)
            result['text_en'] = 'QNI SECURITE RST 599'
            result['text_ru'] = 'ЩРЖ? ЗАН ГР ШТОРМ'
            with redirect_stdout(StringIO()):
                save_results(str(audio), result, result['params'])
            report = audio.with_suffix('.txt').read_text()
            for code in ('QNI', 'SECURITE', 'RST 599', 'ЩРЖ?', 'ЗАН', 'ГР', 'ШТОРМ'):
                self.assertIn(code, report)


class BilingualReportTests(unittest.TestCase):
    def test_shared_structure_and_legacy_match_are_not_repeated(self):
        detector = ProceduralCodeDetector()
        report = detector.format_bilingual_analysis('RPT AL K', 'РПТ АЛ К', language='en')
        self.assertEqual(report.count('PROCEDURAL CODE AND COMMAND ANALYSIS'), 1)
        self.assertEqual(report.count('MESSAGE STRUCTURE:'), 1)
        self.assertEqual(report.count('• РПТ —'), 1)
        self.assertIn('• RPT —', report)
        self.assertIn('• АЛ —', report)
        self.assertNotIn('SOVIET PROCEDURAL CODES:', report)
        self.assertTrue(detector.detect_codes('РПТ')['soviet_codes'])

    def test_distinct_structures_and_conflicting_systems_are_preserved(self):
        detector = ProceduralCodeDetector()
        report = detector.format_bilingual_analysis('QNH QNH', 'ЗАН', language='en')
        self.assertEqual(report.count('MESSAGE STRUCTURE:'), 1)
        self.assertIn('EN:', report)
        self.assertIn('RU:', report)
        self.assertIn('Pressure reduced to sea level', report)
        self.assertIn('Your net frequency is too high', report)
        self.assertIn('Reception is absolutely impossible', report)
        shared = detector.format_bilingual_analysis('QNH QNH', 'QNH', language='en')
        self.assertEqual(shared.count('• QNH — Pressure reduced to sea level'), 2)

    @unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg required')
    def test_decode_cli_prints_one_report_in_each_language(self):
        import json
        import subprocess
        import sys
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'sample.config.json'
            config.write_text(json.dumps({'parameters': {
                'pulse_percentile': 70, 'gap_percentile_dot_dash': 55,
                'gap_percentile_char': 75, 'gap_percentile_word': 90}}))
            for language in ('en', 'ru'):
                for flag in ([], ['--analyze']):
                    command = [sys.executable, str(root / 'morse_cli.py'), 'decode',
                               str(root / 'tests/fixtures/noisy_cw.mp3'), '--config', str(config)]
                    command += flag + (['--ru'] if language == 'ru' else [])
                    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    title = ('АНАЛИЗ ПРОЦЕДУРНЫХ КОДОВ И КОМАНД' if language == 'ru'
                             else 'PROCEDURAL CODE AND COMMAND ANALYSIS')
                    self.assertEqual(result.stdout.count(title), 1)
                    self.assertEqual(result.stdout.count('• РПТ —'), 1)
                    self.assertIn('• АЛ —', result.stdout)
                    self.assertNotIn('🔍 Detected:', result.stdout)
                    self.assertNotIn('🔍 Обнаружено:', result.stdout)
