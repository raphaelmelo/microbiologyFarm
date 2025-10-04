import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi encontrada no arquivo .env")
    
    genai.configure(api_key=api_key)

    print("Modelos disponíveis que suportam 'generateContent':")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")

except Exception as e:
    print(f"Ocorreu um erro: {e}")
