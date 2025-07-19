from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from fastapi.responses import JSONResponse
import re

app = FastAPI()

def normalize_key(key):
    key = key.lower()
    key = key.replace('%', 'pct')
    key = key.replace('/', '_per_')  # or just '_' if you prefer
    key = re.sub(r'[^a-z0-9_]', '_', key)  # replace non-alphanum with '_'
    key = re.sub(r'_+', '_', key)  # replace multiple underscores with one
    key = key.strip('_')
    return key

@app.get("/stock/{symbol}")
def get_stock_snapshot(symbol: str):
    url = f"https://finviz.com/quote.ashx?t={symbol.upper()}&p=d"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return JSONResponse(content={"error": f"Failed to fetch data: {e}"}, status_code=500)

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="snapshot-table2")
    if not table:
        return JSONResponse(content={"error": "Could not find snapshot-table2 for this symbol"}, status_code=404)

    data = {}
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        for i in range(0, len(cells)-1, 2):
            raw_key = cells[i].get_text(strip=True)
            key = normalize_key(raw_key)
            value = cells[i+1].get_text(strip=True)
            data[key] = value

    return data