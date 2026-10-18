import pytest
from pydantic import ValidationError
from src.core import Caso, Predicao, RespostaFinal, selecionar_protocolos, validar_resposta

BASE = dict(idade_media=62,carga_sistema=92,tempo_espera=75,fc_media=118,
            spo2_media=89,pa_sistolica=100,temperatura=37.5,densidade_eventos=7,
            eventos_24h=5,disponibilidade_recursos=25)

def test_protocolos_limites_e_alto():
    caso = Caso(**BASE)
    p = Predicao(probabilidade=.9,classificacao='ALTO',classe_prevista=1)
    regras = selecionar_protocolos(caso,p)
    assert len(regras) == 4
    assert not any('SPO2 < 88%' in r for r in regras)
    assert not any('eventos_24h > 5' in r for r in regras)

def test_sem_protocolos_em_caso_baixo():
    caso = Caso(**(BASE | dict(carga_sistema=40,densidade_eventos=1,disponibilidade_recursos=80)))
    p = Predicao(probabilidade=.1,classificacao='BAIXO',classe_prevista=0)
    assert selecionar_protocolos(caso,p) == []

def test_rejeita_protocolo_inventado():
    caso = Caso(**BASE)
    p = Predicao(probabilidade=.9,classificacao='ALTO',classe_prevista=1)
    r = RespostaFinal(probabilidade=.9,classificacao='ALTO',protocolos=['inexistente'],justificativa='teste',observacao='simulado')
    with pytest.raises(ValueError):
        validar_resposta(r,caso,p)

def test_rejeita_coluna_errada():
    with pytest.raises(ValidationError):
        Caso(**(BASE | {'disponibilidade recursos':25}))
