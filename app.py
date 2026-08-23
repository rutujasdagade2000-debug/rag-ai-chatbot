from google import genai
from dotenv import load_dotenv
import os
import chromadb

from flask import Flask, render_template, request
from pathlib import Path

# -----------------------------
# Flask setup
# -----------------------------
app = Flask(__name__)

# -----------------------------
# Load API key
# -----------------------------
load_dotenv(Path(__file__).parent / ".env")

api_key = os.getenv("GEMINI_API_KEY")

print("API key found:", bool(api_key))

client = genai.Client(api_key=api_key)

# -----------------------------
# Connect to ChromaDB
# -----------------------------
chroma_client = chromadb.PersistentClient(
    path="templates/chroma_db"
)

collection = chroma_client.get_or_create_collection(
    name="my_documents"
)

print("ChromaDB connected!")
print("Documents:", collection.count())


# -----------------------------
# Home page
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def home():

    answer = ""
    question = ""

    if request.method == "POST":

        question = request.form["question"]

        # Search ChromaDB
        results = collection.query(
            query_texts=[question],
            n_results=3
        )

        # Get retrieved documents
        documents = results["documents"][0]

        context = "\n\n".join(documents)

        # Create RAG prompt
        prompt = f"""
You are a helpful AI assistant.

Answer the user's question using the information in the
provided context.

If the answer is not available in the context, say:
"I don't have that information in my documents."

Do not invent facts.

CONTEXT:
{context}

USER QUESTION:
{question}
"""

        # Ask Gemini
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        answer = response.text

    return render_template(
        "index.html",
        answer=answer,
        question=question
    )


# -----------------------------
# Run Flask
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)