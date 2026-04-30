class CanteenAppError(Exception):
    """Base exception class for the Canteen Application."""
    pass

class CanteenNotFoundError(CanteenAppError):
    """Raised when a requested canteen is not found in the database."""
    def __init__(self, canteen_id: int):
        self.message = f"Canteen with ID {canteen_id} was not found."
        super().__init__(self.message)

class InvalidDataError(CanteenAppError):
    """Raised when input data fails validation checks."""
    pass

class AIServiceError(CanteenAppError):
    """Raised when the Gemini API integration fails."""
    pass
