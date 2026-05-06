import re
from app.database import get_db

def normalize_text(text):
    if not text:
        return ""
    # Lowercase and remove extra spaces
    return re.sub(r'\s+', ' ', text.lower().strip())

def search_text(date: str = None, query: str = None):
    if not query:
        return []
        
    db = get_db()
    cursor = db.cursor()
    
    sql = '''
        SELECT e.edition_date, e.pdf_path, p.page_number, p.text
        FROM pages p
        JOIN editions e ON p.edition_id = e.id
    '''
    params = []
    
    if date:
        sql += ' WHERE e.edition_date = ?'
        params.append(date)
        
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    db.close()
    
    results = []
    normalized_query = normalize_text(query)
    context_length = 450
    
    for row in rows:
        text = row['text']
        normalized_page_text = normalize_text(text)
        
        if normalized_query in normalized_page_text:
            idx = normalized_page_text.find(normalized_query)
            start = max(0, idx - context_length)
            end = min(len(normalized_page_text), idx + len(normalized_query) + context_length)
            fragment = normalized_page_text[start:end]
            
            results.append({
                "data_edicao": row['edition_date'],
                "pagina": row['page_number'],
                "termo_pesquisado": query,
                "fragmento_contexto": "..." + fragment + "...",
                "caminho_local_pdf": row['pdf_path']
            })
            
    return results
