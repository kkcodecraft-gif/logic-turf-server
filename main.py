# ---------------------------------------------------------
# Logic Turf Cloud Server (Final Version)
# ---------------------------------------------------------
from fastapi import FastAPI
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

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

@app.get("/")
def read_root():
    return {"status": "Logic Turf Server is Running!"}

@app.get("/api/race")
def get_race_card(place: str, race_num: int, date: str = None):
    print(f"★検索開始: {date} {place} {race_num}R")
    
    horses = []
    race_info = {"weather": "不明", "condition": "不明", "bias_suggestion": "D"}

    try:
        # 1. レース一覧を取得
        base_url = "https://race.netkeiba.com/top/race_list.html"
        if date:
            # YYYY-MM-DD -> YYYYMMDD
            date_param = date.replace("-", "")
            list_url = f"{base_url}?kaisai_date={date_param}"
        else:
            list_url = base_url

        resp = requests.get(list_url, headers=HEADERS, timeout=10)
        resp.encoding = 'EUC-JP'
        soup = BeautifulSoup(resp.text, 'html.parser')

        target_race_id = None
        
        # 2. 指定場所のレースIDを探す
        race_list_divs = soup.find_all('div', class_='RaceList_Box')
        for div in race_list_divs:
            place_header = div.find('div', class_='RaceList_DataHeader')
            if not place_header: continue
            
            # 場所名チェック
            if place in place_header.text.strip():
                race_links = div.find_all('a', href=True)
                for link in race_links:
                    r_span = link.find('span', class_='RaceNum')
                    if r_span:
                        r_txt = r_span.text.replace('R', '').strip()
                        # レース番号とリンクの一致を確認
                        if str(race_num) == r_txt and 'race_id=' in link['href']:
                            target_race_id = link['href'].split('race_id=')[1].split('&')[0]
                            break
            if target_race_id: break
        
        # 3. IDが見つかったら出馬表を取得
        if target_race_id:
            print(f"  -> ID発見: {target_race_id}")
            shutuba_url = f"https://race.netkeiba.com/race/shutuba.html?race_id={target_race_id}"
            resp_card = requests.get(shutuba_url, headers=HEADERS, timeout=10)
            resp_card.encoding = 'EUC-JP'
            soup_card = BeautifulSoup(resp_card.text, 'html.parser')
            
            # 馬場情報の取得
            data_div = soup_card.find('div', class_='RaceData01')
            if data_div:
                text = data_div.text.strip()
                if "天候:晴" in text: race_info["weather"] = "晴"
                elif "天候:雨" in text: race_info["weather"] = "雨"
                
                if "馬場:良" in text: race_info.update({"condition": "良", "bias_suggestion": "D"})
                elif "馬場:稍" in text: race_info.update({"condition": "稍重", "bias_suggestion": "C"})
                elif "馬場:重" in text: race_info.update({"condition": "重", "bias_suggestion": "B"})
                elif "馬場:不" in text: race_info.update({"condition": "不良", "bias_suggestion": "B"})

            # 馬データの取得
            rows = soup_card.select('tr.HorseList')
            for row in rows:
                try:
                    w_tag = row.select_one('td.Waku')
                    n_tag = row.select_one('td.Umaban')
                    name_tag = row.select_one('span.HorseName a')
                    
                    waku = int(w_tag.text.strip()) if w_tag and w_tag.text.strip().isdigit() else 0
                    num = int(n_tag.text.strip()) if n_tag and n_tag.text.strip().isdigit() else 0
                    name = name_tag.text.strip() if name_tag else "不明"
                    
                    if name != "不明":
                        horses.append({"num": num, "waku": waku, "name": name})
                except:
                    continue

    except Exception as e:
        print(f"Error: {e}")

    # 結果を返す（見つからない場合はエラーメッセージを含める）
    if not horses:
        return {
            "status": "error",
            "message": "データが見つかりませんでした。日付や場所が正しいか確認してください。",
            "horses": []
        }

    return {
        "status": "success",
        "meta": {
            "place": place, 
            "race_num": race_num, 
            "date": date,
            "race_info": race_info
        },
        "horses": horses
    }
