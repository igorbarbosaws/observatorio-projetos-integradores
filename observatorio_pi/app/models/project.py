from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descricao = Column(Text)
    turma = Column(String, default="")          # ex: "ADS-2A", "ADS-2B"
    semestre = Column(String, default="")       # ex: "2025-1"
    tecnologias = Column(String, default="")    # tags separadas por vírgula
    link_repositorio = Column(String, default="")
    status = Column(String, default="SUBMETIDO")  # SUBMETIDO, EM_AVALIACAO, AVALIADO
    versao = Column(Integer, default=1)
    data_submissao = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ultima_atualizacao = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    aluno_id = Column(Integer, ForeignKey("users.id"))

    aluno = relationship("User", foreign_keys=[aluno_id], backref="projetos")
    avaliacoes = relationship("Avaliacao", back_populates="projeto", cascade="all, delete-orphan")


class Avaliacao(Base):
    __tablename__ = "avaliacoes"

    id = Column(Integer, primary_key=True, index=True)
    projeto_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    professor_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Critérios da rubrica (0–10 cada)
    nota_conteudo = Column(Float, default=0)        # Conteúdo / Relevância
    nota_tecnica = Column(Float, default=0)         # Qualidade Técnica
    nota_apresentacao = Column(Float, default=0)    # Apresentação / Documentação
    nota_inovacao = Column(Float, default=0)        # Inovação / Criatividade
    nota_final = Column(Float, default=0)           # Média calculada

    comentario = Column(Text, default="")
    data_avaliacao = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    projeto = relationship("Project", back_populates="avaliacoes")
    professor = relationship("User", foreign_keys=[professor_id])
