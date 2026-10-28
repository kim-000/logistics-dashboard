import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz

# 한국/일본 표준시 (KST/JST)
tz = pytz.timezone('Asia/Seoul')
now_str = datetime.now(tz).strftime('%Y-%m-%d %H:%M')

# 1. 환율 수집 (무료 Open FX API)
usd_krw, usd_jpy, jpy_100_krw = 1330.0, 157.0, 847.0
try:
    fx_url = "https://open.er-api.com/v6/latest/USD"
    req = urllib.request.Request(fx_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as res:
        fx_data = json.loads(res.read().decode('utf-8'))
        rates = fx_data.get('rates', {})
        usd_krw = round(rates.get('KRW', 1330.0), 2)
        usd_jpy = round(rates.get('JPY', 157.0), 2)
        jpy_100_krw = round((usd_krw / usd_jpy) * 100, 2)
except Exception as e:
    print(f"FX Fetch Error: {e}")

# 2. 구글 뉴스 RSS 크롤링 함수 (카테고리별 최신 5건 수집)
def fetch_google_news(query, lang='ko', gl='KR', ceid='KR:ko'):
    encoded_q = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_q}&hl={lang}&gl={gl}&ceid={ceid}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    news_items = []
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            root = ET.fromstring(resp.read())
            for item in root.findall('./channel/item')[:5]:
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                source = item.find('source').text if item.find('source') is not None else 'Google News'
                
                # 구글 뉴스 제목 포맷 정제 (보통 '기사제목 - 언론사' 형태)
                clean_title = title.rsplit(' - ', 1)[0] if ' - ' in title else title
                
                news_items.append({
                    "title": clean_title,
                    "link": link,
                    "pubDate": pub_date[:16] if len(pub_date) >= 16 else pub_date,
                    "source": source
                })
    except Exception as e:
        print(f"News Fetch Error ({query}): {e}")
    return news_items

# 3. 데이터 통합
output = {
    "last_updated": f"{now_str} KST/JST",
    "fx": {
        "usd_krw": usd_krw,
        "usd_jpy": usd_jpy,
        "jpy_100_krw": jpy_100_krw
    },
    "news": {
        "logistics": fetch_google_news("해운 물류 무역 관세"),
        "japan_domestic": fetch_google_news("日本 経済 政治", lang="ja", gl="JP", ceid="JP:ja"),
        "japan_visa": fetch_google_news("特定技能 ビザ 在留資格 外国人", lang="ja", gl="JP", ceid="JP:ja"),
        "global": fetch_google_news("글로벌 공급망 무역 환율")
    }
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("data.json successfully generated with live news!")
