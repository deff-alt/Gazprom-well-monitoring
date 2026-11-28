# Демонстрационные сценарии ЛР4

Все клиентские запросы выполняются через API Gateway: `http://localhost:8090`. В Postman откройте `postman/Well-Monitor-Lab4.postman_collection.json`. ID записей в примерах генерируются системой; используйте фактический ID из ответа предыдущего запроса.

## 1. Запуск и проверка сервисов

```powershell
docker compose -f docker-compose.lab4.yml up -d --build
docker compose -f docker-compose.lab4.yml ps
```

Выполните запросы:

- `GET /health/registry`
- `GET /health/telemetry`
- `GET /health/ml`
- `GET /health/alert`

Ожидаемый результат — HTTP 200 и `status: ok` для каждого сервиса.

## 2. Реестр: создание скважины и идемпотентность

`POST /api/v1/wells` с заголовком `Idempotency-Key: well-create-lab4-001` и телом:

```json
{
  "well_number": "LAB4-1001",
  "locality_id": 1,
  "promysel_id": 1,
  "type": "Добывающая",
  "status": "active",
  "depth": 2700,
  "reservoir_pressure": 17.8,
  "temperature": 65,
  "latitude": 45.2,
  "longitude": 38.9
}
```

Ожидается HTTP 201. Повторите тот же запрос с тем же ключом и телом: сервис вернёт тот же объект, не создавая новую скважину. Повторное использование ключа с другим телом должно вернуть HTTP 409 в формате `application/problem+json`. Для повторной демонстрации используйте новое значение `well_number` и новый ключ.

## 3. Приём телеметрии и идемпотентность

`POST /api/v1/telemetry`, заголовок `Idempotency-Key: telemetry-lab4-001`:

```json
{
  "well_id": 1,
  "pressure": 22.5,
  "temperature": 75.0,
  "flow_rate": 125.5,
  "vibration": 3.2
}
```

Подставьте существующий `well_id` из реестра. Ожидается HTTP 201 и поле `replayed: false`. Повторите тот же запрос с тем же ключом: должен вернуться тот же ID и `replayed: true`. Измените любое значение при сохранении ключа — ожидается HTTP 409. Новое измерение публикует событие `telemetry.received`.

## 4. Диагностика и асинхронное оповещение

Для проверки аномалии отправьте измерение с высоким уровнем вибрации:

```json
{
  "well_id": 1,
  "pressure": 22.5,
  "temperature": 75.0,
  "flow_rate": 125.5,
  "vibration": 9.0
}
```

Используйте новый `Idempotency-Key`. Возьмите `id` измерения из ответа и выполните `POST /api/v1/predict` с телом `{"measurement_id": <ID>}`. При достижении порога диагностика возвращает `anomaly: true` и `severity: warning` либо `critical`. Событие `diagnostics.completed` обрабатывается Alert Service.

Проверьте `GET /api/v1/alerts`. При создании нового алерта Alert Service отправляет запрос в `notification-mock`. Историю принятых мок-уведомлений можно посмотреть в RabbitMQ-independent internal mock endpoint, доступном внутри Docker-сети: `GET http://notification-mock:8000/internal/v1/notifications`; также проверьте логи `notification-mock` командой `docker compose -f docker-compose.lab4.yml logs notification-mock`.

## 5. Saga: успешное завершение

`POST /api/v1/workflows/diagnose`, заголовок `Idempotency-Key: saga-success-lab4-001`, тело — измерение из сценария 4. Ожидается HTTP 200 и `status: completed`. Сценарий создаёт измерение, синхронно вызывает ML Diagnostics и публикует `workflow.completed`.

## 6. Saga: сбой и компенсация

1. Остановите ML-сервис:
   ```powershell
   docker compose -f docker-compose.lab4.yml stop ml-diagnostics
   ```
2. Выполните `POST /api/v1/workflows/diagnose` с новым ключом, например `saga-failure-lab4-001`.
3. Ожидается HTTP 502. При успешной компенсации ответ содержит сообщение об удалении созданного измерения.
4. Проверьте логи Telemetry: `docker compose -f docker-compose.lab4.yml logs telemetry`. В них должна быть запись о компенсации и публикации `workflow.compensated`.
5. Попробуйте получить ID компенсированного измерения через `GET /api/v1/telemetry/<ID>` — ожидается HTTP 404.
6. Верните ML-сервис:
   ```powershell
   docker compose -f docker-compose.lab4.yml start ml-diagnostics
   ```
7. Проверьте `GET /health/ml`.

## 7. Единый формат ошибок

Ошибочные ответы сервисов используют медиатип `application/problem+json` и общие поля `type`, `title`, `status`, `detail`, `instance`. Примеры проверок:

- Отправьте телеметрию с отрицательным `pressure` — HTTP 422.
- Передайте несуществующий `well_id` — HTTP 404.
- Повторите `Idempotency-Key` с изменённым телом — HTTP 409.
- Отправьте `measurement_id: 0` в запрос диагностики — HTTP 422.

## 8. Автоматические тесты

Из корня репозитория выполните:

```powershell
.\services\run-lab4-tests.ps1
```

Скрипт запускает unit/API-тесты каждого сервиса отдельно, чтобы изолировать одноимённые Python-пакеты `app`. Для интеграционного теста работающего стенда (Gateway → Registry → Telemetry → ML → Saga) сначала запустите Compose, затем из корня проекта выполните:

```powershell
python -m pip install -r services/integration-tests/requirements.txt
python -m pytest -q services/integration-tests
```
