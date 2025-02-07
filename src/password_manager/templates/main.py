from password_manager.models.database import engine
from password_manager.models.model import Password
from password_manager.views.hasher import FernetHasher
from password_manager.views.password import PasswordService


class UI:
    def __init__(self) -> None:
        self.password_service = PasswordService(engine)

    def add_password(self) -> None:
        domain = input("Enter the domain: ")

        if self.password_service.get(domain=domain) is not None:
            print("Password already exists for this domain")
            return

        password_input = input("Enter the password: ")

        key: str | bytes

        if len(self.password_service.get_all()) == 0:
            key, path = FernetHasher.create_key(archive=True)
            print("\n=====================================\n")
            print(
                "Your key has been created,",
                "save it carefully because if you lose it you won't be able to recover your passwords",
            )
            print(f"Key: {key.decode('utf-8')}")
            if path:
                print("Key saved in file, remember to remove the file after transferring it")
                print(f"Path: {path}")
            print("\n=====================================\n")
        else:
            key = input("Enter your encryption key, always use the same key: ")

        fernet = FernetHasher(key)
        password_input = fernet.encrypt(password_input).decode("utf-8")
        password = Password(domain=domain, password=password_input)
        self.password_service.create(password)

        print("Password saved")

    def view_password(self) -> None:
        domain = input("Enter the domain: ")
        key = input("Enter your encryption key: ")

        fernet = FernetHasher(key)
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

    def start(self) -> None:
        while True:
            print("""
            [1] -> Add password
            [2] -> View password
            [3] -> View domains
            [4] -> Remove password
            [5] -> Exit
            """)
            choice = input("Choose an option: ")

            match choice:
                case "1":
                    self.add_password()
                case "2":
                    self.view_password()
                case "3":
                    self.view_all_domains()
                case "4":
                    self.remove_password()
                case _:
                    break
