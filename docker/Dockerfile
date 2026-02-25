FROM python:3.10-slim

WORKDIR /app

# Installation des dépendances système requises par psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

ENV PYTHONPATH=/app

# Commande de lancement de l'API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]