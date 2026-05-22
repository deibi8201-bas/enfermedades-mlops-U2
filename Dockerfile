FROM python:3.11-slim

WORKDIR /app

# AUTOMATIZACIÓN DE HORA LOCAL (Colombia)
ENV TZ=America/Bogota

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
