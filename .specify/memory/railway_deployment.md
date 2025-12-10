# Railway Deployment Configuration

## Overview
This document outlines the Railway deployment setup for the FastAPI book search application with Qdrant, Gemini, and OpenAI Agents integration.

## Railway Project Structure
- **Main Service**: FastAPI application container
- **Environment Variables**: Secure storage for API keys and configuration
- **Domains**: Custom domain setup for production access

## Dockerfile for Railway Deployment
```Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway provides PORT environment variable)
EXPOSE $PORT

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
```

## Requirements.txt Dependencies
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
qdrant-client==1.8.0
google-generativeai==0.4.1
openai==1.3.5
pydantic==2.5.0
python-multipart==0.0.6
python-dotenv==1.0.0
pydantic-settings==2.1.0
```

## Environment Variables Required
- `GEMINI_API_KEY`: Google Gemini API key for embedding generation
- `OPENAI_API_KEY`: OpenAI API key for Agents SDK
- `QDRANT_HOST`: Qdrant database host (URL or IP)
- `QDRANT_API_KEY`: Qdrant database API key (if authentication enabled)
- `QDRANT_PORT`: Qdrant database port (default: 6333)
- `ENVIRONMENT`: Environment identifier (development, staging, production)

## Railway Configuration (railway.toml)
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[variables]
PORT = 8000
ENVIRONMENT = "production"
```

## Railway Deployment Steps
1. Connect Railway to your GitHub repository
2. Set up automatic deployments from the main branch
3. Configure the environment variables in Railway dashboard
4. Deploy the application using Railway's deployment interface

## Qdrant Integration Options
### Option 1: External Qdrant Service
- Use a cloud Qdrant service or self-hosted instance
- Configure QDRANT_HOST and QDRANT_API_KEY environment variables

### Option 2: Railway Container (if supported)
- Deploy Qdrant as a separate service on Railway
- Use internal service communication between containers

## Health Check Configuration
- **Health Check URL**: `/health`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Threshold**: 3 consecutive failures

## Scaling Configuration
- **Min Instances**: 1 (for availability)
- **Max Instances**: 3 (based on expected load)
- **CPU/RAM Allocation**: Standard-1GB or higher based on performance needs

## Monitoring and Logging
- Enable Railway's built-in logging
- Set up custom log drains if needed for external monitoring
- Monitor application performance and resource usage

## Security Considerations
- Never commit API keys to the repository
- Use Railway's secure environment variable storage
- Implement rate limiting to prevent API abuse
- Use HTTPS for all production traffic

## Backup Strategy
- Regular backup of Qdrant vector database
- Version control for application code
- Environment configuration backup