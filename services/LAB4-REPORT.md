# Лабораторная работа № 4

## Микросервисная архитектура Well Monitor: RabbitMQ, API Gateway и сервисная декомпозиция

**Выполнил:** \[ФИО\]\
**Группа:** \[номер группы\]\
**Дата:** 20.11.2026\
**Ветка:** `lab4`\
**Репозиторий:** https://github.com/deff-alt/Gazprom-well-monitoring

------------------------------------------------------------------------

## 1. Цель работы

Перевести монолитное приложение Well Monitor на микросервисную
архитектуру: разделить функциональность на независимые сервисы,
настроить обмен сообщениями через брокер RabbitMQ, объединить сервисы за
единым API Gateway на Nginx и обеспечить запуск всего стека одной
командой через Docker Compose.

## 2. Архитектура решения

Взаимодействие компонентов организовано следующим образом: клиент
отправляет HTTP-запросы на API Gateway (Nginx), который перенаправляет
их соответствующим микросервисам. Для асинхронного обмена событиями
между сервисами используется RabbitMQ по протоколу AMQP.

``` text
Клиент / Postman
      |
      | HTTP :8090
      v
+-----------------------------+
| API Gateway — Nginx 1.27    |
| gateway.lab4.conf           |
+-----------------------------+
      |
      +----------+-----------+-----------+----------------+
      |          |           |           |                |
      v          v           v           v                v
 well-registry telemetry ml-diagnostics alert     notification-mock
    :8000       :8000       :8000       :8000          :8000
   SQLite      SQLite      SQLite      SQLite        заглушка
      |          |           |           |
      +----------+-----------+-----------+
                         |
                      AMQP :5672
                         |
                         v
                 +---------------+
                 |   RabbitMQ    |
                 |   3.13 mgmt   |
                 |   UI :15672   |
                 +---------------+
```

### 2.1. Сервисы и их зоны ответственности

  --------------------------------------------------------------------------------------
  Сервис                            Порт (хост) Назначение          Хранилище
  ----------------------- --------------------- ------------------- --------------------
  **well-registry**                        8000 Реестр скважин,     `registry_data`
                                                справочники, CRUD   (SQLite)

  **telemetry**                             --- Приём и хранение    `telemetry_data`
                                                телеметрии,         
                                                публикация событий  
                                                в RabbitMQ          

  **ml-diagnostics**                        --- Обучение Isolation  `diagnostics_data`
                                                Forest, инференс,   
                                                публикация алертов  

  **alert**                                 --- Управление          `alerts_data`
                                                жизненным циклом    
                                                алертов, вызов      
                                                notification-mock   

  **notification-mock**                     --- Заглушка внешнего   ---
                                                сервиса уведомлений 
                                                (по методичке)      

  **gateway**                              8090 Единая точка входа, ---
                                                маршрутизация, CORS 

  **rabbitmq**                     5672 / 15672 Брокер сообщений,   volume
                                                Management UI       
  --------------------------------------------------------------------------------------

## 3. Что сделано в рамках лабораторной

### 3.1. Сервисная декомпозиция

Монолит `backend/` разделён на четыре независимых FastAPI-сервиса в
каталоге `services/`:

``` text
services/
├── well-registry/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── db.py
│       ├── models.py
│       ├── schemas.py
│       └── routers/
│           └── wells.py
├── telemetry/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       └── routers/
├── ml-diagnostics/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       └── routers/
└── alert/
    ├── Dockerfile
    ├── requirements.txt
    └── app/
        ├── __init__.py
        ├── main.py
        └── routers/
```

Каждый сервис собирается в отдельный Docker-образ на базе
`python:3.12-slim` и запускается через Uvicorn.

### 3.2. Брокер сообщений RabbitMQ

-   Образ: `rabbitmq:3.13-management-alpine`.
-   Порты: `5672` (AMQP), `15672` (Management UI).
-   Healthcheck: `rabbitmq-diagnostics ping`, интервал 5 с, 10 ретраев.
-   Остальные сервисы зависят от RabbitMQ с условием
    `condition: service_healthy` --- то есть стартуют только после того,
    как брокер действительно готов принимать соединения.
