# Contributing to MorseDecoder

[Русский](CONTRIBUTING.md) | **English**

Thank you for your interest in the project! Contributions to the Morse decoder are welcome.

## 📋 How to Contribute

### 1. Report Bugs

If you find a bug:

- Check whether it has already been reported in [Issues](https://github.com/tixset/MorseDecoder/issues).
- Open a new issue describing:
  - Steps to reproduce it.
  - Expected behavior.
  - Actual behavior.
  - Python version and operating system.
  - A sample audio file, if possible.

Use the [English bug report template](.github/ISSUE_TEMPLATE/bug_report.en.md).

### 2. Suggest Improvements

- Open an issue with the `enhancement` label.
- Describe the proposed feature.
- Explain why it would be useful.

An [English feature request template](.github/ISSUE_TEMPLATE/feature_request.en.md) is available.

### 3. Submit Pull Requests

1. **Fork** the repository.
2. Create a **branch** for your feature:

   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Commit** your changes:

   ```bash
   git commit -m 'feat: Add amazing feature'
   ```

4. **Push** the branch:

   ```bash
   git push origin feature/amazing-feature
   ```

5. Open a **pull request**. You can use the [English PR template](.github/PULL_REQUEST_TEMPLATE.en.md).

## 🔧 Coding Guidelines

### Code Style

- Follow PEP 8.
- Use clear variable names.
- Add docstrings to functions and classes.
- Comment on complex logic.

### Testing

- Run the tests before submitting a PR:

  ```bash
  python run_all_tests.py
  ```

- Add tests for new functionality.
- Make sure all tests pass.

The older Russian guide refers to `run_tests.py`; the current runner is `run_all_tests.py`.

### Commit Messages

Use Conventional Commits:

- `feat:` — a new feature.
- `fix:` — a bug fix.
- `docs:` — documentation changes.
- `refactor:` — code refactoring.
- `test:` — added or updated tests.
- `chore:` — routine maintenance.

Examples:

```text
feat: Add support for RTTY modulation detection
fix: Correct SNR calculation in signal analyzer
docs: Update README with installation instructions
```

## 📚 Areas for Contributions

### Priority Tasks

The original guide refers to `docs/IMPROVEMENT_SUGGESTIONS.md`, which is not present in this checkout. Check the project's [issues](https://github.com/tixset/MorseDecoder/issues) for available tasks.

### Contribution Ideas

- 🎯 Improve decoding accuracy.
- 🔊 Support additional modulation types.
- 🌍 Translate documentation into more languages.
- 📊 Improve result visualization.
- ⚡ Optimize performance.
- 🧪 Add tests.
- 📝 Improve documentation.

## ❓ Questions

- Open an issue with the `question` label.
- Email tixset@gmail.com.

## 📜 License

By contributing to the project, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing! 🎉**
