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

**Уже развёрнуто:** https://translog-sevagd1978.amvera.io (регион msk0, тариф «Пробный»).

Обновление кода:

```bash
git remote add amvera https://git.msk0.amvera.ru/sevagd1978/translog
git push amvera main:master   # Amvera собирает ветку master
```

Amvera автоматически собирает проект по `amvera.yml` из корня (gunicorn, порт 5000).
База SQLite и загруженные файлы сохраняются в постоянном хранилище `/data`
(локально — в папке проекта). Среда определяется по переменной окружения `AMVERA`.
`SECRET_KEY` задан через вкладку «Переменные окружения» в кабинете Amvera.

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
- `POST /api/orders/<order_id>/export` — собрать документы рейса в ZIP `ORD-XXXX_З-NNN.zip`, архив сохраняется в облачном хранилище `/data/exports`
- `GET /api/exports` — список архивов (водитель — только свой рейс)
- `GET /api/exports/<id>/download` — скачать архив
- `GET/POST /api/settings/tt` — настройки TransTrade API (только диспетчер; KEY хранится в БД, в ответе маскируется)
- `POST /api/tt/test` — проверка связи с TransTrade (метод GetDrivers)
- `POST /api/orders/<order_id>/push_tt` — выгрузить заказ в TransTrade (`CreateOrder`, при повторе — `EditOrder` по сохранённому `tt_order_id`)
- `GET/POST /api/settings/mega` — настройки облачного хранилища MEGA (только диспетчер; пароль хранится в БД, в ответе только флаг `has_password`)
- `POST /api/mega/test` — проверка входа в MEGA (логин + квота хранилища)

## Интеграция TransTrade API

В «Настройках» (кнопка в шапке, только диспетчер) задаются API URL, API KEY и
api_user_id из документации [tt-ok.ru/data/api_doc](https://tt-ok.ru/data/api_doc/).
Подпись запросов формируется по алгоритму сервиса:
`md5(API KEY + '###' + data + '###' + method + '###' + random + '###' + API KEY)`.
Кнопка «Отправить заказ в TransTrade» в шапке чата создаёт заказ
(`OrderNum` = рейс, `ClientOrderNum` = номер заявки, маршрут → `Load`/`Unload`),
повторное нажатие выполняет `EditOrder`.

## Облачное хранилище MEGA

В «Настройках» (вкладка «Облачное хранилище MEGA», только диспетчер) задаются
email и пароль аккаунта MEGA. После этого каждый загружаемый документ и каждый
ZIP-архив (`ORD-XXXX_З-NNN.zip`) дополнительно дублируются в MEGA, а в списках
документов и архивов появляется публичная ссылка «MEGA». Скачивание по-прежнему
идёт из локального кэша на сервере — быстро и не зависит от доступности MEGA;
если MEGA недоступен, документ сохраняется только локально, без потери данных.

Требование: у аккаунта MEGA должна быть **выключена** двухфакторная
аутентификация (mega.py не поддерживает 2FA). Проверить вход можно кнопкой
«Проверить вход» в настройках.
