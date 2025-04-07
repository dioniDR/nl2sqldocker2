from dotenv import load_dotenv
import os
from openai import OpenAI

# Cargar las variables del archivo .env
load_dotenv()

# Crear instancia del nuevo cliente
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Solicitud al modelo
response = client.chat.completions.create(
    model="gpt-3.5-turbo",  # o "gpt-4" si tienes acceso
    messages=[
        {"role": "user", "content": "¿Qué es una red neuronal?"}
    ]
)

# Mostrar la respuesta
print(response.choices[0].message.content)
