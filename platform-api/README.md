# SOAT Platform API

A FastAPI-based service for managing and analyzing file uploads (PDF, JPG, PNG).

## Prerequisites

- Python 3.10+
- PostgreSQL (or Docker to run one)

## Installation

### 1. Create a Virtual Environment
```bash
python3 -m venv venv
```

### 2. Activate the Environment

- **Bash / Zsh:**
  ```bash
  source venv/bin/activate
  ```
- **Fish:**
  ```fish
  source venv/bin/activate.fish
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

Before running, ensure your `PYTHONPATH` includes the `src` directory so the application can find its internal modules.

### Development Mode (with Auto-reload)

- **Bash / Zsh:**
  ```bash
  export PYTHONPATH=$PYTHONPATH:$(pwd)/src
  uvicorn src.main:app --reload
  ```
- **Fish:**
  ```fish
  set -x PYTHONPATH $PYTHONPATH (pwd)/src
  uvicorn src.main:app --reload
  ```

The API will be available at `http://127.0.0.1:8000`.

## Testing

### Interactive Documentation (Swagger UI)
Once the server is running, visit:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Automated Tests
Install testing tools:
```bash
pip install pytest httpx
```
Run the suite:
```bash
pytest
```

## Database Configuration
The application connects to PostgreSQL using the following default URL (found in `src/database.py`):
`postgresql://soat_user:soat_password@localhost:5432/soat_db`

Ensure you have a database running with these credentials or update the `DATABASE_URL` in `src/database.py`.
