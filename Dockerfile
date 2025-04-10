# Use the official Playwright base image with Python
FROM mcr.microsoft.com/playwright/python:v1.41.2

# Set working directory
WORKDIR /app

# Copy everything
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose your app port (Render uses this to detect the service)
EXPOSE 5000

# Start your Flask app
CMD ["python", "app.py"]
