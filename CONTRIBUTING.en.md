# 🤝 Contributing to MorseDecoder

[![Русский](https://img.shields.io/badge/Language-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-lightgrey)](CONTRIBUTING.md) [![English](https://img.shields.io/badge/Language-English-blue)](CONTRIBUTING.en.md)

## 🐛 Bugs and suggestions

Check [existing issues](https://github.com/tixset/MorseDecoder/issues). Include the command, expected and actual results, OS, Python version, and FFmpeg version. When possible, attach a short recording and reference Morse transcription; do not publish material you cannot share.

Use the [bug report](.github/ISSUE_TEMPLATE/bug_report.en.md) or [feature request](.github/ISSUE_TEMPLATE/feature_request.en.md) template.

## 🧪 Setup and tests

Install dependencies using the [README](README.en.md). Work on a separate branch in your fork. Run commands from the repository root:

```bash
python run_all_tests.py
python -m unittest discover -s tests -v
python -m unittest tests.test_noisy_cw tests.test_cli_language -v
```

The main runner automatically discovers `test*.py`, counts import failures as errors, and exits nonzero on failure. It saves `reports/test_results_<timestamp>.txt` and a copy at `reports/test_results_latest.txt`. Skips are shown separately and do not count as passed tests. MP3 tests require FFmpeg; inspect the skip list.

`tests/test_procedural_codes.py` also contains older demonstration functions; automated checks should use `unittest.TestCase` with assertions. A `test_*` filename alone does not imply automated coverage.

For DSP changes, use the reference recording and synthetic signals. For CLI changes, check EN/RU, help, and errors. Do not commit generated reports, caches, or personal recordings.

## 🔧 Code and documentation

Follow PEP 8, use clear names, and document public parameters and return formats. See the [architecture guide](docs/ARCHITECTURE.en.md) for module organization.

Update both documentation languages together. Each pair should have reciprocal `img.shields.io` language badges; resolve relative links from each Markdown file's directory. The unchanged MIT license text is exempt. Record unreleased changes in the Unreleased section of both changelogs.

## 🤝 Pull requests

Describe the problem, resulting behavior, and validation. Use the [Russian](.github/PULL_REQUEST_TEMPLATE.md) or [English](.github/PULL_REQUEST_TEMPLATE/english.md) template; the English template can be selected with `template=english.md` in the PR creation URL. Use Conventional Commits: `fix:`, `feat:`, `docs:`, `test:`, `refactor:`, `chore:`. Template selection is described in the [GitHub documentation](https://docs.github.com/en/pull-requests/reference/using-query-parameters-to-create-a-pull-request).

Contributions are distributed under the [MIT license](LICENSE). Ask questions in Issues or email tixset@gmail.com.
