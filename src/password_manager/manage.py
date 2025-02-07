from .models.database import create_db_and_tables


def manage() -> None:
    create_db_and_tables()
