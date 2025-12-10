from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI


# Create a limiter instance
limiter = Limiter(key_func=get_remote_address)


def setup_rate_limiter(app: FastAPI):
    """Setup rate limiting for the FastAPI application"""
    # Add the rate limit exceeded handler
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Define common rate limits
SEARCH_RATE_LIMIT = "100/minute"  # 100 requests per minute for search
CHAT_RATE_LIMIT = "50/minute"     # 50 requests per minute for chat
INGESTION_RATE_LIMIT = "10/hour"  # 10 ingestion requests per hour
HEALTH_RATE_LIMIT = "1000/minute" # Higher limit for health checks