import os
import json
from dotenv import load_dotenv
from mistralai.client import Mistral

from tools import buscar_veiculo, listar_versoes, registrar_conversa

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    raise ValueError("MISTRAL_API_KEY não encontrada no arquivo .env")

client = Mistral(api_key=api_key)

MODEL = "ministral-8b-2512"
MAX_PASSOS = 5

tools = [
   
    {
        "type": "function",
        "function": {
            "name": "buscar_veiculo",
            "description": (
                "Busca informações de um veículo na base de dados do LuxCar. "
                "Use esta ferramenta quando o usuário perguntar sobre um "
                "veículo específico."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "marca": {
                        "type": "string",
                        "description": "Marca do veículo."
                    },
                    "modelo": {
                        "type": "string",
                        "description": "Modelo do veículo."
                    },
                    "ano": {
                        "type": "integer",
                        "description": "Ano do veículo."
                    },
                    "versao": {
                        "type": ["string", "null"],
                        "description": "Versão do veículo, se informada."
                    }
                },
                "required": ["marca", "modelo", "ano", "versao"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_versoes",
            "description": (
                "Lista as versões disponíveis de um veículo na base do LuxCar. "
                "Use esta ferramenta quando o usuário informar marca, modelo e ano, "
                "mas não informar a versão."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "marca": {
                        "type": "string",
                        "description": "Marca do veículo."
                    },
                    "modelo": {
                        "type": "string",
                        "description": "Modelo do veículo."
                    },
                    "ano": {
                        "type": "integer",
                        "description": "Ano do veículo."
                    }
                },
                "required": ["marca", "modelo", "ano"]
            }
        }
    }
]

funcoes = {
    "buscar_veiculo": buscar_veiculo,
    "listar_versoes": listar_versoes,
    "registrar_conversa": registrar_conversa
}

def executar_agente(pergunta):
    
    estado = {
        "pergunta": pergunta,
        "ferramenta_utilizada": None,
        "resultado_consulta": None,
        "resposta": None,
        "motivo_termino": None,
        "passos": 0
    }

    mensagens = [
        {
            "role": "system",
            "content": """
Você é o LuxCar, um agente especializado em responder dúvidas sobre veículos.

Regras:
1. Responda somente sobre veículos.
2. Quando precisar de informações sobre um veículo, use a ferramenta buscar_veiculo.
3. Use exclusivamente as informações retornadas pelas ferramentas.
4. Nunca invente, complete ou suponha informações que não estejam na base.
5. Se o veículo não for encontrado, informe claramente que ele não está cadastrado na base.
6. Se faltarem informações essenciais para identificar o veículo, peça esclarecimento.
7. Se houver conflito entre a pergunta do usuário e os dados da ferramenta, considere os dados da ferramenta como fonte oficial.
8. Não atribua características ao veículo que não tenham sido retornadas pela ferramenta.
9. Seja objetivo e responda em português.
"""
        },
        {
            "role": "user",
            "content": pergunta
        }
    ]

    estado["passos"] += 1

    resposta = client.chat.complete(
        model=MODEL,
        messages=mensagens,
        tools=tools,
        tool_choice="auto",
        parallel_tool_calls=False
    )

    mensagens.append(resposta.choices[0].message)

    while resposta.choices[0].message.tool_calls and estado["passos"] < MAX_PASSOS:

        for chamada in resposta.choices[0].message.tool_calls:

            nome_funcao = chamada.function.name
            estado["ferramenta_utilizada"] = nome_funcao

            argumentos = json.loads(chamada.function.arguments)

            print(f"\n[TOOL] {nome_funcao}")
            print(f"[ARGUMENTOS] {argumentos}")

            if nome_funcao not in funcoes:
                resultado = {
                    "erro": f"Ferramenta '{nome_funcao}' não encontrada."
                }
            else:
                try:
                    resultado = funcoes[nome_funcao](**argumentos)
                except Exception as erro:
                    resultado = {
                        "erro": str(erro)
                    }

            estado["resultado_consulta"] = resultado

            mensagens.append(
                {
                    "role": "tool",
                    "name": nome_funcao,
                    "content": json.dumps(
                        resultado,
                        ensure_ascii=False
                    ),
                    "tool_call_id": chamada.id
                }
            )

        estado["passos"] += 1

        resposta = client.chat.complete(
            model=MODEL,
            messages=mensagens,
            tools=tools,
            tool_choice="auto",
            parallel_tool_calls=False
        )

        mensagens.append(resposta.choices[0].message)

    estado["resposta"] = resposta.choices[0].message.content

    if (
        estado["passos"] >= MAX_PASSOS
        and resposta.choices[0].message.tool_calls
    ):
        estado["motivo_termino"] = "limite_de_passos"
    else:
        estado["motivo_termino"] = "resposta_final"

    registrar_conversa(
        pergunta=estado["pergunta"],
        resposta=estado["resposta"],
        ferramenta_utilizada=estado["ferramenta_utilizada"]
    )

    return estado["resposta"]


if __name__ == "__main__":

    pergunta = input("Usuário: ")

    resposta = executar_agente(pergunta)

    print("\nLuxCar:", resposta)

