# Use the latest Playwright Docker image with Python
FROM mcr.microsoft.com/playwright/python:v1.51.0-jammy

# Set the working directory inside the container
WORKDIR /app

# Copy the application files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and dependencies
RUN playwright install --with-deps

# Expose the port the application runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
