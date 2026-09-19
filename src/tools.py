import json
from pathlib import Path


def buscar_veiculo(
    marca: str,
    modelo: str,
    ano: int,
    versao: str | None = None
):
    """
    Busca um veículo na base simulada do LuxCar.
    """

    caminho_base = Path(__file__).parent.parent / "dados" / "veiculos.json"

    with open(caminho_base, "r", encoding="utf-8") as arquivo:
        veiculos = json.load(arquivo)

    resultados = []

    for veiculo in veiculos:
        if (
            veiculo["marca"].lower() == marca.lower()
            and veiculo["modelo"].lower() == modelo.lower()
            and veiculo["ano"] == ano
        ):
            if versao is None or veiculo["versao"].lower() == versao.lower():
                resultados.append(veiculo)

    if not resultados:
        return {
            "encontrado": False,
            "mensagem": "Nenhum veículo correspondente foi encontrado na base."
        }

    return {
        "encontrado": True,
        "veiculos": resultados
    }

def registrar_conversa(pergunta: str, resposta: str, ferramenta_utilizada: str | None = None):
    """
    Registra uma interação do LuxCar em um arquivo de histórico.
    """

    caminho_logs = Path(__file__).parent.parent / "logs" / "historico.jsonl"

    registro = {
        "pergunta": pergunta,
        "resposta": resposta,
        "ferramenta_utilizada": ferramenta_utilizada
    }

    with open(caminho_logs, "a", encoding="utf-8") as arquivo:
        arquivo.write(
            json.dumps(registro, ensure_ascii=False) + "\n"
        )

    return {
        "registrado": True,
        "arquivo": "logs/historico.jsonl"
    }

def listar_versoes(marca: str, modelo: str, ano: int):
    """
    Lista as versões disponíveis de um veículo na base do LuxCar.
    """

    caminho_dados = Path(__file__).parent.parent / "dados" / "veiculos.json"

    with open(caminho_dados, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    versoes = []

    for veiculo in dados:
        if (
            veiculo.get("marca", "").lower() == marca.lower()
            and veiculo.get("modelo", "").lower() == modelo.lower()
            and veiculo.get("ano") == ano
        ):
            versao = veiculo.get("versao")

            if versao and versao not in versoes:
                versoes.append(versao)

    if not versoes:
        return {
            "encontrado": False,
            "versoes": [],
            "mensagem": "Nenhuma versão encontrada para esse veículo."
        }

    return {
        "encontrado": True,
        "versoes": versoes
    }