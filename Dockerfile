# Use official Python 3.11 slim image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements file first (for caching dependencies)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Expose port (if your app uses a web server, e.g., Flask, FastAPI)
# If not, you can skip this
EXPOSE 8080

# Command to run the app
CMD ["python", "main.py"]
