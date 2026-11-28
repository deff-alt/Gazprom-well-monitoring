$ErrorActionPreference = "Stop"
$services = @(
    "telemetry",
    "ml-diagnostics",
    "alert",
    "well-registry"
)
foreach ($service in $services) {
    Write-Host "`n========== TEST: $service ==========" -ForegroundColor Cyan
    Push-Location (Join-Path $PSScriptRoot $service)
    try {
        python -m pip install -r requirements-dev.txt
        python -m pytest -q tests
        if ($LASTEXITCODE -ne 0) { throw "Тесты сервиса $service завершились с ошибкой" }
    } finally {
        Pop-Location
    }
}
Write-Host "`nВсе наборы тестов успешно завершены." -ForegroundColor Green
