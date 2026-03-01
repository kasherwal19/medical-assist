# =========================
# Stage 1: Base image
# =========================
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies (common to all stages)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    ca-certificates \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*


# =========================
# Stage 2: Dependencies
# =========================
FROM base AS dependencies

# Copy requirements
COPY src/requirements.txt .

# Upgrade pip first (important for resolver stability)
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ---- Playwright system dependencies (Debian slim compatible) ----
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    fonts-liberation \
    fonts-unifont \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright browser ONLY (no --with-deps)
RUN playwright install chromium


# =========================
# Stage 3: Production
# =========================
FROM base AS production

# Install Playwright system dependencies
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    fonts-liberation \
    fonts-unifont \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages & Playwright browser from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin
COPY --from=dependencies /root/.cache/ms-playwright /root/.cache/ms-playwright

# Copy application code
COPY src/ /app/

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p /home/appuser/.cache && \
    cp -r /root/.cache/ms-playwright /home/appuser/.cache/ && \
    chown -R appuser:appuser /home/appuser/.cache

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health-check')" || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
