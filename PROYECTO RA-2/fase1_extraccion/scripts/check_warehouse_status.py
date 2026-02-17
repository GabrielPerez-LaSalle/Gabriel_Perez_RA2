"""Verificar estado completo de todas las tablas"""
import psycopg2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fase2_warehouse.neondb_config import get_connection_string

conn = psycopg2.connect(get_connection_string('development'))
cursor = conn.cursor()

print("Estado actual del Data Warehouse:\n")
print("="*70)

tables = [
    'dim_time',
    'dim_series', 
    'dim_tag',
    'dim_event',
    'dim_market',
    'bridge_market_tag',
    'fact_market_metrics'
]

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    status = "OK" if count > 0 else "VACIO"
    print(f"{table:25s} {count:>12,} registros  [{status}]")

print("\n" + "="*70)

cursor.close()
conn.close()
