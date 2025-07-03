ARG BASE_IMAGE=python
ARG BASE_IMAGE_TAG=3.12-slim

FROM $BASE_IMAGE:$BASE_IMAGE_TAG

# Install system packages needed for development
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    make \
    procps \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install and configure poetry
RUN pip install --no-cache-dir poetry==1.8.2 && \
    poetry config virtualenvs.create false && \
    poetry config virtualenvs.in-project false

WORKDIR /app
COPY pyproject.toml poetry.lock ./
COPY devops/scripts/entrypoint.sh /app/devops/scripts/entrypoint.sh

# Install dependencies and set permissions in a single layer
RUN poetry install --with dev \
    && chmod +x /app/devops/scripts/entrypoint.sh

ENTRYPOINT ["/app/devops/scripts/entrypoint.sh"]
