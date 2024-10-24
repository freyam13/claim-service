# Claim Service

This is a FastAPI-based service that provides claim handling functionality. The service is containerized with 
Docker and uses PostgreSQL and Redis for persistence and caching. Below are the steps to get started, build, run, 
test, and view the documentation.

## System Requirements

To build and run this application, you will need the following installed:

- [Docker](https://docs.docker.com/get-docker/): to containerize and run the application
- [Docker Compose](https://docs.docker.com/compose/install/): to orchestrate the multi-container environment
- Python 3.11: if you want to run the app locally without Docker (optional)

## Getting Started

To build and run the service:
```bash
$ docker-compose up --build
```
This command will:
- build the application Docker image
- start the service along with the database and Redis container

To Access the application endpoints:
- API Endpoint: http://localhost:8000
- Interactive API Docs: http://localhost:8000/docs (Swagger UI)
- Alternative Docs: http://localhost:8000/redoc (ReDoc)

## Running Tests
To run unit tests (pytest) with the appropriate dependencies in a virtual environment, do the following:

To run all tests:
```bash
$ pipenv run pytest
```

To run a specific module:
```bash
$ pipenv run pytest tests/test_main.py
```

## Managing the Database
The database service is provided by PostgreSQL and it’s initialized with the script init-db.sql. You can find this 
file in the project root. Any changes you make here will be applied when the container is started.

If you need to inspect or interact with the database, you can use the following command to log into the PostgreSQL 
container:
```bash
$ docker exec -it claim-service-db-1 psql -U claim_user -d claim
```
