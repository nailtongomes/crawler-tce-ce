import logging
import os
import hashlib
import re
from datetime import datetime
import time
from seleniumbase import SB
from app.settings import PDF_DIR
from app.database import get_db
from app.parser import extract_text_from_pdf

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://doe-consulta.tce.ce.gov.br/doeconsulta/paginas/consulta-textual-ou-data-edicao-do.xhtml"

def calculate_hash(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def collect_editions():
    logger.info("Starting collection of TCE-CE Diário Oficial using SeleniumBase...")
    
    temp_download_dir = os.path.join(PDF_DIR, "tmp_dl")
    os.makedirs(temp_download_dir, exist_ok=True)
    
    # Limpa a pasta temporária de arquivos antigos
    for f in os.listdir(temp_download_dir):
        os.remove(os.path.join(temp_download_dir, f))
    
    try:
        # Use Chrome
        with SB(headless=True, browser="chrome", disable_csp=True) as sb:
            # We explicitly configure the download behavior
            sb.driver.execute_cdp_cmd("Page.setDownloadBehavior", {
                "behavior": "allow",
                "downloadPath": temp_download_dir
            })
            
            sb.open(BASE_URL)
            sb.sleep(2)
            
            selector = 'input[name^="formUltimasEdicoes:consultaAvancadaDataTable:"][title="Visualizar Edição."]'
            elements = sb.find_elements(selector)
            logger.info(f"Found {len(elements)} edition buttons.")
            
            for index in range(len(elements)):
                current_selector = f'input[name^="formUltimasEdicoes:consultaAvancadaDataTable:{index}:"][title="Visualizar Edição."]'
                if sb.is_element_visible(current_selector):
                    logger.info(f"Clicking download button {index}...")
                    sb.click(current_selector)
                    
                    downloaded_file = None
                    for _ in range(30):
                        sb.sleep(1)
                        files = os.listdir(temp_download_dir)
                        pdf_files = [f for f in files if f.endswith('.pdf')]
                        if pdf_files:
                            cr_files = [f for f in files if f.endswith('.crdownload') or f.endswith('.tmp')]
                            if not cr_files:
                                downloaded_file = os.path.join(temp_download_dir, pdf_files[0])
                                break
                    
                    if downloaded_file:
                        logger.info(f"Downloaded file: {downloaded_file}")
                        process_downloaded_file(downloaded_file)
                    else:
                        logger.error(f"Download {index} timed out or failed.")
                        
                    # Limpar pasta de download
                    for f in os.listdir(temp_download_dir):
                        try:
                            os.remove(os.path.join(temp_download_dir, f))
                        except Exception:
                            pass
                else:
                    logger.warning(f"Button {index} not found.")
                    
    except Exception as e:
        logger.error(f"Error during collection: {e}")
        
def process_downloaded_file(temp_filepath):
    filename = os.path.basename(temp_filepath)
    edition_date = datetime.now().strftime("%Y-%m-%d")
    edition_number = ""
    
    m = re.search(r'(?:Edicao|Edi[cç][ãa]o)[_\s]*(\d+)', filename, re.IGNORECASE)
    if m:
        edition_number = m.group(1)
        
    final_filepath = os.path.join(PDF_DIR, filename)
    
    file_hash = calculate_hash(temp_filepath)
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM editions WHERE pdf_hash = ?", (file_hash,))
    existing = cursor.fetchone()
    
    if existing:
        logger.info("PDF already exists in the database. Skipping extraction.")
        db.close()
        return
        
    if os.path.exists(final_filepath):
        logger.info(f"File {final_filepath} already exists locally but not in DB. Overwriting.")
        os.remove(final_filepath)
        
    # Copy from temp to final so we can keep the temp dir clean
    import shutil
    shutil.copy2(temp_filepath, final_filepath)
    logger.info(f"Saved new PDF: {final_filepath}")
    
    pdf_link = BASE_URL
    
    cursor.execute('''
        INSERT INTO editions (edition_date, edition_number, pdf_url, pdf_path, pdf_hash)
        VALUES (?, ?, ?, ?, ?)
    ''', (edition_date, edition_number, pdf_link, final_filepath, file_hash))
    edition_id = cursor.lastrowid
    db.commit()
    
    logger.info("Extracting text from PDF...")
    pages = extract_text_from_pdf(final_filepath)
    
    for page in pages:
        cursor.execute('''
            INSERT INTO pages (edition_id, page_number, text)
            VALUES (?, ?, ?)
        ''', (edition_id, page["page_number"], page["text"]))
        
    db.commit()
    db.close()
    logger.info("Extraction and saving complete.")

if __name__ == "__main__":
    collect_editions()
