from fastapi import HTTPException, status


class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvalidTokenError(AppException):
    """Raised when JWT token is invalid."""
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class InvalidCredentialsError(AppException):
    """Raised when login credentials are invalid."""
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class UserAlreadyExistsError(AppException):
    """Raised when user already exists."""
    def __init__(self, message: str = "User with this email already exists"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class UserNotFoundError(AppException):
    """Raised when user is not found."""
    def __init__(self, message: str = "User not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class InvalidOTPError(AppException):
    """Raised when OTP is invalid or expired."""
    def __init__(self, message: str = "Invalid or expired OTP"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class UnauthorizedError(AppException):
    """Raised when user is not authorized."""
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class ValidationError(AppException):
    """Raised when validation fails."""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)
