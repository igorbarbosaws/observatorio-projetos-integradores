FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/observatorio_pi

COPY observatorio_pi/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY observatorio_pi/ .

RUN chmod +x start.sh

EXPOSE 8000

CMD ["sh", "start.sh"]
