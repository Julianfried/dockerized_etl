FROM python:3.10-slim

ARG AIRFLOW_VERSION=2.7.3
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION=1.6.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    AIRFLOW_HOME=/opt/airflow

# Install essential packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

# Create airflow user
RUN useradd -ms /bin/bash -d ${AIRFLOW_HOME} airflow

WORKDIR ${AIRFLOW_HOME}

# Copy poetry configuration files
COPY pyproject.toml ./
# Generate a fresh poetry.lock file
RUN poetry lock
# Instalar las dependencias del proyecto con Poetry
RUN poetry install --no-root --no-interaction --no-ansi

    
   
# Optional: Install dev dependencies for linting if ARG DEV_MODE=true
ARG DEV_MODE=false
RUN if [ "$DEV_MODE" = "true" ]; then \
        pip install --no-cache-dir black==23.11.0 \
        isort==5.12.0 \
        flake8==6.1.0 \
        pylint==3.0.2 \
        mypy==1.7.0 \
        pre-commit==3.5.0; \
    fi

# Copy the entrypoint script
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create required directories
RUN mkdir -p ${AIRFLOW_HOME}/dags ${AIRFLOW_HOME}/logs ${AIRFLOW_HOME}/plugins ${AIRFLOW_HOME}/data

# Set ownership of files to airflow user
RUN chown -R airflow: ${AIRFLOW_HOME}

USER airflow
ENTRYPOINT ["/entrypoint.sh"]