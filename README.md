# TransLog — обмен документами и чат для логистической компании

Веб-приложение для обмена документами (CMR, ТТН, путевые листы и т.д.) между водителями
и диспетчерами с чатом по каждому рейсу.

## Стек

- **Backend:** Python 3.11, Flask, SQLite (стандартная библиотека `sqlite3`)
- **Frontend:** ванильный JS (без сборки), поллинг чата каждые 2,5 с
- **Запуск:** gunicorn

## Возможности

- Роли «водитель» и «диспетчер» (сессии, хеширование паролей)
- Загрузка документов к рейсу, скачивание файлов
- Статусы документов: на проверке → одобрен / отклонён → повторная отправка
- Чат по каждому рейсу с прикреплением документов, непрочитанные сообщения
- Панель диспетчера: все рейсы, фильтры и поиск по документам

## Демо-учётные записи

| Логин        | Пароль          | Роль        | Рейс      |
|--------------|-----------------|-------------|-----------|
| `dispatcher` | `dispatcher123` | диспетчер   | все рейсы |
| `ivan`       | `driver123`     | водитель    | ORD-1042  |
| `maria`      | `driver123`     | водитель    | ORD-1043  |
| `oleg`       | `driver123`     | водитель    | ORD-1044  |
| `dmitry`     | `driver123`     | водитель    | ORD-1045  |

## Запуск локально

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Откройте http://localhost:5000

## Деплой на Amvera.ai

1. Создайте репозиторий на GitHub и залейте код:

   ```bash
   git init
   git add .
   git commit -m "TransLog initial commit"
   git branch -M main
   git remote add origin https://github.com/<ваш-логин>/translog.git
   git push -u origin main
   ```

2. В [Amvera Cloud](https://cloud.amvera.ru/projects) нажмите «Создать» → «Приложение»,
   выберите Python и подключите репозиторий GitHub (либо склонируйте выданный Amvera
   репозиторий: `git remote add amvera https://git.amvera.ru/<пользователь>/translog && git push amvera main`).

3. Файл `amvera.yml` уже лежит в корне — сборка и запуск пройдут автоматически
   (gunicorn, порт 5000). Дождитесь статуса «Успешно развернуто».

4. База SQLite и загруженные файлы автоматически сохраняются в постоянном хранилище `/data`
   (на локальной машине — в папке проекта). Приложение определяет среду по переменной
   окружения `AMVERA`.

5. Рекомендуется задать переменную окружения `SECRET_KEY` (в настройках проекта Amvera)
   со случайной строкой для подписи сессий.

## Структура проекта

```
translog/
├── app.py              # backend: API, SQLite, загрузка файлов
├── requirements.txt    # зависимости
├── amvera.yml          # конфигурация сборки/запуска Amvera
├── static/
│   ├── index.html      # страница (логин + приложение)
│   ├── style.css       # стили
│   └── app.js          # frontend-логика
└── README.md
```

## API (кратко)

- `POST /api/login`, `POST /api/logout`, `GET /api/me`
- `GET /api/orders` — рейсы (для водителя — только свой)
- `GET/POST /api/docs` — список / загрузка документа (multipart)
- `POST /api/docs/<id>/approve|reject|resend`
- `GET /api/docs/<id>/download`
- `GET /api/msgs?order_id=&after_id=` — чат (поллинг), отметка прочтения
- `POST /api/msgs` — отправить сообщение (`text` и/или `doc_id`)
