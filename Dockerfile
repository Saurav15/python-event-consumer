FROM python:3.12-slim

WORKDIR /app

# Create directory for health check file
RUN mkdir -p /tmp

# Copy requirements first for better caching
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

# Copy application code
COPY . .

# Set environment variables
ENV HEALTH_CHECK_INTERVAL=30
ENV HEALTH_CHECK_FILE=/tmp/health.json

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD cat ${HEALTH_CHECK_FILE} | grep -q '"status":"healthy"' || exit 1

# Run the application
CMD ["python", "main.py"]
