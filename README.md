# teaching-assistant-RAG

A fully local, cloud-independent Retrieval-Augmented Generation (RAG) web application for querying PDF lecture notes without API costs or external data sharing.

## Tech Stack

- **LLM:** Ollama (`qwen2.5:7b`)
- **Embedding Model:** Ollama (`bge-m3`)
- **Vector Database:** ChromaDB (persistent local storage)
- **PDF Parsing:** PyMuPDF (`pymupdf`)
- **Web Interface:** Streamlit

## Features

- **Multi-PDF Ingestion:** Extracts text page-by-page, chunks content with overlap, and stores embeddings along with source filename, file path, and page metadata.
- **Metadata Filtering:** Query across all indexed course notes or filter searches to a specific PDF document via the sidebar.
- **Configurable Context Retrieval (`top_k`):** Dynamically adjust the number of retrieved source chunks (from 1 to 10) directly from the UI sidebar to balance answer breadth and speed.
- **Grounded Answers & Citations:** Restricts responses to the retrieved context to reduce hallucinations and displays the exact source chunks and page numbers used.
- **Interactive Upload & Auto-Reset:** Upload and index multiple PDFs directly through the Streamlit sidebar with automatic uploader state reset and confirmation feedback.

## Project Structure

```text
teaching-assistant-RAG/
├── data/
│   └── pdfs/               # Place PDF course notes here (ignored by Git)
├── chroma_db/              # Local ChromaDB persistence directory (ignored by Git)
├── src/
│   ├── ingest.py           # PDF parsing, chunking, embedding, and indexing pipeline
│   ├── rag_engine.py       # Semantic retrieval and grounded LLM response generation
│   └── app.py              # Streamlit user interface
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup & Installation

### 1. Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.com/)** installed and running in the background

Pull the required local models:

```bash
ollama pull qwen2.5:7b
ollama pull bge-m3
```

### 2. Clone & Environment Setup

```bash
git clone https://github.com/<your-username>/teaching-assistant-RAG.git
cd teaching-assistant-RAG

python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## Usage

> Run all commands from the project root directory. The database (`./chroma_db`) and PDF folder (`data/pdfs`) are resolved relative to it.

### 1. Index PDFs via CLI (Optional)

The `data/pdfs/` folder is not included in the repository, so create it first:

```bash
# Windows
mkdir data\pdfs

# macOS / Linux
mkdir -p data/pdfs
```

Place your PDF files inside `data/pdfs/` and run:

```bash
python src/ingest.py
```

### 2. Launch the Web Interface

```bash
streamlit run src/app.py
```

From the sidebar, you can upload new PDFs, filter searches by a specific document, and adjust the `top_k` slider to control how many source chunks are passed to the LLM.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.