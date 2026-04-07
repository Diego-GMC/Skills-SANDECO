---
name: chat-csv-autos
description: Permite consultar a base de autos (CSV) via linguagem natural. útil para contagens, listagens e frequencias.
argument-hint: "[pergunta em linguagem natural]"
---

# chat-csv-autos: CSV Query Skill

## Overview

Esta skill recebe uma pergunta em texto livre sobre a base de autos, converte a intenção numa query estruturada e executa um script Python (Pandas) para processar o CSV estático (`base_de_dados/autos.csv`), retornando o resultado.
Campos suportados: `assunto_completo`, `nr_objeto_tramitacao`, e `area_atuacao`.

## On Activation

1. **Analise a Pergunta:** Determine a ação desejada:
   - `COUNT`: Contar quantidade de registros baseados em filtros.
   - `LIST` / `DISTINCT`: Listar ou extrair registros únicos baseados em filtros.
   - `FREQ`: Agrupamento simplificado restrito a um ÚNICO campo por vez (`assunto_completo` ou `area_atuacao`). Retorna no máximo o Top 10 itens para rankings.

2. **Gere o Payload JSON:** Monte o payload respeitando o contrato abaixo. `filters` é **sempre um dicionário** `{"campo": "valor"}`, NUNCA uma lista de objetos.

   ```json
   // COUNT
   { "action": "COUNT", "filters": { "assunto_completo": "<valor>" } }

   // LIST ou DISTINCT (retorna até 50 registros)
   { "action": "LIST", "filters": { "area_atuacao": "<valor>" } }

   // FREQ — sem filters; usa "target" para indicar o campo de agrupamento
   { "action": "FREQ", "filters": {}, "target": "assunto_completo" }
   ```
   Campos válidos em `filters` e `target`: `assunto_completo`, `nr_objeto_tramitacao`, `area_atuacao`.
   `filters` pode ser `{}` quando não há filtro (ex.: FREQ global).

3. **Grave o Payload:** Salve o JSON gerado em um arquivo temporário único chamado `payload_<UUID_UNICO>.json`. Este passo é crucial para evitar problemas de concorrência. Coloque este arquivo na subpasta da skill (ou uma pasta de temp).

4. **Execute a Busca do CSV:** Chame o script de execução interativo (no BMad) via CLI executando:
   `python .agent/skills/chat-csv-autos/scripts/query_csv.py payload_<UUID_UNICO>.json`
   *Nota:* Aplique flag de *timeout* (ex. 10s) na chamada do SO se disponível.

5. **Interprete e Formate o Sucesso ou Erro:**
   O script Python retornará APENAS um Log JSON limpo.
   - Se `ok: true`, pegue o resultado e formule uma frase amigável com a resposta.
   - Se `ok: false`, um `error_type` estará presente (ex: `AMBIGUOUS_FILTER`, `TOO_BROAD`, `UNSUPPORTED_FIELD`, `IO_ERROR`, `NO_MATCH`). Formate o erro de forma clara sem falar termos técnicos difíceis para o usuário.

6. **Cleaning Up:**
   Emita um comando no SO para remover o `payload_<UUID_UNICO>.json` como passo de higienização.
