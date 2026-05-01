# 🧠 Smart Text-to-SQL Assistant

A powerful, secure, and intuitive natural language interface for your databases. This application uses **Google Gemini 2.5 Flash** and **Retrieval-Augmented Generation (RAG)** to translate plain English questions into optimized SQLite queries.

---

## ✨ Features

- **Natural Language to SQL**: Ask questions like *"Who are our top 5 customers in Bangalore?"* and get instant results.
- **RAG-Powered Schema Awareness**: Automatically retrieves relevant table schemas and descriptions to maintain context and accuracy.
- **Few-Shot Learning**: Guided by high-quality examples to ensure queries follow SQLite best practices.
- **Multi-Layered Security**:
    - **Read-Only Database**: Forced at the connection level via SQLite URI.
    - **Validation Layer**: Python-level checks to block any destructive commands (`DROP`, `DELETE`, `UPDATE`).
    - **Prompt Guardrails**: Strict instructions to the LLM to only generate `SELECT` queries.
- **Rich UI/UX**:
    - Built with **Streamlit** for a modern, responsive feel.
    - **Markdown Summaries**: AI-generated answers with bolding and bullet points.
    - **Interactive Data Tables**: View raw results in a clean, filterable format.

---

## 🛠️ Technology Stack

- **LLM**: [Google Gemini 2.5 Flash](https://aistudio.google.com/api-keys)
- **Framework**: [LangChain](https://www.langchain.com/)
- **UI**: [Streamlit](https://streamlit.io/)
- **Vector DB**: [ChromaDB](https://www.trychroma.com/)
- **Database**: SQLite with [SQLAlchemy](https://www.sqlalchemy.org/)
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher.
- A **Google Gemini API Key** (Get one for free at [Google AI Studio](https://aistudio.google.com/api-keys)).

### Installation

1. **Clone the Repository**:
   ```bash
   git clone <your-repo-url>
   cd Text2Sql
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the root directory and add your API key:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```
   *(You can also use `.env.example` as a template).*

### 📦 Database Initialization

Before running the app, you need to index your database schema so the assistant "knows" your tables:

```bash
python -m src.indexing
```

---

## 🖥️ Running the Application

Launch the Streamlit interface:

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`.

---

## 💡 Example Questions

Once the app is running, try asking:
- *"Show all orders made by a customer named Alice Sharma."*
- *"List the top 5 customers by total spending."*
- *"How many customers do we have in Mumbai?"*
- *"What was the average order amount in April 2025?"*

---

## 📂 Project Structure

```text
.
├── app.py              # Main Streamlit Application
├── src/
│   ├── chains.py       # RAG and LLM Chain Logic
│   ├── database.py     # Database Execution & Security
│   ├── indexing.py     # Vector Store & Schema Indexing
│   └── __init__.py
├── data/
│   ├── main.db         # Sample SQLite Database
│   ├── schema_docs.yaml# Table & Column Descriptions
│   └── chroma_db/      # Vector store for schema retrieval
├── requirements.txt    # Project Dependencies
└── .env                # Private API Keys (DO NOT COMMIT)
```

---

## 🛡️ Security Note

This application is designed for **read-only** interactions. Destructive queries are blocked at three different levels (Prompt, Code, and Database). However, always ensure your production database users have limited permissions.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
