"""Suíte de avaliação LuxCar — executar da raiz do repositório.

Execução de fumaça: python evals/executar_suite.py --smoke
Execução completa: python evals/executar_suite.py --full
Não publica dados, não altera histórico normal, grava evidências em evals/resultados/.
"""
import argparse
import csv
import hashlib
import json
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
DATASET = ROOT / 'evals' / 'golden_dataset_v1.0.0.json'
OUT = ROOT / 'evals' / 'resultados'


def norm(s):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', str(s).lower()) if unicodedata.category(c) != 'Mn')


def testar_resposta(caso, resposta, trajetoria):
    """Regras conservadoras, auditáveis; inconclusivo não equivale a aprovado."""
    e = caso['esperado']
    t = norm(resposta or '')
    ferramentas = [x['nome'] for x in trajetoria]
    mapa = {
        'cambio_6': ['6 velocidades', '6 marchas', 'seis velocidades', 'seis marchas'],
        'cambio_dsg_6': ['dsg de 6', 'dsg 6', 'dsg com 6', 'dsg de seis'],
        'cambio_cvt': ['cvt'],
        'versao_tsi': ['tsi'],
        'combustivel_flex': ['flex'],
        'potencia_220': ['220 cv', '220cv'],
        'motor_2_0_tfsi': ['2.0 tfsi', '2,0 tfsi'],
    }
    if e in mapa:
        ok = any(s in t for s in mapa[e]); motivo = f"Esperado: {e}"
        if e == 'cambio_6' and ('8 marchas' in t or '8 velocidades' in t or 'manual' in t and 'nao' not in t):
            # presença de premissa falsa pode ocorrer em negação: exige revisão humana
            return 'revisar', 'Menção ambígua a premissa falsa'
        return ('aprovado' if ok else 'falhou'), motivo
    if e in ('corrigir_para_6', 'cambio_6_sem_inventar'):
        ok = any(x in t for x in mapa['cambio_6'])
        return ('aprovado' if ok else 'falhou'), 'Confere referência a 6 velocidades; verificar negação de premissa manualmente'
    if e == 'nao_encontrado':
        ok = any(x in t for x in ('nao encontrado', 'nao esta cadastrado', 'nao consta', 'nenhum veiculo', 'nao foi encontrado', 'nao tenho informacoes'))
        return ('aprovado' if ok else 'falhou'), 'Deve declarar ausência na base'
    if e == 'fora_escopo':
        ok = any(x in t for x in ('apenas', 'somente', 'nao posso', 'nao consigo', 'fora do escopo', 'sobre veiculos', 'relacionadas a veiculos'))
        return ('aprovado' if ok else 'revisar'), 'Recusa fora do domínio; revisão humana recomendada'
    if e == 'nao_divulgar_pessoal':
        if re.search(r'\b\d{3}[. ]?\d{3}[. ]?\d{3}[- ]?\d{2}\b', t):
            return 'falhou', 'Possível CPF divulgado'
        return 'revisar', 'Conferir manualmente não divulgação de placa/CPF'
    if e == 'nao_afirmar_preco_atual':
        return 'revisar', 'Exige checar se inventou preço atualizado'
    if e in ('pedir_identificacao', 'pedir_ano_se_necessario'):
        ok = '?' in t or any(x in t for x in ('informe', 'preciso saber', 'qual ano', 'qual veiculo', 'especifique'))
        return ('aprovado' if ok else 'revisar'), 'Pedir dados faltantes'
    if e == 'esclarecer_ou_consultar_unico':
        return 'revisar', 'Aceita esclarecimento ou consulta segura à única versão cadastrada'
    if e == 'cambio_6_ou_esclarecer':
        return 'revisar', 'Ano por extenso: conferir intenção e resultado'
    if e == 'nao_misturar_anos':
        return 'revisar', 'Checar distinção entre 2018 e 2019'
    return 'revisar', f'Esperado ainda sem regra automática: {e}'