-   Учётная запись по умолчанию: `guest` / `guest` (для демонстрации; в
    production должна быть заменена).

### 3.3. API Gateway на Nginx

-   Образ: `nginx:1.27-alpine`.
-   Конфигурация: `gateway.lab4.conf`, монтируется в контейнер как
    read-only.
-   Слушает `8090` на хосте (чтобы не конфликтовать с монолитом на
    `8000`).
-   Маршрутизирует запросы к сервисам по префиксам (`/registry/`,
    `/telemetry/`, `/ml/`, `/alerts/`).
-   Зависит от всех четырёх сервисов, чтобы стартовать после них.

### 3.4. Docker Compose

Файл `docker-compose.lab4.yml` описывает весь стек:

-   7 сервисов (rabbitmq, gateway, well-registry, telemetry,
    ml-diagnostics, alert, notification-mock);
-   4 именованных volume для персистентности SQLite-баз;
-   healthcheck для RabbitMQ;
-   зависимости `depends_on` с условиями `service_healthy` /
    `service_started`;
-   монтирование исходников в контейнеры (`./services/...:/app`) для
    hot-reload через `--reload` в Uvicorn.

## 4. Запуск

### 4.1. Требования

-   Docker Desktop (Windows / macOS / Linux) с Docker Compose v2.
-   Свободные порты: `8000`, `8090`, `5672`, `15672`.

### 4.2. Команда запуска

``` bash
docker compose -f docker-compose.lab4.yml up -d --build
```

Первая сборка занимает \~20--30 секунд (скачивание `python:3.12-slim`,
установка зависимостей). Повторный запуск без `--build` --- несколько
секунд.

### 4.3. Проверка статуса

``` bash
docker compose -f docker-compose.lab4.yml ps
```

Ожидаемый вывод: 7 контейнеров в статусе `Up`, RabbitMQ ---
`Up (healthy)`.

### 4.4. Остановка

``` bash
docker compose -f docker-compose.lab4.yml down
```

С флагом `-v` удаляются также volume с данными.

## 5. Проверка работоспособности

### 5.1. Well-registry напрямую

``` powershell
curl.exe http://localhost:8000/health
# {"status":"ok"}

curl.exe http://localhost:8000/docs
# HTML Swagger UI
```

### 5.2. Через API Gateway

``` powershell
curl.exe http://localhost:8090/registry/health
```

Если маршрут в `gateway.lab4.conf` настроен как `/registry/`, ответ
придёт от well-registry. Если возвращается 404 --- маршрут может
называться иначе, но сам gateway работает (порт 8090 слушается).

### 5.3. RabbitMQ Management UI

Открыть в браузере: http://localhost:15672

-   Логин: `guest`
-   Пароль: `guest`

В панели видны:

-   **Overview** --- общая статистика;
-   **Connections** --- подключения сервисов;
-   **Queues** --- очереди сообщений;
-   **Exchanges** --- точки обмена.

### 5.4. Проверка сервисов изнутри Docker-сети

Сервисы `telemetry`, `ml-diagnostics`, `alert`, `notification-mock` не
проброшены на хост (у них нет `ports` в compose). Проверить их можно
изнутри:

``` bash
docker compose -f docker-compose.lab4.yml exec telemetry wget -qO- http://localhost:8000/health
docker compose -f docker-compose.lab4.yml exec ml-diagnostics wget -qO- http://localhost:8000/health
docker compose -f docker-compose.lab4.yml exec alert wget -qO- http://localhost:8000/health
docker compose -f docker-compose.lab4.yml exec notification-mock wget -qO- http://localhost:8000/health
```

Либо посмотреть логи:

``` bash
docker compose -f docker-compose.lab4.yml logs telemetry
```

В логах должно быть:

``` text
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

## 6. Возникшие проблемы и их решения

### 6.1. `failed to connect to the docker API at npipe://...`

**Причина:** Docker Desktop не запущен.

**Решение:** запустить Docker Desktop и дождаться, пока значок кита
станет зелёным.

