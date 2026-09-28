"""Business errors. The logic layer raises these; the presentation layer maps
them to HTTP status codes (see presentation/error_handlers.py), so nothing in
here knows about HTTP."""


class DomainError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    def __init__(self, entity: str, entity_id: object):
        super().__init__(f"{entity} {entity_id} not found")


class ConflictError(DomainError):
    pass


class ConsentRequiredError(DomainError):
    pass
