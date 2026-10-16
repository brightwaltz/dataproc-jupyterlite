"""ビルドした JupyterLite で、Python（Pyodide）が左のファイル一覧（/drive）とつながらないようにする（2026-10-16）。

JupyterLite は Service Worker の登録に成功すると、Python をファイル一覧につなぐ（mountDrive）。
ところが、登録はできてもページが Service Worker を通っていない場合（強制再読み込みの直後、Teams の中の表示など）は、
Python がファイル一覧の応答を待ち続け、ノートブックの最初のセルから [*] のまま何も出力されなかった。
ノートブックはデータとフォントをサイトから /tmp/data/ に取り込むので（make_notebooks.py）、つながなくてよい。

使い方: python patch_no_drive.py <ビルドの出力先>
置き換える箇所がちょうど 1 か所でなければ失敗する（jupyterlite-pyodide-kernel の版を上げて形が変わったら、ここを直す）。
"""
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1]) / "extensions" / "@jupyterlite" / "pyodide-kernel-extension" / "static"
pat = re.compile(r"(\w)=!!\(\(null==(\w)\?void 0:\2\.enabled\)\|\|crossOriginIsolated\)")
hits = []
for f in sorted(root.glob("*.js")):
    s = f.read_text(encoding="utf-8")
    n = len(pat.findall(s))
    if n:
        f.write_text(pat.sub(lambda m: m.group(1) + "=!1", s), encoding="utf-8")
        hits.append((f.name, n))
if sum(n for _, n in hits) != 1:
    sys.exit(f"patch_no_drive: 置き換える箇所が 1 か所ではない: {hits}")
print("patch_no_drive:", hits[0][0])
