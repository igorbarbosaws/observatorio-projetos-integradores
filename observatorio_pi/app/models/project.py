"""
Modelos do domínio de projetos integradores.

Hierarquia:
  Turma  →  Tematica  →  Equipe  →  EntregaProjeto
                                 ↘  Avaliacao
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


# ── Conceitos de avaliação (escala SENAC) ─────────────────────────────────────
# Ordem crescente: 1=Insuficiente … 5=Excelente
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
    """Turma do curso — criada pelo Coordenador/Admin."""
    __tablename__ = "turmas"

    id           = Column(Integer, primary_key=True, index=True)
    nome         = Column(String, nullable=False)           # ex: "ADS-2A"
    semestre     = Column(String, nullable=False)           # ex: "2025-1"
    descricao    = Column(Text, default="")
    ativa        = Column(Boolean, default=True, nullable=False)
    criado_em    = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    tematicas    = relationship("Tematica", back_populates="turma", cascade="all, delete-orphan")


class Tematica(Base):
    """Temática de projeto — criada pelo Coordenador/Admin e atribuída a uma Turma + Professor."""
    __tablename__ = "tematicas"

    id              = Column(Integer, primary_key=True, index=True)
    titulo          = Column(String, nullable=False)
    descricao       = Column(Text, default="")
    turma_id        = Column(Integer, ForeignKey("turmas.id"), nullable=False)
    professor_id    = Column(Integer, ForeignKey("users.id"), nullable=True)   # professor responsável
    status          = Column(String, default="ABERTA")  # ABERTA, EM_ANDAMENTO, CONCLUIDA
    criado_em       = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em   = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    turma           = relationship("Turma", back_populates="tematicas")
    professor       = relationship("User", foreign_keys=[professor_id])
    equipes         = relationship("Equipe", back_populates="tematica", cascade="all, delete-orphan")


class Equipe(Base):
    """Equipe de alunos vinculada a uma Temática — montada pelo Professor."""
    __tablename__ = "equipes"

    id              = Column(Integer, primary_key=True, index=True)
    nome            = Column(String, nullable=False)          # ex: "Equipe Alpha"
    tematica_id     = Column(Integer, ForeignKey("tematicas.id"), nullable=False)
    scrum_master_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # aluno líder
    status          = Column(String, default="EM_ANDAMENTO")  # EM_ANDAMENTO, FINALIZADO
    criado_em       = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    tematica        = relationship("Tematica", back_populates="equipes")
    scrum_master    = relationship("User", foreign_keys=[scrum_master_id])
    membros         = relationship("EquipeMembro", back_populates="equipe", cascade="all, delete-orphan")
    entregas        = relationship("EntregaProjeto", back_populates="equipe", cascade="all, delete-orphan")
    avaliacoes      = relationship("Avaliacao", back_populates="equipe", cascade="all, delete-orphan")


class EquipeMembro(Base):
    """Associação Equipe ↔ Aluno."""
    __tablename__ = "equipe_membros"

    id          = Column(Integer, primary_key=True, index=True)
    equipe_id   = Column(Integer, ForeignKey("equipes.id"), nullable=False)
    aluno_id    = Column(Integer, ForeignKey("users.id"), nullable=False)

    equipe      = relationship("Equipe", back_populates="membros")
    aluno       = relationship("User", foreign_keys=[aluno_id])


class EntregaProjeto(Base):
    """
    Entrega/contribuição de um aluno ao projeto da equipe.
    Qualquer membro pode criar entregas.
    Apenas o Scrum Master pode excluir ou marcar como finalizado.
    """
    __tablename__ = "entregas_projeto"

    id                  = Column(Integer, primary_key=True, index=True)
    equipe_id           = Column(Integer, ForeignKey("equipes.id"), nullable=False)
    autor_id            = Column(Integer, ForeignKey("users.id"), nullable=False)  # aluno que subiu
    titulo              = Column(String, nullable=False)
    descricao           = Column(Text, default="")
    tecnologias         = Column(String, default="")   # tags separadas por vírgula
    link_repositorio    = Column(String, default="")
    versao              = Column(Integer, default=1)
    finalizado          = Column(Boolean, default=False)  # só Scrum Master pode marcar
    criado_em           = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em       = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    equipe              = relationship("Equipe", back_populates="entregas")
    autor               = relationship("User", foreign_keys=[autor_id])


class Avaliacao(Base):
    """
    Avaliação de uma Equipe pelo Professor usando conceitos SENAC.
    Critérios: Conteúdo, Técnica, Apresentação, Inovação, Trabalho em Equipe.
    """
    __tablename__ = "avaliacoes"

    id                  = Column(Integer, primary_key=True, index=True)
    equipe_id           = Column(Integer, ForeignKey("equipes.id"), nullable=False)
    professor_id        = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Critérios → valores: INSUFICIENTE | REGULAR | BOM | OTIMO | EXCELENTE
    conceito_conteudo       = Column(String, default="BOM")
    conceito_tecnica        = Column(String, default="BOM")
    conceito_apresentacao   = Column(String, default="BOM")
    conceito_inovacao       = Column(String, default="BOM")
    conceito_equipe         = Column(String, default="BOM")
    # Conceito final (determinado pelo professor, pode ser diferente da média)
    conceito_final          = Column(String, default="BOM")

    comentario          = Column(Text, default="")
    data_avaliacao      = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    equipe              = relationship("Equipe", back_populates="avaliacoes")
    professor           = relationship("User", foreign_keys=[professor_id])
