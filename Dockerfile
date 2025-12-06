FROM python:3.11-slim

# Instalar dependências do sistema necessárias para Whisper e FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app.py .

# Expor porta
EXPOSE 8484

# Variável de ambiente para o modelo Whisper (pode ser: tiny, base, small, medium, large)
ENV WHISPER_MODEL=base
ENV PORT=8484

# Comando para iniciar a aplicação
CMD ["python", "app.py"]

