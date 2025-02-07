from password_manager.models.database import engine
from password_manager.models.model import Password
from password_manager.views.hasher import FernetHasher
from password_manager.views.password import PasswordService


class UI:
    def __init__(self) -> None:
        self.password_service = PasswordService(engine)

    def add_password(self, fernet: FernetHasher) -> None:
        domain = input("Enter the domain: ")

        if self.password_service.get(domain=domain) is not None:
            print("Password already exists for this domain")
            return

        password_input = input("Enter the password: ")

        password_input = fernet.encrypt(password_input).decode("utf-8")
        password = Password(domain=domain, password=password_input)
        self.password_service.create(password)

        print("Password saved")

    def view_password(self, fernet: FernetHasher) -> None:
        domain = input("Enter the domain: ")

        data = self.password_service.get(domain=domain)
        if data is None:
            print("No password found for this domain")
            return

        pwd = fernet.decrypt(data.password)
        print(f"Password for {domain}: {pwd}")

    def view_all_domains(self) -> None:
        passwords = self.password_service.get_all()
        for password in passwords:
            print(f"Domain: {password.domain}")

    def remove_password(self) -> None:
        domain = input("Enter the domain: ")
        password = self.password_service.get(domain=domain)

        if password is None:
            print("No password found for this domain")
            return

        self.password_service.delete(password.id)
        print("Password removed")

    def get_master_password(self) -> bytes:
        master_password = input("Enter your master password: ")
        return FernetHasher.make_key(master_password)

    def create_master_password(self) -> bytes | None:
        print("If you want to generate automatically, type 1 or 2 to exit.")
        master_password: str | bytes = input("Enter your master password: ")

        match master_password:
            case "1":
                master_password, path = FernetHasher.create_key(archive=True)
                print("\n=====================================\n")
                print(
                    "Your master password has been created,",
                    "save it carefully because if you lose it you won't be able to recover your passwords.",
                )
                print(f"Master password: {master_password.decode('utf-8')}")
                if path:
                    print("Master password saved in file, remember to remove the file after transferring it.")
                    print(f"Path: {path}")
                print("\n=====================================\n")
            case "2":
                print("Exiting...")
                return None
            case _:
                raw_master_password = master_password
                master_password = FernetHasher.make_key(master_password)
                print("\n=====================================\n")
                print(
                    "Your master password has been created,",
                    "save it carefully because if you lose it you won't be able to recover your passwords.",
                )
                print(f"Master password: {raw_master_password!s}")
                print("\n=====================================\n")

        return master_password

    def menu(self, fernet: FernetHasher) -> None:
        while True:
            print("""
            1. Add a password
            2. View a password
            3. View all domains
            4. Remove a password
            5. Exit
            """)
            choice = input("Enter your choice: ")

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
                    print("Exiting...")
                    break
                case _:
                    print("Invalid choice, please try again")

    def start(self) -> None:
        master_password: str | bytes | None = None

        if len(self.password_service.get_all()) == 0:
            print("""
            Welcome to the password manager, you don't have any passwords yet.
            Please create a master password to start using the password manager.
            """)

            master_password = self.create_master_password()

        else:
            master_password = self.get_master_password()

        if master_password is None:
            print("No master password provided. Exiting...")
            return

        fernet = FernetHasher(master_password)

        self.menu(fernet)
