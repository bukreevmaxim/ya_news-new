# YaNews: начальное состояние для unittest

## Подготовка и запуск

Для проекта нужен Python 3.14.

```bash
python -m venv venv
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata news.json
python manage.py runserver
```

Тесты запускаются из директории с файлом `manage.py`:

```bash
python manage.py test
```

До создания пакета `news/tests/` Django сообщит, что тесты не найдены.
