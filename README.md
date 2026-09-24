# データ処理 発展課題サイト（JupyterLite）試作

ブラウザだけで動く Jupyter（JupyterLite、Python は Pyodide）。アカウント不要、インストール不要。
発展課題（第 8 回の相関の再現、第 6 回の 2 表の結合、第 2〜3 回の要約）で「同じ処理を数行の Python で」やるためのもの。
学生はコードを書かない。セルは全部書いてあり、「実行」と「★の行の書き換え」だけ。

## 学生向け：使い方

1. Teams のタブ（または配布 URL）でサイトを開く。左のファイル一覧から `notebooks/01_hajimete.ipynb` を開く。
2. 上のセルから順に **Shift + Enter** で実行する。最初の 1 回だけ Python の読み込みに 30 秒〜1 分かかる。
3. 「★」と書かれた行だけ書き換えてよい（列名、都道府県名など）。書き換えたら、そのセルから下をもう一度実行する。
4. 提出は、各ノートブックの最後「確かめること」を課題の回答欄（WebClass）に書く。ノートブック自体を出すときは、ファイルを右クリック →「ダウンロード」で手元に保存してから提出する。
5. 注意：作業内容はブラウザの中にだけ保存される。ブラウザのデータを消す、別の PC で開く、シークレットウィンドウを閉じる、と消える。必要なものはダウンロードしておく。
6. 表示が崩れたら、ページを再読み込みして最初から実行し直す。

## 教員向け

### 中身
- `notebooks/`：4 冊（`01_hajimete` 読む・要約・棒グラフ／`02_ketsugo` 結合と人口あたり／`03_sokan` 散布図と相関／`04_yoyaku` 要約統計を Excel と照合（第3回 発展課題 B））。`make_notebooks.py` で生成。
- `data/`：実データ 3 つ（統計ダッシュボード API から取得、`fetch_data.py`、出典は `SOURCES.md`）と日本語フォント（BIZ UDP ゴシック、OFL）。
- `jupyter_lite_config.json`, `jupyter-lite.json`：サイト設定。
- `build.sh`：ビルド。

### ビルド
```
sh build.sh [出力先]
```
既定の出力先は Claude ジョブの tmp。venv は環境変数 `JL_VENV` で差し替え可（`pip install jupyterlite-core jupyterlite-pyodide-kernel jupyter-server` が入っていればよい）。Drive にはビルド成果物を置かない（ファイル数が多く同期が重い）。

ローカル確認：
```
cd <出力先> && python -m http.server 8765
```
http://localhost:8765/ を開く。

### 配置（公開）
- GitHub Pages：リポジトリを作り、ビルド成果物（出力先の中身）を `gh-pages` ブランチか `docs/` に置く。あるいは公式の `jupyterlite/demo` テンプレートを fork し、`content/` にこの `notebooks/` と `data/` を入れると GitHub Actions が自動でビルド・公開する。
- Vercel：出力先フォルダをそのまま静的サイトとしてデプロイ（`vercel --prod`、Framework は Other）。
- どちらも https になる。

### Teams の Web サイトタブに貼る
チャンネル上部の「＋」→「Web サイト」→ 名前「発展課題（Python）」、URL に公開 URL → 保存。
埋め込み表示できないテナント設定の場合はタブから「ブラウザーで開く」で開ける。

### Pyodide の制約
- ブラウザから外部 API（統計ダッシュボード、e-Stat）を直接取りに行くと CORS で失敗しうる。**データは `data/` に同梱する**（教員が `fetch_data.py` で更新）。
- 使えるライブラリは Pyodide に含まれるもの（pandas、matplotlib、numpy など）。`import` すると自動で読み込まれる。
- 日本語フォントは同梱の TTF をノートブック冒頭で読み込む（matplotlib はそのままだと日本語が □ になる）。
- 重い処理（数十万行）は向かない。47 都道府県・数千行程度に留める。
- 学生の作業はブラウザ内保存。回収はダウンロードさせるか、回答欄に書かせる。

### 更新の流れ
1. `data/fetch_data.py` でデータ更新 →  `SOURCES.md` の取得日を直す。
2. `make_notebooks.py` を編集して `python make_notebooks.py`。
3. `sh build.sh` → 配置先に上書き。

## 公開先（GitHub Pages）

- リポジトリ：https://github.com/brightwaltz/dataproc-jupyterlite （Drive のこのフォルダが正本、GitHub は配置用）
- 公開 URL：https://brightwaltz.github.io/dataproc-jupyterlite/lab/index.html
- `main` に push すると `.github/workflows/deploy.yml` がビルドして Pages に出す。
- Teams：授業チャンネルの「＋」→「Web サイト」→ 上の URL を貼る。学内ネットワークから届くかは教室で確認。
