from password_manager.models.password import Password
from password_manager.views.password import FernetHasher


def main_template() -> None:
    action = input("Type 1 to save a new password, type 2 to view existing passwords: ")

    match action:
        case "1":
            domain = input("Enter the domain: ")
            password_input = input("Enter the password: ")

            password = Password(domain, password_input)
            key: str | bytes

            if len(password.get_all()) == 0:
                key, path = FernetHasher.create_key(archive=True)
                print(
                    "Your key has been created,",
                    "save it carefully because if you lose it you won't be able to recover your passwords",
                )
                print(f"Key: {key.decode('utf-8')}")
                if path:
                    print("Key saved in file, remember to remove the file after transferring it")
                    print(f"Path: {path}")
            else:
                key = input("Enter your encryption key, always use the same key: ")

            fernet = FernetHasher(key)
            password = Password(domain, fernet.encrypt(password_input).decode("utf-8"))
            password.save()

            print("Password saved")
        case "2":
            domain = input("Enter the domain: ")
            key = input("Enter your encryption key: ")

            fernet = FernetHasher(key)
            data = Password.get(domain=domain)
            if data is None:
                print("No password found for this domain")
                return

            pwd = fernet.decrypt(data["password"])
            print(f"Password for {domain}: {pwd}")

        case _:
            print("Invalid input")
