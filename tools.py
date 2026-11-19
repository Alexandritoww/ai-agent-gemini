import csv
import os
from datetime import datetime
import mysql.connector
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper, DuckDuckGoSearchAPIWrapper
from langchain_core.tools import Tool


def save_to_txt(data: str, filename: str = "research_output.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"--- Research Output ---\nTimestamp: {timestamp}\n\n{data}\n\n"

    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)
    
    return f"Data successfully saved to {filename}"

save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description="Saves structured research data to a text file.",
)


ddg_wrapper = DuckDuckGoSearchAPIWrapper(backend="lite")
search = DuckDuckGoSearchRun(api_wrapper=ddg_wrapper)

def safe_search(query: str) -> str:
    try:
        return search.run(query)
    except Exception as e:
        return f"Search unavailable ({e}). Rely on Wikipedia results or your own knowledge."

search_tool = Tool(
    name="search",
    func=safe_search,
    description="Search the web for information",
)


api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=500)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

def analyze_csv(filepath: str) -> str:
    clean_path = filepath.strip().strip('"').strip("'")
    if not os.path.exists(clean_path):
        return f"Error: El archivo '{clean_path}' no existe en la carpeta del proyecto."
    try:
        with open(clean_path, mode="r", encoding="utf-8-sig") as f:
            reader = list(csv.reader(f))
        if not reader:
            return "El archivo CSV está vacío."
        
        headers = reader[0]
        rows = reader[1:]
        sample = rows[:5]
        return (
            f"Archivo: {clean_path}\n"
            f"Total de registros: {len(rows)}\n"
            f"Columnas ({len(headers)}): {', '.join(headers)}\n"
            f"Primeras 5 filas: {sample}"
        )
    except Exception as e:
        return f"Error leyendo el CSV: {e}"

csv_tool = Tool(
    name="analyze_csv",
    func=analyze_csv,
    description="Reads a local CSV file path (e.g., 'datos.csv') and returns its columns, row count, and sample rows.",
)


def query_mysql(sql_query: str) -> str:
    clean_query = sql_query.strip().rstrip(";")
    upper_query = clean_query.upper()

    if not (upper_query.startswith("SELECT") or upper_query.startswith("SHOW") or upper_query.startswith("DESCRIBE")):
        return "Error de seguridad: Solo se permiten consultas de lectura (SELECT, SHOW, DESCRIBE)."

    try:
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE")
        )
        cursor = conn.cursor()
        cursor.execute(clean_query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        cursor.close()
        conn.close()

        if not rows:
            return "La consulta no devolvió resultados."

        limited_rows = rows[:50]
        return f"Columnas: {columns}\nTotal filas: {len(rows)} (mostrando {len(limited_rows)}):\n{limited_rows}"
    except Exception as e:
        return f"Error de conexión o consulta MySQL: {e}"

mysql_tool = Tool(
    name="query_mysql",
    func=query_mysql,
    description="Executes read-only SQL queries (SELECT, SHOW TABLES, DESCRIBE table) against the local MySQL database.",
)