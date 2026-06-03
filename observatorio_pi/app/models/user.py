from sqlalchemy import Column, Integer, String, Boolean, Text
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, index=True)
    nome         = Column(String, nullable=False)
    email        = Column(String, unique=True, index=True, nullable=False)
    senha_hash   = Column(String, nullable=False)
    # ALUNO, PROFESSOR, COORDENADOR, EMPRESA, ADMIN
    tipo         = Column(String, default="ALUNO", nullable=False)
    ativo        = Column(Boolean, default=True, nullable=False)

    # ── Campos de perfil (visíveis no portfólio — relevantes para ALUNOs) ─────
    bio          = Column(Text, default="")          # apresentação pessoal
    linkedin     = Column(String, default="")        # URL LinkedIn
    github       = Column(String, default="")        # URL GitHub
    portfolio_url= Column(String, default="")        # site/portfolio pessoal
    area_interesse = Column(String, default="")      # ex: "Backend, IA, Mobile"
    cidade       = Column(String, default="")        # localização
    telefone     = Column(String, default="")        # contato para empresas
