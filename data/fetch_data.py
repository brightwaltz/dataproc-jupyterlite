"""統計ダッシュボード API（登録不要）から都道府県別データを取得して CSV にする（教員用）。

実行: python fetch_data.py   （このフォルダで）
出典: https://dashboard.e-stat.go.jp/static/api
"""
import csv
import json
import urllib.request

API = "https://dashboard.e-stat.go.jp/api/1.0/Json/getData?IndicatorCode={code}&RegionalRank=3&Time={time}"
PREF = {
    "01": "北海道", "02": "青森県", "03": "岩手県", "04": "宮城県", "05": "秋田県", "06": "山形県", "07": "福島県",
    "08": "茨城県", "09": "栃木県", "10": "群馬県", "11": "埼玉県", "12": "千葉県", "13": "東京都", "14": "神奈川県",
    "15": "新潟県", "16": "富山県", "17": "石川県", "18": "福井県", "19": "山梨県", "20": "長野県", "21": "岐阜県",
    "22": "静岡県", "23": "愛知県", "24": "三重県", "25": "滋賀県", "26": "京都府", "27": "大阪府", "28": "兵庫県",
    "29": "奈良県", "30": "和歌山県", "31": "鳥取県", "32": "島根県", "33": "岡山県", "34": "広島県", "35": "山口県",
    "36": "徳島県", "37": "香川県", "38": "愛媛県", "39": "高知県", "40": "福岡県", "41": "佐賀県", "42": "長崎県",
    "43": "熊本県", "44": "大分県", "45": "宮崎県", "46": "鹿児島県", "47": "沖縄県",
}
INDICATORS = {
    "人口_2020": ("0201010000000010000", "2020CY00"),   # 総人口（総数）国勢調査／人口推計
    "面積_km2": ("0101010000000010010", "2020CY00"),    # 総面積（北方地域及び竹島を除く）
    "病院数_2020": ("1505020000000010000", "2020CY00"),  # 病院数
    "医師数_2020": ("1505040000000010000", "2020CY00"),  # 医師数
}


def fetch(code, time):
    with urllib.request.urlopen(API.format(code=code, time=time), timeout=60) as r:
        d = json.load(r)
    objs = d["GET_STATS"]["STATISTICAL_DATA"]["DATA_INF"]["DATA_OBJ"]
    return {o["VALUE"]["@regionCode"][:2]: o["VALUE"]["$"] for o in objs}


def main():
    cols = {k: fetch(*v) for k, v in INDICATORS.items()}
    rows = []
    for code, name in PREF.items():
        row = {"都道府県コード": code, "都道府県": name}
        for k in INDICATORS:
            v = cols[k].get(code, "")
            if k == "面積_km2" and v != "":
                v = f"{int(v) / 100:.2f}"  # API の単位は ha なので km2 に直す
            row[k] = v
        rows.append(row)
    # 01 きれいな表（人口・面積）
    with open("todofuken_jinko.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["都道府県コード", "都道府県", "人口_2020", "面積_km2"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in w.fieldnames})
    # 02 わざと表記を揺らした表（病院数）: 結合の練習用。コード列は無い。
    messy = {"東京都": "東京", "大阪府": "大阪府　", "京都府": "京都", "北海道": " 北海道", "神奈川県": "神奈川",
             "鹿児島県": "鹿児島県 ", "沖縄県": "沖繩県"}
    with open("todofuken_byoin.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["都道府県名", "病院数"])
        for r in rows:
            w.writerow([messy.get(r["都道府県"], r["都道府県"]), r["病院数_2020"]])
    # 03 相関用（人口・面積・病院数・医師数）
    with open("todofuken_iryo.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["都道府県コード", "都道府県", "人口_2020", "面積_km2", "病院数_2020", "医師数_2020"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in w.fieldnames})
    print("wrote 3 csv")


if __name__ == "__main__":
    main()
