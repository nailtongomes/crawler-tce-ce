# TCE-CE Diário Monitor

Sistema para monitorar, baixar e buscar no Diário Oficial do TCE-CE de forma local, sem uso de API externa.

## Tecnologias

- Python 3.11
- FastAPI
- SQLite
- Docker e Docker Compose
- BeautifulSoup (Coleta)
- PyMuPDF (Extração de texto)
- APScheduler (Agendamento)

## Executando com Docker

1. Clone o repositório ou acesse a pasta do projeto.
2. Execute o comando:

```bash
docker compose up --build -d
```

O sistema ficará disponível em `http://localhost:8000`.

## Endpoints

### `GET /buscar?data=YYYY-MM-DD&q=texto`

Busca por termos no banco de dados local (arquivos PDF já processados).

**Parâmetros:**
- `data` (opcional): Filtra pela data da edição (formato YYYY-MM-DD).
- `q` (obrigatório): O termo de pesquisa.

**Exemplo de uso:**
```bash
curl "http://localhost:8000/buscar?q=licitação"
```

## Executando Localmente (Sem Docker)

1. Crie um ambiente virtual e instale as dependências:
```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
```

2. Para rodar a API:
```bash
uvicorn app.main:app --reload
```

3. Para executar a coleta manual:
```bash
python -m app.collector
```

## Funcionamento

- A aplicação realiza a coleta diária (agendada via APScheduler) do site do TCE-CE.
- Os PDFs são baixados para a pasta `/data/pdfs`.
- Os textos de cada página do PDF são extraídos e armazenados no banco SQLite em `/data/diario.db`.
- A API `/buscar` lê as informações no banco de dados, com normalização de texto (minúsculas e remoção de espaços extras) para melhorar as buscas.
