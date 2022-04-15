FROM python:3.10-slim as base

ARG APP_HOME=/app
ARG BUILD_ENV=production

ENV BUILD_ENV=${BUILD_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100\
  DJANGO_SETTINGS_MODULE=core.settings.test

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # psycopg2 dependencies
  libpq-dev \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

WORKDIR ${APP_HOME}

RUN addgroup --system web && adduser --system --ingroup web web

RUN chown web:web -R ${APP_HOME} \
  && mkdir -p /var/www/django/static /var/www/django/media \
  && chown web:web /var/www/django/static /var/www/django/media

COPY --chown=web:web ./Pipfile ./Pipfile.lock ${APP_HOME}/

RUN pipenv install --system --deploy --ignore-pipfile --clear

USER web


# App
FROM base AS app

EXPOSE 8000

COPY --chown=web:web . ${APP_HOME}
