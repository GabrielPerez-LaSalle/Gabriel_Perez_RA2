"""Explorar estructura de tags en eventos"""
import pandas as pd
import json

df_events = pd.read_csv("data/exported/events_20260216_193533.csv", low_memory=False)

print("Explorando estructura de tags en events...\n")

# Buscar un evento que tenga tags y markets
for idx, row in df_events.head(100).iterrows():
    tags_str = row.get('tags')
    markets_str = row.get('markets')
    
    if pd.notna(tags_str) and pd.notna(markets_str):
        try:
            # Parsear tags
            tags_list = json.loads(tags_str.replace("'", '"')) if isinstance(tags_str, str) else tags_str
            markets_list = json.loads(markets_str.replace("'", '"')) if isinstance(markets_str, str) else markets_str
            
            if isinstance(tags_list, list) and len(tags_list) > 0:
                if isinstance(markets_list, list) and len(markets_list) > 0:
                    print(f"Evento {row.get('id')} - '{row.get('title', '')[:60]}'")
                    print(f"  Tags ({len(tags_list)}):")
                    for tag in tags_list[:3]:
                        print(f"    {tag}")
                    print(f"  Markets ({len(markets_list)}):")
                    for market in markets_list[:3]:
                        print(f"    {market}")
                    print()
                    
                    if idx > 10:  # Ya tenemos suficiente info
                        break
        except Exception as e:
            continue

print("\n" + "="*80)
print("\nVerificando si markets tienen tags directamente...")

df_markets = pd.read_csv("data/exported/markets_20260216_193645.csv", low_memory=False)

# Ver si markets tiene una columna tags
print(f"\nColumnas en markets CSV que contienen 'tag': {[c for c in df_markets.columns if 'tag' in c.lower()]}")

# Buscar market que tenga tags
if 'tags' in df_markets.columns:
    for idx, row in df_markets.head(100).iterrows():
        tags_str = row.get('tags')
        if pd.notna(tags_str) and tags_str != '[]':
            print(f"\nMarket {row.get('id')}: {tags_str}")
            break
