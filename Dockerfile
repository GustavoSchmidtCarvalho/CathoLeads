# Imagem oficial do Playwright para Python (já vem com browsers + deps)
# Versão alinhada com playwright==1.57.0 do requirements.txt
FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy

WORKDIR /app

# Instala dependências Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copia o código do projeto
COPY src/ /app/src/

# Pasta de saída (normalmente será montada como volume)
RUN mkdir -p /app/output

# Rodar sempre em headless via config.json (recomendado)
CMD ["python", "-u", "src/catho_leads.py"]
