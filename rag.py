import chromadb
from dotenv import load_dotenv
import os
from google import genai

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
print("KEY LOADED: ", bool(os.getenv("GEMINI_API_KEY")))
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

chroma_client = chromadb.PersistentClient(path="templates/chroma_db")

collection = chroma_client.get_or_create_collection(name="my_documents")
chroma_client.delete_collection("my_documents")
collection = chroma_client.get_or_create_collection(name="my_documents")

files = [
    "knowledge.txt",
    "companies.txt",
    "ai_news.txt",
    "models.txt"
]

def chunk_text(text, chunk_size=30, overlap=5):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size- overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)

    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"{file}_{i}"],
            metadatas=[{"source": file}]
        )
0
print("Documents added to ChromaDB!")
print("Chunks created:", len(chunks))
print("Number of documents:", collection.count())

question = "What is artificial intelligence?"

results = collection.query(
    query_texts=[question],
    n_results=3
)

sources = results["metadatas"][0]
print("Sources:", sources)

print("\nQUESTION:")
print(question)

print("\nRETRIEVED DOCUMENTS:")
print(results["documents"])

context = "\n".join(results["documents"][0])

prompt = f"""
Answer the user's question using the retrieved context below.

Retrieved context:
{context}

User question:
{question}

Give a clear and helpful answer.
"""

'''response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)'''

print("\nFINAL ANSWER:")
#print(response.text)
conversation_history = []
while True:
    question = input("\nYou: ")

    if question.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    # Search ChromaDB
    results = collection.query(
        query_texts=[question],
        n_results=2
    )
    if results["distances"][0][0] > 1.65:
        print("\nBot: I don't have that information in my documents.")
        continue
    if not results["documents"][0]:
        print("\nBot: I don't have that information in my documents.")
        continue

    print("Distances:", results["distances"][0])
    sources = results["metadatas"][0]
    source_names = list(set(source["source"] for source in sources))
    print("Used sources:", source_names)
    print("Sources:", sources)

    context = "\n".join(results["documents"][0])

    print("Retrieved chunks:")
    for doc in results["documents"][0]:
        print("-", doc)

    print("Sources:", results["metadatas"][0])

    history_text = "\n".join(
        f"User: {item['user']}\nBot: {item['bot']}"
        for item in conversation_history
    )

    prompt = f"""
    You are a helpful conversational chatbot.

    Previous conversation:
    {history_text}

Answer the user's question using the context below.
If the answer is not in the context, say you don't know.

Context:
{context}

Question:
{question}

Answer using only the information in the Context above.
Do not use outside knowledge.
If the Context says "Alphabet", answer "Alphabet".

Sources:
{source_names}

When answering, use only the retrieved context.
if the answer is not supported by the context, say you don't know.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    print("\nBot:", response.text)
    conversation_history.append({
        "user": question,
        "bot": response.text
    })
    print("Sources:", ",".join(source_names))