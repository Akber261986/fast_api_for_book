import time
from typing import Callable, Dict
from collections import defaultdict
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST


# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'Duration of HTTP requests in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections',
    multiprocess_mode='livesum'
)

SEARCH_COUNT = Counter(
    'search_requests_total',
    'Total number of search requests'
)

CHAT_COUNT = Counter(
    'chat_requests_total',
    'Total number of chat requests'
)

EMBEDDING_COUNT = Counter(
    'embedding_requests_total',
    'Total number of embedding requests'
)

ERROR_COUNT = Counter(
    'error_requests_total',
    'Total number of error requests',
    ['method', 'endpoint', 'error_type']
)


class MetricsMiddleware:
    """Middleware to collect metrics for API endpoints"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)
        start_time = time.time()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Record metrics when response starts
                status_code = message["status"]
                method = request.method
                endpoint = request.url.path

                # Update metrics
                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code
                ).inc()

                duration = time.time() - start_time
                REQUEST_DURATION.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)

            await send(message)

        await self.app(scope, receive, send_wrapper)


def get_metrics():
    """Get the current metrics in Prometheus format"""
    return generate_latest(), CONTENT_TYPE_LATEST


def increment_search_counter():
    """Increment the search request counter"""
    SEARCH_COUNT.inc()


def increment_chat_counter():
    """Increment the chat request counter"""
    CHAT_COUNT.inc()


def increment_embedding_counter():
    """Increment the embedding request counter"""
    EMBEDDING_COUNT.inc()


def increment_error_counter(method: str, endpoint: str, error_type: str = "unknown"):
    """Increment the error counter"""
    ERROR_COUNT.labels(
        method=method,
        endpoint=endpoint,
        error_type=error_type
    ).inc()