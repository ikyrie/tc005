from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# URL de conexão com o banco local rodando no Docker
DATABASE_URL = "postgresql://soat_user:soat_password@localhost:5432/soat_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # pylint: disable=invalid-name

# Dependência para injetar a sessão do banco no FastAPI


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
