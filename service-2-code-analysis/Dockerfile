# Use the official Python image as the base
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the application files into the container
COPY . /app

RUN apt-get update && apt-get install -y git && apt-get clean

# Install required Python packages from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your service runs on
EXPOSE 8002

# Use CMD or ENTRYPOINT to run the service
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]
