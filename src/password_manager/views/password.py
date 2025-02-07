from collections.abc import Sequence

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from password_manager.models.model import Password


class PasswordService:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def create(self, password: Password) -> Password:
        with Session(self.engine) as session:
            session.add(password)
            session.commit()
            return password

    def get(self, domain: str) -> Password | None:
        with Session(self.engine) as session:
            return session.exec(
                select(Password).where(Password.domain == domain),
            ).first()

    def get_all(self) -> Sequence[Password]:
        with Session(self.engine) as session:
            return session.exec(select(Password)).all()

    def delete(self, password_id: int) -> None:
        with Session(self.engine) as session:
            password = session.exec(
                select(Password).where(Password.id == password_id),
            ).one()
            session.delete(password)
            session.commit()