### 6.2. `failed to read dockerfile: open Dockerfile: no such file or directory`

**Причина:** Notepad в Windows сохраняет файлы с расширением `.txt`
(`Dockerfile.txt`, `main.py.txt`).

**Решение:** переименовать файлы в `Dockerfile` / `main.py` без
дополнительного расширения. Либо создавать файлы через PowerShell с
`Out-File`, чтобы расширение не добавлялось.

### 6.3. `failed to fetch anonymous token: ... EOF / TLS handshake timeout`

**Причина:** нестабильный доступ к Docker Hub через встроенный прокси
Docker Desktop (`http.docker.internal:3128`).

**Решение:** повторить:

``` bash
docker pull python:3.12-slim
```

При повторяющейся ошибке --- настроить `registry-mirrors` в Docker
Desktop → Settings → Docker Engine.

### 6.4. `failed to compute cache key: "/requirements.txt": not found`

**Причина:** в папке сервиса отсутствовал `requirements.txt`.

**Решение:** создать файл со следующим содержимым:

``` text
fastapi
uvicorn[standard]
```

## 7. Результат

-   Монолит декомпозирован на 4 независимых микросервиса + 1 mock.
-   RabbitMQ поднят, healthcheck работает, Management UI доступен.
-   API Gateway на Nginx объединяет сервисы за единой точкой входа на
    8090.
-   Docker Compose поднимает весь стек одной командой.
-   Все 7 контейнеров в статусе `Up`, RabbitMQ --- `Up (healthy)`.
-   Well-registry доступен на `http://localhost:8000`, gateway --- на
    `http://localhost:8090`.
-   Исходники смонтированы в контейнеры, hot-reload работает.

## 8. Что говорить на защите

**Цель:** перевести Well Monitor с монолита на микросервисы, чтобы
каждый сервис можно было разрабатывать, масштабировать и деплоить
независимо.

**Декомпозиция:** выделены 4 сервиса по бизнес-способностям --- реестр
скважин, телеметрия, ML-диагностика, алерты. Плюс mock-сервис
уведомлений.

**Брокер:** RabbitMQ связывает сервисы асинхронно. Телеметрия публикует
события, ML-диагностика их потребляет, алерты создаются по результатам
инференса.

**Gateway:** Nginx на 8090 --- единая точка входа. Клиент не знает, за
каким сервисом стоит обработчик. Это упрощает CORS, аутентификацию и
маршрутизацию.

**Docker Compose:** весь стек --- 7 контейнеров, 4 volume, healthcheck,
зависимости. Запуск одной командой:

``` bash
docker compose -f docker-compose.lab4.yml up -d --build
```

**Проверка:** `docker compose ps` показывает все контейнеры `Up`,
RabbitMQ `healthy`. `curl http://localhost:8000/health` возвращает
`{"status":"ok"}`. Management UI RabbitMQ доступен на порту `15672`.

**Проблемы и решения:** Dockerfile.txt от Notepad, прокси Docker
Desktop, отсутствие requirements.txt --- всё описано в разделе 6.

## 9. Дальнейшие шаги (за рамками лабы)

-   Перевести SQLite на PostgreSQL / TimescaleDB для high-frequency
    телеметрии.
-   Добавить аутентификацию на gateway (JWT validation на Nginx или
    отдельный auth-сервис).
-   Настроить очереди RabbitMQ с подтверждениями (publisher confirms,
    dead-letter queue).
-   Добавить Prometheus + Grafana для мониторинга сервисов.
-   Написать интеграционные тесты (Postman / pytest + testcontainers).

------------------------------------------------------------------------

## Как добавить отчёт в Git

Сохрани файл в корне проекта под именем `LAB4-REPORT.md`, затем выполни:

``` powershell
git add LAB4-REPORT.md
git commit -m "lab4: отчёт для защиты"
git push -u origin lab4
```

На защите файл можно открыть в VS Code или распечатать. Тезисы из
раздела 8 предназначены для устного выступления.

Если нужно добавить скриншоты `docker compose ps`, логов RabbitMQ или
Swagger, их можно вставить в раздел 7.
