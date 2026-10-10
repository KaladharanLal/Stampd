from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session

DB_PATH = Path(__file__).resolve().parent.parent / "stampd.db"
SQLITE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLITE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

def init_db():
    SQLModel.metadata.create_all(engine)
    with engine.connect() as conn:
        try:
            from sqlalchemy import text
            conn.execute(text("ALTER TABLE destination ADD COLUMN image_url TEXT"))
            conn.commit()
        except Exception:
            pass

def get_session():
    with Session(engine) as session:
        yield session
