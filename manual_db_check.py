from getpass import getpass

from sqlalchemy import BigInteger, String, create_engine, text, select, ForeignKey
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, sessionmaker, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)


url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password=getpass("MySQL password: "),
    host="127.0.0.1",
    port=3307,
    database="rag_learning",
)

engine = create_engine(url)

SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


with engine.connect() as conn:
    result = conn.execute(
        text("SELECT id, title FROM documents WHERE user_id=:user_id"), {"user_id": 1}
    )

    for row in result:
        print(f"id:{row.id}\ttitle:{row.title}")

with engine.begin() as conn:
    result = conn.execute(
        text("insert into documents (user_id,title)  values(:user_id,:title)"),
        {"user_id": 1, "title": "SQLAlchemy Tutorial"},
    )

with Session(engine) as session:
    stmt = select(User).where(User.username == "Alice")

    result = session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is not None:
        print(user.id, user.username)
    else:
        print("User not found")

with Session(engine) as session:
    user = User(username="orm_crud_demo")
    session.add(user)
    session.commit()
    print(user.id)

with Session(engine) as session:
    stmt = select(User).where(User.username == "orm_crud_demo")
    result = session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is not None:
        user.username = "orm_update_demo"
        session.commit()
        print(user.username)
    else:
        print("user not found")

with Session(engine) as session:
    stmt = select(User).where(User.username == "orm_update_demo")
    result = session.execute(stmt)
    user = result.scalar_one_or_none()
    if user is not None:
        session.delete(user)
        session.commit()
    else:
        print("user not found")
