#!/usr/bin/env python3
import sys
import requests
import json
from pathlib import Path

def test_api():
    # Probar el endpoint de clientes
    print("Probando endpoint de clientes...")
    response = requests.get("http://localhost:8000/api/clientes")
    if response.status_code == 200:
        data = response.json()
        print(f"Éxito! Se encontraron {len(data)} clientes")
        if data:
            print("Primer cliente:")
            print(json.dumps(data[0], indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    
    # Probar el endpoint de productos
    print("\nProbando endpoint de productos...")
    response = requests.get("http://localhost:8000/api/productos")
    if response.status_code == 200:
        data = response.json()
        print(f"Éxito! Se encontraron {len(data)} productos")
        if data:
            print("Primer producto:")
            print(json.dumps(data[0], indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    
    # Probar el endpoint de ventas
    print("\nProbando endpoint de ventas...")
    response = requests.get("http://localhost:8000/api/ventas")
    if response.status_code == 200:
        data = response.json()
        print(f"Éxito! Se encontraron {len(data)} ventas")
        if data:
            print("Primera venta:")
            print(json.dumps(data[0], indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_api()