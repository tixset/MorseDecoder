"""Check that repository test failures cannot produce a successful report."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from run_all_tests import generate_report


class TestRunnerRegression(unittest.TestCase):
    def test_import_failure_exits_nonzero_and_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(Path(__file__).resolve().parents[1] / 'run_all_tests.py',
                            root / 'run_all_tests.py')
            (root / 'tests').mkdir()
            (root / 'tests' / '__init__.py').touch()
            (root / 'tests' / 'test_broken.py').write_text(
                'raise ImportError("deliberate import failure")\n')
            result = subprocess.run([sys.executable, 'run_all_tests.py'], cwd=root,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            report = (root / 'reports' / 'test_results_latest.txt').read_text()
            self.assertIn('deliberate import failure', report)
            self.assertIn('Ошибки:           1', report)
            self.assertIn('Успешно:          0', report)

    def test_skips_are_not_reported_as_passes(self):
        result = unittest.TestResult()
        case = unittest.FunctionTestCase(lambda: None)
        result.startTest(case)
        result.addSkip(case, 'not available')
        result.stopTest(case)
        report = generate_report(result, 0, '')
        self.assertIn('Успешно:          0', report)
        self.assertIn('Пропущено:        1', report)
        self.assertIn('Процент успеха:   0.0%', report)
