# Minimal production-ready image for nhs-number-api
# - runs as non-root user
# - keeps runtime-writable paths under /tmp and /var/tmp so the container can run with a read-only root filesystem
# - uses a slim Python base

FROM python:3.11-slim

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    TMPDIR=/tmp

# Create non-root user and application dir
RUN groupadd --system app \
    && useradd --system --gid app --create-home --home-dir /nonexistent --shell /usr/sbin/nologin app \
    && mkdir -p /app /var/tmp /tmp /var/log

WORKDIR /app

# Install build deps briefly (if any packages need compilation). Keep minimal and clean apt lists
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy project files early to enable layer caching for dependencies
COPY pyproject.toml setuptools.cfg* ./
COPY src ./src
COPY README.md ./

# Install the package and its dependencies into the system Python (no virtualenv)
# This will read pyproject.toml and install required dependencies (fastapi, uvicorn, nhs-number)
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir .

# Make sure runtime-writable paths are owned by the non-root user
RUN chown -R app:app /app /var/tmp /tmp /var/log

# Drop privileges for runtime
USER app

# Expose port
EXPOSE 8000

# Run using uvicorn directly (do NOT use the provided CLI which enables reload)
# Keep the root filesystem read-only at runtime; Kubernetes should set `securityContext.readOnlyRootFilesystem: true`
CMD ["uvicorn", "nhs_number_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
