import os
import psycopg
import pandas as pd

# Parámetros de conexión a PostgreSQL
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "gestion_apuestas"
DB_USER = "postgres"
DB_PASS = "workbench333"

# Nombres exactos de las 13 tablas extraídas del dump DDL
TABLES = [
    "users",
    "payment_methods",
    "sports",
    "leagues",
    "teams",
    "team_leagues",
    "sports_events",
    "market_types",
    "markets",
    "market_selections",
    "odds_history",
    "bet_tickets",
    "bet_selections",
    "financial_transactions"
]

OUTPUT_DIR = "CSV"
os.makedirs(OUTPUT_DIR, exist_ok=True)

conn_str = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASS}"

print("Iniciando exportación de tablas a CSV...")
try:
    with psycopg.connect(conn_str) as conn:
        for table in TABLES:
            df = pd.read_sql_query(f"SELECT * FROM {table};", conn)
            filepath = os.path.join(OUTPUT_DIR, f"{table}.csv")
            df.to_csv(filepath, index=False, encoding="utf-8")
            print(f"✅ Tabla exportada: {table:<22} ({len(df):>5} filas) -> {filepath}")
            
    print("\n🎉 ¡Todas las tablas se exportaron con éxito a la carpeta CSV/!")

except Exception as e:
    print(f"❌ Error durante la exportación: {e}")