# Build stage
FROM python:3.9-slim AS builder

WORKDIR /app

# Install build dependencies
COPY requirements.docker.txt .

RUN pip install --user -r requirements.docker.txt

# Copy application code
COPY . .

# Final stage
FROM python:3.9-slim

WORKDIR /app

# Install only runtime dependencies
COPY --from=builder /root/.local /root/.local

COPY . .

# Set the path to include user-installed packages
ENV PATH=/root/.local/bin:$PATH

CMD ["python", "./main.py"]
