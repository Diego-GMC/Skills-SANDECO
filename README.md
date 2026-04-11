# Skills SANDECO

Repositório central para as skills (habilidades) desenvolvidas para o ecossistema do agente BMad no projeto Extrator de Tabelas.

## 🛠 Skills Disponíveis

### 1. `chat-csv-autos`
Permite que o usuário consulte uma base de autos em CSV utilizando linguagem natural. O agente é capaz de realizar contagens, listar processos únicos e extrair frequências dos dados.

**Campos Suportados para Pergunta:**
- `assunto_completo`
- `nr_objeto_tramitacao`
- `area_atuacao`

#### Pré-requisitos e Execução
A skill assume que existe uma base de dados local na raiz do projeto (como `base_de_dados/autos.csv`) que **não deve ser enviada para o repositório** por questões de sigilo/tamanho (ela já está ignorada no `.gitignore`).

Para rodar essa skill, certifique-se de instalar as dependências de Python listadas no `requirements.txt`.

### 2. `plot-bar-chart`
Gera e exibe na tela do usuário um **gráfico de barras interativo** a partir de dados sumarizados. É normalmente utilizada em conjunto com a skill `chat-csv-autos`: primeiro o agente consulta a base e consolida os números; depois a skill `plot-bar-chart` renderiza o resultado visualmente.

**Principais características:**
- Recebe um payload JSON com `labels` (rótulos) e `values` (valores numéricos) de mesmo tamanho.
- Consolida automaticamente categorias excedentes: quando há mais de 8 categorias, as excedentes são agrupadas sob o rótulo **"Outros"**.
- Exibe os valores numéricos sobre cada barra para leitura rápida.
- Abre uma janela interativa do Matplotlib diretamente na tela do usuário.

**Exemplo de payload:**
```json
{
  "title": "Top 10 Assuntos",
  "labels": ["Assunto A", "Assunto B", "Assunto C"],
  "values": [35, 12, 10],
  "xlabel": "Assuntos",
  "ylabel": "Quantidade"
}
```

**Dependência adicional:** `matplotlib` (já listada no `requirements.txt`).

---

## 🚀 Instalação (Uso Local)

1. Clone esse repositório:
   ```bash
   git clone https://github.com/Diego-GMC/Skills-SANDECO.git
   ```
2. Instale as dependências da skill (a principal é o Pandas):
   ```bash
   pip install -r requirements.txt
   ```
3. Garanta que o arquivo CSV (`autos.csv`) com a base esteja acessível conforme definido pela rotina de extração da skill.

## 🤝 Como Contribuir
Se for criar uma nova skill, coloque as instruções e o contrato na sintaxe Markdown (`SKILL.md`) acompanhado dos scripts da execução. Mantenha os novos pacotes listados no `requirements.txt`.
