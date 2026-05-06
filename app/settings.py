import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = os.environ.get("DATA_DIR", str(BASE_DIR / "data"))
PDF_DIR = os.path.join(DATA_DIR, "pdfs")
DB_PATH = os.path.join(DATA_DIR, "diario.db")

os.makedirs(PDF_DIR, exist_ok=True)
