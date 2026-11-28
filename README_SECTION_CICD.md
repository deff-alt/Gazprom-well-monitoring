## CI/CD (ЛР5)

GitHub Actions workflow: [Well Monitor CI/CD](.github/workflows/cicd.yml).

Workflow запускается при push и Pull Request в `main`/`master`, тестирует четыре бизнес-сервиса, проверяет Docker Compose, собирает их образы и публикует `telemetry` в GHCR при push в основную ветку. Для публикации используется защищённый `GITHUB_TOKEN`.

Описание этапов и инструкции: [docs/cicd.md](docs/cicd.md).

Локальные команды:
```powershell
.\services\run-lab4-tests.ps1
python -m pytest -v services/integration-tests
docker compose -f docker-compose.lab4.yml build well-registry telemetry ml-diagnostics alert
```
