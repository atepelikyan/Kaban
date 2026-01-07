# Kaban

Kaban is a web-based project management that uses a Kanban-style approach to help individuals and teams organize and track their tasks. It provides an interface with boards, sections and tasks allowing users to create and assign tasks and collaborate with team members. Trello helps streamline workflows and facilitates efficient project management.


## Prerequisites
Before you begin, ensure you have the following installed:

- Docker

- Docker Compose

## Quick Start
1. Build and Start the Application

Run the following command to build the image and start the container:

```sh
docker-compose up --build
```
The server will start at http://localhost:8000.

2. Access API Documentation

Once the server is running, you can explore the API interactively:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

3. Testing
```sh
docker-compose exec app uv run pytest
```
