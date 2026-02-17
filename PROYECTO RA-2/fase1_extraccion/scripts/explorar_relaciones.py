"""Explorar relaciones market-event-tag"""
import pandas as pd
import json

print("Explorando relaciones market-event-tag...\n")

df_markets = pd.read_csv("data/exported/markets_20260216_193645.csv", low_memory=False)
df_events = pd.read_csv("data/exported/events_20260216_193533.csv", low_memory=False)

print("="*70)
print("COLUMNAS EN MARKETS:")
print("="*70)
print([col for col in df_markets.columns if 'event' in col.lower() or 'tag' in col.lower()])

print("\n" + "="*70)
print("EJEMPLO DE MARKET:")
print("="*70)
market_sample = df_markets.iloc[0]
print(f"ID: {market_sample.get('id')}")
print(f"Question: {market_sample.get('question')}")

# Verificar todas las columnas que podrían tener relación
for col in df_markets.columns:
    val = market_sample.get(col)
    if 'event' in col.lower() or 'tag' in col.lower():
        print(f"{col}: {val}")

print("\n" + "="*70)
print("COLUMNAS EN EVENTS:")
print("="*70)
print([col for col in df_events.columns if 'market' in col.lower() or 'tag' in col.lower()])

print("\n" + "="*70)
print("EJEMPLO DE EVENT:")
print("="*70)
event_sample = df_events.iloc[0]
print(f"ID: {event_sample.get('id')}")
print(f"Title: {event_sample.get('title')}")

# Verificar columnas relevantes
for col in df_events.columns:
    if 'market' in col.lower() or 'tag' in col.lower():
        val = event_sample.get(col)
        if pd.notna(val):
            val_str = str(val)
            if len(val_str) > 100:
                val_str = val_str[:100] + "..."
            print(f"{col}: {val_str}")

# Buscar event con tags y markets
print("\n" + "="*70)
print("BUSCANDO EVENT CON TAGS Y MARKETS:")
print("="*70)

for idx, row in df_events.head(50).iterrows():
    tags = row.get('tags')
    markets = row.get('markets')
    
    if pd.notna(tags) and pd.notna(markets):
        tags_str = str(tags)
        markets_str = str(markets)
        
        if tags_str not in ['[]', ''] and markets_str not in ['[]', '']:
            print(f"\nEvent ID: {row.get('id')}")
            print(f"Title: {row.get('title')[:60]}")
            print(f"Tags: {tags_str[:150]}...")
            print(f"Markets: {markets_str[:150]}...")
            
            # Parsear
            try:
                tags_list = json.loads(tags_str.replace("'", '"'))
                markets_list = json.loads(markets_str.replace("'", '"'))
                print(f"  -> {len(tags_list)} tags, {len(markets_list)} markets")
                
                if len(tags_list) > 0:
                    print(f"  Tag ejemplo: {tags_list[0]}")
                if len(markets_list) > 0:
                    print(f"  Market ejemplo: {markets_list[0]}")
            except Exception as e:
                print(f"  Error parseando: {e}")
            
            break
