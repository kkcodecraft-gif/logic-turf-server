# ---------------------------------------------------------
# Logic Turf Cloud Server (Real Data Version)
# ---------------------------------------------------------
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 場所名の変換辞書（netkeibaの表記に合わせる）
PLACE_MAP = {
    '札幌': '01', '函館': '02', '福島': '03', '新潟': '04',
    '東京': '05', '中山': '06', '中京': '07', '京都': '08',
    '阪神': '09', '小倉': '10'
}

@app.get("/")
def read_root():
    return {"status": "Logic Turf Real-Data Server is Running!"}

@app.get("/api/race")
def get_race_card(place: str, race_num: int):
    """
    netkeibaの「本日のレース一覧」から、指定された場所・Rの出馬表を取得する
    """
    print(f"Fetching: {place} {race_num}R")

    try:
        # 1. 今日のレース一覧ページを取得
        list_url = "https://race.netkeiba.com/top/race_list.html"
        resp = requests.get(list_url)
        resp.encoding = 'EUC-JP' # netkeibaの文字コード
        soup = BeautifulSoup(resp.text, 'html.parser')

        # 2. 指定された場所のレースIDを探す
        # htmlの中から「東京」などの文字と「11R」などのリンクを探すロジック
        target_race_id = None
        
        # 簡易検索：ページ内の全リンクから ?race_id=2024... を探す
        # ID形式: YYYY PP RR DD RR (年 場所 回 日 R)
        # 例: 2024 05 02 02 11
        
        # 場所コードを取得
        p_code = PLACE_MAP.get(place)
        if not p_code:
            # マップになければ文字そのままで探してみる（公営など）
            pass

        # レース一覧のブロックを取得
        race_list_divs = soup.find_all('div', class_='RaceList_Box')
        
        for div in race_list_divs:
            # 場所名チェック（例：東京）
            place_name_tag = div.find('div', class_='RaceList_DataHeader')
            if not place_name_tag or place not in place_name_tag.text:
                continue
            
            # その場所のレースリストから対象Rを探す
            race_links = div.find_all('a', href=True)
            for link in race_links:
                href = link['href']
                # hrefには "../race/result.html?race_id=..." や "shutuba.html..." がある
                if 'race_id=' in href:
                    # R番号チェック
                    r_text = link.find('span', class_='RaceNum')
                    if r_text and str(race_num) == r_text.text.strip():
                        target_race_id = href.split('race_id=')[1].split('&')[0]
                        break
            if target_race_id:
                break
        
        if not target_race_id:
             # 見つからない場合はエラーではなくデモデータを返す（アプリが止まらないように）
            return {"status": "error", "message": "Race not found", "horses": []}

        # 3. 出馬表ページを取得
        shutuba_url = f"https://race.netkeiba.com/race/shutuba.html?race_id={target_race_id}"
        r_card = requests.get(shutuba_url)
        r_card.encoding = 'EUC-JP'
        soup_card = BeautifulSoup(r_card.text, 'html.parser')

        # 4. 馬データを抽出
        horses = []
        # 行を取得 (netkeibaのテーブル構造依存)
        rows = soup_card.select('tr.HorseList')

        for row in rows:
            try:
                # 枠番
                waku_td = row.select_one('td.Waku')
                waku = int(waku_td.text.strip()) if waku_td else 0
                
                # 馬番
                num_td = row.select_one('td.Umaban')
                num = int(num_td.text.strip()) if num_td else 0
                
                # 馬名
                name_tag = row.select_one('span.HorseName a')
                name = name_tag.text.strip() if name_tag else "取得エラー"
                
                # 騎手
                jockey_tag = row.select_one('td.Jockey a')
                jockey = jockey_tag.text.strip() if jockey_tag else "不明"

                horses.append({
                    "num": num,
                    "waku": waku,
                    "name": name,
                    "jockey": jockey
                })
            except Exception as e:
                continue

        return {
            "status": "success",
            "meta": {"place": place, "race_num": race_num, "source": "netkeiba"},
            "horses": horses
        }

    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e), "horses": []}
