FROM python:3.11-slim

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all Python files
COPY *.py .

# Expose port
EXPOSE 8080

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]