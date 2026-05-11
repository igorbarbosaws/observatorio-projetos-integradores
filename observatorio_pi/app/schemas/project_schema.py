from pydantic import BaseModel
from typing import Optional

class ProjectCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None

class ProjectUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None