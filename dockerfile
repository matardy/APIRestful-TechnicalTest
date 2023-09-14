# Usar una imagen base de Python
FROM python:3.8

# Establecer una variable de entorno para asegurarse de que la salida de Python se envía directamente al terminal
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar requirements.txt y instalar las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Ejecutar la aplicación
CMD ["python", "app.py"]
