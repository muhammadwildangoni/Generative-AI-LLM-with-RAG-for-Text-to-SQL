import psycopg2
import streamlit as st
from psycopg2.extras import RealDictCursor

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

    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(query)

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result
