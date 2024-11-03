from pathlib import Path


class BaseModel:
    """Base model class for handling database operations.

    Provides basic database functionality for storing and retrieving data in text files.
    Data is stored in pipe-delimited format in a 'db' directory relative to this file.
    The class implements a simple file-based database with basic CRUD operations.

    Attributes:
        BASE_DIR (Path): Base directory path resolved from current file location
        DB_DIR (Path): Directory path where database files are stored
        DELIMITER (str): Character used to separate fields in the data file
        table_name (str): Name of the database table, derived from class name

    Example:
        ```python
        class User(BaseModel):
            def __init__(self, name: str, email: str):
                super().__init__()
                self.name = name
                self.email = email

        user = User("John", "john@example.com")
        user.save()  # Saves to db/User.txt
        users = user.get_all()  # Returns all users
        ```
    """

    BASE_DIR = Path(__file__).resolve().parent.parent
    DB_DIR = BASE_DIR / "db"
    DELIMITER = "|"
    table_name: str | None = None

    def __init__(self) -> None:
        """Initialize a new BaseModel instance."""
        if not self.table_name:
            self.table_name = self.__class__.__name__

    @classmethod
    def _get_table_path(cls) -> Path:
        """Get the full path to the table file.

        Returns:
            Path: Full path to the table's data file

        Raises:
            ValueError: If table_name is not set
        """
        if not cls.table_name:
            msg = "table_name must be set"
            raise ValueError(msg)
        return cls.DB_DIR / f"{cls.table_name}.txt"

    def save(self) -> None:
        """Save the model instance data to a text file.

        Creates the database directory and table file if they don't exist.
        Writes instance attributes as delimiter-separated values with headers.

        Raises:
            OSError: If unable to create directory or write to file
            ValueError: If table_name is not set
        """
        table_path = self._get_table_path()
        self.DB_DIR.mkdir(exist_ok=True, parents=True)
        table_path.touch(exist_ok=True)

        with table_path.open("a") as file:
            if table_path.stat().st_size == 0:
                header = self.DELIMITER.join(self.__dict__.keys())
                file.write(f"{header}\n")

            row = self.DELIMITER.join(str(value) for value in self.__dict__.values())
            file.write(f"{row}\n")

    @classmethod
    def get_all(cls) -> list[dict[str, str]]:
        """Retrieve all records from the database.

        Returns:
            list[dict[str, str]: List of dictionaries where each dict represents a record.
            Empty list if table doesn't exist or is empty.

        Raises:
            ValueError: If table_name is not set
            IOError: If file cannot be read
        """
        table_path = cls._get_table_path()

        if not table_path.exists() or table_path.stat().st_size == 0:
            return []

        with table_path.open("r") as file:
            header = file.readline().strip().split(cls.DELIMITER)
            return [dict(zip(header, line.strip().split(cls.DELIMITER), strict=False)) for line in file]

    @classmethod
    def get(cls, **kwargs: str) -> dict[str, str] | None:
        """Retrieve first record matching the search criteria.

        Args:
            **kwargs: Field name and value pairs to match against records

        Returns:
            dict[str, str] | None: Matching record as dictionary, or None if not found

        Example:
            ```python
            user = User().get(email="john@example.com")
            ```

        Raises:
            ValueError: If table_name is not set
            IOError: If database file cannot be read
        """
        data = cls.get_all()

        if not data:
            return None

        return next(
            (row for row in data if all(str(row.get(key)) == str(value) for key, value in kwargs.items())),
            None,
        )
