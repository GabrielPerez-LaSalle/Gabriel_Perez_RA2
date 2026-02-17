# -*- coding: utf-8 -*-
"""
Script simple de prueba para la API
"""
import requests

BASE_URL = "http://localhost:8000"

print("\n" + "="*60)
print("PRUEBAS RAPIDAS DE LA API")
print("="*60 + "\n")

# Test 1: Root
print("1. Testing root endpoint...")
r = requests.get(f"{BASE_URL}/")
print(f"   Status: {r.status_code}")  
print(f"   Response: {r.json()}\n")

# Test 2: Health
print("2. Testing health endpoint...")
r = requests.get(f"{BASE_URL}/health")
print(f"   Status: {r.status_code}")
print(f"   Response: {r.json()}\n")

# Test 3: Top Markets
print("3. Testing top markets by volume...")
r = requests.get(f"{BASE_URL}/markets/top-volume?limit=3")
print(f"   Status: {r.status_code}")
data = r.json()
print(f"   Total markets: {len(data)}")
if len(data) > 0:
    print(f"   Top market: {data[0]['question']}")
    print(f"   Volume: ${float(data[0]['volume']):,.2f}\n")

# Test 4: Category Stats
print("4. Testing category stats...")
r = requests.get(f"{BASE_URL}/analytics/category-stats?limit=3")
print(f"   Status: {r.status_code}")
data = r.json()
print(f"   Categories: {len(data)}")
if len(data) > 0:
    print(f"   Top category: {data[0]['category']}")
    print(f"   Total volume: ${float(data[0]['total_volume']):,.2f}\n")

# Test 5: Search markets
print("5. Testing market search...")
r = requests.get(f"{BASE_URL}/markets/search/?query=Trump&limit=2")
print(f"   Status: {r.status_code}")
data = r.json()
print(f"   Results: {len(data)}")
if len(data) > 0:
    print(f"   First result: {data[0]['question']}\n")

print("="*60)
print("TODAS LAS PRUEBAS COMPLETADAS")
print("Visita http://localhost:8000/docs para la documentacion completa")
print("="*60 + "\n")
