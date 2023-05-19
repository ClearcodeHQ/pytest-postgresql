"""pytest-postgresql's exceptions."""


class ExecutableMissingException(FileNotFoundError):
    """Exception risen when PgConfig was not found."""


class PostgreSQLUnsupported(Exception):
    """Exception raised when unsupported postgresql would be detected."""
