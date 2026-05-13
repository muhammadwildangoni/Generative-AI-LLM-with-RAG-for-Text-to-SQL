import psycopg2
import streamlit as st

DB_CONFIG = {
    "host": st.secrets["DB_HOST"],
    "database": st.secrets["DB_NAME"],
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "port": st.secrets["DB_PORT"],
    "sslmode": "require"
}


def execute_sql(query):
    conn = psycopg2.connect(**DB_CONFIG)

    cur = conn.cursor()

    cur.execute(query)

    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    result = [dict(zip(columns, row)) for row in rows]

    cur.close()
    conn.close()

    return result
