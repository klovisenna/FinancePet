from sqlalchemy.orm import Session

from app.models import User

def get_user_by_login(db: Session, login: str) -> User | None:
    # .query Возвращает кортеж из одного элемента (User,)
    # Scalar возвращает первое значение первой строки элемента т.е. User
    return db.query(User).filter(User.login == login).scalar()

def create_user(db: Session, login: str) -> User:
    user = User(login=login)
    db.add(user)
    db.flush()
    return user