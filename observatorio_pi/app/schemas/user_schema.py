from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re

TIPOS_VALIDOS = {"ALUNO", "PROFESSOR", "COORDENADOR", "EMPRESA", "ADMIN"}


class UserCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=150)
    email: str = Field(..., max_length=254)
    senha: str = Field(..., min_length=8, max_length=128)
    tipo: str = Field(default="ALUNO")

    @field_validator("email")
    @classmethod
    def email_valido(cls, v: str) -> str:
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("E-mail inválido")
        return v.lower()

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, v: str) -> str:
        v = v.upper()
        if v not in TIPOS_VALIDOS:
            raise ValueError(f"Tipo deve ser um de: {', '.join(TIPOS_VALIDOS)}")
        return v


class UserUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=150)
    email: Optional[str] = Field(None, max_length=254)
    tipo: Optional[str] = None
    ativo: Optional[bool] = None
    senha: Optional[str] = Field(None, min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def email_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("E-mail inválido")
        return v.lower()

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.upper()
        if v not in TIPOS_VALIDOS:
            raise ValueError(f"Tipo deve ser um de: {', '.join(TIPOS_VALIDOS)}")
        return v


class UserLogin(BaseModel):
    email: str
    senha: str = Field(..., min_length=6, max_length=128)


class UserResponse(BaseModel):
    id: int
    nome: str
    email: str
    tipo: str
    ativo: bool

    model_config = {"from_attributes": True}
