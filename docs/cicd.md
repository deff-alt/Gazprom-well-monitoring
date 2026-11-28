# CI/CD для Well Monitor — лабораторная работа №5

## Выбор платформы
GitHub Actions выбран потому, что конфигурация пайплайна хранится в репозитории рядом с кодом, запускается автоматически при push и Pull Request и интегрируется с GitHub Container Registry (GHCR).

## Этапы workflow
1. **Test** — четыре параллельных задания для `well-registry`, `telemetry`, `ml-diagnostics`, `alert`. Используется Python 3.12; устанавливаются зависимости и запускаются unit-тесты.
2. **Docker Build** — проверяется `docker-compose.lab4.yml` и собираются образы четырёх бизнес-сервисов.
3. **Publish** — при push в `main` или `master` образ `telemetry` публикуется в GHCR с тегами `latest` и commit SHA. При Pull Request публикация не выполняется.

## Секреты
Для авторизации применяется автоматически выдаваемый GitHub Actions `GITHUB_TOKEN`. Он не хранится в исходниках. Workflow получает `packages: write`, необходимое для публикации. Не помещайте токены в YAML, Dockerfile или README.

## Подключение
1. Добавьте `.github/workflows/cicd.yml` в корень проекта.
2. Проверьте наличие `Dockerfile`, `requirements.txt`, `requirements-dev.txt` и `tests/` у каждого из четырёх сервисов.
3. Выполните:
   ```bash
   git add .github/workflows/cicd.yml docs/cicd.md README.md
   git commit -m "ci: configure GitHub Actions"
   git push origin main
   ```
   Если основная ветка `master`, используйте её.
4. Откройте GitHub → вкладка **Actions** → **Well Monitor CI/CD**.
5. После успешного прогона откройте GitHub Packages и проверьте образ telemetry.

## Локальная проверка
```powershell
.\services\run-lab4-tests.ps1
python -m pytest -v services/integration-tests
docker compose -f docker-compose.lab4.yml config --quiet
docker compose -f docker-compose.lab4.yml build well-registry telemetry ml-diagnostics alert
```
Unit-тесты запускаются в CI отдельно для каждого сервиса. Интеграционный тест через Gateway выполняется локально отдельно, так как требует работающего стенда ЛР4.

## Демонстрация успешного и неуспешного запуска
- Успешный прогон: GitHub Actions → последний workflow → jobs завершились `Success`.
- Неуспешный прогон: в отдельной ветке временно измените ожидаемое значение в unit-тесте на неверное, отправьте commit и откройте Pull Request. Job сервиса упадёт; Docker Build и Publish не запустятся, так как зависят от успешных тестов. Затем отмените тестовое изменение и повторите запуск.
- Не вносите намеренную ошибку в основную ветку.

## Примечание по структуре
Перед первым push убедитесь, что у каждого сервиса действительно есть `requirements-dev.txt` и Dockerfile по указанному пути. Если структура или имя основной ветки отличаются, исправьте workflow.
