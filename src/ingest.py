from pathlib import Path
import pymupdf
import ollama
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="pdf_collection")

def _embed_and_store(ids, chunks, metadatas):
    if not chunks:
        return
    embeddings = ollama.embed(model="bge-m3", input=chunks)["embeddings"]
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )


def ingest_pdf(file_path: str, chunk_size: int = 800, overlap: int = 150, batch_size: int = 32):
    doc_name = Path(file_path).name
    ids, chunks, metadatas = [], [], []

    with pymupdf.open(file_path) as doc:
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if not text:
                continue

            for i in range(0, len(text), chunk_size - overlap):
                ids.append(f"{doc_name}_page_{page_num}_chunk_{i}")
                chunks.append(text[i : i + chunk_size])
                metadatas.append({
                    "page": page_num,
                    "source": doc_name,
                    "file_path": str(file_path),
                })

                if len(chunks) >= batch_size:
                    _embed_and_store(ids, chunks, metadatas)
                    ids, chunks, metadatas = [], [], []

    _embed_and_store(ids, chunks, metadatas)  
    print(f"Completed indexing: {doc_name}")


def index_folder(folder_path: str = "data/pdfs"):
    pdf_folder = list(Path(folder_path).glob("*.pdf"))
    if not pdf_folder:
        print(f"No PDF files found in '{folder_path}'.")
        return

    for pdf_path in pdf_folder:
        ingest_pdf(str(pdf_path))


if __name__ == "__main__":
    index_folder("data/pdfs")