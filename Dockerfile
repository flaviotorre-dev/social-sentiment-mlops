FROM python:3.14-slim

WORKDIR /app

# 1. dipendenze: layer in cache finché requirements.txt non cambia
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. modello scaricato in build: l'avvio del container non richiede rete
RUN python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='cardiffnlp/twitter-roberta-base-sentiment-latest')"

# 3. codice: cambia spesso, quindi va per ultimo
COPY app/ app/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
