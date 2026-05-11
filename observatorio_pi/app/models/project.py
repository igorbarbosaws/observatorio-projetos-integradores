from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descricao = Column(String)
    versao = Column(Integer, default=1)
    data_submissao = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ultima_atualizacao = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    aluno_id = Column(Integer, ForeignKey("users.id"))
