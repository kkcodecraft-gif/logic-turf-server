# ---------------------------------------------------------
# Logic Turf Cloud Server (Robust Version)
# ---------------------------------------------------------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ネット上のサイトを見るための「名札」
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

@app.get("/")
def read_root():
    return {"status": "Logic Turf Server is Running!"}

@app.get("/api/race")
def get_race_card(place: str, race_num: int):
    print(f"★検索開始: {place} {race_num}R")

    try:
        # 1. 今日のレース一覧を取得
        list_url = "https://race.netkeiba.com/top/race_list.html"
        resp = requests.get(list_url, headers=HEADERS)
        resp.encoding = 'EUC-JP'
        soup = BeautifulSoup(resp.text, 'html.parser')

        target_race_id = None
        
        # ページ内のレースリストを探す
        race_list_divs = soup.find_all('div', class_='RaceList_Box')
        
        for div in race_list_divs:
            # 会場名を取得
            place_header = div.find('div', class_='RaceList_DataHeader')
            if not place_header:
                continue
            
            place_name = place_header.text.strip()
            
            # ユーザーが指定した場所が含まれているか
            if place in place_name:
                # その会場の全レースリンクをチェック
                race_links = div.find_all('a', href=True)
                for link in race_links:
                    href = link['href']
                    # リンクテキストから数字を探す
                    race_num_span = link.find('span', class_='RaceNum')
                    
                    if race_num_span:
                        r_txt = race_num_span.text.replace('R', '').strip()
                        if str(race_num) == r_txt:
                            # ID発見！
                            if 'race_id=' in href:
                                target_race_id = href.split('race_id=')[1].split('&')[0]
                                break
            if target_race_id:
                break
        
        if not target_race_id:
            return {
                "status": "error", 
                "message": f"本日、{place} {race_num}R の開催が見つかりませんでした。",
                "horses": []
            }

        # 2. 出馬表ページを取得
        shutuba_url = f"https://race.netkeiba.com/race/shutuba.html?race_id={target_race_id}"
        resp_card = requests.get(shutuba_url, headers=HEADERS)
        resp_card.encoding = 'EUC-JP'
        soup_card = BeautifulSoup(resp_card.text, 'html.parser')

        # 3. 馬データを抽出
        horses = []
        rows = soup_card.select('tr.HorseList')

        for row in rows:
            try:
                # 枠
                waku_td = row.select_one('td.Waku')
                waku = int(waku_td.text.strip()) if waku_td and waku_td.text.strip().isdigit() else 0
                # 番
                num_td = row.select_one('td.Umaban')
                num = int(num_td.text.strip()) if num_td and num_td.text.strip().isdigit() else 0
                # 名
                name_tag = row.select_one('span.HorseName a')
                name = name_tag.text.strip() if name_tag else "データなし"
                
                horses.append({"num": num, "waku": waku, "name": name})
            except:
                continue

        if len(horses) == 0:
            return {"status": "error", "message": "出馬表データが空でした", "horses": []}

        return {
            "status": "success",
            "meta": {"place": place, "race_num": race_num},
            "horses": horses
        }

    except Exception as e:
        return {"status": "error", "message": str(e), "horses": []}
