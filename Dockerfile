FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home appuser
COPY --chown=appuser:appuser . .
RUN mkdir -p /app/staticfiles /app/media && chown appuser:appuser /app/staticfiles /app/media
USER appuser
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "2", "--access-logfile", "-", "--error-logfile", "-"]
