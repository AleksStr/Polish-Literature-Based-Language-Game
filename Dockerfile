# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all Python files
COPY *.py .

# Copy extracts directory
COPY extracts/ ./extracts/

# Create non-root user for security
RUN useradd -m -u 1000 appuser
USER appuser

# Expose port (Cloud Run sets PORT env variable)
EXPOSE 8080

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]