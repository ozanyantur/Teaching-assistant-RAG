from pathlib import Path
import fitz
import ollama
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="pdf_collection")



def ingest_pdf(file_path: str, chunk_size: int = 800, overlap: int = 150):
    doc_name = Path(file_path).name

    with fitz.open(file_path) as doc:
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if not text:
                continue

            for i in range(0, len(text), chunk_size - overlap):
                chunk = text[i : i + chunk_size]
                chunkid = f"{doc_name}_page_{page_num}_chunk_{i}"

                embedding = ollama.embed(model="bge-m3", input=chunk)["embeddings"][0]

                collection.upsert(
                    ids=[chunkid],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{
                        "page": page_num,
                        "source": doc_name,
                        "file_path": str(file_path),
                    }],
                )

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