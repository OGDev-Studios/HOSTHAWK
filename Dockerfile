FROM python:3.11-slim

LABEL maintainer="team@hosthawk.io"
LABEL description="HostHawk - Enterprise Network Scanner"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y \
    gcc \
    libpcap-dev \
    tcpdump \
    nmap \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

RUN useradd -m -u 1000 hosthawk && \
    chown -R hosthawk:hosthawk /app

RUN mkdir -p /app/logs /app/output /app/reports && \
    chown -R hosthawk:hosthawk /app/logs /app/output /app/reports

EXPOSE 5000

VOLUME ["/app/logs", "/app/output", "/app/reports"]

USER hosthawk

CMD ["python", "-m", "web.app"]
