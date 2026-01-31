# ---------------------------------------------------------
# Logic Turf Cloud Server
# ---------------------------------------------------------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FAMOUS_HORSES = [
    "ドウデュース", "リバティアイランド", "ジャスティンパレス", "スターズオンアース",
    "ソールオリエンス", "タスティエーラ", "ドゥレッツァ", "ベラジオオペラ",
    "ローシャムパーク", "プログノーシス", "レガレイラ", "シンエンペラー",
    "ジャンタルマンタル", "アスコリピチェーノ", "ステレンボッシュ", "チェルヴィニア"
]

@app.get("/")
def read_root():
    return {"status": "Logic Turf Server is Running!"}

@app.get("/api/race")
def get_race_card(place: str, race_num: int):
    current_horses = random.sample(FAMOUS_HORSES, 16)
    results = []
    for i in range(16):
        horse_data = {
            "num": i + 1,
            "waku": (i // 2) + 1,
            "name": current_horses[i],
            "jockey": "未定"
        }
        results.append(horse_data)
    
    return {
        "status": "success",
        "meta": {"place": place, "race_num": race_num},
        "horses": results
    }
