# Code Review System

## Overview
This project consists of two services built using FastAPI:
1. **Service 1 LLM Service**: Handles connection to gpt4 and deepseek you can choose any of them from the .env file in service 1.
Service 1 is responsible for handling requests to the LLM model and returning the generated text. And also this 
service provides an endpoint to analyze the code using the LLM models.
2. **Service 2 Code Analysis**: Manages downloading asynchronously git repos and analyzing the functions via calling service1 API.

Both services are containerized using Docker and orchestrated using Docker Compose for easy deployment and scalability.

---

## Technologies Used

### Backend
- **FastAPI**: A modern Python web framework for building APIs.
  - Chosen for its speed, simplicity, and built-in support for OpenAPI documentation.
- **Python**: The core programming language used for its rich ecosystem and compatibility with FastAPI.

### Containerization
- **Docker**: Ensures consistent environments for running services.
- **Docker Compose**: Simplifies orchestration of multiple services, networking, and volume management.

---

## Design Choices
1. **Microservice Architecture**:
   - Each service is independent and focuses on specific functionality. This makes scaling and maintenance easier.
2. **Docker**:
   - Simplifies deployment and ensures consistent environments across development, testing, and production.
3. **RESTful API Design**:
   - Enables clear, predictable endpoints for clients to interact with the services.
4. **Volumes**:
   - Persistent storage is implemented for Service 2 to ensure files downloaded during runtime are saved permanently.
5. **Networking**:
   - Services communicate via Docker Compose using service names.

---

## How to Run the Project

### Prerequisites
Ensure you have the following installed:
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Steps to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/MeyKermani/code-review-system.git
   cd code-review-system
   docker-compose up --build

## API Endpoints

### Service 1 Endpoint

#### **POST `/analyze`**
**Description**: Gives suggestion for function improvement.

**Request**:
```bash
curl --location 'http://127.0.0.1:8001/analyze' \
--header 'Content-Type: application/json' \
--data ' {"function_code": "def add(a,b): return a+b"}'
```
**Response**:
```json
{
    "suggestions": [
        "Add type hints for parameters",
        "Add type hints for the return value",
        "Use docstring to describe the function",
        "Use descriptive parameter names",
        "Check for invalid inputs",
        "Handle non-numeric inputs gracefully",
        "Add unit tests for the function",
        "Use consistent formatting",
        "Make function name more descriptive if needed"
    ]
}
```

### Service 2 Endpoints

#### **POST `/analyze/start`**
**Description**: Gets a repo URL and asynchronously downloads the repo.

**Request**:
```bash
curl --location 'http://127.0.0.1:8002/analyze/start' \
--header 'Content-Type: application/json' \
--data '{
  "repo_url": "https://github.com/KeithGalli/python-api-example"
}'
```
**Response**:
```
{
 "job_id": "4776c78d-5098-4f51-a739-bacb0d7f30ae"
}
```

#### **POST `/analyze/function`**
**Description**: From the downloaded repo, analyzes the functions and sends them to Service 1 for suggestions.

**Request**:
```bash
curl --location 'http://127.0.0.1:8002/analyze/function' \
--header 'Content-Type: application/json' \
--data '{
  "job_id":"4776c78d-5098-4f51-a739-bacb0d7f30ae",
  "function_name": "book_review.add_record"
}'
```
**Response**:
```json
{
    "suggestions": [
        "Check type of 'data' to ensure it's a dictionary",
        "Use 'get' method to access 'Book' and 'Rating'",
        "Validate 'Rating' value is an integer or float",
        "Return an error message instead of False for missing keys",
        "Use logging to track missing 'Book' or 'Rating'",
        "Document the function to clarify input expectations",
        "Consider using exceptions for handling missing keys",
        "Initialize default values for missing keys using 'setdefault'",
        "Check if 'Book' value is a non-empty string"
    ]
}
```
