from pathlib import Path
import streamlit as st
from ingest import ingest_pdf
from rag_engine import ask_question

st.set_page_config(page_title="Local Course Note Assistant", layout="centered")
st.title("Local Course Note Assistant")

PDF_FOLDER = Path("data/pdfs")
PDF_FOLDER.mkdir(parents=True, exist_ok=True)

if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

with st.sidebar:
    st.header("Course Notes Management")

    
    uploaded_files = st.file_uploader(
        "Add New PDF Course Notes",
        type=["pdf"],
        accept_multiple_files=True,
        key=f"pdf_uploader_{st.session_state['uploader_key']}",
    )

    if st.button("Index Uploaded Files") and uploaded_files:
        with st.spinner("Indexing uploaded PDFs..."):
            for uploaded_file in uploaded_files:
                save_path = Path(uploaded_file.name).name
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                ingest_pdf(str(save_path))

        st.session_state["index_msg"] = f"{len(uploaded_files)} file(s) indexed successfully!"
        st.session_state["uploader_key"] += 1
        st.rerun()

    if "index_msg" in st.session_state:
        st.success(st.session_state.pop("index_msg"))

    st.divider()

    
    current_pdfs = sorted([p.name for p in PDF_FOLDER.glob("*.pdf")])
    options = ["All Files"] + current_pdfs

    selected_source = st.selectbox(
        "Source to search in:",
        options=options
    )

    top_k = st.slider(
        "Number of source chunks to retrieve (Top-K):",
        min_value=1,
        max_value=10,
        value=4
    )    


question = st.text_input("Ask a question about your course notes:")

if question:
    file_filter = None if selected_source == "All Files" else selected_source

    with st.spinner("Searching and generating answer..."):
        answer, sources = ask_question(question, top_k=top_k, source_file=file_filter)

    st.markdown("### Answer:")
    st.write(answer)

    if sources:
        with st.expander("Used Source Chunks"):
            for text, meta in sources:
                meta = meta or {}
                source_name = meta.get("source") or (
                    Path(meta["file_path"]).name if meta.get("file_path") else "Unknown Source"
                )
                page_num = meta.get("page", "?")
                st.caption(f"Source: {source_name} | Page: {page_num}")
                st.text(text)