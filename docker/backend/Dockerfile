FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./

FROM base AS dev

RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM base AS prod

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DEBUG=false
RUN SECRET_KEY=collectstatic-build-key-not-used-at-runtime-0123456789 \
    ALLOWED_HOSTS=localhost \
    python manage.py collectstatic --noinput \
    && useradd --create-home --uid 1000 --shell /usr/sbin/nologin app \
    && mkdir -p /app/media \
    && chown -R app:app /app

USER app

EXPOSE 8000

CMD ["gunicorn", "-c", "gunicorn.conf.py", "backend.wsgi:application"]
