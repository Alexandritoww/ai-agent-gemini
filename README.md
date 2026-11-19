# AI Research & Data Agent (LangChain + Gemini)

Agente de inteligencia artificial conversacional desarrollado en Python con **LangChain** y **Google Gemini (`gemini-3.8-flash`)**. Combina memoria de sesión con herramientas personalizadas para consultar bases de datos **MySQL**, inspeccionar archivos **CSV**, investigar en **Wikipedia** y la web, y exportar reportes estructurados con **Pydantic**.

## Características principales

* **Memoria conversacional:** Mantiene el contexto de la conversación entre turnos mediante `HumanMessage` y `AIMessage`.
* **Salida estructurada:** Formatea las respuestas bajo el esquema `ResearchResponse` (`topic`, `summary`, `sources`, `tools_used`).
* **Tolerancia a fallos:** Incluye reintentos automáticos ante saturación temporal de la API (`max_retries=3`) y respaldo en búsquedas web.

## Herramientas integradas (`tools.py`)

| Herramienta | Función | Descripción |
| :--- | :--- | :--- |
| `query_mysql` | `query_mysql()` | Ejecuta consultas de solo lectura (`SELECT`, `SHOW`, `DESCRIBE`) en MySQL con bloqueo de escritura/borrado. |
| `analyze_csv` | `analyze_csv()` | Lee archivos `.csv` locales y extrae número de registros, columnas y una muestra de filas. |
| `search` | `safe_search()` | Realiza búsquedas web mediante DuckDuckGo (`backend="lite"`). |
| `wikipedia` | `WikipediaQueryRun` | Consulta resúmenes de artículos directamente en Wikipedia. |
| `save_text_to_file` | `save_to_txt()` | Guarda los resultados estructurados con marca de tiempo en `research_output.txt`. |

## Estructura del proyecto

```text
ai-agent-gemini/
├── main.py              # Configuración del agente, esquema Pydantic y bucle de chat con memoria
├── tools.py             # Definición de las 5 herramientas (MySQL, CSV, Web, Wikipedia, TXT)
├── requirements.txt     # Dependencias del proyecto
├── .env.example         # Plantilla de variables de entorno
└── .gitignore           # Exclusión de credenciales (.env), entorno virtual y archivos generados
```

## Instalación y configuración

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/Alexandritoww/ai-agent-gemini.git](https://github.com/Alexandritoww/ai-agent-gemini.git)
   cd ai-agent-gemini
   ```

2. **Crear y activar el entorno virtual:**
   ```bash
   python -m venv venv
   ```
   * **Windows (PowerShell):** `.\venv\Scripts\activate`
   * **Linux / macOS:** `source ./venv/bin/activate`

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   Crea un archivo `.env` en la raíz del proyecto (puedes basarte en `.env.example`) con tu clave de Google AI Studio y las credenciales de tu servidor MySQL:
   ```env
   GOOGLE_API_KEY="tu_api_key_de_gemini"

   MYSQL_HOST="localhost"
   MYSQL_PORT="3306"
   MYSQL_USER="root"
   MYSQL_PASSWORD=""
   MYSQL_DATABASE="ai_agent"
   ```

## Uso

Ejecuta el agente desde la terminal con el entorno virtual activo:

```bash
python main.py
```

### Ejemplos de consultas
* **Base de datos MySQL:** *"¿Qué tablas existen en la base de datos y qué columnas tiene cada una?"*
* **Análisis de datos locales:** *"Analiza el archivo ventas.csv y dime cuántas filas y columnas tiene"*
* **Investigación y exportación:** *"Investiga qué es XGBoost en Wikipedia y guarda un resumen en un archivo"*
* **Finalizar sesión:** Escribe `salir` en el chat.
