import json
import urllib.request
from datetime import datetime
import pytz

# 한국/일본 시간(KST/JST, UTC+9) 기준
tz = pytz.timezone('Asia/Seoul')
now_str = datetime.now(tz).strftime('%Y-%m-%d %H:%M')

# 무료 오픈 환율 API 호출
fx_url = "https://open.er-api.com/v6/latest/USD"
req = urllib.request.Request(fx_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response:
    fx_data = json.loads(response.read().decode('utf-8'))

rates = fx_data.get('rates', {})
usd_krw = round(rates.get('KRW', 1330.0), 2)
usd_jpy = round(rates.get('JPY', 157.0), 2)
jpy_100_krw = round((usd_krw / usd_jpy) * 100, 2) if usd_jpy else 845.0

# data.json 생성
output = {
    "last_updated": f"{now_str} KST",
    "fx": {
        "usd_krw": usd_krw,
        "usd_jpy": usd_jpy,
        "jpy_100_krw": jpy_100_krw
    }
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Data updated successfully: {output}")
