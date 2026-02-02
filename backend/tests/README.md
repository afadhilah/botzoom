# Unit Tests

This directory contains comprehensive unit tests for the backend application.

## Test Structure

```
tests/
├── conftest.py                      # Shared fixtures and test configuration
├── test_core_security.py            # Password hashing, OTP generation
├── test_core_jwt.py                 # JWT token creation and verification
├── test_auth_service.py             # Auth business logic (signup, login, OTP)
├── test_user_service.py             # User CRUD operations
├── test_whisper_transcription.py    # Whisper transcription (mocked)
└── test_workers.py                  # Background worker tests
```

## Running Tests

### Install Test Dependencies

```bash
pip install pytest pytest-mock pytest-cov
```

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_auth_service.py -v
pytest tests/test_transcript_api.py -v -W default::DeprecationWarning
```

### Run Tests by Marker

```bash
# Run only auth tests
pytest -m auth

# Run only unit tests
pytest -m unit
```

### Run with Coverage

```bash
pytest tests/ --cov=core --cov=domains --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`.

## Test Categories

- **Core Tests**: Security utilities, JWT handling
- **Auth Tests**: Signup, login, OTP verification, token refresh
- **User Tests**: User CRUD, validation, OTP management
- **Transcript Tests**: Whisper transcription (mocked)
- **Worker Tests**: Background job processing

## Mocking Strategy

All tests use mocking to avoid:
- ❌ Real database connections
- ❌ External API calls
- ❌ File system operations
- ❌ Network requests

Tests use:
- ✅ `unittest.mock.Mock` for simple mocks
- ✅ `unittest.mock.MagicMock` for complex objects
- ✅ `@patch` decorator for dependency injection
- ✅ Pytest fixtures for reusable test data

## Writing New Tests

1. Create test file: `test_<module_name>.py`
2. Import module under test
3. Create test class: `class Test<Feature>:`
4. Write test methods: `def test_<behavior>():`
5. Use descriptive names explaining what is tested
6. Mock external dependencies
7. Follow AAA pattern: Arrange, Act, Assert

Example:
```python
def test_create_user_hashes_password(self, mock_db_session):
    # Arrange
    user_data = UserCreate(email="test@example.com", password="plain")
    
    # Act
    result = UserService.create(mock_db_session, user_data)
    
    # Assert
    assert result.hashed_password != "plain"
```

## Test Coverage Goals

- Core modules: > 90%
- Domain services: > 85%
- API routes: > 80%
- Workers: > 75%

## Continuous Integration

Tests should be run on every commit:
```bash
pytest tests/ --cov=core --cov=domains --cov-report=term-missing
```

All tests must pass before merging to main branch.
