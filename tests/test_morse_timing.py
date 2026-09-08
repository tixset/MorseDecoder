"""Known Morse timing must determine speed independently of message length."""
import unittest
import numpy as np
from modules.morse_timing import estimate_timing
from modules.morse_decoder import MorseDecoder
from modules.signal_analyzer import SignalAnalyzer


class MorseTimingTests(unittest.TestCase):
    def test_known_speeds_and_unequal_dot_dash_counts(self):
        for wpm in (3, 8, 20, 50, 90):
            for lengths in ([1] * 30 + [3] * 3, [1] * 3 + [3] * 30):
                with self.subTest(wpm=wpm, lengths=lengths):
                    pulses = [{'duration': value * 1.2 / wpm} for value in lengths]
                    result = estimate_timing(pulses)
                    self.assertTrue(result['reliable'])
                    self.assertAlmostEqual(result['wpm'], wpm, delta=0.2)

    def test_ambiguous_or_insufficient_pulses_do_not_invent_speed(self):
        for values in ([], [0.06], [0.06] * 40, [0.18] * 40):
            result = estimate_timing([{'duration': value} for value in values])
            self.assertFalse(result['reliable'])
            self.assertEqual(result['wpm'], 0)

    def test_broad_noise_durations_are_not_reliable(self):
        durations = np.geomspace(0.0005, 0.9, 200)
        self.assertFalse(estimate_timing([{'duration': d} for d in durations])['reliable'])

    def test_clean_message_with_standard_gaps(self):
        # PARIS PARIS at 20 WPM; includes dot-heavy and dash-heavy letters.
        letters = ['.--.', '.-', '.-.', '..', '...', ' ', '.--.', '.-', '.-.', '..', '...']
        durations, gaps = [], []
        for index, letter in enumerate(letters):
            if letter == ' ':
                continue
            for symbol_index, symbol in enumerate(letter):
                durations.append(0.06 if symbol == '.' else 0.18)
                if symbol_index < len(letter) - 1:
                    gaps.append(0.06)
                elif index < len(letters) - 1:
                    gaps.append(0.42 if letters[index + 1] == ' ' else 0.18)
        pulses = [{'duration': duration} for duration in durations]
        decoder = MorseDecoder()
        classified = decoder.classify_morse(pulses, gaps, verbose=False)
        self.assertEqual(decoder.decode_morse(classified), 'PARIS PARIS')
        self.assertEqual(decoder.estimate_wpm(pulses), 20)

    def test_operator_is_unknown_without_reliable_signal(self):
        pulses = [{'duration': d} for d in [0.001, 0.04, 0.2] * 10]
        result = SignalAnalyzer().analyze_operator_skill(pulses, [0.02] * 29)
        self.assertEqual(result['skill_level'], 'UNKNOWN')


if __name__ == '__main__':
    unittest.main()
