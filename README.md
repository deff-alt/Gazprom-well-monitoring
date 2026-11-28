# Well Monitor — мониторинг и предиктивная диагностика скважин

Веб-сервис для мониторинга фонда скважин, приёма телеметрии, выявления аномальных режимов и обработки диагностических событий. Проект подготовлен как прототип ВКР для предметной области газодобывающего предприятия.

## Быстрый запуск

Требуется Docker Desktop с Docker Compose.

```bash
docker compose up -d --build
```

После запуска:

| Компонент | Адрес |
|---|---|
| Веб-интерфейс | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

Демонстрационная учётная запись, создаваемая при первом старте: `admin` / `admin123`.

## Основные разделы

- **Обзор** — KPI фонда, карта, распределение скважин, последние события.
- **Фонд скважин** — реестр и карточки скважин.
- **Алерты и события** — фильтрация, назначение в работу, закрытие инцидентов.
- **ML-диагностика** — обучение Isolation Forest и ручной анализ последней точки телеметрии.
- **Месторождения / Промыслы / Пользователи** — справочники и администрирование в рамках RBAC.

## ML-диагностика

Модель обучается администратором в разделе «ML-диагностика». Минимум для демонстрационного обучения — 20 точек телеметрии. После обучения пользователь с соответствующей ролью может запустить диагностику конкретной скважины. Если модель помечает точку как аномальную, создаётся алерт; повторный активный алерт по тому же параметру в течение двух часов не создаётся.

Важно: Isolation Forest в текущей версии выявляет нетипичное поведение, но не предсказывает вероятность аварии или точное время до отказа. Подробности и план дальнейшего развития — в `docs/ROADMAP-AND-TECHNICAL-NOTES.md`.

## Безопасность конфигурации

Перед использованием вне локальной демонстрации:

1. Создайте `.env` на основе `.env.example`.
2. Задайте уникальные длинные `JWT_SECRET` и `TELEMETRY_API_KEY`.
3. Не публикуйте `.env` и не используйте демонстрационный пароль в рабочей среде.
4. Настройте HTTPS, резервное копирование PostgreSQL, аудит действий и управление секретами.

Шлюз телеметрии должен передавать `X-Telemetry-Key` в запросах к `POST /internal/v1/telemetry`.

## Технологии

- Backend: Python 3.12, FastAPI, SQLAlchemy 2 async, PostgreSQL 16, JWT.
- ML: scikit-learn Isolation Forest, NumPy, pandas, joblib.
- Frontend: React 18, Vite 5, React Router, Recharts, Leaflet / OpenStreetMap.
- Deployment: Docker Compose.

## Проверки

Python-модули проходят `compileall`; JSON package manifest и Docker Compose YAML проверены. Полную сборку Vite и запуск контейнеров следует выполнить локально командой выше после установки npm-зависимостей.


## Лабораторная работа №4 — запуск микросервисов

Запускать отдельно от основной ВКР:

```powershell
docker compose -f docker-compose.lab4.yml up -d --build
docker compose -f docker-compose.lab4.yml ps
```

API Gateway: `http://localhost:8090`; RabbitMQ Management: `http://localhost:15672` (`guest/guest`). Коллекция Postman: `postman/Well-Monitor-Lab4.postman_collection.json`. Сценарии: `docs/demo-scenarios.md`. Остановка: `docker compose -f docker-compose.lab4.yml down` (без `-v`, чтобы сохранить SQLite volumes).

## Лабораторная работа №4 — микросервисная архитектура

ЛР4 запускается отдельно от основной ВКР и не изменяет её Compose-конфигурацию. Для неё используются четыре бизнес-сервиса (`well-registry`, `telemetry`, `ml-diagnostics`, `alert`), отдельные SQLite-хранилища, RabbitMQ, Nginx API Gateway и мок внешнего сервиса уведомлений.

### Запуск ЛР4

```powershell
docker compose -f docker-compose.lab4.yml up -d --build
docker compose -f docker-compose.lab4.yml ps
```

Единая точка входа: `http://localhost:8090`. RabbitMQ Management: `http://localhost:15672` (учётные данные по умолчанию `guest` / `guest`).

Postman-коллекция: `postman/Well-Monitor-Lab4.postman_collection.json`. Подробные шаги демонстрации: `docs/demo-scenarios.md`. Отчёт: `services/LAB4-REPORT.md`.

### Автоматические тесты ЛР4

Тесты расположены в каталогах `services/<service>/tests`. Запуск из PowerShell из корня репозитория:

```powershell
.\services\run-lab4-tests.ps1
```

Скрипт устанавливает тестовые зависимости из `requirements-dev.txt` каждого сервиса и запускает его unit/API-тесты отдельно. Для запуска требуется доступ к Python package index при первой установке зависимостей. Для интеграционной проверки работающего стенда сначала запустите Compose, затем выполните `python -m pip install -r services/integration-tests/requirements.txt` и `python -m pytest -q services/integration-tests`.

### Остановка ЛР4

```powershell
docker compose -f docker-compose.lab4.yml down
```

Команда не удаляет Docker volumes с данными. Не используйте `-v`, если хотите сохранить тестовые записи.