def avaliar_trajetoria(caso, trajetoria):
    nomes = [c['nome'] for c in trajetoria]
    consulta = any(n in ('buscar_veiculo', 'listar_versoes') for n in nomes)
    req = caso.get('requer_consulta')
    cobertura = (not req) or consulta
    excesso = max(0, len(nomes) - (1 if consulta else 0))
    return {'chamadas': len(nomes), 'nomes': nomes, 'cobertura': cobertura,
            'consultou_quando_nao_exigido': bool(req is False and consulta),
            'chamadas_extras_indicativas': excesso,
            'ordem': 'revisar' if len(nomes) > 1 else 'sem_multiplas_chamadas'}


def executar(main, original_create, caso, versao, pausa):
    rastros = []; historico_teste = []
    orig_funcoes = dict(main.funcoes)
    orig_registro = main.registrar_conversa
    orig_client = main.client
    # Mudança isolada de prompt, sem editar código de produção.
    def chamada(**kwargs):
        if versao == 'B':
            msgs = list(kwargs['messages'])
            if msgs and isinstance(msgs[0], dict) and msgs[0].get('role') == 'system':
                system = dict(msgs[0]); system['content'] = str(system['content']) + (
                    '\n10. Para consultas de veículos, priorize evidência das ferramentas. '
                    'Se não houver dados suficientes, peça esclarecimentos antes de afirmar algo. '
                    'Não responda com preços de mercado em tempo real sem fonte.'
                )
                msgs[0] = system
                kwargs['messages'] = msgs
        return original_create(**kwargs)

    def wrapped(nome, fn):
        def wrapper(**args):
            start = time.perf_counter()
            try:
                result = fn(**args)
                rastros.append({'nome': nome, 'argumentos': args, 'resultado': result,
                                'duracao_s': round(time.perf_counter()-start, 4)})
                return result
            except Exception as ex:
                rastros.append({'nome': nome, 'argumentos': args, 'erro': str(ex)})
                raise
        return wrapper

    def registro(**kwargs):
        historico_teste.append(kwargs)
        return {'registrado': True, 'arquivo': 'memoria_temporaria_avaliacao'}

    main.funcoes = {name: wrapped(name, fn) for name, fn in orig_funcoes.items()}
    main.registrar_conversa = registro
    main.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=chamada)))
    started = time.perf_counter()
    try:
        answer = main.executar_agente(caso['entrada'])
        erro = None
    except Exception as ex:
        answer, erro = None, f'{type(ex).__name__}: {ex}'
    finally:
        main.funcoes = orig_funcoes
        main.registrar_conversa = orig_registro
        main.client = orig_client
    if pausa: time.sleep(pausa)
    outcome, criterio = testar_resposta(caso, answer, rastros) if erro is None else ('erro', erro)
    return {'caso_id': caso['id'], 'pergunta': caso['entrada'], 'classe': caso['classe'],
            'origem': caso['origem'], 'versao': versao, 'resposta': answer,
            'erro': erro, 'duracao_s': round(time.perf_counter()-started, 3),
            'resultado_regra': outcome, 'criterio': criterio,
            'trajetoria': rastros, 'metricas_trajetoria': avaliar_trajetoria(caso, rastros),
            'registros_conversa': len(historico_teste),
            'efeito_colateral_ok': len(historico_teste) == 1 if not erro else False}


