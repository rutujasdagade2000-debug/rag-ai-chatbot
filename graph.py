
import re
import chromadb
from dotenv import load_dotenv
import os
from google import genai
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

chroma_client = chromadb.PersistentClient(path="templates/chroma_db")
collection = chroma_client.get_or_create_collection(name="my_documents")


class ChatState(TypedDict):
    question: str
    context: str
    answer: str
    sources: list


def retrieve(state: ChatState):
    results = collection.query(
        query_texts=[state["question"]],
        n_results=2
    )

    context = "\n".join(results["documents"][0])

    sources = list(set(
        item["source"] for item in results["metadatas"][0]
    ))

    return {
        "context": context,
        "sources": sources
    }



def chatbot(state: ChatState):
    if re.fullmatch(r"[0-9+\-*/(). ]+", state["question"]):
        try:
            result = eval(state["question"], {"__builtins__":None}, {})
            return {"answer": str(result)}
        except:
            pass

    # your existing chatbot code continues here

    prompt = f"""
Answer the question using the context.
Answer in the same language as the user's question.

Context:
{state["context"]}

Question:
{state["question"]}

Do not use outside knowledge.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return {"answer": response.text}


graph = StateGraph(ChatState)

graph.add_node("retrieve", retrieve)
graph.add_node("chatbot", chatbot)

graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "chatbot")
graph.add_edge("chatbot", END)

app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({
        "question": "What companies are mentioned in the documents?"
    })

    print("\nBot:", result["answer"])