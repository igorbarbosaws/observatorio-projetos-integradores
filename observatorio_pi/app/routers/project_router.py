# Router de API REST legado — mantido para compatibilidade com /docs
# A lógica principal agora está nas rotas HTML em main.py
from fastapi import APIRouter

router = APIRouter(prefix="/projects", tags=["Projetos (API)"])
