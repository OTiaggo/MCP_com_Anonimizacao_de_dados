FROM python:3.9-slim

# WORKDIR /app

# # Instala dependências do SO necessárias para compilar algumas libs
# RUN apt-get update && apt-get install -y build-essential

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Baixa o modelo do Spacy durante o build
# RUN python -m spacy download pt_core_news_lg

# COPY . .

# # Assume que seu código roda em servidor web para teste (ou stdio se preferir)
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]