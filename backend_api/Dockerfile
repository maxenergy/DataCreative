```dockerfile
# Start with a Python base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY ./app /app/app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Uvicorn
# The main:app refers to the 'app' instance in 'main.py'
# --host 0.0.0.0 makes it accessible from outside the container
# --reload is useful for development, can be removed for production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
