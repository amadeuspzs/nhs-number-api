FROM python:3.11-slim

# Create non-root user and application dir
RUN useradd app && mkdir -p /app

WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY src ./src

# This will read pyproject.toml and install required dependencies (fastapi, uvicorn, nhs-number)
RUN pip install --no-cache-dir .

# Make sure runtime-writable paths are owned by the non-root user
RUN chown -R app:app /app /var/tmp /tmp /var/log

# Drop privileges for runtime
USER app

# Run using uvicorn directly (do NOT use the provided CLI which enables reload)
CMD ["uvicorn", "nhs_number_api.main:app", "--host", "0.0.0.0", "--port", "8888"]
