"""End-to-end noisy audio checks, including an independently supplied recording."""
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import numpy as np
from scipy.io import wavfile

from modules.auto_tune import auto_tune_parameters
from modules.morse_decoder import MorseDecoder
from modules.cw_frontend import detect_keying, select_carrier


class NoisyCWTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg is required for the MP3 fixture')
    def test_recording_matches_user_reference_with_automatic_parameters(self):
        fixtures = Path(__file__).parent / 'fixtures'
        reference = json.loads((fixtures / 'noisy_cw.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            audio = Path(directory) / 'input.mp3'
            shutil.copyfile(fixtures / 'noisy_cw.mp3', audio)
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                result = auto_tune_parameters(audio)
            self.assertIsNotNone(result)
            self.assertEqual(result['text_ru'], reference['text_ru'])
            self.assertEqual(result['stats']['pulses'], 110)
            actual_morse = result['stats']['morse_code'].split()
            expected_morse = reference['morse'].replace('/', '').split()
            self.assertEqual(actual_morse, expected_morse)
            self.assertAlmostEqual(result['stats']['carrier_frequency'], 1189.5, delta=2)
            config = json.loads(audio.with_suffix('.config.json').read_text())['parameters']
            decoder = MorseDecoder(**config, use_cache=False)
            with redirect_stdout(StringIO()):
                _, decoded, _ = decoder.process_file(audio, verbose=False)
            self.assertEqual(decoded, reference['text_ru'])

    def test_other_messages_frequencies_speeds_and_noise(self):
        alphabet = {'P': '.--.', 'A': '.-', 'R': '.-.', 'I': '..', 'S': '...',
                    'T': '-', 'E': '.', '1': '.----', '2': '..---', '3': '...--'}
        expected = 'PARIS TEST 123'
        sample_rate = 8000
        for wpm in (12, 20, 35, 50):
            for carrier, noise in ((450, .15), (900, .5), (2400, .3)):
                with self.subTest(wpm=wpm, carrier=carrier, noise=noise):
                    unit = 1.2 / wpm
                    chunks = [np.zeros(sample_rate // 2)]
                    words = expected.split()
                    for wi, word in enumerate(words):
                        for ci, char in enumerate(word):
                            marks = alphabet[char]
                            for mi, mark in enumerate(marks):
                                chunks.append(np.ones(round(sample_rate * unit * (1 if mark == '.' else 3))))
                                if mi < len(marks) - 1:
                                    chunks.append(np.zeros(round(sample_rate * unit)))
                            if ci < len(word) - 1:
                                chunks.append(np.zeros(round(sample_rate * unit * 3)))
                        if wi < len(words) - 1:
                            chunks.append(np.zeros(round(sample_rate * unit * 7)))
                    chunks.append(np.zeros(sample_rate // 2))
                    keyed = np.concatenate(chunks)
                    time = np.arange(len(keyed)) / sample_rate
                    fading = .75 + .2 * np.sin(2 * np.pi * .5 * time)
                    rng = np.random.default_rng(10)
                    audio = (keyed * fading * np.sin(2 * np.pi * carrier * time)
                             + rng.normal(0, noise, len(time))
                             + .1 * np.sin(2 * np.pi * (carrier + 300) * time))
                    with tempfile.TemporaryDirectory() as directory:
                        path = Path(directory) / 'signal.wav'
                        wavfile.write(path, sample_rate, audio.astype(np.float32))
                        decoder = MorseDecoder(pulse_percentile=70, use_cache=False)
                        with redirect_stdout(StringIO()):
                            decoded, _, stats = decoder.process_file(path, verbose=False)
                    self.assertEqual(decoded, expected)
                    self.assertTrue(stats['timing']['reliable'])
                    self.assertAlmostEqual(stats['carrier_frequency'], carrier, delta=2)

    def test_silence_and_constant_amplitude_have_no_keying(self):
        for value in (0, 1):
            self.assertEqual(detect_keying(np.full(8000, value), 8000, 70), ([], []))
        self.assertIsNone(select_carrier(np.zeros(8000), 8000))

    def test_fixed_frequency_band_is_respected(self):
        decoder = MorseDecoder(min_freq=400, max_freq=800, auto_frequency=False)
        time = np.arange(8000) / 8000
        decoder.bandpass_filter(np.sin(2 * np.pi * 1200 * time), 8000)
        self.assertIsNone(decoder.carrier_frequency)
        self.assertEqual(decoder.filter_band, (400, 800))


if __name__ == '__main__':
    unittest.main()
