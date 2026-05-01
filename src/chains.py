from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from src.indexing import build_schema_index
from src.database import execute_sql

load_dotenv(override=True)


# =========================
# FEW SHOT (UPDATED)
# =========================
example_prompt = PromptTemplate(
    input_variables=["question", "query"],
    template="Question: {question}\nSQL: {query}\n---",
)

examples = [

    # =========================
    # SALES & AGGREGATION
    # =========================
    {
        "question": "Tampilkan total penjualan per customer",
        "query": """
        SELECT c.company_name,
               SUM(od.quantity * od.unit_price * (1 - od.discount)) AS total_sales
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_details od ON o.order_id = od.order_id
        GROUP BY c.company_name
        ORDER BY total_sales DESC;
        """,
    },
    {
        "question": "Berapa total revenue perusahaan",
        "query": """
        SELECT SUM(od.quantity * od.unit_price * (1 - od.discount)) AS total_revenue
        FROM order_details od;
        """,
    },

    # =========================
    # PRODUCT ANALYSIS
    # =========================
    {
        "question": "Top 5 produk paling laris",
        "query": """
        SELECT p.product_name,
               SUM(od.quantity) AS total_sold
        FROM products p
        JOIN order_details od ON p.product_id = od.product_id
        GROUP BY p.product_name
        ORDER BY total_sold DESC
        LIMIT 5;
        """,
    },
    {
        "question": "Total sales per product",
        "query": """
        SELECT p.product_name,
               SUM(od.quantity * od.unit_price * (1 - od.discount)) AS total_sales
        FROM products p
        JOIN order_details od ON p.product_id = od.product_id
        GROUP BY p.product_name
        ORDER BY total_sales DESC;
        """,
    },

    # =========================
    # CATEGORY ANALYSIS
    # =========================
    {
        "question": "Total penjualan per kategori",
        "query": """
        SELECT cat.category_name,
               SUM(od.quantity * od.unit_price * (1 - od.discount)) AS total_sales
        FROM categories cat
        JOIN products p ON cat.category_id = p.category_id
        JOIN order_details od ON p.product_id = od.product_id
        GROUP BY cat.category_name
        ORDER BY total_sales DESC;
        """,
    },

    # =========================
    # TIME SERIES
    # =========================
    {
        "question": "Total penjualan per bulan",
        "query": """
        SELECT DATE_TRUNC('month', o.order_date) AS month,
               SUM(od.quantity * od.unit_price * (1 - od.discount)) AS total_sales
        FROM orders o
        JOIN order_details od ON o.order_id = od.order_id
        GROUP BY month
        ORDER BY month;
        """,
    },
    {
        "question": "Daily number of orders",
        "query": """
        SELECT o.order_date,
               COUNT(DISTINCT o.order_id) AS total_orders
        FROM orders o
        GROUP BY o.order_date
        ORDER BY o.order_date;
        """,
    },

    # =========================
    # FILTERING
    # =========================
    {
        "question": "Pesanan dikirim ke Jerman",
        "query": """
        SELECT o.order_id, o.ship_country
        FROM orders o
        WHERE o.ship_country = 'Germany';
        """,
    },
    {
        "question": "Customers from USA",
        "query": """
        SELECT c.company_name
        FROM customers c
        WHERE c.country = 'USA';
        """,
    },

    # =========================
    # CUSTOMER ANALYSIS
    # =========================
    {
        "question": "10 pelanggan teratas berdasarkan pengeluaran",
        "query": """
        SELECT c.company_name,
               SUM(od.quantity * od.unit_price * (1 - od.discount)) AS total_spent
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_details od ON o.order_id = od.order_id
        GROUP BY c.company_name
        ORDER BY total_spent DESC
        LIMIT 10;
        """,
    },
    {
        "question": "Jumlah pesanan per customer",
        "query": """
        SELECT c.company_name,
               COUNT(DISTINCT o.order_id) AS total_orders
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.company_name
        ORDER BY total_orders DESC;
        """,
    },

    # =========================
    # EMPLOYEE ANALYSIS
    # =========================
    {
        "question": "Total pesanan yang ditangani oleh setiap karyawan",
        "query": """
        SELECT e.first_name, e.last_name,
               COUNT(o.order_id) AS total_orders
        FROM employees e
        JOIN orders o ON e.employee_id = o.employee_id
        GROUP BY e.first_name, e.last_name
        ORDER BY total_orders DESC;
        """,
    },

    # =========================
    # SHIPPING ANALYSIS
    # =========================
    {
        "question": "Total pesanan berdasarkan perusahaan pengiriman",
        "query": """
        SELECT s.company_name,
               COUNT(o.order_id) AS total_orders
        FROM shippers s
        JOIN orders o ON s.shipper_id = o.ship_via
        GROUP BY s.company_name
        ORDER BY total_orders DESC;
        """,
    },

    # =========================
    # EDGE CASES
    # =========================
    {
        "question": "Pesanan yang belum dikirim",
        "query": """
        SELECT o.order_id
        FROM orders o
        WHERE o.shipped_date IS NULL;
        """,
    },
    {
        "question": "Produk yang tidak lagi dijual",
        "query": """
        SELECT p.product_name
        FROM products p
        WHERE p.discontinued = TRUE;
        """,
    },

]


