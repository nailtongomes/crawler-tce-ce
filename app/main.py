from app.database import get_db
import logging
from fastapi import FastAPI, Query
from contextlib import asynccontextmanager

from app.collector import collect_editions
from app.search import search_text
from app.database import init_db

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    init_db()
    
    yield
    # Shutdown
    logger.info("Application shutdown.")

app = FastAPI(title="TCE-CE Diário Monitor", lifespan=lifespan)

@app.get("/buscar")
def buscar(data: str = Query(None, description="Data no formato YYYY-MM-DD"),
           q: str = Query(..., description="Termo para pesquisar")):
    results = search_text(date=data, query=q)
    return {"resultados": results}

@app.post("/coletar")
def coletar():
    try:
        collect_editions()
        return {"status": "sucesso", "mensagem": "Coleta executada com sucesso."}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@app.get("/diarios")
def listar_diarios():
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT id, edition_date, edition_number, pdf_path, downloaded_at 
        FROM editions 
        ORDER BY id DESC
    ''')
    rows = cursor.fetchall()
    db.close()
    
    return {"diarios": [dict(row) for row in rows]}

