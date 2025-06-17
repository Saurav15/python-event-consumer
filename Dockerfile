FROM python:3.11-slim-bullseye

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

CMD ["python", "main.py"] 