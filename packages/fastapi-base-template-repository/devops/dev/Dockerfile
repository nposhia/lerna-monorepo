ARG BASE_IMAGE=python
ARG BASE_IMAGE_TAG=3.12-slim

FROM $BASE_IMAGE:$BASE_IMAGE_TAG AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry==1.8.2

WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --only main

# Copy application code
COPY . .

# Final stage
FROM $BASE_IMAGE:$BASE_IMAGE_TAG

# Create a non-root user
ARG USERNAME=appuser
ARG SCRIPTS_PATH=/app/devops/scripts
RUN useradd -m ${USERNAME}

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /app .
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Make entrypoint script executable
RUN chmod +x "${SCRIPTS_PATH}/entrypoint.sh"

# Set correct permissions
RUN chown -R ${USERNAME}:${USERNAME} /app && \
    chown -R ${USERNAME}:${USERNAME} /usr/local/lib/python3.12/site-packages && \
    chown -R ${USERNAME}:${USERNAME} /usr/local/bin

# Switch to non-root user
USER ${USERNAME}

# Use the entrypoint script
ENTRYPOINT ["${SCRIPTS_PATH}/entrypoint.sh"]
