# Use a slim Python 3.12 image
FROM python:3.12-slim

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv (no-dev for production)
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source
COPY agents agents
COPY app app

# Expose Cloud Run standard port
EXPOSE 8080

# Environment variables for production
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8080
ENV GOOGLE_GENAI_USE_VERTEXAI=true

# Start the application using uvicorn with uvloop
CMD ["uv", "run", "python", "-m", "app.main"]
