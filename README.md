# データ処理 発展課題サイト（JupyterLite）試作

ブラウザだけで動く Jupyter（JupyterLite、Python は Pyodide）。アカウント不要、インストール不要。
発展課題（第 8 回の相関の再現、第 6 回の 2 表の結合、第 2〜3 回の要約）で「同じ処理を数行の Python で」やるためのもの。
学生はコードを書かない。セルは全部書いてあり、「実行」と「★の行の書き換え」だけ。

このリポジトリは Claude Code（Anthropic）を使って作っています。

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
出力先は引数で渡す（例：`sh build.sh /tmp/jl-site`）。venv は環境変数 `JL_VENV` で差し替え可（`pip install jupyterlite-core jupyterlite-pyodide-kernel jupyter-server` が入っていればよい）。Drive にはビルド成果物を置かない（ファイル数が多く同期が重い）。

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
授業チャンネル上部の「＋」（タブを追加）→「Web サイト」→ タブ名「発展課題（JupyterLite）」、URL は lab のトップ（下の「公開先」の URL）→ 保存。
- タブ名は第 3・6・8 回の報告用紙の「Teams の『発展課題（JupyterLite）』タブ」と同じにする。
- URL はノートブックを指定しないトップにする。同じタブで 02・03・04 を開くため。
- 新しい Teams の Web サイトタブは、2024 年 7 月から一般の組織ではブラウザーの新しいタブで開く。教育機関は対象外と告知された（2024 年。続報は見つかっていない）。玉川のテナントでどう開くかは未確認。
- Teams の中で開いた場合とブラウザーで開いた場合では、ブラウザ内の保存場所が別になることがある。学生には「始めた場所で最後まで続ける」「数値はすぐ報告用紙に写す」と伝える。

### Pyodide の制約
- ブラウザから外部 API（統計ダッシュボード、e-Stat）を直接取りに行くと CORS で失敗しうる。**データは `data/` に同梱する**（教員が `fetch_data.py` で更新）。
- 使えるライブラリは Pyodide に含まれるもの（pandas、matplotlib、numpy など）。`import` すると自動で読み込まれる。
- 日本語フォントは同梱の TTF をノートブック冒頭で読み込む（matplotlib はそのままだと日本語が □ になる）。
- 重い処理（数十万行）は向かない。47 都道府県・数千行程度に留める。
- 学生の作業はブラウザ内保存。回収はダウンロードさせるか、回答欄に書かせる。
- **データとフォントは、ノートブックの最初のコードセルで、サイトから `/tmp/data/` に取り込んで読む**（2026-10-16）。左のファイル一覧（`../data/`）から読む方法は JupyterLite の Service Worker が要り、それが使えない環境（Teams の中の表示、InPrivate、サイトのデータを保存できない設定など）では、最初のセルが `[*]` のまま止まって何も出力されなかった（先生の PC では動き、ほかの人の PC で止まった）。Python 自体は Service Worker なしでも動く。`make_notebooks.py` の `nb()` が、本文の `"../data/○○"` を見つけて取り込みのコードを自動で入れる。あわせて、ビルドのあとに `patch_no_drive.py` で、Python を左のファイル一覧（/drive）につながないようにしている（JupyterLite は Service Worker の登録に成功するとつなぐが、登録できてもページが Service Worker を通っていない場合〔強制再読み込みの直後など〕に、つないだまま止まるため）。このため Python からは左のファイル一覧のファイルを読めない。新しいノートブックでも、データは `"../data/○○"` と書いて nb() に取り込ませる。
- Service Worker が使えない環境では、書き換えた内容もブラウザに残らないことがある。出た数値はその場で報告書に写すよう伝える（報告用紙にも書いてある）。
- Python 本体（Pyodide）とライブラリは cdn.jsdelivr.net から、一部は pypi.org・files.pythonhosted.org から読み込む。学内のネットワークでこれらが止められると動かない（10/15 に教室で開けることは確認済み）。

### 更新の流れ
1. `data/fetch_data.py` でデータ更新 →  `SOURCES.md` の取得日を直す。
2. `make_notebooks.py` を編集して `python make_notebooks.py`。
3. `sh build.sh` → 配置先に上書き。

## 公開先（GitHub Pages）

- リポジトリ：https://github.com/brightwaltz/dataproc-jupyterlite （Drive のこのフォルダが正本、GitHub は配置用）
- 公開 URL：https://brightwaltz.github.io/dataproc-jupyterlite/lab/index.html
- `main` に push すると `.github/workflows/deploy.yml` がビルドして Pages に出す。
- 特定のノートブックを直接開く URL：`lab/index.html?path=notebooks/04_yoyaku.ipynb`（WebClass の案内に載せる）。例：https://brightwaltz.github.io/dataproc-jupyterlite/lab/index.html?path=notebooks/04_yoyaku.ipynb
- Teams：上の「Teams の Web サイトタブに貼る」のとおり、タブ名「発展課題（JupyterLite）」で lab のトップの URL を貼る。学内ネットワークから届くかは教室で確認。

## 統計ダッシュボード API の URL ビルダー（第5回 発展課題）

- 公開 URL：https://brightwaltz.github.io/dataproc-jupyterlite/url-builder.html
- 正本は `授業資料2026/05データの重要性と利活用/build_urlbuilder.py`。作り直したら `site_extra/url-builder.html` に上書きコピーして push する。
- Teams の授業チャンネルに Web サイトタブ「URL ビルダー」として貼る（2026-10-22 先生作成済み。タブ名は「URLビルダー」）。
- Teams のタブは、ページの枠が見えている範囲より広く取られることがあり（Teams 自身の帯も右端で切れる）、中央寄せのページは右に寄って右側が切れた。ページは左寄せにし、見えている幅を IntersectionObserver で測ってその幅に収める（2026-10-22）。