# =========================
# SQL PROMPT (FIXED)
# =========================
SQL_GENERATOR_PROMPT = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="""
You are an expert PostgreSQL SQL generator.
Follow these steps:
1. Identify relevant tables
2. Identify join relationships
3. Identify required aggregations
4. Apply business logic
5. Generate final SQL
6. SQL tetap menggunakan bahasa SQL (keyword Inggris), Namun pemahaman pertanyaan berasal dari Bahasa Indonesia

Schema Context:
{context}

STRICT RULES:
- Only use tables and columns from schema
- NEVER invent columns
- ALWAYS use correct joins
- Use aliases (c, o, od, p)
- For sales calculation ALWAYS use:
  SUM(order_details.quantity * order_details.unit_price * (1 - order_details.discount))
- NEVER use products.unit_price for historical sales
- For top N per group use ROW_NUMBER()
- Return ONLY SQL
""",
    suffix="""
Question: {question}
SQL:
""",
    input_variables=["context", "question"],
)


# =========================
# ANSWER PROMPT
# =========================
ANSWER_PROMPT_TEMPLATE = """
Anda adalah seorang data analyst profesional.

Pertanyaan:
{question}

SQL Query:
{generated_query}

Hasil:
{query_result}

Instruksi:
- Jawab SELURUHNYA dalam Bahasa Indonesia
- Gunakan bahasa yang jelas dan profesional
- Gunakan bullet point jika perlu
- Jangan menambahkan data yang tidak ada
- Jika tidak ada hasil, tulis: "Tidak ditemukan data"
- Gunakan istilah bisnis dalam Bahasa Indonesia seperti:
  "penjualan", "pelanggan", "produk", "pendapatan"
Jawaban:
"""


# =========================
# LLM
# =========================
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0,
    )


# =========================
# MAIN CHAIN
# =========================
def get_sql_rag_chain():
    print("Building RAG Chain...")

    retriever = build_schema_index().as_retriever(
        search_kwargs={"k": 6}  # sebelumnya 2 → terlalu kecil
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # =========================
    # SQL GENERATION
    # =========================
    sql_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | SQL_GENERATOR_PROMPT
        | get_llm()
        | StrOutputParser()
        | RunnableLambda(clean_sql)
        | RunnableLambda(validate_sql)
    )

    # =========================
    # EXECUTE + FORMAT
    # =========================
    def execute_and_format(inputs):
        question = inputs["question"]
        query = inputs["generated_query"]

        try:
            results = execute_sql(query)

            if not results:
                query_result = "NO_RESULTS"
                raw_data = []
            else:
                query_result = "\n".join(
                    ", ".join(f"{k}: {v}" for k, v in row.items())
                    for row in results
                )
                raw_data = results

        except Exception as e:
            error_msg = str(e)

            fix_prompt = f"""
            The following SQL has an error:

            {query}

            Error:
            {error_msg}

            Fix the SQL query. Return ONLY corrected SQL.
            """

            try:
                fixed_query = get_llm().invoke(fix_prompt).content
                fixed_query = clean_sql(fixed_query)

                results = execute_sql(fixed_query)

                query_result = "\n".join(
                    ", ".join(f"{k}: {v}" for k, v in row.items())
                    for row in results
                )

                raw_data = results
                query = fixed_query  # replace with fixed query

            except Exception as e2:
                query_result = f"ERROR: {str(e2)}"
                raw_data = []

        return {
            "question": question,
            "generated_query": query,
            "query_result": query_result,
            "raw_data": raw_data,
        }

    # =========================
    # FINAL CHAIN
    # =========================
    answer_prompt = PromptTemplate.from_template(ANSWER_PROMPT_TEMPLATE)

    chain = (
        {"generated_query": sql_chain, "question": RunnablePassthrough()}
        | RunnableLambda(execute_and_format)
        | {
            "answer": answer_prompt | get_llm() | StrOutputParser(),
            "sql": lambda x: x["generated_query"],
            "results": lambda x: x["query_result"],
            "raw_results": lambda x: x["raw_data"],
        }
    )

    return chain


# =========================
# CLEAN SQL
# =========================
def clean_sql(sql):
    sql = sql.strip()
    sql = sql.replace("```sql", "").replace("```", "")
    sql = sql.split(";")[0] + ";"
    return sql

def validate_sql(sql: str):
    if "products.unit_price" in sql:
        raise Exception("Invalid SQL: gunakan order_details.unit_price")

    if "LIMIT" not in sql and "COUNT" not in sql:
        # opsional: enforce limit
        pass

    return sql


# =========================
# ENTRY POINT
# =========================
def run_text2sql(question: str):
    chain = get_sql_rag_chain()

    result = chain.invoke(question)

    return {
        "question": question,
        "answer": result["answer"],
        "sql": result["sql"],
        "results": result["results"],
        "raw_data": result["raw_results"],
    }