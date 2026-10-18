"""Orquestração com handoffs reais do OpenAI Agents SDK."""
import json
from dataclasses import dataclass
from agents import Agent, Runner, RunContextWrapper, function_tool
from .core import Caso, Predicao, RespostaFinal, prever, selecionar_protocolos, validar_resposta

@dataclass
class Estado:
    caso: Caso
    predicao: Predicao | None = None
    protocolos: list[str] | None = None

@function_tool
def consultar_modelo(ctx: RunContextWrapper[Estado]) -> str:
    """Consulta o classificador treinado para o caso recebido; não inventa scores."""
    resultado = prever(ctx.context.caso)
    ctx.context.predicao = resultado
    return resultado.model_dump_json()

@function_tool
def consultar_protocolos(ctx: RunContextWrapper[Estado]) -> str:
    """Retorna somente os protocolos sintéticos cujas condições são satisfeitas."""
    if ctx.context.predicao is None:
        raise ValueError('A predição precisa ocorrer antes da consulta de protocolos.')
    resultado = selecionar_protocolos(ctx.context.caso, ctx.context.predicao)
    ctx.context.protocolos = resultado
    return json.dumps(resultado, ensure_ascii=False)

@function_tool
def consultar_resultados(ctx: RunContextWrapper[Estado]) -> str:
    """Recupera predição e protocolos calculados para construir a resposta final."""
    if ctx.context.predicao is None or ctx.context.protocolos is None:
        raise ValueError('Etapas anteriores incompletas.')
    return json.dumps({'predicao': ctx.context.predicao.model_dump(), 'protocolos': ctx.context.protocolos}, ensure_ascii=False)

planejador = Agent[Estado](
    name='Planejador de Resposta',
    instructions=('Use consultar_resultados obrigatoriamente. Retorne saída estruturada. '
                  'Copie exatamente probabilidade, classificacao e protocolos, sem adicionar ou omitir itens. '
                  'A justificativa deve ser curta e baseada nos dados; observacao deve afirmar '
                  'que é uma simulação educacional, não uma recomendação clínica.'),
    tools=[consultar_resultados],
    output_type=RespostaFinal,
)

especialista = Agent[Estado](
    name='Especialista em Protocolos',
    instructions=('Chame consultar_protocolos exatamente uma vez e depois faça handoff '
                  'ao Planejador de Resposta. Não altere os protocolos.'),
    tools=[consultar_protocolos],
    handoffs=[planejador],
)

analista = Agent[Estado](
    name='Analista de Risco',
    instructions=('Chame consultar_modelo exatamente uma vez. Em seguida, faça handoff '
                  'ao Especialista em Protocolos. Nunca estime probabilidades por conta própria.'),
    tools=[consultar_modelo],
    handoffs=[especialista],
)

orquestrador = Agent[Estado](
    name='Orquestrador',
    instructions=('Você coordena o fluxo. Encaminhe imediatamente ao Analista de Risco '
                  'usando handoff. Não calcule risco nem escreva a resposta final.'),
    handoffs=[analista],
)

async def executar(caso: Caso) -> tuple[RespostaFinal, list[dict]]:
    estado = Estado(caso=caso)
    resultado = await Runner.run(
        orquestrador,
        input='Analise o caso simulado armazenado no contexto e execute o fluxo completo.',
        context=estado,
        max_turns=20,
    )
    if not isinstance(resultado.final_output, RespostaFinal):
        raise ValueError('Saída final não corresponde ao esquema esperado.')
    if estado.predicao is None or estado.protocolos is None:
        raise ValueError('Handoffs/tools não concluíram o fluxo.')
    validar_resposta(resultado.final_output, caso, estado.predicao)
    historico = resultado.to_input_list()
    return resultado.final_output, historico
