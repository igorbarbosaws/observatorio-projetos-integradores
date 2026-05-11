<<<<<<< HEAD
FROM python:3.11-slim

# Evita arquivos .pyc e garante logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/observatorio_pi

# Instala dependências primeiro (aproveita cache do Docker)
COPY observatorio_pi/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY observatorio_pi/ .

RUN chmod +x start.sh

EXPOSE 8000

CMD ["sh", "start.sh"]
=======
FROM python:3.11-slim

# Evita arquivos .pyc e garante logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/observatorio_pi

# Instala dependências primeiro (aproveita cache do Docker)
COPY observatorio_pi/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY observatorio_pi/ .

RUN chmod +x start.sh

EXPOSE 8000

CMD ["sh", "start.sh"]
>>>>>>> 0879f9fd2a49c43f324990846de2e8d558d87942
