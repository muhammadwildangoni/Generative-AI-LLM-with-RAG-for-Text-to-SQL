import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="northwind",
        user="postgres",
        password="admin",
        port="5432"
    )

    print("✅ CONNECTED SUCCESSFULLY")

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers LIMIT 5;")
    rows = cursor.fetchall()

    print("✅ QUERY SUCCESS")
    print(rows)

    cursor.close()
    conn.close()

except Exception as e:
    print("❌ ERROR")
    print(e)