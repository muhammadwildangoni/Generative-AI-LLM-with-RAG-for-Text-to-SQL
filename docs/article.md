---

Building a Smart Text-to-SQL System with RAG and LangChain 🧠
Ever wanted to ask questions in plain English and have your AI write the SQL for you - then explain the results too? That's exactly what I've built using LangChain, SQLCoder, ChromaDB, and a simple SQLite database.
Let me walk you through how this Text-to-SQL Retrieval-Augmented Generation (RAG) system works, step-by-step - from dataset creation to full chain orchestration.
🚀 What We're Building
We're creating an AI system that can:
Understand a natural language question.
Generate a valid SQL query based on database schema.
Execute that query on a live database.
Return a friendly, natural-language answer based on the result.

Perfect for analytics dashboards, internal tools, or even chatbots with data access.
📦 Step 1: Setting Up the Environment
We start by installing the core libraries:
pip install langchain chromadb transformers PyYAML sqlalchemy huggingface_hub
pip install -U langchain-community faker
These tools help us manage vector stores, LLMs, data generation, and database interaction.

---

🏗️ Step 2: Creating a Realistic Sample Database
Using faker, we create two tables:
customers: 100 fake users
orders: 1000 fake purchases

This helps simulate real-world data for our SQL assistant to query.
# Insert 100 customers with realistic data
customers = []
for i in range(1, 101):
    name = fake.name()
    city = fake.city()
    address = fake.address().replace("\n", ", ")
    customers.append((i, name, city, address))
    ...

# Insert 1000 orders with realistic data
orders = []
for i in range(1, 1001):
    customer_id = random.randint(1, 100)
    amount = round(random.uniform(50.0, 2000.0), 2)
    days_ago = random.randint(1, 365)
    date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    orders.append((i, customer_id, amount, date))
    ...
Once populated, we save this as main.db.
🧠 Step 3: Loading the Schema as Context
We use a YAML file (schema_docs.yaml) to define human-readable descriptions for our tables and columns. For example:
- name: customers
  description: Customer details
  columns:
    - name: id
      description: Unique customer ID
    ...
This schema is then transformed into LangChain Document objects to feed into the retriever.

---

🧬 Step 4: Vectorize the Schema with ChromaDB
Using HuggingFace's all-MiniLM-L6-v2 model, we embed the schema documents and load them into ChromaDB:
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectordb = Chroma.from_documents(split_docs, embedding=embeddings)
This allows relevant schema parts to be retrieved based on the user's question.

---

🧠 Step 5: Power the Brain with SQLCoder
We load the defog/sqlcoder-7b-2 model using HuggingFace:
tokenizer = AutoTokenizer.from_pretrained("defog/sqlcoder-7b-2")
model = AutoModelForCausalLM.from_pretrained("defog/sqlcoder-7b-2")
Wrapped with a text generation pipeline, this model serves as the core logic that transforms questions into SQL queries.

---

🔁 Step 6: Two-Stage RAG Chain
🧩 Part 1: SQL Generation Prompt
This prompt instructs the model to:
Use only documented schema elements
Generate only SELECT queries
Format with aliases and indentation

Prompt:
You are an expert SQL assistant. Your task is to generate a valid SQL query based on the user's question and the database schema provided. Use only the information in the schema context below. Ensure your query is syntactically correct, semantically accurate, and limited to SELECT queries only.

Schema:
{context}

Guidelines:
- Only use tables, columns, and relationships defined in the schema.
- Do not invent column or table names. If something is unclear, write a SQL comment.
- Use JOINs where necessary to combine data across tables.
- Use GROUP BY and aggregate functions when the question implies summarization.
- Always use LIMIT in queries requesting a preview or top-N results.
- Format queries cleanly with appropriate indentation.
- Never write DELETE, INSERT, UPDATE, DROP, or DDL statements.
- Prefer using table aliases (`c` for customers, `o` for orders) when dealing with multiple tables.
- All dates must follow 'YYYY-MM-DD' format.

---

Here are some examples to guide your output:

Example 1:
Question:
Show all orders made by a customer named Alice Sharma.

SQL Query:
SELECT 
    o.order_id,
    o.amount,
    o.date,
    c.name,
    c.city
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE c.name = 'Alice Sharma';

---

Example 2:
Question:
What is the total number of orders and total sales for April 1, 2025?

SQL Query:
SELECT 
    COUNT(order_id) AS total_orders,
    SUM(amount) AS total_sales
FROM orders
WHERE date = '2025-04-01';

---

Example 3:
Question:
List the top 5 customers by total spending.

SQL Query:
SELECT 
    c.name,
    c.city,
    SUM(o.amount) AS total_spent
FROM orders o
JOIN customers c ON o.customer_id = c.id
GROUP BY c.id
ORDER BY total_spent DESC
LIMIT 5;

---

Example 4:
Question:
Find all orders made by customers from Mumbai.

SQL Query:
SELECT 
    o.order_id,
    o.amount,
    o.date,
    c.name,
    c.city
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE c.city = 'Mumbai';

---

Now use the same format to answer the user question below.

Question:
{question}

