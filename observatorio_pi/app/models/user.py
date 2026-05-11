from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    # ALUNO, PROFESSOR, COORDENADOR, EMPRESA, ADMIN
    tipo = Column(String, default="ALUNO", nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
