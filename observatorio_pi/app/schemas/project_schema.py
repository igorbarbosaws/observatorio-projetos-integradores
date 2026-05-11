<<<<<<< HEAD
from pydantic import BaseModel
from typing import Optional

class ProjectCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None

class ProjectUpdate(BaseModel):
    titulo: Optional[str] = None
=======
from pydantic import BaseModel
from typing import Optional

class ProjectCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None

class ProjectUpdate(BaseModel):
    titulo: Optional[str] = None
>>>>>>> 0879f9fd2a49c43f324990846de2e8d558d87942
    descricao: Optional[str] = None