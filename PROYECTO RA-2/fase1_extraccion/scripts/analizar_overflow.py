"""Analizar campos numéricos que causan overflow"""
import pandas as pd
import numpy as np

df_markets = pd.read_csv("data/exported/markets_20260216_193645.csv", low_memory=False)

print("Analizando campos numericos en markets_CSV...\n")

# Columnas numericas que se insertan en fact_market_metrics
numeric_cols = [
    'liquidity', 'liquidityAmm', 'liquidityClob',
    'volume', 'volume24hr', 'volume1wk', 'volume1mo', 'volume1yr',
    'volumeAmm', 'volumeClob', 'volume24hrAmm', 'volume24hrClob',
    'volume1wkAmm', 'volume1wkClob', 'volume1moAmm', 'volume1moClob',
    'volume1yrAmm', 'volume1yrClob',
    'lastTradePrice', 'bestBid', 'bestAsk', 'spread',
    'oneHourPriceChange', 'oneDayPriceChange', 'oneWeekPriceChange',
    'oneMonthPriceChange', 'oneYearPriceChange',
    'fee', 'takerBaseFee', 'makerBaseFee', 'competitive'
]

print("MAXIMOS POR COLUMNA:")
print("="*80)

for col in numeric_cols:
    if col in df_markets.columns:
        # Convertir a numeric ignorando errores
        values = pd.to_numeric(df_markets[col], errors='coerce')
        
        max_val = values.max()
        min_val = values.min()
        
        # Verificar si excede NUMERIC(20,10) limit: abs(value) < 10^10
        exceeds = False
        if pd.notna(max_val) and abs(max_val) >= 10**10:
            exceeds = True
        if pd.notna(min_val) and abs(min_val) >= 10**10:
            exceeds = True
        
        flag = "!!! OVERFLOW" if exceeds else ""
        
        print(f"{col:25s} | MAX: {max_val:20.2f} | MIN: {min_val:20.2f} {flag}")
    else:
        print(f"{col:25s} | NO EXISTE EN CSV")

print("\n" + "="*80)
print("\nBuscando valores especificos que excedan 10^10...")

for col in numeric_cols:
    if col in df_markets.columns:
        values = pd.to_numeric(df_markets[col], errors='coerce')
        overflow_mask = values.abs() >= 10**10
        
        if overflow_mask.any():
            overflow_count = overflow_mask.sum()
            print(f"\n{col}: {overflow_count:,} valores exceden 10^10")
            print(f"  Valores: {values[overflow_mask].head(5).tolist()}")