SQL Query:
Example Queries:
Example 1:
 Question: Show all orders made by a customer named Alice Sharma.
SELECT 
    o.order_id,
    o.amount,
    o.date,
    c.name,
    c.city
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE c.name = 'Alice Sharma';
Example 2:
 Question: What is the total number of orders and total sales for April 1, 2025?
SELECT 
    COUNT(order_id) AS total_orders,
    SUM(amount) AS total_sales
FROM orders
WHERE date = '2025-04-01';
Example 3:
 Question: List the top 5 customers by total spending.
SELECT 
    c.name,
    c.city,
    SUM(o.amount) AS total_spent
FROM orders o
JOIN customers c ON o.customer_id = c.id
GROUP BY c.id
ORDER BY total_spent DESC
LIMIT 5;
Example 4:
 Question: Find all orders made by customers from Mumbai.
SELECT 
  o.order_id,
  o.amount,
  o.date,
  c.name,
  c.city
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE c.city = 'Mumbai';
LangChain's RetrievalQA combines schema retrieval and the SQL generation prompt to produce the final query.

---

💬 Part 2: Natural Language Answer Prompt
After executing the SQL, we format the result into a human-readable response:
Prompt:
You are a helpful assistant. Based on the user's question, the generated SQL query, and the SQL result, write a clear and natural language answer.

Guidelines:
- Do not repeat the SQL query.
- Focus only on summarizing the result in plain language.
- If the result is a list or table, summarize it or highlight the top results.
- Avoid guessing or adding information not in the SQL result.

Here are a few examples:

Example 1:
Question: How many orders were placed by each customer?
SQL Result: [('Alice', 5), ('Bob', 3), ('Charlie', 7)]
Answer: Alice placed 5 orders, Charlie placed 7, and Bob placed 3. This gives an overview of how many times each customer made a purchase.

Example 2:
Question: What are the top 3 customers by total orders?
SQL Result: [('Charlie', 15), ('Alice', 13), ('Bob', 12)]
Answer: The top three customers by number of orders are Charlie with 15, Alice with 13, and Bob with 12.

Example 3:
Question: What is the average order amount?
SQL Result: [(57.82,)]
Answer: The average order amount is $57.82.

Now answer the following:

<[EOS]>

Question:
{question}

Generated SQL Query:
{generated_query}

SQL Query Result:
{query_result}

Answer:
Example Answers:
Example 1:
Question:
How many orders were placed in April?

SQL Query Result:
(39,)

Answer:
39 orders were placed in April.
Example 2:
Question:
What are the top 3 customers by total orders?

SQL Query Result:
('Donald Myers', 'Williamshaven', 18)
('Laura Randolph', 'Wrightchester', 18)
('Timothy Robertson', 'Vaughanberg', 18)

Answer:
The top three customers by total orders are Donald Myers from Williamshaven with 18 orders, Laura Randolph from Wrightchester with 18 orders, and Timothy Robertson from Vaughanberg with 18 orders.
Example 3:
Question:
What is the average order amount?

SQL Query Result:
(1029.4882499999978,)

Answer:
The average order amount is $1029.49.

---

🛠️ Step 7: Executing SQL Queries
We use SQLAlchemy to run queries on the SQLite database, and pass results into the final stage for interpretation.
def execute_sql(sql):
    ...
    return result

---

🧪 How It Works (Demo Time!)
Let's say you ask:
"Who are the top 5 customers by total spending?"
The system:
Retrieves relevant schema about orders and customers
Generates a SQL query with joins and aggregates
Runs the query
Responds with:
 "The top five customers by spending are Alice, Bob, Charlie…"

Example:
Question:
Who are the top 3 customers by total spending?

Generated SQL Query:
SELECT 
    c.name,
    c.city,
    SUM(o.amount) AS total_spent
FROM orders o
JOIN customers c ON o.customer_id = c.id
GROUP BY c.id
ORDER BY total_spent DESC
LIMIT 3;

SQL Query Result:
('Timothy Robertson', 'Vaughanberg', 20727.100000000002)
('Laura Randolph', 'Wrightchester', 18677.289999999997)
('Amber Coleman', 'Moraville', 18479.52)

Answer:
The top 3 customers by total spending are Timothy Robertson, Laura Randolph, and Amber Coleman.
Magic, right?

---

🎯 Why This Matters
This setup shows how you can:
Build a real-world Text-to-SQL engine
Combine schema-aware retrieval with LLM reasoning
Create analytics agents that talk to databases in plain English

It's flexible, open-source, and works locally - no cloud dependencies required.

---

📚 What's Next?
Some potential extensions:
Add a web UI using Streamlit or Gradio
Log query history and audit trails
Connect to live Postgres/MySQL databases
Fine-tune the LLM on your domain

🧩 Final Thoughts
By combining ChromaDB, Hugging Face models, and LangChain's composable chains, we built a powerful system that speaks SQL and speaks human. Whether you're building internal tools, customer support dashboards, or BI assistants - this is a solid foundation.
Want full code, visit here.

---

If you found this helpful, follow me for more AI + data science tutorials. Got questions or want to collaborate? Drop a comment or DM me!
🧑‍💻✨