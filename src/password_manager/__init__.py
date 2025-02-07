from .main import password_manager
from .manage import manage as main_manage


def main() -> None:
    password_manager()


def manage() -> None:
    main_manage()
