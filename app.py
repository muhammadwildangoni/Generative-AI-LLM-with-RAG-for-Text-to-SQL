import streamlit as st
from src.chains import get_sql_rag_chain
from src.database import execute_sql

st.set_page_config(page_title="Text2SQL Assistant", layout="wide")


# LOAD CHAIN (CACHE)
@st.cache_resource
def load_chain():
    return get_sql_rag_chain()


chain = load_chain()


# UI HEADER
st.title("🧠 AI Data Analyst (Text-to-SQL)")
st.markdown("Tanyakan apa saja tentang data Anda, dan dapatkan query SQL serta insight secara otomatis.")


# SIDEBAR (POSTGRES)
with st.sidebar:
    st.header("Database Info")


    try:
        tables = execute_sql("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        table_names = [t["table_name"] for t in tables]

        st.success("Connected to PostgreSQL")
        st.write("**Tables:**")
        st.write(table_names)

        # sample data
        selected_table = st.selectbox("Preview Table", table_names)

        if selected_table:
            sample = execute_sql(f"SELECT * FROM {selected_table} LIMIT 5;")
            st.dataframe(sample)

    except Exception as e:
        st.error(f"DB Error: {str(e)}")

    st.divider()
    st.info("Text2SQL v2.0 (RAG Enabled)")


# =========================
# CHAT STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================
# DISPLAY CHAT
# =========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if "sql" in msg:
            with st.expander("SQL Query"):
                st.code(msg["sql"], language="sql")

        if "data" in msg and msg["data"]:
            with st.expander("Result"):
                st.dataframe(msg["data"])


# =========================
# USER INPUT
# =========================
if prompt := st.chat_input("Tanyakan sesuatu tentang data Anda..."):

    # user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            try:
                result = chain.invoke(prompt)

                answer = result["answer"]
                sql = result["sql"]
                data = result.get("raw_results", [])

                st.markdown(answer)

                with st.expander("SQL Query"):
                    st.code(sql, language="sql")

                if data:
                    with st.expander("Result Table"):
                        st.dataframe(data)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sql": sql,
                    "data": data
                })

            except Exception as e:
                st.error(f"Error: {str(e)}")