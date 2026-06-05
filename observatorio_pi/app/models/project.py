"""
Modelos do domínio de projetos integradores.

Hierarquia:
  Turma  →  Tematica  →  Equipe  →  EntregaProjeto
                                 ↘  Avaliacao          (da equipe)
                                 ↘  AvaliacaoAluno     (individual por aluno)
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

CONCEITOS = ["INSUFICIENTE", "REGULAR", "BOM", "OTIMO", "EXCELENTE"]
CONCEITO_LABEL = {
    "INSUFICIENTE": "Insuficiente",
    "REGULAR":      "Regular",
    "BOM":          "Bom",
    "OTIMO":        "Ótimo",
    "EXCELENTE":    "Excelente",
}
CONCEITO_ORDEM = {c: i for i, c in enumerate(CONCEITOS)}


class Turma(Base):
    __tablename__ = "turmas"
    id        = Column(Integer, primary_key=True, index=True)
    nome      = Column(String, nullable=False)
    semestre  = Column(String, nullable=False)
    descricao = Column(Text, default="")
    ativa     = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    tematicas = relationship("Tematica", back_populates="turma", cascade="all, delete-orphan")


class Tematica(Base):
    __tablename__ = "tematicas"
    id            = Column(Integer, primary_key=True, index=True)
    titulo        = Column(String, nullable=False)
    descricao     = Column(Text, default="")
    turma_id      = Column(Integer, ForeignKey("turmas.id"), nullable=False)
    professor_id  = Column(Integer, ForeignKey("users.id"), nullable=True)
    status        = Column(String, default="ABERTA")  # ABERTA | EM_ANDAMENTO | CONCLUIDA
    criado_em     = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    turma         = relationship("Turma", back_populates="tematicas")
    professor     = relationship("User", foreign_keys=[professor_id])
    equipes       = relationship("Equipe", back_populates="tematica", cascade="all, delete-orphan")


class Equipe(Base):
    __tablename__ = "equipes"
    id              = Column(Integer, primary_key=True, index=True)
    nome            = Column(String, nullable=False)
    tematica_id     = Column(Integer, ForeignKey("tematicas.id"), nullable=False)
    scrum_master_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status          = Column(String, default="EM_ANDAMENTO")  # EM_ANDAMENTO | FINALIZADO
    criado_em       = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    tematica        = relationship("Tematica", back_populates="equipes")
    scrum_master    = relationship("User", foreign_keys=[scrum_master_id])
    membros         = relationship("EquipeMembro", back_populates="equipe", cascade="all, delete-orphan")
    entregas        = relationship("EntregaProjeto", back_populates="equipe", cascade="all, delete-orphan")
    avaliacoes      = relationship("Avaliacao", back_populates="equipe", cascade="all, delete-orphan")
    avaliacoes_aluno = relationship("AvaliacaoAluno", back_populates="equipe", cascade="all, delete-orphan")


class EquipeMembro(Base):
    __tablename__ = "equipe_membros"
    id        = Column(Integer, primary_key=True, index=True)
    equipe_id = Column(Integer, ForeignKey("equipes.id"), nullable=False)
    aluno_id  = Column(Integer, ForeignKey("users.id"), nullable=False)
    equipe    = relationship("Equipe", back_populates="membros")
    aluno     = relationship("User", foreign_keys=[aluno_id])


class EntregaProjeto(Base):
    """Entrega de um aluno. Links adicionais para Canva, Docs e Drive."""
    __tablename__ = "entregas_projeto"
    id               = Column(Integer, primary_key=True, index=True)
    equipe_id        = Column(Integer, ForeignKey("equipes.id"), nullable=False)
    autor_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    titulo           = Column(String, nullable=False)
    descricao        = Column(Text, default="")
    tecnologias      = Column(String, default="")
    link_repositorio = Column(String, default="")   # GitHub
    link_apresentacao= Column(String, default="")   # Canva / Slides
    link_documento   = Column(String, default="")   # Word Online / Google Docs
    link_drive       = Column(String, default="")   # Google Drive / pasta
    versao           = Column(Integer, default=1)
    finalizado       = Column(Boolean, default=False)
    criado_em        = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em    = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    equipe           = relationship("Equipe", back_populates="entregas")
    autor            = relationship("User", foreign_keys=[autor_id])


class Avaliacao(Base):
    """Avaliação coletiva da equipe pelo professor."""
    __tablename__ = "avaliacoes"
    id                   = Column(Integer, primary_key=True, index=True)
    equipe_id            = Column(Integer, ForeignKey("equipes.id"), nullable=False)
    professor_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    conceito_conteudo    = Column(String, default="BOM")
    conceito_tecnica     = Column(String, default="BOM")
    conceito_apresentacao= Column(String, default="BOM")
    conceito_inovacao    = Column(String, default="BOM")
    conceito_equipe      = Column(String, default="BOM")
    conceito_final       = Column(String, default="BOM")
    comentario           = Column(Text, default="")
    data_avaliacao       = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    equipe               = relationship("Equipe", back_populates="avaliacoes")
    professor            = relationship("User", foreign_keys=[professor_id])


class AvaliacaoAluno(Base):
    """Avaliação individual de um aluno dentro de uma equipe pelo professor."""
    __tablename__ = "avaliacoes_aluno"
    id             = Column(Integer, primary_key=True, index=True)
    equipe_id      = Column(Integer, ForeignKey("equipes.id"), nullable=False)
    aluno_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    professor_id   = Column(Integer, ForeignKey("users.id"), nullable=False)
    conceito       = Column(String, default="BOM")   # conceito individual geral
    comentario     = Column(Text, default="")
    data_avaliacao = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    equipe         = relationship("Equipe", back_populates="avaliacoes_aluno")
    aluno          = relationship("User", foreign_keys=[aluno_id])
    professor      = relationship("User", foreign_keys=[professor_id])
