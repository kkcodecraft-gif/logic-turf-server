# ---------------------------------------------------------
# Logic Turf Cloud Server (Final Version)
# ---------------------------------------------------------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# ▼ どうしてもデータが取れない時に表示する「伝説のレース（デモ用）」
DEMO_HORSES = [
    {"num": 1, "waku": 1, "name": "リバティアイランド", "jockey": "川田"},
    {"num": 2, "waku": 1, "name": "イクイノックス", "jockey": "ルメール"},
    {"num": 3, "waku": 2, "name": "タイトルホルダー", "jockey": "横山和"},
    {"num": 4, "waku": 2, "name": "スタニングローズ", "jockey": "吉田隼"},
    {"num": 5, "waku": 3, "name": "ドウデュース", "jockey": "戸崎圭"},
    {"num": 6, "waku": 3, "name": "フォワードアゲン", "jockey": "黛"},
    {"num": 7, "waku": 4, "name": "イレジン", "jockey": "ヴェロン"},
    {"num": 8, "waku": 4, "name": "パンサラッサ", "jockey": "吉田豊"},
    {"num": 9, "waku": 5, "name": "ヴェラアズール", "jockey": "マーカンド"},
    {"num": 10, "waku": 5, "name": "ダノンベルーガ", "jockey": "モレイラ"},
    {"num": 11, "waku": 6, "name": "トラストケンシン", "jockey": "荻野極"},
    {"num": 12, "waku": 6, "name": "チェスナットコート", "jockey": "田辺"},
    {"num": 13, "waku": 7, "name": "クリノメガミエース", "jockey": "吉村"},
    {"num": 14, "waku": 7, "name": "ディープボンド", "jockey": "和田竜"},
    {"num": 15, "waku": 8, "name": "ショウナンバシット", "jockey": "デムーロ"},
    {"num": 16, "waku": 8, "name": "インプレス", "jockey": "三浦"},
    {"num": 17, "waku": 8, "name": "スターズオンアース", "jockey": "ビュイック"},
]

@app.get("/")
def read_root():
    return {"status": "Logic Turf Server is Running!"}

@app.get("/api/race")
def get_race_card(place: str, race_num: int):
    print(f"★検索開始: {place} {race_num}R")
    
    # 取得できた馬リストを入れる箱
    horses = []
    message = "Real Data Scraped"

    try:
        # --- 1. netkeibaにアクセス ---
        list_url = "https://race.netkeiba.com/top/race_list.html"
        resp = requests.get(list_url, headers=HEADERS, timeout=5)
        resp.encoding = 'EUC-JP'
        soup = BeautifulSoup(resp.text, 'html.parser')

        target_race_id = None
        
        # 今日のレースを探す
        race_list_divs = soup.find_all('div', class_='RaceList_Box')
        for div in race_list_divs:
            place_header = div.find('div', class_='RaceList_DataHeader')
            if not place_header: continue
            
            # 場所名チェック
            if place in place_header.text.strip():
                race_links = div.find_all('a', href=True)
                for link in race_links:
                    # レース番号チェック
                    r_span = link.find('span', class_='RaceNum')
                    if r_span:
                        r_txt = r_span.text.replace('R', '').strip()
                        if str(race_num) == r_txt and 'race_id=' in link['href']:
                            target_race_id = link['href'].split('race_id=')[1].split('&')[0]
                            break
            if target_race_id: break
        
        # --- 2. もし見つかったら出馬表を取得 ---
        if target_race_id:
            print(f"  -> ID発見: {target_race_id}")
            shutuba_url = f"https://race.netkeiba.com/race/shutuba.html?race_id={target_race_id}"
            resp_card = requests.get(shutuba_url, headers=HEADERS, timeout=5)
            resp_card.encoding = 'EUC-JP'
            soup_card = BeautifulSoup(resp_card.text, 'html.parser')
            
            rows = soup_card.select('tr.HorseList')
            for row in rows:
                try:
                    w_tag = row.select_one('td.Waku')
                    n_tag = row.select_one('td.Umaban')
                    name_tag = row.select_one('span.HorseName a')
                    
                    waku = int(w_tag.text.strip()) if w_tag else 0
                    num = int(n_tag.text.strip()) if n_tag else 0
                    name = name_tag.text.strip() if name_tag else "不明"
                    
                    horses.append({"num": num, "waku": waku, "name": name})
                except:
                    continue

    except Exception as e:
        print(f"Scraping Error: {e}")
        # エラーが起きても処理を止めない

    # --- 3. 最終チェック（もし空っぽならデモデータを返す） ---
    if len(horses) == 0:
        print("  -> データなし。デモデータを返します。")
        horses = DEMO_HORSES
        message = "Demo Data (Today's race not found)"

    return {
        "status": "success",
        "meta": {"place": place, "race_num": race_num, "info": message},
        "horses": horses
    }
