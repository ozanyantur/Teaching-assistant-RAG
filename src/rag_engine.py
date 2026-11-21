import ollama
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="pdf_collection")

def ask_question(question: str, top_k: int = 4, source_file: str | None = None):
    # Embed the question using Ollama
    embedding = ollama.embed(model="bge-m3", input=question)["embeddings"][0]

    where = {"source": source_file} if source_file else None
    # Query ChromaDB for the most relevant chunks
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        where=where
    )

    documents = results['documents'][0]
    metadatas = results['metadatas'][0]

    if not documents:
        return "This information is not found in the uploaded course notes.", []

    context = "\n\n----\n\n".join(documents)
    system_prompt = ("You are a course assistant. Answer the question using only the context provided in the COURSE NOTES below. "
        "If the answer is not present in the provided texts, do not attempt to guess; "
        "instead, state: 'This information is not found in the uploaded course notes.'")

    user_prompt = f"COURSE NOTES:\n{context}\n\nQuestion: {question}"

    answer = ollama.chat(
        model="qwen2.5:7b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return answer["message"]["content"], list(zip(documents, metadatas))
