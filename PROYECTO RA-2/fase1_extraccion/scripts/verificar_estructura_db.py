"""Verificar estructura y duplicados en NeonDB"""
import psycopg2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fase2_warehouse.neondb_config import get_connection_string

conn = psycopg2.connect(get_connection_string('development'))
cursor = conn.cursor()

print("Verificando structure y datos en NeonDB...\n")

# Constraints de dim_event
print("CONSTRAINTS DE dim_event:")
cursor.execute("""
    SELECT conname, pg_get_constraintdef(oid) 
    FROM pg_constraint 
    WHERE conrelid = 'dim_event'::regclass
""")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

print("\n" + "="*70)

# Verificar si hay event_ids duplicados en dim_event
print("\nEVENT_IDs DUPLICADOS EN dim_event:")
cursor.execute("""
    SELECT event_id, COUNT(*) as cnt
    FROM dim_event
    WHERE event_key > 0
    GROUP BY event_id
    HAVING COUNT(*) > 1
    LIMIT 10
""")
dupes = cursor.fetchall()
if dupes:
    for row in dupes:
        print(f"  event_id={row[0]}: {row[1]} veces")
else:
    print("  Ningun duplicado")

print("\n" + "="*70)

# Counts actuales
print("\nCONTEOS ACTUALES:")
tables = ['dim_series', 'dim_tag', 'dim_event', 'dim_market']
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {table.replace('dim_', '')}_key > 0")
    count = cursor.fetchone()[0]
    print(f"  {table}: {count:,}")

cursor.close()
conn.close()
