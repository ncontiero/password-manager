import base64
import hashlib
import secrets
import string
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken


class FernetHasher:
    """
    A class for generating cryptographically secure random strings and
    handling encryption/decryption using the Fernet algorithm.

    This class provides functionality to:
    - Generate random strings using cryptographically secure methods
    - Create and archive encryption keys
    - Encrypt and decrypt data using Fernet symmetric encryption
    - Secure key storage and management

    Attributes:
        RANDOM_STRING_CHARS (str): Characters used for random string generation (ASCII letters + digits)
        BASE_DIR (Path): Base directory path of the project
        KEY_DIR (Path): Directory for storing key files
        DEFAULT_KEY_LENGTH (int): Default length for generated random strings
        KEY_FILE_PREFIX (str): Prefix used for key filenames
        KEY_FILE_EXTENSION (str): File extension for key files
        fernet (Fernet): Fernet instance for encryption/decryption
    """

    RANDOM_STRING_CHARS = string.ascii_letters + string.digits
    BASE_DIR = Path(__file__).resolve().parent.parent
    KEY_DIR = BASE_DIR / "keys"
    DEFAULT_KEY_LENGTH = 32
    KEY_FILE_PREFIX = "key_"
    KEY_FILE_EXTENSION = ".key"

    def __init__(self, key: bytes | str) -> None:
        """
        Initialize FernetHasher with an encryption key.

        Args:
            key (bytes | str): Encryption key for Fernet algorithm.
                            If string is provided, it will be encoded to bytes.

        Raises:
            ValueError: If the key is not valid for Fernet encryption
        """
        if isinstance(key, str):
            key = key.encode("utf-8")

        # Ensure key directory exists
        self.KEY_DIR.mkdir(parents=True, exist_ok=True)
        try:
            self.fernet = Fernet(key)
        except Exception as e:
            msg = f"Invalid key: {e!s}"
            raise ValueError(msg) from e

    @classmethod
    def _get_random_string(cls, length: int = DEFAULT_KEY_LENGTH) -> str:
        """
        Generate a cryptographically secure random string of specified length.

        Args:
            length (int): The length of the random string to generate.
                        Defaults to DEFAULT_KEY_LENGTH.

        Returns:
            str: A random string containing ASCII letters and digits.

        Raises:
            ValueError: If length is less than 1.
        """
        if length < 1:
            msg = "Length must be positive"
            raise ValueError(msg)

        return "".join(secrets.choice(cls.RANDOM_STRING_CHARS) for _ in range(length))

    @classmethod
    def create_key(cls, archive: bool = False) -> tuple[bytes, str | None]:
        """
        Create a new Fernet encryption key.

        Args:
            archive (bool): Whether to save the key to a file. Defaults to False.

        Returns:
            tuple[bytes, str | None]: A tuple containing:
                - The generated key as bytes
                - The file path where the key was saved (if archive=True), None otherwise

        Raises:
            IOError: If key archiving fails
        """
        value = cls._get_random_string()
        hasher = hashlib.sha256(value.encode("utf-8")).digest()
        key = base64.b64encode(hasher)

        if archive:
            try:
                return key, cls.archive_key(key)
            except OSError as e:
                msg = f"Failed to archive key: {e!s}"
                raise OSError(msg) from e
        return key, None

    @classmethod
    def archive_key(cls, key: bytes) -> str:
        """
        Save an encryption key to a file with a unique name.

        Args:
            key (bytes): The key to archive

        Returns:
            str: Path to the saved key file

        Raises:
            IOError: If unable to write to the key file
            TypeError: If key is not bytes
        """
        if not isinstance(key, bytes):
            msg = "Key must be bytes"
            raise TypeError(msg)

        # Ensure key directory exists
        cls.KEY_DIR.mkdir(parents=True, exist_ok=True)
        file = f"{cls.KEY_FILE_PREFIX}{cls._get_random_string(5)}{cls.KEY_FILE_EXTENSION}"
        file_path = cls.KEY_DIR / file

        try:
            file_path.write_bytes(key)
            return str(file_path)
        except Exception as e:
            msg = f"Failed to write key file: {e!s}"
            raise OSError(msg) from e

    def encrypt(self, value: str | bytes) -> bytes:
        """
        Encrypt data using the Fernet algorithm.

        Args:
            value (str | bytes): Data to encrypt

        Returns:
            bytes: Encrypted data

        Raises:
            TypeError: If value is neither string nor bytes
        """
        if isinstance(value, str):
            value = value.encode("utf-8")
        elif not isinstance(value, bytes):
            msg = "Value must be string or bytes"
            raise TypeError(msg)

        return self.fernet.encrypt(value)

    def decrypt(self, value: str | bytes) -> str:
        """
        Decrypt Fernet-encrypted data.

        Args:
            value (str | bytes): Encrypted data to decrypt

        Returns:
            str: Decrypted data as string

        Raises:
            ValueError: If the token is invalid or decryption fails
            TypeError: If value is neither string nor bytes
        """
        if isinstance(value, str):
            value = value.encode("utf-8")
        elif not isinstance(value, bytes):
            msg = "Value must be string or bytes"
            raise TypeError(msg)

        try:
            return self.fernet.decrypt(value).decode()
        except InvalidToken as e:
            msg = "Invalid token or corrupted data"
            raise ValueError(msg) from e
        except Exception as e:
            msg = f"Decryption failed: {e!s}"
            raise ValueError(msg) from e
