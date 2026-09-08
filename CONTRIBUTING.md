# 🤝 Участие в разработке MorseDecoder

[![Русский](https://img.shields.io/badge/Language-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-blue)](CONTRIBUTING.md) [![English](https://img.shields.io/badge/Language-English-lightgrey)](CONTRIBUTING.en.md)

## 🐛 Ошибки и предложения

Проверьте [существующие задачи](https://github.com/tixset/MorseDecoder/issues). В отчёте укажите команду, ожидаемый и фактический результат, ОС, версию Python и FFmpeg. По возможности приложите короткую запись и эталон Морзе; не публикуйте материалы, которыми нельзя делиться.

Есть шаблоны [ошибки](.github/ISSUE_TEMPLATE/bug_report.md) и [предложения](.github/ISSUE_TEMPLATE/feature_request.md).

## 🧪 Подготовка и тесты

Установите зависимости по [README](README.md). Работайте в отдельной ветке своего форка. Команды выполняются из корня проекта:

```bash
python run_all_tests.py
python -m unittest discover -s tests -v
python -m unittest tests.test_noisy_cw tests.test_cli_language -v
```

Основной запускатель автоматически обнаруживает `test*.py`, учитывает ошибки импорта и завершает процесс с ненулевым кодом при провале. Он сохраняет `reports/test_results_<timestamp>.txt` и копию `reports/test_results_latest.txt`. Пропуски отображаются отдельно и не считаются успешными тестами. Для MP3-тестов нужен FFmpeg; проверяйте список пропусков.

`tests/test_procedural_codes.py` содержит также старые демонстрационные функции; автоматические проверки должны использовать `unittest.TestCase` с утверждениями. Наличие файла с именем `test_*` само по себе не означает наличие автоматических проверок.

Для изменений DSP используйте эталонную запись и синтетические сигналы. Для CLI проверяйте EN/RU, справку и сообщения об ошибках. Не включайте сгенерированные отчёты, кэши и личные записи в коммит.

## 🔧 Код и документация

Следуйте PEP 8, выбирайте понятные имена, документируйте публичные параметры и формат возвращаемых данных. Структура модулей описана в [архитектуре](docs/ARCHITECTURE.md).

Обновляйте обе языковые версии документации вместе. Каждая пара должна иметь взаимные переключатели через `img.shields.io`; относительные ссылки проверяйте из папки конкретного Markdown-файла. Исключение — неизменяемый текст лицензии MIT. Записывайте ещё не выпущенные изменения в раздел Unreleased обоих CHANGELOG.

## 🤝 Pull request

Опишите проблему, итоговое поведение и выполненные проверки. Используйте [русский](.github/PULL_REQUEST_TEMPLATE.md) или [английский](.github/PULL_REQUEST_TEMPLATE/english.md) шаблон; английский можно выбрать параметром `template=english.md` в URL создания PR. Коммиты оформляйте в стиле Conventional Commits: `fix:`, `feat:`, `docs:`, `test:`, `refactor:`, `chore:`. Выбор шаблона описан в [документации GitHub](https://docs.github.com/en/pull-requests/reference/using-query-parameters-to-create-a-pull-request).

Вклад распространяется по [лицензии MIT](LICENSE). Вопросы можно задать в Issues или по адресу tixset@gmail.com.
