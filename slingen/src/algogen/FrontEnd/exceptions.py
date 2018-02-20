class BaseError(Exception):
    pass

class SizeError(BaseError):
    pass

class UndeclaredError(BaseError):
    pass

class RedeclarationError(BaseError):
    pass

