"""3 冊のノートブック（.ipynb）を生成する（教員用）。python make_notebooks.py"""
import json

def md(s): return {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n")}
def code(s): return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s.strip("\n")}
def nb(cells):
    return {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python (Pyodide)", "language": "python", "name": "python"},
            "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}

NB1 = [
md("""
# 01 はじめての数行：CSV を読んで、要約して、グラフにする

**この課題で体験するデータ工学的な難しさ**
1. データは「読み込んだ瞬間に型が決まる」。都道府県コード `01` が数字の `1` になっていないかを確かめる。
2. `describe()` の要約値は、Excel の AVERAGE や MEDIAN と同じもの。同じ値になるかを確かめる。
3. グラフは「並べ替えてから」描くと読める。並べ替えないグラフと比べる。

**やること**：上から順にセルを実行する（Shift + Enter）。コードは書かない。「★」のある行だけ書き換えてよい。
"""),
md("## 1. 道具を読み込む"),
code("""
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
font_manager.fontManager.addfont("../data/BIZUDPGothic-Regular.ttf")   # 日本語フォント（同梱）
plt.rcParams["font.family"] = "BIZ UDPGothic"
print("準備できました")
"""),
md("## 2. CSV を読む\n`data/todofuken_jinko.csv` は 47 都道府県の人口（2020 年国勢調査）と面積（km²）。出典は `data/SOURCES.md`。"),
code("""
df = pd.read_csv("../data/todofuken_jinko.csv", dtype={"都道府県コード": str})
df.head()   # 先頭 5 行
"""),
md("## 3. 型を確かめる\n`都道府県コード` が文字列（object）になっているか。数値になっていると `01` の 0 が消える。"),
code("""
df.dtypes
"""),
md("## 4. 要約する（Excel の AVERAGE・MEDIAN・MAX と同じ値になるか）"),
code("""
df.describe()
"""),
md("## 5. 人口密度を計算して列を足す\n人口 ÷ 面積。Excel なら 1 列ぶん数式をコピーするところ。"),
code("""
df["人口密度"] = df["人口_2020"] / df["面積_km2"]
df.sort_values("人口密度", ascending=False).head(10)
"""),
md("## 6. 棒グラフ 1 枚\n★ `列名` を `\"人口_2020\"` や `\"面積_km2\"` に書き換えて、別の列でも描いてみる。"),
code("""
列名 = "人口密度"   # ★ ここを書き換える
上位 = df.sort_values(列名, ascending=False).head(15)
plt.figure(figsize=(10, 4))
plt.bar(上位["都道府県"], 上位[列名])
plt.xticks(rotation=60)
plt.title(f"{列名} 上位 15（2020 年）")
plt.tight_layout()
plt.show()
"""),
md("""
## 7. 確かめること（提出用に 3 行で書く）
- `describe()` の人口の平均は、Excel で AVERAGE を取った値と一致したか。
- 人口密度 1 位はどこか。面積 1 位はどこか。同じ都道府県か。
- 並べ替えずに描いたグラフ（`上位 = df.head(15)` に変えて実行）と比べて、どちらが読みやすいか。
"""),
]

NB2 = [
md("""
# 02 2 つの表を結合して、人口あたりに直す

**この課題で体験するデータ工学的な難しさ**
1. 2 つの表を「都道府県名」でつなぐとき、表記が少し違うだけでつながらない（「東京」と「東京都」、末尾の空白、旧字体）。
2. つながらなかった行は黙って消える。だから **結合のあとに行数を数える**。
3. 「病院数が多い県」と「人口あたり病院数が多い県」は別物。比べるときは分母を揃える。

**やること**：上から順に実行。「★」の行だけ書き換えてよい。
"""),
md("## 1. 2 つの表を読む"),
code("""
import pandas as pd
jinko = pd.read_csv("../data/todofuken_jinko.csv", dtype={"都道府県コード": str})
byoin = pd.read_csv("../data/todofuken_byoin.csv")
print(len(jinko), "行と", len(byoin), "行")
byoin.head(8)
"""),
md("## 2. そのまま結合してみる（失敗を見る）\n`merge` は Excel の VLOOKUP／XLOOKUP と同じ発想。キーが一致した行だけ残る（inner）。"),
code("""
結合1 = jinko.merge(byoin, left_on="都道府県", right_on="都道府県名", how="inner")
print("結合できた行数:", len(结合1) if False else len(結合1), "/ 47")
"""),
md("## 3. 結合できなかった行はどれか（必ず確かめる）\n`how=\"left\"` にすると、相手が見つからない行も残り、病院数が空（NaN）になる。"),
code("""
確認 = jinko.merge(byoin, left_on="都道府県", right_on="都道府県名", how="left")
確認[確認["病院数"].isna()][["都道府県コード", "都道府県"]]
"""),
md("## 4. 相手の表の表記を見る\n空白や「都・府・県」の有無、旧字体が混ざっていないか。`repr` で見ると空白が見える。"),
code("""
for 名前 in byoin["都道府県名"]:
    if 名前 not in set(jinko["都道府県"]):
        print(repr(名前))
"""),
md("## 5. キーを正規化する\n前後の空白（全角も）を取り、「都・府・県」を補い、旧字体を直す。正規化は **新しい列** に入れて、元の列は残す。"),
code("""
def 正規化(s):
    s = str(s).replace("\\u3000", " ").strip()
    s = s.replace("沖繩", "沖縄")
    if s == "北海道":
        return s
    if s in ("東京",):
        return "東京都"
    if s in ("大阪", "京都"):
        return s + "府"
    if not s.endswith(("都", "府", "県")):
        return s + "県"
    return s

byoin["都道府県_正規化"] = byoin["都道府県名"].map(正規化)
結合2 = jinko.merge(byoin, left_on="都道府県", right_on="都道府県_正規化", how="left")
print("病院数が空の行数:", 結合2["病院数"].isna().sum(), "（0 になれば成功）")
"""),
md("## 6. 人口 10 万人あたりに直す"),
code("""
結合2["病院数_10万人あたり"] = 結合2["病院数"] / 結合2["人口_2020"] * 100000
列 = ["都道府県", "人口_2020", "病院数", "病院数_10万人あたり"]
print("--- 病院数そのもの 上位 5")
display(結合2.sort_values("病院数", ascending=False)[列].head(5))
print("--- 人口 10 万人あたり 上位 5")
display(結合2.sort_values("病院数_10万人あたり", ascending=False)[列].head(5))
print("--- 人口 10 万人あたり 下位 5")
display(結合2.sort_values("病院数_10万人あたり", ascending=True)[列].head(5))
"""),
md("""
## 7. 確かめること（提出用に 3 行で書く）
- 正規化しないと何県が消えたか。消えたことに気づく方法は何だったか。
- 「病院数 上位 5」と「10 万人あたり 上位 5」で顔ぶれはどう変わったか。どちらが「病院が身近な県」を表すか。
- ★ 分母を `面積_km2` に変えて（`* 100` にして 100 km² あたり）実行すると、順位はどう変わるか。
"""),
]

NB3 = [
md("""
# 03 散布図と相関係数：Excel の CORREL と同じ値になるか

**この課題で体験するデータ工学的な難しさ**
1. 相関係数は道具が変わっても同じ値になるはず。Excel の分析ツール（第 8 回）と照合して「再現できた」と言えるようにする。
2. 人口が多い県は何でも多い。「人口あたり」に直すと相関は消えるか、残るか。
3. 相関があっても因果ではない。散布図の外れ値（東京都）を除くとどうなるかを見る。

**やること**：上から順に実行。「★」の行だけ書き換えてよい。
"""),
md("## 1. 表を読む\n人口・面積・病院数・医師数（すべて 2020 年、出典は `data/SOURCES.md`）。"),
code("""
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
font_manager.fontManager.addfont("../data/BIZUDPGothic-Regular.ttf")   # 日本語フォント（同梱）
plt.rcParams["font.family"] = "BIZ UDPGothic"
df = pd.read_csv("../data/todofuken_iryo.csv", dtype={"都道府県コード": str})
df.head()
"""),
md("## 2. 2 つの列を選んで散布図\n★ `x` と `y` を別の列名に書き換える。使える列：`人口_2020` `面積_km2` `病院数_2020` `医師数_2020`"),
code("""
x = "人口_2020"     # ★
y = "医師数_2020"   # ★
plt.figure(figsize=(6, 5))
plt.scatter(df[x], df[y])
for _, r in df.iterrows():
    plt.annotate(r["都道府県"], (r[x], r[y]), fontsize=7)
plt.xlabel(x); plt.ylabel(y); plt.title(f"{x} と {y}")
plt.tight_layout(); plt.show()
"""),
md("## 3. 相関係数（Excel の `=CORREL(範囲1, 範囲2)` と同じ計算）\nExcel で同じ 2 列の CORREL を取り、小数第 4 位まで一致するか確かめる。"),
code("""
r = df[x].corr(df[y])
print(f"{x} と {y} の相関係数 r = {r:.4f}")
"""),
md("## 4. 全部の組み合わせを一度に見る（相関行列）"),
code("""
df[["人口_2020", "面積_km2", "病院数_2020", "医師数_2020"]].corr().round(3)
"""),
md("## 5. 人口あたりに直すと相関は残るか\n「多い県は何でも多い」を取り除く。"),
code("""
df["病院数_10万人あたり"] = df["病院数_2020"] / df["人口_2020"] * 100000
df["医師数_10万人あたり"] = df["医師数_2020"] / df["人口_2020"] * 100000
print("そのまま      r =", round(df["病院数_2020"].corr(df["医師数_2020"]), 4))
print("10万人あたり  r =", round(df["病院数_10万人あたり"].corr(df["医師数_10万人あたり"]), 4))
"""),
md("## 6. 外れ値を除くと\n★ 除く都道府県を書き換える。"),
code("""
除く = ["東京都"]   # ★
sub = df[~df["都道府県"].isin(除く)]
print("除く前 r =", round(df[x].corr(df[y]), 4))
print("除いた後 r =", round(sub[x].corr(sub[y]), 4))
"""),
md("""
## 7. 確かめること（提出用に 3 行で書く）
- Excel の CORREL（または分析ツールの相関）と、ここで出た r は一致したか。一致しなければ、どの範囲を選んだかを見直す。
- 人口あたりに直すと、病院数と医師数の相関はどう変わったか。それは何を意味するか。
- 相関が強い組み合わせに「原因と結果」があると言えるか。言えないとしたら、何が両方を増やしているか。
"""),
]
NB2[3] = code("""
結合1 = jinko.merge(byoin, left_on="都道府県", right_on="都道府県名", how="inner")
print("結合できた行数:", len(結合1), "/ 47")
""")

for name, cells in [("01_hajimete.ipynb", NB1), ("02_ketsugo.ipynb", NB2), ("03_sokan.ipynb", NB3)]:
    with open(f"notebooks/{name}", "w", encoding="utf-8") as f:
        json.dump(nb(cells), f, ensure_ascii=False, indent=1)
    print("wrote", name)
