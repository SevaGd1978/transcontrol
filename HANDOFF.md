# TransLog — передаточный документ (HANDOFF)

## Что это
Веб-приложение логистической компании: обмен документами (CMR, ТТН, путевые листы)
между водителями и диспетчерами + чат по каждому рейсу.

## Стек
Python 3.11 · Flask · SQLite (stdlib sqlite3) · gunicorn · ванильный JS (поллинг чата 2,5 с)

## Что уже сделано
- Backend (app.py): сессии, роли driver/dispatcher, загрузка/скачивание файлов,
  статусы документов review → approved/rejected → resend, чат с last_read (непрочитанные),
  авто-сид демо-данных при первом запуске
- Frontend (static/): логин, панель диспетчера (рейсы, фильтры, поиск, одобрение/отклонение),
  кабинет водителя (форма загрузки, мои документы), чат с прикреплением документов
- Деплой: amvera.yml (gunicorn, порт 5000, persistenceMount /data), Dockerfile, README
- GitHub-репозиторий: https://github.com/SevaGd1978/transcontrol (ПУСТОЙ — пуш ещё не выполнен!)

## Демо-учётки
- dispatcher / dispatcher123 (диспетчер)
- ivan, maria, oleg, dmitry / driver123 (водители, рейсы ORD-1042…1045)

## Текущая проблема
Пуш на GitHub не выполнен: выданные fine-grained токены имеют Contents: **Read**.
Лечение: github.com/settings/tokens?type=beta → открыть токен → Edit →
Permissions → Repository permissions → **Contents → Read and write** → Save.
Либо создать классический токен (Tokens classic) с галочкой **repo** — проще.

## Дальнейшие шаги
1. Запушить проект (git push origin main из папки проекта)
2. Развернуть на Amvera Cloud: Создать → Приложение → Python → подключить репозиторий
   (amvera.yml уже в корне; данные в /data; задать SECRET_KEY)
3. Опционально: заменить поллинг на WebSocket (Flask-SocketIO), добавить PostgreSQL,
   уведомления по email/Telegram, загрузку фото с камеры телефона для водителей
