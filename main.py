"""Execução: python main.py [caminho_para_caso.json]"""
import asyncio
import json
import sys
from pathlib import Path
from src.core import Caso
from src.multiagente import executar

async def main():
    caminho = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('exemplo_caso.json')
    caso = Caso.model_validate_json(caminho.read_text(encoding='utf-8'))
    resposta, historico = await executar(caso)
    print(resposta.model_dump_json(indent=2))
    Path('artefatos').mkdir(exist_ok=True)
    Path('artefatos/historico_execucao.json').write_text(json.dumps(historico, indent=2, ensure_ascii=False, default=str), encoding='utf-8')
    print('\nHistórico salvo em artefatos/historico_execucao.json')

if __name__ == '__main__':
    asyncio.run(main())
