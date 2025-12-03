import json
import numpy as np
import warnings
from typing import Annotated
from dotenv import load_dotenv, find_dotenv
from typing_extensions import TypedDict
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import START, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.graph.message import add_messages
from visualizer import visualize

# Potlačit pydantic warnings (ale LangSmith tracking zůstává aktivní)
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

_ = load_dotenv(find_dotenv())  # read local .env file

# ---------------------------
# Define the graph
# ---------------------------

# State
class State(TypedDict):
    messages: Annotated[list, add_messages]
    question: str  
    query: str     
    docs: list     
    answer: str    

# Model
llm = ChatOpenAI(model="gpt-4o-mini")

def AnswerNode(state: State, config: RunnableConfig):
    messages = [
        SystemMessage(
            "Jsi zkušený aromaterapeut a expert na přírodní medicínu s mnohaletou praxí. "
            "Odpovídej přátelsky, ale profesionálně - jako by ses bavil s klientem při konzultaci. "
            "\n\n"
            "DŮLEŽITÉ POKYNY:\n"
            "1. Odpovídej POUZE na základě poskytnutého kontextu z databáze\n"
            "2. Odpovídej STEJNÝM JAZYKEM jako otázka uživatele (čeština/slovenština)\n"
            "3. Používej přirozený, vstřícný tón - ne jako databáze, ale jako expert který radí\n"
            "4. VŽDY doporuč KOMBINACI esenciálních olejů A bylinných přípravků (čaje, tinktury, atd.)\n"
            "5. Pro každé doporučení uveď:\n"
            "   - Konkrétní názvy (esenciální oleje + bylinky)\n"
            "   - Jak je používat (inhalace, masáž, difuzér, čaj, tinktura)\n"
            "   - Případná upozornění\n"
            "6. Struktura odpovědi:\n"
            "   - Nejdřív esenciální oleje (pokud jsou v kontextu)\n"
            "   - Pak bylinné alternativy/doplňky (pokud jsou v kontextu)\n"
            "7. Nepiš to jako seznam z databáze, ale jako radu od zkušeného terapeuta"
        ),
        HumanMessage(
            f"Klient se ptá: {state['question']}\n\n"
            f"Máš k dispozici tyto informace:\n{state['docs']}\n\n"
            f"Doporuč KOMBINACI esenciálních olejů i bylinných přípravků, pokud jsou dostupné:"
        ),
    ]
    response = llm.invoke(messages)
    return {"answer": response.content}


# RAG - Načte data
with open("chunked_data_with_embeddings.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    chunks = data["chunks"]

def search_similar_chunks(query_embedding, top_k=5):
    """
    Najde top_k nejpodobnějších chunků s prioritou pro esenciální oleje.
    Vrací 50% z olejů a 50% z ostatních zdrojů.
    """
    similarities = []
    for chunk in chunks:
        chunk_embedding = np.array(chunk["embedding"])
        similarity = cosine_similarity(
            [query_embedding],
            [chunk_embedding]
        )[0][0]
        similarities.append((chunk, similarity))

    # Seřadí podle similarity
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Rozdělí na oleje a ostatní
    oil_chunks = [(chunk, score) for chunk, score in similarities if chunk.get('type') == 'essential_oil']
    other_chunks = [(chunk, score) for chunk, score in similarities if chunk.get('type') != 'essential_oil']

    # Vezme top_k/2 z každé kategorie
    half = top_k // 2
    selected_oils = oil_chunks[:half]
    selected_others = other_chunks[:half]

    # Pokud jedna kategorie nemá dost chunků, doplní z druhé
    if len(selected_oils) < half:
        needed = half - len(selected_oils)
        selected_others = other_chunks[:half + needed]
    elif len(selected_others) < half:
        needed = half - len(selected_others)
        selected_oils = oil_chunks[:half + needed]

    # Spojí a vrátí jen chunky (bez score)
    result = selected_oils + selected_others
    return [chunk for chunk, score in result]

# RAG - Seřadí data pro embedding query
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

def GetDataFromDBNode(state: State, config: RunnableConfig):
      # Vytvoří embedding z query
      query_embedding = embeddings.embed_query(state["query"])

      # Najde podobné chunky (6 = 3 oleje + 3 ostatní)
      relevant_docs = search_similar_chunks(query_embedding, top_k=6)

      return {"docs": relevant_docs}


#Prepare query node (Chain) ----------
def PrepareQueryNode(state: State, config: RunnableConfig):
    messages = [
        (
            "system",
            "Improve the user query, so it can be used for a query in vector DB.",
        ),
        ("human", "User question: {question}"),
    ]
    prompt = ChatPromptTemplate.from_messages(messages)

    chain = prompt | llm | StrOutputParser()

    result = chain.invoke({"question": state["question"]})

    return {"query": result}

def save_conversation(log):
    # Vytvoř název souboru s dnešním datem
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"conversation_log_{today}.txt"

    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Session: {datetime.now().strftime('%H:%M:%S')}\n")
        f.write(f"{'='*60}\n\n")

        for entry in log:
            f.write(f"[{entry['timestamp']}]\n")
            f.write(f"Q: {entry['question']}\n")
            f.write(f"A: {entry['answer']}\n\n")

    print(f"✅ Konverzace uložena do {filename}")


# Build the graph
builder = StateGraph(State)
builder.add_node("Prepare_query", PrepareQueryNode)
builder.add_node("AnswerNode", AnswerNode)
builder.add_node("GetDataFromDBNode", GetDataFromDBNode)

builder.add_edge(START, "Prepare_query")
builder.add_edge("Prepare_query", "GetDataFromDBNode")
builder.add_edge("GetDataFromDBNode", "AnswerNode")
builder.add_edge("AnswerNode", END)

# Graph object
graph = builder.compile()

# Visualize the graph
visualize(graph, "graph.png")

# Hlavní konverzační loop
def main_loop():
    print("=== Aromatherapy AI Assistant ===")
    print("(Zadej 'konec' pro ukončení)\n")

    conversation_log = []

    while True:
        question = input("Vaše otázka: ").strip()

        if question.lower() in ['konec', 'exit', 'quit']:
            break

        # Spusť graph
        result = graph.invoke({"question": question})

        answer = result["answer"]
        print(f"\nOdpověď: {answer}\n")

        # Zaloguj
        conversation_log.append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })

    # Ulož konverzaci
    save_conversation(conversation_log)

if __name__ == "__main__":
    main_loop()


    




