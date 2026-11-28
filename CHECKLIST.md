# Checklist перед сдачей ЛР5

- [ ] `.github/workflows/cicd.yml` добавлен в репозиторий.
- [ ] Основная ветка — `main` или `master` (либо workflow скорректирован).
- [ ] У четырёх сервисов есть Dockerfile, requirements.txt, requirements-dev.txt и tests/.
- [ ] Локальный тестовый скрипт проходит.
- [ ] Docker Compose config и build проходят.
- [ ] Commit и push отправлены в GitHub.
- [ ] GitHub Actions завершился успешно.
- [ ] В GHCR появился telemetry image с тегами SHA и latest.
- [ ] В отдельном PR показан упавший тест; после демонстрации изменение отменено.
- [ ] README обновлён, docs/cicd.md добавлен.
