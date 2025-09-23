FROM mcr.microsoft.com/playwright/python:v1.54.0-noble

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

# Copy application code
COPY . .

USER pwuser

# Expose port
EXPOSE 8822

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8822

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8822/health || exit 1

# Run the application
CMD ["python", "main.py"]
