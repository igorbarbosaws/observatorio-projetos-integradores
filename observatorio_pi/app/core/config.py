import os

# Em produção, defina a variável de ambiente SECRET_KEY com um valor seguro.
# Exemplo: export SECRET_KEY="sua-chave-secreta-longa-e-aleatoria"
SECRET_KEY = os.getenv("SECRET_KEY", "observatorio_secret_key_dev_only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
