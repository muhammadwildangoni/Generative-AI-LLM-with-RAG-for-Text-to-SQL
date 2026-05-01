import yaml
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SCHEMA_PATH = os.path.join(BASE_DIR, "data", "schema_docs.yaml")
CHROMA_PATH = os.path.join(BASE_DIR, "data", "chroma_db")


def load_schema_docs():
    with open(SCHEMA_PATH, "r") as f:
        return yaml.safe_load(f)


def build_documents():
    schema = load_schema_docs()
    docs = []

    db = schema["database"]

    # ======================
    # 0. METADATA DOC
    # ======================
    if "metadata" in schema:
        meta = schema["metadata"]
        content = f"""
Metadata:
Author: {meta.get('author','')}
Version: {meta.get('version','')}
Description:
{meta.get('description','')}
"""
        docs.append(Document(page_content=content, metadata={"type": "metadata"}))

    # ======================
    # 1. TABLE + COLUMN COMBINED
    # ======================
    for table in db["tables"]:
        content = f"Table: {table['name']}\n"
        content += f"Description: {table.get('description','')}\n"

        content += "\nColumns:\n"
        for col in table["columns"]:
            content += f"- {col['name']} ({col.get('type','')}): {col.get('description','')}\n"

        docs.append(
            Document(
                page_content=content,
                metadata={"type": "table_full", "table": table["name"]},
            )
        )

    # ======================
    # 2. COLUMN DETAIL
    # ======================
    for table in db["tables"]:
        for col in table["columns"]:
            content = f"Table: {table['name']}\n"
            content += f"Column: {col['name']}\n"
            content += f"Type: {col.get('type','')}\n"
            content += f"Description: {col.get('description','')}\n"

            docs.append(
                Document(
                    page_content=content,
                    metadata={
                        "type": "column",
                        "table": table["name"],
                        "column": col["name"],
                    },
                )
            )

    # ======================
    # 3. RELATIONSHIPS
    # ======================
    if "relationships" in db:
        for rel in db["relationships"]:
            content = f"Join: {rel['join']}\n"
            content += f"Description: {rel.get('description','')}\n"

            docs.append(
                Document(
                    page_content=content,
                    metadata={"type": "relationship"},
                )
            )

    # ======================
    # 4. BUSINESS LOGIC
    # ======================
    if "business_logic" in db:
        for logic in db["business_logic"]:
            content = f"Business Logic: {logic['name']}\n"
            content += f"Description: {logic.get('description','')}\n"
            content += f"Formula: {logic['formula']}\n"

            docs.append(
                Document(
                    page_content=content,
                    metadata={"type": "business_logic"},
                )
            )

    # ======================
    # 5. QUERY EXAMPLES 🔥
    # ======================
    if "queries" in db:
        for q in db["queries"]:
            content = f"Question Type: {q['name']}\n"
            content += f"Description: {q.get('description','')}\n"
            content += f"SQL:\n{q['sql']}\n"

            docs.append(
                Document(
                    page_content=content,
                    metadata={"type": "query_example"},
                )
            )

    return docs


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def build_schema_index():
    embeddings = get_embeddings()

    # 👉 kalau sudah ada, load saja
    if os.path.exists(CHROMA_PATH):
        print("Loading existing index...")
        return Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings
        )

    print("Creating new index...")
    docs = build_documents()

    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )

    return vectordb


if __name__ == "__main__":
    print("Building advanced schema index...")
    build_schema_index()
    print("Done.")