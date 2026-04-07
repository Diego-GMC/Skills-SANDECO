---
name: plot-bar-chart
description: Gera e exibe na tela um gráfico de barras a partir de dados sumarizados (normalmente derivados de outras consultas).
argument-hint: "[dados em contexto para o gráfico]"
---

# plot-bar-chart: Bar Chart Generator

## Overview
Esta skill processa pares de dados (rótulos e valores) presentes no contexto atual da conversa (geralmente gerados pela skill `chat-csv-autos`) e plota um gráfico de barras que será exibido e aberto diretamente na tela do usuário.

## On Activation

1. **Analise o Contexto:** Identifique na memória da conversa os dados numéricos consolidados que o usuário deseja visualizar. (ex: lista top 10 assuntos).
2. **Extraia Rótulos e Valores:** Extraia os textos (como "labels") e as quantidades (como "values").
3. **Gere o Payload JSON:** Crie a estrutura exata conforme o contrato abaixo.

   ```json
   {
     "title": "Gráfico gerado pelo Assistente",
     "labels": ["Dado A", "Dado B", "Dado C"],
     "values": [35, 12, 10],
     "xlabel": "Categorias",
     "ylabel": "Quantidades Consolidadas"
   }
   ```
   *Nota:* Mantenha os arrays `labels` e `values` com o mesmo tamanho. Escolha títulos descritivos lendo o contexto.

4. **Grave o Payload:** Salve localmente como `payload_chart_<UUID>.json`. 
5. **Execute a Plotagem:** Chame o script para abrir a janela interativa:
   `python .agent/skills/plot-bar-chart/scripts/plot.py payload_chart_<UUID>.json`
6. **Limpeza:** Emita o comando para deletar o arquivo temporário `payload_chart_<UUID>.json`.
7. **Resposta:** Formule uma frase natural avisando o usuário de que o gráfico foi renderizado e está aberto em uma nova janela na tela dele.
