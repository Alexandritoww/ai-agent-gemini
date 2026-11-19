from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool, csv_tool, mysql_tool

load_dotenv()

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", max_retries=3)
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a research and data assistant.
            Answer the user query, use the conversation history for context, and call the necessary tools.
            Wrap the final output in this format and provide no other text\n{format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [search_tool, wiki_tool, save_tool, csv_tool, mysql_tool]
agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

chat_history = []
print("Agente listo con memoria. Escribe 'salir' para terminar.")

while True:
    query = input("\nTú: ")
    if query.strip().lower() in ["salir", "exit", "quit"]:
        print("Sesión finalizada.")
        break
    if not query.strip():
        continue

    try:
        raw_response = agent_executor.invoke({
            "query": query,
            "chat_history": chat_history
        })
    except Exception as e:
        print(f"\nServidor ocupado o error temporal de Gemini, intenta de nuevo: {e}")
        continue

    output = raw_response.get("output")
    text_output = output[0]["text"] if isinstance(output, list) else output

    chat_history.append(HumanMessage(content=query))
    chat_history.append(AIMessage(content=text_output))

    try:
        structured = parser.parse(text_output)
        print(f"\nTema: {structured.topic}")
        print(f"Resumen: {structured.summary}")
        print(f"Fuentes: {', '.join(structured.sources)}")
        print(f"Herramientas usadas: {', '.join(structured.tools_used)}")
    except Exception:
        print("\nRespuesta:", text_output)