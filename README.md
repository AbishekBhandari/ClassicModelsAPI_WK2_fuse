# postgres-docker

ClassicModels API built with FastAPI and PostgreSQL.

## Overview

This project provides a REST API for the ClassicModels database with routes for:
- `customers`
- `products`
- `productlines`
- `offices`
- `employees`
- `orders`
- `orderdetails`
- `payments`

It also includes an aggregated endpoint:
- `GET /overall_counts`

## Requirements

- Python 3.11+ or 3.14
- PostgreSQL
- Docker / Docker Compose (recommended)
- `pip` for Python dependencies

## Setup

1. Create and activate the virtual environment:
   ```bash
   python -m venv venc
   .\venc\Scripts\activate

2. Install dependencies
    ```bash
    pip install -r requirements.txt

3. Create a .env file in the project root with database settings:
    POSTGRES_USER=admin
    POSTGRES_PASSWORD=password
    POSTGRES_DB=mydatabase
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432

 4.If you are using docker-compose.yml
    ```bash
    docker compose up --build

 5.Run Locally
    ```bash
    uvicorn main:app --reload

 6.Then open:
    http://localhost:8000
    http://localhost:8000/docs for Swagger UI


For all the tables we have REST API with the 4 layer architecture (database.py, schemas.py, crud.py, router.py)
