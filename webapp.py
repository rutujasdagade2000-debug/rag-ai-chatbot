from flask import Flask, render_template, request
import os
from pypdf import PdfReader
from graph import app, collection

app_web = Flask(__name__)


@app_web.route("/", methods=["GET", "POST"])
def home():
    answer = ""
    question = ""
    sources = []
    upload_message = ""

    if request.method == "POST" and "file" in request.files:
        file = request.files["file"]

        if file.filename.endswith(".txt") or file.filename.endswith(".pdf"):
            file.save(file.filename)

            if file.filename.endswith(".pdf"):
                reader = PdfReader(file.filename)
                text = ""

                for page in reader.pages:
                    text += page.extract_text() or ""
            else:
                with open(file.filename, "r", encoding="utf-8") as f:
                    text = f.read()

            chunks = text.split("\n")

            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    collection.add(
                        documents=[chunk],
                        ids=[f"{file.filename}_{i}"],
                        metadatas=[{"source": file.filename}]
                    )
                    upload_message= f"{file.filename} uploaded successfully"
                    print("UPLOADED", file.filename)

    if request.method == "POST" and "question" in request.form:
        question = request.form.get("question", "")

        result = app.invoke({
            "question": question
        })

        answer = result["answer"]
        sources = result["sources"]

    return render_template(
        "index.html",
        answer=answer,
        question=question,
        sources=sources,
        upload_message=upload_message
    )


if __name__ == "__main__":
    app_web.run(debug=True)