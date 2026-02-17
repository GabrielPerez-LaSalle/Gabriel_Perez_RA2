"""Analizar duplicados en CSVs"""
import pandas as pd

data_dir = "data/exported"

print("Analizando duplicados en CSVs...\n")

# Series
df_series = pd.read_csv(f"{data_dir}/series_20260216_193759.csv")
print(f"SERIES:")
print(f"  Total registros: {len(df_series):,}")
print(f"  Registros unicos (id): {df_series['id'].nunique():,}")
print(f"  Duplicados: {len(df_series) - df_series['id'].nunique():,}\n")

# Tags  
df_tags = pd.read_csv(f"{data_dir}/tags_20260216_193829.csv")
print(f"TAGS:")
print(f"  Total registros: {len(df_tags):,}")
print(f"  Registros unicos (id): {df_tags['id'].nunique():,}")
print(f"  Duplicados: {len(df_tags) - df_tags['id'].nunique():,}\n")

# Events
df_events = pd.read_csv(f"{data_dir}/events_20260216_193533.csv", low_memory=False)
print(f"EVENTS:")
print(f"  Total registros: {len(df_events):,}")
print(f"  Registros unicos (id): {df_events['id'].nunique():,}")
print(f"  Duplicados: {len(df_events) - df_events['id'].nunique():,}\n")

# Markets
df_markets = pd.read_csv(f"{data_dir}/markets_20260216_193645.csv", low_memory=False)
print(f"MARKETS:")
print(f"  Total registros: {len(df_markets):,}")
print(f"  Registros unicos (id): {df_markets['id'].nunique():,}")
print(f"  Duplicados: {len(df_markets) - df_markets['id'].nunique():,}\n")
