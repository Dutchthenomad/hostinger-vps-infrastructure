FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for SSE server
RUN pip install --no-cache-dir uvicorn starlette

# Copy application
COPY src/ ./src/

# Expose port
EXPOSE 8001

# Run server
CMD ["python", "-m", "src.server"]