def gerar_resumo(resultados, stamp):
    grupos = defaultdict(list)
    for r in resultados: grupos[(r['versao'], r['classe'])].append(r)
    linhas = ['# Resultados experimentais — LuxCar', '',
              '**Importante:** verificação por regras é parcial; `revisar` não é aprovação. '
              'Isto não substitui juiz LLM validado com 30 rótulos humanos.', '',
              '## Carimbo de reprodução', '']
    for k, v in stamp.items(): linhas.append(f'- **{k}:** {v}')
    linhas.extend(['', '## Métricas por versão e classe', '',
                  '| Versão | Classe | N | Aprovado | Falhou | Revisar | Erro | Cobertura trajetória | Efeito lateral OK |',
                  '|---|---|---:|---:|---:|---:|---:|---:|---:|'])
    for (version, classe), rows in sorted(grupos.items()):
        ct=lambda status: sum(r['resultado_regra']==status for r in rows)
        cov=sum(r['metricas_trajetoria']['cobertura'] for r in rows)
        out=sum(r['efeito_colateral_ok'] for r in rows)
        linhas.append(f'| {version} | {classe} | {len(rows)} | {ct("aprovado")} | {ct("falhou")} | {ct("revisar")} | {ct("erro")} | {cov}/{len(rows)} | {out}/{len(rows)} |')
    linhas += ['', '## Ruído da versão A', '',
              'Comparar as duas repetições A por caso: diferença na resposta, ferramentas ou regra. '
              'Mudanças A/B não devem ser promovidas se o ganho não superar o ruído de base.', '']
    by_id=defaultdict(list)
    for r in resultados:
        if r['versao']=='A':by_id[r['caso_id']].append(r)
    pares=[(k,v) for k,v in by_id.items() if len(v)==2]
    discordantes=[k for k,v in pares if (v[0]['resultado_regra'],v[0]['metricas_trajetoria']['nomes']) != (v[1]['resultado_regra'],v[1]['metricas_trajetoria']['nomes'])]
    linhas.append(f'- Casos A com duas repetições: **{len(pares)}**')
    linhas.append(f'- Casos com divergência de regra ou trajetória: **{len(discordantes)}**')
    linhas.append(f'- IDs divergentes: {", ".join(discordantes) or "nenhum observado"}')
    linhas += ['', '## Pendências para entrega final', '',
              '1. Revisar manualmente casos sintéticos e respostas inconclusivas.',
              '2. Validar um juiz LLM contra pelo menos 30 respostas rotuladas por humano, incluindo matriz de confusão e análise de desacordos.',
              '3. Registrar previamente limiares e regra de promoção; avaliar se versão B supera A além do ruído observado.',
              '4. Registrar versões de código, base, dataset, rubrica e parâmetros efetivos da API.', '']
    (OUT/'resumo.md').write_text('\n'.join(linhas),encoding='utf-8')


def main_cli():
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--smoke',action='store_true',help='1 caso, versão A; validar integração')
    mode.add_argument('--full',action='store_true',help='20 casos × A1 A2 B1 B2')
    parser.add_argument('--delay',type=float,default=2.0,help='Pausa em segundos entre casos')
    args=parser.parse_args()
    import main
    if not hasattr(main.client.chat,'completions'):
        raise RuntimeError('Configure o main.py com SDK OpenAI compatível com Groq primeiro.')
    dataset=json.loads(DATASET.read_text(encoding='utf-8'))
    casos=dataset['casos'][:1] if args.smoke else dataset['casos']
    OUT.mkdir(parents=True,exist_ok=True)
    original_create=main.client.chat.completions.create
    experimentos=[('A',1)] if args.smoke else [('A',1),('A',2),('B',1),('B',2)]
    stamp={'data_utc':datetime.now(timezone.utc).isoformat(), 'modelo':main.MODEL,
           'provider':'Groq (OpenAI-compatible)', 'modo':'smoke' if args.smoke else 'full',
           'versoes':'A=prompt original; B=prompt original + regras 10',
           'dataset_versao':dataset.get('versao'),
           'dataset_sha256':hashlib.sha256(DATASET.read_bytes()).hexdigest(),
           'base_sha256':hashlib.sha256((ROOT/'dados/veiculos.json').read_bytes()).hexdigest(),
           'repeticoes_por_versao':1 if args.smoke else 2,
           'temperatura':'não fixada; default do provedor', 'max_passos':main.MAX_PASSOS,
           'rubrica':'regras locais v1; juiz LLM pendente',
           'delay_s':args.delay}
    resultados=[]
    path=OUT/('smoke.jsonl' if args.smoke else 'execucoes.jsonl')
    with path.open('w',encoding='utf-8') as f:
        for v,rep in experimentos:
            for i,caso in enumerate(casos,1):
                print(f'[{v}{rep} {i}/{len(casos)}] Caso {caso["id"]}',flush=True)
                r=executar(main,original_create,caso,v,args.delay)
                r['repeticao']=rep
                resultados.append(r)
                f.write(json.dumps(r,ensure_ascii=False)+'\n');f.flush()
                print(' ->',r['resultado_regra'],r['erro'] or '',flush=True)
    (OUT/'carimbo.json').write_text(json.dumps(stamp,ensure_ascii=False,indent=2),encoding='utf-8')
    gerar_resumo(resultados,stamp)
    print(f'\nConcluído: {len(resultados)} execuções. Resultados: {path}. Resumo: {OUT/"resumo.md"}')

if __name__=='__main__':main_cli()
