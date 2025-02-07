from password_manager.models.database import engine
from password_manager.models.model import Password
from password_manager.views.hasher import FernetHasher
from password_manager.views.password import PasswordService

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

SEPARATOR = f"\n{BLUE}====================================={RESET}\n"
MENU_OPTIONS = f"""
{BLUE}1.{RESET} Add a password
{BLUE}2.{RESET} View a password
{BLUE}3.{RESET} View all domains
{BLUE}4.{RESET} Remove a password
{BLUE}5.{RESET} Exit
"""


class UI:
    def __init__(self) -> None:
        self.password_service = PasswordService(engine)

    def add_password(self, fernet: FernetHasher) -> None:
        domain = input(f"{BLUE}Enter the domain:{RESET} ").strip()
        if not domain:
            print(f"{RED}Domain cannot be empty{RESET}")
            return

        if self.password_service.get(domain=domain) is not None:
            print(f"{RED}Password already exists for this domain{RESET}")
            return

        password_input = input(f"{BLUE}Enter the password:{RESET} ").strip()
        if not password_input:
            print(f"{RED}Password cannot be empty{RESET}")
            return

        password_input = fernet.encrypt(password_input).decode("utf-8")
        password = Password(domain=domain, password=password_input)
        self.password_service.create(password)

        print(f"{GREEN}Password saved successfully{RESET}")

    def view_password(self, fernet: FernetHasher) -> None:
        domain = input(f"{BLUE}Enter the domain:{RESET} ").strip()
        if not domain:
            print(f"{RED}Domain cannot be empty{RESET}")
            return

        data = self.password_service.get(domain=domain)
        if data is None:
            print(f"{RED}No password found for this domain{RESET}")
            return

        try:
            pwd = fernet.decrypt(data.password)
            print(f"{GREEN}Password for {domain}: {YELLOW}{pwd}{RESET}")
        except Exception as e:  # noqa: BLE001
            print(f"{RED}Error decrypting password: {e!s}{RESET}")

    def view_all_domains(self) -> None:
        passwords = self.password_service.get_all()
        if not passwords:
            print(f"{YELLOW}No passwords stored yet{RESET}")
            return

        print(f"\n{BLUE}Stored domains:{RESET}")
        for password in passwords:
            print(f"{YELLOW}- {password.domain}{RESET}")

    def remove_password(self) -> None:
        domain = input(f"{BLUE}Enter the domain:{RESET} ").strip()
        if not domain:
            print(f"{RED}Domain cannot be empty{RESET}")
            return

        password = self.password_service.get(domain=domain)

        if password is None:
            print(f"{RED}No password found for this domain{RESET}")
            return

        confirm = input(f"{YELLOW}Are you sure you want to delete password for {domain}? (y/n):{RESET} ")
        if confirm.lower() != "y":
            print(f"{BLUE}Deletion cancelled{RESET}")
            return

        self.password_service.delete(password.id)
        print(f"{GREEN}Password removed successfully{RESET}")

    def get_master_password(self) -> bytes:
        while True:
            if master_password := input(f"{BLUE}Enter your master password:{RESET} ").strip():
                return FernetHasher.make_key(master_password)
            print(f"{RED}Master password cannot be empty{RESET}")

    def create_master_password(self) -> bytes | None:
        print(f"{YELLOW}If you want to generate automatically, type 1 or 2 to exit.{RESET}")
        master_password: str | bytes = input(f"{BLUE}Enter your master password:{RESET} ").strip()

        match master_password:
            case "1":
                master_password, path = FernetHasher.create_key(archive=True)
                print(SEPARATOR)
                print(
                    f"{YELLOW}Your master password has been created,",
                    "save it carefully because if you lose it you won't be able to recover your passwords.{RESET}",
                )
                print(f"{GREEN}Master password: {master_password.decode('utf-8')}{RESET}")
                if path:
                    print(
                        f"{YELLOW}Master password saved in file, remember to remove the file after transferring it.{RESET}",
                    )
                    print(f"{BLUE}Path: {path}{RESET}")
                print(SEPARATOR)
            case "2":
                print(f"{BLUE}Exiting...{RESET}")
                return None
            case _:
                if not master_password:
                    print(f"{RED}Master password cannot be empty{RESET}")
                    return None

                raw_master_password = master_password
                master_password = FernetHasher.make_key(master_password)
                print(SEPARATOR)
                print(
                    f"{YELLOW}Your master password has been created,",
                    "save it carefully because if you lose it you won't be able to recover your passwords.{RESET}",
                )
                print(f"{GREEN}Master password: {raw_master_password!s}{RESET}")
                print(SEPARATOR)

        return master_password

    def menu(self, fernet: FernetHasher) -> None:
        while True:
            print(MENU_OPTIONS)
            choice = input(f"{BLUE}Enter your choice:{RESET} ").strip()

            match choice:
                case "1":
                    self.add_password(fernet)
                case "2":
                    self.view_password(fernet)
                case "3":
                    self.view_all_domains()
                case "4":
                    self.remove_password()
                case "5":
                    print(f"{BLUE}Exiting...{RESET}")
                    break
                case _:
                    print(f"{RED}Invalid choice, please try again{RESET}")

    def start(self) -> None:
        master_password: bytes | None = None

        if len(self.password_service.get_all()) == 0:
            print(f"""
            {YELLOW}Welcome to the password manager, you don't have any passwords yet.
            Please create a master password to start using the password manager.{RESET}
            """)

            master_password = self.create_master_password()

        else:
            master_password = self.get_master_password()

        if master_password is None:
            print(f"{RED}No master password provided. Exiting...{RESET}")
            return

        fernet = FernetHasher(master_password)

        self.menu(fernet)
