import os
import re
import requests
from dotenv import load_dotenv


def carregar_chave_api() -> str:
    """Carrega e valida a existência da chave da API no arquivo .env."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "sua_chave_api_aqui":
        raise ValueError("Chave GEMINI_API_KEY ausente ou não configurada no arquivo .env.")
    return api_key


def anonimizar_relato(texto: str) -> str:
    """Remove padrões sensíveis (CPF, datas, telefones) localmente antes do envio."""
    texto_limpo = re.sub(r"\d{3}\.\d{3}\.\d{3}-\d{2}", "[CPF REMOVIDO]", texto)
    texto_limpo = re.sub(r"\d{2}/\d{2}/\d{4}", "[DATA REMOVIDA]", texto_limpo)
    texto_limpo = re.sub(r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}", "[TELEFONE REMOVIDO]", texto_limpo)
    return texto_limpo.strip()


def validar_entrada(texto: str) -> str:
    """Garante que a entrada não esteja vazia nem curta demais para análise."""
    texto_limpo = texto.strip()
    if not texto_limpo:
        raise ValueError("A entrada está vazia. Por favor, insira as observações do aluno.")
    if len(texto_limpo) < 15:
        raise ValueError("Relato muito curto. Forneça mais detalhes comportamentais ou pedagógicos.")
    return texto_limpo


def consultar_gemini(relato_seguro: str, api_key: str) -> str:
    """Envia o relato anonimizado para a API REST do Gemini e retorna os guias gerados."""
    dominio = "https://generativelanguage." + "googleapis.com"
    caminho = "/v1beta/models/gemini-flash-latest:generateContent"
    url = dominio + caminho

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    prompt_sistema = (
        "Você é um psicólogo escolar especialista em Educação Inclusiva. "
        "Traduza observações técnicas em dois guias práticos, éticos e livres de jargões clínicos: "
        "1) Guia Prático para o Professor (manejo de sala e adaptações); "
        "2) Guia Acolhedor para a Família (rotina em casa e vínculo). "
        "Nunca faça diagnósticos médicos e substitua qualquer nome próprio esquecido por 'o(a) estudante'."
    )

    payload = {
        "system_instruction": {"parts": [{"text": prompt_sistema}]},
        "contents": [{"parts": [{"text": f"Observações técnicas: {relato_seguro}"}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1200
        }
    }

    resposta = requests.post(url, headers=headers, json=payload, timeout=30)
    resposta.raise_for_status()

    dados = resposta.json()
    try:
        return dados["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as erro:
        raise RuntimeError(f"Formato inesperado na resposta da API: {erro}")


def main():
    print("=== PONTE ESCOLAR: TRADUTOR PSICOEDUCACIONAL (v2.0) ===")
    try:
        api_key = carregar_chave_api()

        print("Digite ou cole as observações técnicas anonimizadas do aluno:")
        entrada_bruta = input("> ")

        relato_valido = validar_entrada(entrada_bruta)
        relato_seguro = anonimizar_relato(relato_valido)

        print("\nProcessando e gerando orientações... Aguarde.\n")
        resultado = consultar_gemini(relato_seguro, api_key)

        print("=== RESULTADO GERADO ===\n")
        print(resultado)

    except ValueError as erro_validacao:
        print(f"\n[Erro de Entrada/Configuração]: {erro_validacao}")
    except requests.exceptions.Timeout:
        print("\n[Erro de Rede]: O servidor demorou muito para responder (Timeout). Tente novamente.")
    except requests.exceptions.ConnectionError:
        print("\n[Erro de Conexão]: Sem acesso à internet ou falha ao alcançar o servidor da API.")
    except requests.exceptions.HTTPError as erro_http:
        status = erro_http.response.status_code if erro_http.response is not None else "Desconhecido"
        if status in (401, 403):
            print("\n[Erro de Autenticação]: Chave de API inválida ou sem permissão.")
        elif status == 429:
            print("\n[Limite Excedido]: Muitas requisições em pouco tempo. Aguarde 1 minuto.")
        elif status == 503:
            print("\n[Serviço Indisponível]: O servidor do Gemini está temporariamente sobrecarregado (Erro 503). Tente novamente em instantes.")
        else:
            print(f"\n[Erro HTTP {status}]: Falha na comunicação com a API.")
    except Exception as erro_geral:
        print(f"\n[Erro Inesperado]: {erro_geral}")


if __name__ == "__main__":
    main()
