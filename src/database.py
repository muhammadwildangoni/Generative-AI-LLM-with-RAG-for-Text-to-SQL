import psycopg2
from psycopg2 import OperationalError

DB_CONFIG = {
    "host":     "localhost",
    "database": "northwind",
    "user":     "postgres",
    "password": "admin",
    "port":     "5432",
    "options":  "-c search_path=public"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# ── 1. CEK KONEKSI ────────────────────────────────────
def cek_koneksi():
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT version();")
        versi = cur.fetchone()[0]
        print(f"✅ Koneksi berhasil!\n   {versi}\n")
        cur.close(); conn.close()
    except OperationalError as e:
        print(f"❌ Gagal konek: {e}")

# ── 2. LIST SEMUA TABEL ───────────────────────────────
def list_tabel():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'      -- pastikan ini 'public'
          AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    tabel = cur.fetchall()
    print(f"📋 Daftar tabel ({len(tabel)} tabel):")
    for t in tabel:
        print(f"   - {t[0]}")
    print()
    cur.close(); conn.close()

# ── 3. LIHAT KOLOM SEBUAH TABEL ───────────────────────
def lihat_kolom(nama_tabel):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
    """, (nama_tabel,))
    kolom = cur.fetchall()
    print(f"🔍 Kolom tabel '{nama_tabel}':")
    for col, dtype in kolom:
        print(f"   {col:<25} {dtype}")
    print()
    cur.close(); conn.close()

# ── 4. JALANKAN QUERY BEBAS ───────────────────────────
def jalankan_query(sql, params=None):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(sql, params)
    # ambil nama kolom dari cursor.description
    headers = [desc[0] for desc in cur.description]
    rows    = cur.fetchall()
    print("  ".join(f"{h:<20}" for h in headers))
    print("-" * 60)
    for row in rows:
        print("  ".join(f"{str(v):<20}" for v in row))
    print(f"\n({len(rows)} baris)\n")
    cur.close(); conn.close()


# ── 5. EXECUTE SQL (UNTUK AI) ─────────────────────────
def execute_sql(sql, params=None):
    """
    Execute SQL and return results as list of dict.
    Designed for LLM pipeline (chains.py).
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(sql, params)

        # kalau query SELECT
        if cur.description:
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            result = [
                dict(zip(columns, row))
                for row in rows
            ]
        else:
            # kalau INSERT/UPDATE/DELETE
            conn.commit()
            result = []

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cur.close()
        conn.close()

    return result

# ══ MAIN ══════════════════════════════════════════════
if __name__ == "__main__":

    cek_koneksi()

    list_tabel()

    lihat_kolom("customers")   # ganti nama tabel sesuai DB

    jalankan_query("SELECT * FROM public.customers LIMIT 5;")