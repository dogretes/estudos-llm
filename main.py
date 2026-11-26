import os
import requests
from dotenv import load_dotenv

# 1. Carregamento da credencial
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Chave GEMINI_API_KEY não encontrada no arquivo .env")

# 2. Captura da entrada pelo terminal
print("=== PONTE ESCOLAR: TRADUTOR PSICOEDUCACIONAL ===")
print("Digite ou cole as observações técnicas anonimizadas do aluno:")
relato_tecnico = input("> ")

# 3. Preparação da solicitação REST para o Gemini
dominio = "https://generativelanguage." + "googleapis.com"
caminho = "/v1beta/models/gemini-2.5-flash-lite:generateContent"
url = dominio + caminho

headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": api_key
}

prompt_sistema = (
    "Você é um psicólogo escolar. Traduza observações técnicas em dois guias práticos, "
    "éticos e livres de jargões clínicos: um para o professor e outro para a família. "
    "Nunca faça diagnósticos médicos."
)

payload = {
    "system_instruction": {
        "parts": [{"text": prompt_sistema}]
    },
    "contents": [
        {
            "parts": [{"text": f"Observações: {relato_tecnico}"}]
        }
    ],
    "generationConfig": {
        "temperature": 0.3
    }
}

# 4. Chamada ao modelo via API REST
print("\nGerando orientações... Aguarde.\n")
resposta = requests.post(url, headers=headers, json=payload)
resposta.raise_for_status()

# 5. Interpretação e apresentação da saída
dados = resposta.json()
texto_gerado = dados["candidates"][0]["content"]["parts"][0]["text"]

print("=== RESULTADO GERADO ===\n")
print(texto_gerado)
