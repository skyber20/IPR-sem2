# Лабораторная работа 7

Observability: Prometheus, Grafana, Grafana Tempo

Приложение: TODO Matrix на FastAPI  
База данных: PostgreSQL

## Что сделано

- добавлен endpoint `/metrics` в формате Prometheus
- добавлены HTTP-метрики `http_requests_total` и `http_request_duration_seconds`
- добавлена бизнес-метрика `todo_tasks_created_total`
- labels у HTTP-метрик используют шаблон маршрута, например `/done_task/{task_id}`
- добавлен OpenTelemetry tracing с экспортом OTLP в Tempo
- приложение работает без Tempo, если `OTEL_EXPORTER_OTLP_ENDPOINT` пустой
- добавлен Docker Compose overlay для Prometheus, Grafana и Tempo
- Grafana автоматически получает datasources Prometheus и Tempo
- добавлен dashboard `TODO Matrix Observability`
- добавлен Kubernetes `ServiceMonitor` для `/metrics`
- в Helm chart добавлена настройка `serviceMonitor` и OTEL переменные
- добавлены манифесты Tempo и values для `kube-prometheus-stack`
- добавлена папка `docs/screenshots/lab7/` для скриншотов

## Docker Compose

Если файла `.env` нет:

```bash
cp .env.example .env
```

Запуск:

```bash
docker compose --profile development \
  -f docker-compose.yml \
  -f docker-compose.observability.yml \
  up -d --build
```

Проверка API:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/get_tasks
curl http://localhost:8000/metrics
```

Создать тестовую задачу:

```bash
curl -X POST http://localhost:8000/add_task \
  -H "Content-Type: application/json" \
  -d '{"text":"Проверка observability","quadrant":1}'
```

Адреса:

- приложение `http://localhost:8000`
- Prometheus `http://localhost:9090`
- Grafana `http://localhost:3001`
- Tempo `http://localhost:3200`
- pgAdmin `http://localhost:5050`

Grafana:

```text
Dashboards -> Lab7 -> TODO Matrix Observability
Explore -> Tempo
```

Логи:

```bash
docker compose --profile development \
  -f docker-compose.yml \
  -f docker-compose.observability.yml \
  logs app prometheus grafana tempo
```

## Скриншоты

Файлы лежат в `docs/screenshots/lab7/`:

- `prometheus-targets.png`
- `grafana-dashboard.png`
- `tempo-trace.png`
