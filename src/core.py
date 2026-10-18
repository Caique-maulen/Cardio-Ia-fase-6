"""Camada determinística: predição, validação e protocolos sintéticos."""
from pathlib import Path
import json
import math
import joblib
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parents[1]
ARTEFATOS = ROOT / 'artefatos'
COLUNAS = ['idade_media','carga_sistema','tempo_espera','fc_media','spo2_media',
           'pa_sistolica','temperatura','densidade_eventos','eventos_24h','disponibilidade_recursos']

class Caso(BaseModel):
    model_config = ConfigDict(extra='forbid')
    idade_media: float = Field(ge=18, le=90)
    carga_sistema: float = Field(ge=0, le=100)
    tempo_espera: float = Field(ge=0)
    fc_media: float = Field(gt=0)
    spo2_media: float = Field(ge=0, le=100)
    pa_sistolica: float = Field(gt=0)
    temperatura: float = Field(ge=0, le=50)
    densidade_eventos: int = Field(ge=0)
    eventos_24h: int = Field(ge=0)
    disponibilidade_recursos: float = Field(ge=0, le=100)

class Predicao(BaseModel):
    probabilidade: float = Field(ge=0, le=1)
    classificacao: str
    classe_prevista: int = Field(ge=0, le=1)

class RespostaFinal(BaseModel):
    probabilidade: float = Field(ge=0, le=1)
    classificacao: str
    protocolos: list[str]
    justificativa: str
    observacao: str

def prever(caso: Caso) -> Predicao:
    modelo_path = ARTEFATOS / 'modelo_risco.joblib'
    colunas_path = ARTEFATOS / 'colunas_modelo.json'
    if not modelo_path.exists() or not colunas_path.exists():
        raise FileNotFoundError('Execute o notebook e copie modelo_risco.joblib e colunas_modelo.json para artefatos/.')
    colunas = json.loads(colunas_path.read_text(encoding='utf-8'))
    if colunas != COLUNAS:
        raise ValueError('As colunas salvas não correspondem ao esquema esperado.')
    modelo = joblib.load(modelo_path)  # carregar somente artefatos próprios confiáveis
    dados = pd.DataFrame([caso.model_dump()])[colunas]
    prob = float(modelo.predict_proba(dados)[0, 1])
    classe = int(modelo.predict(dados)[0])
    if not math.isfinite(prob):
        raise ValueError('Probabilidade inválida.')
    return Predicao(probabilidade=prob, classificacao='ALTO' if classe == 1 else 'BAIXO', classe_prevista=classe)

REGRAS = [
    ('spo2_media', '<', 88, 'Se SPO2 < 88% → iniciar suporte respiratório imediato'),
    ('carga_sistema', '>', 85, 'Se carga do sistema > 85% → abrir unidades temporárias'),
    ('fc_media', '>', 120, 'Se FC > 120 → iniciar monitoramento intensivo'),
    ('eventos_24h', '>', 5, 'Se eventos_24h > 5 → ativar equipe de resposta rápida'),
    ('disponibilidade_recursos', '<', 30, 'Se disponibilidade_recursos < 30% → redistribuir insumos'),
    ('tempo_espera', '>', 90, 'Se tempo_espera > 90 min → priorizar triagem emergencial'),
    ('temperatura', '>', 38, 'Se temperatura > 38°C média → iniciar protocolo infeccioso'),
    ('densidade_eventos', '>', 6, 'Se densidade_eventos > 6 → ativar plano de contingência'),
    ('pa_sistolica', '<', 90, 'Se PA sistólica < 90 → iniciar protocolo de choque'),
]
PROTOCOLO_ALTO = 'Se risco sistêmico alto → ativar estado de emergência'

def selecionar_protocolos(caso: Caso, predicao: Predicao) -> list[str]:
    dados = caso.model_dump()
    resultado = [texto for campo, op, limite, texto in REGRAS
                 if (dados[campo] < limite if op == '<' else dados[campo] > limite)]
    if predicao.classe_prevista == 1:
        resultado.append(PROTOCOLO_ALTO)
    return resultado

def validar_resposta(resposta: RespostaFinal, caso: Caso, predicao: Predicao) -> None:
    esperados = selecionar_protocolos(caso, predicao)
    if abs(resposta.probabilidade - predicao.probabilidade) > 1e-6:
        raise ValueError('A resposta alterou a probabilidade do modelo.')
    if resposta.classificacao != predicao.classificacao:
        raise ValueError('Classificação inconsistente.')
    if len(resposta.protocolos) != len(set(resposta.protocolos)) or set(resposta.protocolos) != set(esperados):
        raise ValueError('Protocolos inventados, omitidos ou duplicados.')
