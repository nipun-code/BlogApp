# BloggingApp
A modern blogging application built with FastAPI, PostgreSQL, and JWT authentication.

## Features

-  Secure JWT Authentication
-  User Profiles
-  Blog Post Management
-  Search Functionality
-  Rich Text Support
-  RESTful API Design
-  Password Hashing with BCrypt
-  PostgreSQL Database
-  Comprehensive Test Suite

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt
- **Testing**: pytest with pytest-cov
- **Documentation**: Swagger/OpenAPI
- **Code Quality**: mypy, ruff, pre-commit hooks
- **API Client**: HTTPx

## Prerequisites

- Python 3.11+
- PostgreSQL
- Virtual Environment

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/nipun-code/BloggingApp.git
   cd BloggingApp
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (create .env file):
   ```env
   DATABASE_URL= your-database-url
   SECRET_KEY=your-secret-key
   APP_NAME=BloggingApp
   APP_VERSION=1.0.0
   DEBUG=True
   ```

## Running the Application

1. Start the development server:
   ```bash
   uvicorn main:app --reload
   ```

2. Visit the API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Project Structure

```
BloggingApp/
    auth/              # Authentication utilities
    config/            # Configuration settings
    database/          # Database models and connection
    routers/           # API route handlers
    schemas/           # Pydantic models/schemas
    services/          # Business logic
    tests/             # Test suite
    main.py            # Application entry point
    requirements.txt   # Project dependencies
```

## API Endpoints

- **Authentication**
  - POST `/auth/register`: Register new user
  - POST `/auth/login`: Login user
  - POST `/auth/refresh`: Refresh access token
  - POST `/auth/logout`: Logout user

- **Profile**
  - GET `/profile/me`: Get current user profile
  - PUT `/profile/me`: Update user profile

- **Blog**
  - POST `/blog/posts`: Create new post
  - GET `/blogs/search`: List all blog posts
  - GET `/blogs/category/{category}`: Search blog by category
  - GET `/blog/posts/{id}`: Get specific post by id
  - PUT `/blog/posts/{id}`: Update post
  - DELETE `/blog/posts/{id}`: Delete post

## Testing

Run the test suite:
```bash
python -m pytest --cov=. tests/
```

Generate coverage report:
```bash
python -m pytest --cov=. --cov-report=xml tests/
```

## Code Quality

Run code quality checks:
```bash
# Type checking
mypy .

# Style checking
ruff check .

# Run pre-commit hooks
pre-commit run --all-files
```

## Author
Nipun Singhal