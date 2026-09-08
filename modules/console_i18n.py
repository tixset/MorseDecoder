"""Console translations; decoded data and saved reports are not translated."""

import json
from pathlib import Path

# Keep existing behavior for library/GUI callers. The CLI selects English at entry.
_language = 'ru'
_ENGLISH = json.loads(Path(__file__).with_name('console_en.json').read_text(encoding='utf-8'))


def set_console_language(language):
    """Select the language shared by console output and worker threads."""
    if language not in ('en', 'ru'):
        raise ValueError('Unsupported console language: ' + language)
    global _language
    _language = language


def get_console_language():
    return _language


def console_text(message, *values, language=None):
    """Translate a literal template before interpolating user data."""
    selected = _language if language is None else language
    template = _ENGLISH.get(message, message) if selected == 'en' else message
    return template.format(*values) if values else template


def console_signal_warning(message):
    """Translate stored signal warnings without changing report data."""
    import re

    patterns = (
        (r'Пики слишком близко \((\d+) Hz\) - возможно это один сигнал с гармониками',
         'Пики слишком близко ({0} Hz) - возможно это один сигнал с гармониками'),
        (r'Близкие амплитуды \(([\d.]+)\) и частоты - возможно один широкополосный сигнал',
         'Близкие амплитуды ({0}) и частоты - возможно один широкополосный сигнал'),
        (r'Все (\d+) пика находятся в узком диапазоне \((\d+) Hz\) - вероятно это один сигнал',
         'Все {0} пика находятся в узком диапазоне ({1} Hz) - вероятно это один сигнал'),
        (r'Малое расстояние между пиками \(среднее (\d+) Hz\) - вероятно это один сигнал',
         'Малое расстояние между пиками (среднее {0} Hz) - вероятно это один сигнал'),
    )
    for pattern, template in patterns:
        match = re.fullmatch(pattern, message)
        if match:
            return console_text(template, *match.groups())
    return console_text(message)
