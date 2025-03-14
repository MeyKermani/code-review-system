# Use the official Python image as the base
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the application files into the container
COPY . /app

# Install required Python packages from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your service runs on (optional)
EXPOSE 8001

# Run the service
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
