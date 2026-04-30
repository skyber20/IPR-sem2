import logging
import os
import time

from fastapi import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

logger = logging.getLogger(__name__)

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests processed by the application.",
    ["method", "route", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "route", "status_code"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)

TODO_TASKS_CREATED_TOTAL = Counter(
    "todo_tasks_created_total",
    "Total tasks created through the TODO Matrix API.",
)


def setup_metrics(app):
    if getattr(app.state, "metrics_enabled", False):
        return

    @app.middleware("http")
    async def collect_http_metrics(request, call_next):
        start_time = time.perf_counter()
        status_code = "500"

        try:
            response = await call_next(request)
            status_code = str(response.status_code)
            return response
        finally:
            route = _get_route_template(request)
            if route != "/metrics":
                duration = time.perf_counter() - start_time
                method = request.method

                HTTP_REQUESTS_TOTAL.labels(
                    method=method,
                    route=route,
                    status_code=status_code,
                ).inc()
                HTTP_REQUEST_DURATION_SECONDS.labels(
                    method=method,
                    route=route,
                    status_code=status_code,
                ).observe(duration)

    @app.get("/metrics", include_in_schema=False)
    def get_metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    app.state.metrics_enabled = True


def setup_tracing(app, engine=None):
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    if not otlp_endpoint:
        logger.info("OTLP endpoint is not set, tracing is disabled")
        return

    if getattr(app.state, "tracing_enabled", False):
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        logger.exception("OpenTelemetry packages are not installed, tracing is disabled")
        return

    service_name = os.getenv("OTEL_SERVICE_NAME", "todo-matrix-app")
    resource = Resource.create({"service.name": service_name})
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    exporter = OTLPSpanExporter(endpoint=_get_traces_endpoint(otlp_endpoint))
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))

    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)
    if engine is not None:
        SQLAlchemyInstrumentor().instrument(engine=engine)

    app.state.tracing_enabled = True
    logger.info("Tracing is enabled, OTLP endpoint: %s", otlp_endpoint)


def record_task_created():
    TODO_TASKS_CREATED_TOTAL.inc()


def _get_route_template(request):
    route = request.scope.get("route")
    if route is not None and getattr(route, "path", None):
        return route.path

    path = request.url.path
    if path.startswith("/static/"):
        return "/static/{path}"
    return path


def _get_traces_endpoint(otlp_endpoint):
    endpoint = otlp_endpoint.rstrip("/")
    if endpoint.endswith("/v1/traces"):
        return endpoint
    return f"{endpoint}/v1/traces"
