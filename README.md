# CardioIA — Fase 6 | Sistema Preditivo Multiagente

Projeto educacional FIAP: classificação supervisionada de `pico_risco` a partir de dados sintéticos e orquestração de quatro agentes com OpenAI Agents SDK.

> **Não é um dispositivo médico.** A variável-alvo é artificial e mistura sinais fisiológicos e variáveis operacionais. Resultados não devem orientar decisões clínicas reais.

## Integrantes
- **Integrante 1:** [NOME COMPLETO] — RM: [RM]
- **Integrante 2:** [NOME COMPLETO] — RM: [RM]
- **Integrante 3:** [NOME COMPLETO] — RM: [RM]
- **Integrante 4:** [NOME COMPLETO] — RM: [RM]
- **Integrante 5 (se houver):** [NOME COMPLETO] — RM: [RM]

## Arquitetura
Orquestrador → **handoff** → Analista de Risco (`consultar_modelo`) → **handoff** → Especialista em Protocolos (`consultar_protocolos`) → **handoff** → Planejador de Resposta (`consultar_resultados`) → `RespostaFinal` validada.

As tools consultam funções determinísticas. O estado compartilhado (`Estado`) mantém caso, predição e protocolos; `Runner.run` registra o histórico. Pydantic valida as entradas e a saída, e `validar_resposta` compara a resposta final com os resultados calculados.

## Execução
1. Abra `CardioIA_Fase6_Modelo_Preditivo.ipynb` no Colab e execute todas as células.
2. Baixe `artefatos/modelo_risco.joblib` e `artefatos/colunas_modelo.json` produzidos no Colab e coloque-os na pasta `artefatos/` deste projeto. **Não execute o sistema sem esses arquivos.**
3. Crie um ambiente Python 3.10+ e instale `pip install -r requirements.txt`.
4. Configure `OPENAI_API_KEY` no ambiente. Nunca publique a chave no GitHub. O SDK poderá usar seu modelo padrão; confirme modelo e custos na sua conta.
5. Execute `python main.py` ou `python main.py exemplo_caso.json`.
6. Execute testes locais com `python -m pytest -q` (não exigem API nem modelo treinado).

### Windows PowerShell
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:OPENAI_API_KEY="SUA_CHAVE"
python -m pytest -q
python main.py
```

## Estrutura
- `src/core.py`: validação, carregamento do classificador e protocolos.
- `src/multiagente.py`: agentes, tools, handoffs, contexto e validação final.
- `main.py`: execução e exportação do histórico.
- `tests/test_core.py`: testes de regras e validação.
- `exemplo_caso.json`: caso fornecido no enunciado (com nome da coluna corrigido).
- `CardioIA_Fase6_Modelo_Preditivo.ipynb`: treinamento, comparação e avaliação.
- `artefatos/`: arquivos de modelo gerados pelo notebook.

## Exemplo do caso
Para carga 92%, SpO₂ 89%, recursos 25%, densidade de eventos 7 e classe prevista ALTO, são aplicáveis: abrir unidades temporárias, redistribuir insumos, ativar plano de contingência e ativar estado de emergência. **SpO₂ 89% não satisfaz o protocolo SpO₂ < 88%.** A probabilidade deve ser calculada pelo modelo, não fixada neste README.

## Limitações
Base sintética com alvo criado por limiares, possível superestimação de desempenho e ausência de validação clínica externa. Regras e predições são separadas para evitar protocolos inventados. Recomenda-se avaliar calibração, dados externos e revisão especializada antes de qualquer pesquisa aplicada à saúde.

## Evidências e documentação
- `documentacao/Relatorio_Tecnico_CardioIA_Fase6.pdf`: relatório técnico (até 2 páginas).
- `documentacao/Arquitetura_Multiagente_CardioIA_Fase6.pdf`: arquitetura, tools, handoffs e execução (até 3 páginas).
- `artefatos/historico_execucao.json`: histórico real de uma execução bem-sucedida.
- `artefatos/comparacao_modelos.csv`: comparação por validação cruzada.
- `artefatos/matriz_confusao.png`, `curva_roc.png`, `distribuicao_alvo.png`: gráficos do notebook.
- `ROTEIRO_VIDEO.md`: roteiro cronometrado para apresentação.

**Atenção:** o histórico demonstra um caso bem-sucedido, não garante comportamento em todas as entradas. O arquivo `.joblib` e `colunas_modelo.json` precisam ser gerados no notebook e colocados em `artefatos/` antes de rodar `main.py`.

## Vídeo demonstrativo (até 4 min)
**Link:** PREENCHER_APOS_PUBLICAR_NO_YOUTUBE_NAO_LISTADO

## Entrega
Repositório GitHub **privado** e compartilhado com `fiap-tutoria`; enviar no portal somente `.txt` com URL do repositório e URL do vídeo não listado. Adequar a estrutura ao template oficial da coordenação.

## Checklist antes do envio
- [ ] Confirmar estrutura com o template oficial da coordenação.
- [ ] Preencher nomes e RMs acima.
- [ ] Incluir `modelo_risco.joblib` e `colunas_modelo.json` em `artefatos/` (se permitidos pelo template).
- [ ] Executar notebook e `python -m pytest -q` e `python main.py` no ambiente final.
- [ ] Gravar e publicar vídeo como **não listado**, inserir URL no README e ENTREGA.txt.
- [ ] Criar repositório **privado**, convidar `fiap-tutoria` e confirmar acesso.
- [ ] Enviar somente `ENTREGA.txt` no Portal do Aluno.

**Nunca publique** `.env`, chaves da API, `.venv/` ou dados reais de pacientes.
