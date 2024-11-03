from datetime import UTC, datetime

from .base import BaseModel


class Password(BaseModel):
    """A class to represent a password with its associated domain and expiration status.

    This class stores and validates password information including the domain it belongs to,
    the password itself, creation timestamp, and whether it expires.

    Attributes:
        domain (str): The domain/website the password belongs to
        password (str): The actual password string
        expires (bool): Whether the password has an expiration
    """

    table_name = "passwords"

    def __init__(self, domain: str, password: str, expires: bool = False) -> None:
        """Initialize a new Password instance.

        Args:
            domain (str): The domain/website the password belongs to
            password (str): The password string
            expires (bool, optional): Whether the password expires. Defaults to False.

        Raises:
            ValueError: If domain or password is empty or whitespace only
            TypeError: If domain or password is not a string, or expires is not a boolean
        """
        super().__init__()

        # Validate required fields are not empty or whitespace
        if not domain or not domain.strip() or not password or not password.strip():
            msg = "Domain and password are required and cannot be whitespace only"
            raise ValueError(msg)

        # Validate input types
        if not isinstance(domain, str) or not isinstance(password, str):
            msg = "Domain and password must be strings"
            raise TypeError(msg)
        if not isinstance(expires, bool):
            msg = "Expires must be a boolean"
            raise TypeError(msg)

        self.domain = domain.strip().lower()
        self.password = password
        self.created_at = datetime.now(tz=UTC).isoformat()
        self.expires = expires
