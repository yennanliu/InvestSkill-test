"""Pages and manifest for the live showcase (``docs/showcase/live/``).

Layout — every run is kept, one directory per run:

    live/index.html                  the archive: every showcase, newest first
    live/runs.json                   the manifest the index is rendered from
    live/assets/live.css, live.js    shared by every page, rewritten each run
    live/<yyyymmdd>/show_case.html   one showcase (``<yyyymmdd>-<ticker>`` when a
                                     second ticker runs on the same day)
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

from . import mdhtml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "showcase"))   # flat modules: shell
import shell  # noqa: E402  (the curated showcase's CSS / JS, reused as-is)

LIVE_DIR = REPO / "docs" / "showcase" / "live"
MANIFEST = "runs.json"
HISTORY_CAP = 1500        # about six years of weekday runs
PAGE_NAME = "show_case.html"
LANDING = REPO / "docs" / "index.html"
LANDING_START, LANDING_END = "<!-- live-runs:start -->", "<!-- live-runs:end -->"
FAILED_PREFIX = "_模組生成失敗"

GH = shell.GH
IS = shell.IS

CSS_EXTRA = """
.lv-code{background:#0f1720;color:#e6edf3;border-radius:10px;padding:14px 16px;overflow-x:auto;
font-size:.8125rem;line-height:1.5;margin-block:var(--s-16)}
.lv-code code{background:none;border:0;padding:0;color:inherit;white-space:pre}
.doc blockquote{border-left:4px solid var(--line);margin:var(--s-16) 0;padding:2px var(--s-16);
color:var(--ink-2)}
.doc hr{border:0;border-top:1px solid var(--line);margin-block:var(--s-24)}
.lv-mod>h2{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
.lv-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(232px,1fr));gap:var(--s-16);
margin-top:var(--s-16)}
.lv-card{display:flex;flex-direction:column;gap:6px;padding:var(--s-16);border:1px solid var(--line);
border-radius:14px;background:#fff;color:inherit;text-decoration:none;transition:transform .15s,box-shadow .15s}
.lv-card:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(16,24,40,.10);text-decoration:none}
.lv-card__d{font-size:.75rem;color:var(--ink-3);font-family:var(--mono)}
.lv-card__t{font-family:var(--display);font-weight:800;font-size:1.35rem;line-height:1.1}
.lv-card__n{font-size:.8125rem;color:var(--ink-2);min-height:1.2em}
.lv-card__m{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-top:4px;
font-size:.8125rem;color:var(--ink-2)}
.lv-card__s{font-family:var(--display);font-weight:800;font-size:1.05rem;color:var(--ink)}
.lv-month{margin-top:var(--s-32);font-family:var(--display);font-weight:800;font-size:1rem;
color:var(--ink-2)}
.lv-filter{display:flex;flex-wrap:wrap;gap:8px;margin-top:var(--s-16)}
.lv-filter button{font:inherit;font-size:.8125rem;font-weight:600;padding:5px 12px;border-radius:999px;
border:1px solid var(--line);background:#fff;color:var(--ink-2);cursor:pointer}
.lv-filter button[aria-pressed="true"]{background:var(--green);border-color:var(--green);color:#fff}
.lv-pager{display:flex;justify-content:space-between;gap:var(--s-16);flex-wrap:wrap;
margin-top:var(--s-32);padding-top:var(--s-24);border-top:1px solid var(--line);font-weight:600}
[hidden]{display:none!important}
"""

_FOOTER = re.compile(r'\{\s*"investskill"\s*:.*?\}', re.S)
_BOX_SIGNAL = re.compile(r"Signal:\s*(BULLISH|NEUTRAL|BEARISH)")
_BOX_SCORE = re.compile(r"Score:\s*(\d+(?:\.\d+)?)\s*/\s*10")
_BOX_ACTION = re.compile(r"Action:\s*(BUY|HOLD|SELL)")
_BOX_CONF = re.compile(r"Confidence:\s*(HIGH|MEDIUM|LOW)")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


# ── signal parsing ──────────────────────────────────────────────────────────
def parse_signal(text: str) -> dict:
    """Read a module's result from its JSON footer, else from the signal box.

    Returns ``{}`` when neither is present: a module whose output carries no
    machine-readable signal is reported as such, never given a default.
    """
    for raw in reversed(_FOOTER.findall(text or "")):
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        score = data.get("score")
        out = {k: data[k] for k in ("signal", "action", "confidence", "horizon")
               if isinstance(data.get(k), str)}
        if isinstance(score, (int, float)) and not isinstance(score, bool) and 0 <= score <= 10:
            out["score"] = float(score)
        if out:
            out["source"] = "json"
            return out
    out = {}
    for key, pattern in (("signal", _BOX_SIGNAL), ("action", _BOX_ACTION),
                         ("confidence", _BOX_CONF)):
        m = pattern.search(text or "")
        if m:
            out[key] = m.group(1)
    m = _BOX_SCORE.search(text or "")
    if m and 0 <= float(m.group(1)) <= 10:
        out["score"] = float(m.group(1))
    if out:
        out["source"] = "box"
    return out


def module_record(slug: str, label: str, content: str) -> dict:
    if (content or "").lstrip().startswith(FAILED_PREFIX):
        return {"slug": slug, "label": label, "status": "failed"}
    rec = {"slug": slug, "label": label, "status": "ok"}
    rec.update({k: v for k, v in parse_signal(content).items() if k != "source"})
    return rec


def mean_score(modules: list[dict]) -> tuple[float | None, int]:
    scores = [m["score"] for m in modules if m.get("status") == "ok" and "score" in m]
    return (round(sum(scores) / len(scores), 2), len(scores)) if scores else (None, 0)


# ── manifest ────────────────────────────────────────────────────────────────
def load_manifest(live_dir: Path = LIVE_DIR) -> dict:
    path = live_dir / MANIFEST
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"runs": []}


def sort_runs(runs: list[dict]) -> list[dict]:
    """Newest first; a same-day pair keeps a stable order by ticker."""
    return sorted(runs, key=lambda r: (r["date"], r["ticker"]), reverse=True)


def page_for(runs: list[dict], ticker: str, date: str) -> str:
    """The run's page path, relative to the live directory.

    ``<yyyymmdd>/show_case.html``. A re-run of the same ticker on the same day
    reuses its directory; a different ticker on a day that already has a
    showcase gets ``<yyyymmdd>-<ticker>/``.
    """
    for run in runs:
        if run["ticker"] == ticker and run["date"] == date:
            return run["page"]
    slot = date.replace("-", "")
    taken = {run["page"].split("/")[0] for run in runs}
    if slot in taken:
        slot = f"{slot}-{ticker.lower()}"
    return f"{slot}/{PAGE_NAME}"


def write_assets(live_dir: Path = LIVE_DIR) -> None:
    """The stylesheet and script every live page links to (kept out of the pages
    so an archive of hundreds of runs does not repeat them)."""
    assets = live_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "live.css").write_text(shell.CSS + CSS_EXTRA, encoding="utf-8")
    (assets / "live.js").write_text(shell.JS + LIVE_JS, encoding="utf-8")


def save_manifest(manifest: dict, live_dir: Path = LIVE_DIR) -> None:
    live_dir.mkdir(parents=True, exist_ok=True)
    manifest["runs"] = sort_runs(manifest["runs"])[:HISTORY_CAP]
    (live_dir / MANIFEST).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def latest_per_ticker(runs: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out = []
    for run in runs:                              # newest first
        if run["ticker"] not in seen:
            seen.add(run["ticker"])
            out.append(run)
    return out


# ── shared chrome ───────────────────────────────────────────────────────────
# ``up`` is the path from the page to the live directory: "" for the index,
# "../" for a showcase one directory down.
LIVE_JS = r"""
(function(){
  /* archive filter: buttons narrow the cards to one ticker */
  var bar=document.querySelector('.lv-filter');
  if(bar){
    bar.hidden=false;
    bar.addEventListener('click',function(e){
      var b=e.target.closest('button'); if(!b) return;
      var want=b.getAttribute('data-t');
      bar.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});
      document.querySelectorAll('.lv-card').forEach(function(c){
        c.hidden=!!want && c.getAttribute('data-t')!==want;});
      document.querySelectorAll('.lv-group').forEach(function(g){
        g.hidden=!g.querySelector('.lv-card:not([hidden])');});
    });
  }
  /* a showcase page learns its newer neighbour from the manifest, so an old
     page never has to be re-rendered when a new run is published */
  var pager=document.querySelector('.lv-pager[data-page]');
  if(pager && window.fetch){
    fetch('../runs.json').then(function(r){return r.json()}).then(function(m){
      var runs=m.runs||[], here=pager.getAttribute('data-page');
      for(var i=0;i<runs.length;i++){
        if(runs[i].page===here && i>0){
          var n=runs[i-1], a=pager.querySelector('.lv-newer');
          a.href='../'+n.page; a.textContent=n.date+' · '+n.ticker+' →'; a.hidden=false;
        }
      }
    }).catch(function(){});
  }
})();
"""


def _nav(active: str, up: str) -> str:
    items = [(f"{up}../index.html", "展示櫃總覽", "hub"), (f"{up}index.html", "所有即時展示", "live")]
    links = "".join(
        f'<a href="{h}"{shell.CURRENT_ATTR if key == active else ""}>{t}</a>' for h, t, key in items)
    return f"""<header class="nav"><div class="wrap nav__in">
<a class="brand" href="{up}../../index.html"><span class="brand__mark">{shell.MARK}</span>
<span class="brand__text">InvestSkill Autopilot</span></a>
<nav class="nav__links" aria-label="展示頁面">{links}</nav>
<a class="btn btn--sm nav__cta" href="{GH}"><span class="nav__cta-label">GitHub</span></a>
</div><div class="prog" aria-hidden="true"><i></i></div></header>"""


def _page(title: str, desc: str, body: str, *, up: str = "", active: str = "",
          model_written: bool = False) -> str:
    origin = '<meta name="content-origin" content="model-written">\n' if model_written else ""
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#00b14f">
<meta name="robots" content="index,follow">
{origin}<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800&family=Inter:wght@400;500;600;700&family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}assets/live.css">
<script>document.documentElement.className="js"</script>
</head>
<body>
<a class="skip" href="#main">跳至主要內容</a>
{_nav(active, up)}
<main id="main">
{body}
</main>
<footer class="foot"><div class="wrap">
<p><strong>InvestSkill Autopilot — 即時展示</strong>　·　每次執行都取用當時最新的
<a href="{IS}">InvestSkill</a> 框架，隨機挑選一檔標的，由 LLM 依 yfinance 公開資料生成；每一次都保留。</p>
<p style="margin-top:8px"><a href="{up}index.html">所有即時展示</a>　·　<a href="{up}../index.html">策展展示櫃</a>　·　<a href="{GH}">原始碼與報告存檔</a></p>
<div class="disc"><strong>免責聲明</strong>　本頁為框架能力展示，並非投資建議。內容由大型語言模型自動生成、
<strong>未經人工審閱</strong>，數字未經逐一重算，可能有錯誤、過時或前後不一致之處。
任何投資決策前請自行查證第一手文件（SEC EDGAR、公司投資人關係網站）。</div>
</div></footer>
<script src="{up}assets/live.js"></script>
</body>
</html>
"""


_SIGNAL_KIND = {"BULLISH": "good", "NEUTRAL": "neut", "BEARISH": "bad"}


def _signal_chip(rec: dict) -> str:
    signal = rec.get("signal")
    if not signal:
        return '<span class="st st--neut">▬ 未解析</span>'
    return shell_st(_SIGNAL_KIND.get(signal, "neut"), signal)


def shell_st(kind: str, text: str) -> str:
    icon = {"good": "✅", "warn": "⚠", "bad": "🚩", "neut": "▬"}[kind]
    return f'<span class="st st--{kind}">{icon} {esc(text)}</span>'


def _score(rec: dict) -> str:
    return f"{rec['score']:.1f}" if "score" in rec else "—"


def _headline(run: dict) -> tuple[str, str]:
    """(value, note) for the headline tile — the synthesis signal, else the mean."""
    if "score" in run:
        return f"{run['score']:.1f}", "／10 · 綜合結論的訊號框"
    if run.get("mean_score") is not None:
        return (f"{run['mean_score']:.1f}",
                f"／10 · {run['mean_n']} 個模組分數的算術平均（未加權，非框架的綜合評分）")
    return "—", "綜合結論未附可解析的訊號框"


# ── per-ticker page ─────────────────────────────────────────────────────────
def render_report(run: dict, sections: list[tuple[str, str]], synthesis: str,
                  older: dict | None = None) -> str:
    ticker = run["ticker"]
    mods = run["modules"]
    ok = [m for m in mods if m["status"] == "ok"]
    failed = [m for m in mods if m["status"] == "failed"]
    missing = [m for m in mods if m["status"] == "missing"]
    value, note = _headline(run)
    kind = "ETF／基金" if run["kind"] == "etf" else "個股"
    title = f"{ticker} — {run['name']}" if run.get("name") else ticker
    version = run.get("skill_version") or "—"
    commit = (run.get("skill_commit") or "")[:7] or "—"

    rows = ""
    for n, m in enumerate(mods, 1):
        if m["status"] == "ok":
            cells = (f'<td style="text-align:left">{_signal_chip(m)}</td>'
                     f'<td style="text-align:right">{_score(m)}</td>'
                     f'<td style="text-align:left">{esc(m.get("action", "—"))}</td>'
                     f'<td style="text-align:left">{esc(m.get("confidence", "—"))}</td>')
            name = f'<a href="#m{n}"><code>{esc(m["slug"])}</code></a>'
        else:
            why = "未評估 — 生成失敗" if m["status"] == "failed" else "未評估 — 上游沒有這個框架"
            cells = f'<td colspan="4" style="text-align:left">{shell_st("warn", why)}</td>'
            name = f'<code>{esc(m["slug"])}</code>'
        rows += (f'<tr><td style="text-align:right;color:var(--ink-3)">{n}</td>'
                 f'<th scope="row" style="text-align:left">{name}</th>'
                 f'<td style="text-align:left">{esc(m["label"])}</td>{cells}</tr>')

    body = [f"""<section class="rhero"><div class="wrap rhero__in">
<p class="crumb"><a href="../../../index.html">InvestSkill Autopilot</a> ／ <a href="../../index.html">展示櫃</a> ／ <a href="../index.html">即時展示</a> ／ {esc(run["date"])} · {esc(ticker)}</p>
<p class="eyebrow">live run · {esc(run["mode"])} · {len(ok)} of {len(mods)} modules · zh-TW</p>
<h1>{esc(title)}</h1>
<p class="rhero__sub">{esc(run["date"])} 的自動實跑。使用 InvestSkill v{esc(version)}（{esc(commit)}），
由 {esc(run["provider"])}／{esc(run["model"])} 生成，未經人工審閱。</p>
<div class="grid g4" style="margin-top:var(--s-32)">
<div class="tile" style="background:rgba(255,255,255,.10);border-color:rgba(255,255,255,.28)"><div class="tile__k" style="color:#9ce8bd">類型</div><div class="tile__v" style="color:#fff">{kind}</div>
<div class="tile__n" style="color:rgba(255,255,255,.82)">{esc(run["mode"])}</div></div>
<div class="tile" style="background:rgba(255,255,255,.10);border-color:rgba(255,255,255,.28)"><div class="tile__k" style="color:#9ce8bd">分數</div><div class="tile__v" style="color:#fff">{value}</div>
<div class="tile__n" style="color:rgba(255,255,255,.82)">{note}</div></div>
<div class="tile" style="background:rgba(255,255,255,.10);border-color:rgba(255,255,255,.28)"><div class="tile__k" style="color:#9ce8bd">模組</div><div class="tile__v" style="color:#fff">{len(ok)}／{len(mods)}</div>
<div class="tile__n" style="color:rgba(255,255,255,.82)">{len(failed)} 個生成失敗 · {len(missing)} 個上游缺少</div></div>
<div class="tile" style="background:rgba(255,255,255,.10);border-color:rgba(255,255,255,.28)"><div class="tile__k" style="color:#9ce8bd">InvestSkill</div><div class="tile__v" style="color:#fff">v{esc(version)}</div>
<div class="tile__n" style="color:rgba(255,255,255,.82)">commit {esc(commit)}</div></div>
</div></div></section>"""]

    toc_mods = [(f"m{m['n']}", m["label"]) for m in mods_with_sections(mods)]
    toc = shell.toc([(None, [("sources", "資料來源"), ("scorecard", "模組一覽"),
                             ("verdict", "綜合結論")]),
                     ("模組", [(a, esc(l)) for a, l in toc_mods])])
    body.append(f"""<div class="wrap shell">{toc}<article class="doc">
<section id="sources"><h2>資料來源</h2>
<div class="call call--ink"><div class="call__h">📋 Data &amp; Sources — 資料來源與可信度</div>
<div class="tblwrap"><table class="dt dt--sm"><tbody>
<tr><th scope="row" style="width:112px;text-align:left">As of</th><td style="text-align:left">{esc(run["date"])}（執行當下的 yfinance 快照）</td></tr>
<tr><th scope="row" style="text-align:left">Source</th><td style="text-align:left">yfinance（Yahoo Finance）：報價、TTM 財務數據、四個會計年度損益表與現金流量表、近六個月價格</td></tr>
<tr><th scope="row" style="text-align:left">Retrieval</th><td style="text-align:left">程式化擷取 · 單次快照 · 本頁所有模組共用同一份資料</td></tr>
<tr><th scope="row" style="text-align:left">Confidence</th><td style="text-align:left">LOW — 資料商資料、LLM 生成、未經人工審閱，數字未逐一重算</td></tr>
</tbody></table></div></div>
<div class="call call--warn"><div class="call__h">這一頁與策展展示櫃有什麼不同</div>
<p><a href="../../index.html">策展展示櫃</a>的每個數字都由程式從固定快照重算，並經 CI 逐位元組比對。
本頁沒有這層保證：它是把當時最新的 InvestSkill 框架原樣交給模型的結果，用來觀察框架在不同標的上的實際輸出。
各模組的分數與訊號直接取自該模組輸出末端的訊號框或 JSON footer；沒有的就標示「未解析」，不補中性值。</p></div>
</section>
<section id="scorecard"><h2>模組一覽</h2>
<div class="tblwrap"><table class="dt dt--sm">
<thead><tr><th scope="col" style="text-align:right;width:44px">#</th><th scope="col" style="text-align:left">框架</th>
<th scope="col" style="text-align:left">模組</th><th scope="col" style="text-align:left">訊號</th>
<th scope="col" style="text-align:right">分數</th><th scope="col" style="text-align:left">動作</th>
<th scope="col" style="text-align:left">信心</th></tr></thead><tbody>{rows}</tbody></table></div>
</section>
<section id="verdict"><h2>綜合結論</h2>
{mdhtml.convert(synthesis)}
</section>""")

    for n, ((label, content), m) in enumerate(zip(sections, mods_with_sections(mods)), 1):
        tag = f'<span class="skilltag">{esc(m["slug"])}</span>'
        if m["status"] == "failed":
            inner = ('<div class="call call--warn"><p>這個模組生成失敗，未評估。'
                     '它不計入任何分數，也不以中性值替代。</p></div>')
        else:
            inner = mdhtml.convert(content)
        body.append(f'<section class="lv-mod" id="m{m["n"]}"><h2>{esc(label)} {tag}</h2>\n'
                    f'{inner}\n</section>')

    if older:
        older_link = (f'<a href="../{esc(older["page"])}">← {esc(older["date"])} · '
                      f'{esc(older["ticker"])}</a>')
    else:
        older_link = "<span></span>"
    body.append(f'<nav class="lv-pager" data-page="{esc(run["page"])}" aria-label="其他展示">'
                f'{older_link}<a href="../index.html">所有即時展示</a>'
                f'<a class="lv-newer" href="../index.html" hidden>較新的展示 →</a></nav>')
    body.append("</article></div>")
    return _page(f"{ticker} 即時展示 {run['date']} — InvestSkill Autopilot",
                 f"{ticker} 於 {run['date']} 以 InvestSkill v{version} 自動生成的{kind}分析（{len(ok)} 個模組，LLM 生成、未經審閱）。",
                 "\n".join(body), up="../", model_written=True)


def mods_with_sections(mods: list[dict]) -> list[dict]:
    """Modules that have a section (ok or failed), each tagged with its table row number."""
    out = []
    for n, m in enumerate(mods, 1):
        if m["status"] != "missing":
            out.append({**m, "n": n})
    return out


# ── index ───────────────────────────────────────────────────────────────────
_MONTH = re.compile(r"^(\d{4})-(\d{2})")


def _card(run: dict, prefix: str = "") -> str:
    value, _ = _headline(run)
    ok = sum(1 for m in run["modules"] if m["status"] == "ok")
    return (f'<a class="lv-card" data-t="{esc(run["ticker"])}" href="{prefix}{esc(run["page"])}">'
            f'<span class="lv-card__d">{esc(run["date"])}</span>'
            f'<span class="lv-card__t">{esc(run["ticker"])}</span>'
            f'<span class="lv-card__n">{esc(run.get("name") or ("ETF／基金" if run["kind"] == "etf" else "個股"))}</span>'
            f'<span class="lv-card__m">{_signal_chip(run)}<span class="lv-card__s">{value}</span></span>'
            f'<span class="lv-card__m"><span>{ok}／{len(run["modules"])} 模組</span>'
            f'<span>v{esc(run.get("skill_version") or "—")}</span></span></a>')


def render_index(manifest: dict, universe: tuple[str, ...]) -> str:
    runs = sort_runs(manifest.get("runs", []))
    latest = latest_per_ticker(runs)
    done = {r["ticker"] for r in latest}
    waiting = [t for t in universe if t not in done]

    if runs:
        newest = runs[0]
        value, note = _headline(newest)
        feature = f"""<a class="card" href="{esc(newest["page"])}" style="display:block;margin-top:var(--s-24)">
<div class="card__h">最新一次 · {esc(newest["date"])}</div>
<p style="font-family:var(--display);font-weight:800;font-size:1.6rem;margin:4px 0">{esc(newest["ticker"])}
<span style="font-weight:600;font-size:1rem;color:var(--ink-2)">{esc(newest.get("name") or "")}</span></p>
<p>{_signal_chip(newest)}　分數 <strong>{value}</strong> <span style="color:var(--ink-3)">{note}</span></p>
<p style="color:var(--ink-3);font-size:.8125rem">InvestSkill v{esc(newest.get("skill_version") or "—")} · {esc(newest["mode"])} · {esc(newest["model"])}</p></a>"""

        tickers = sorted({r["ticker"] for r in runs})
        buttons = '<button type="button" data-t="" aria-pressed="true">全部</button>' + "".join(
            f'<button type="button" data-t="{esc(t)}" aria-pressed="false">{esc(t)} '
            f'<span style="opacity:.7">{sum(1 for r in runs if r["ticker"] == t)}</span></button>'
            for t in tickers)
        groups, current = [], None
        for run in runs:
            month = run["date"][:7]
            if month != current:
                if current is not None:
                    groups.append("</div></div>")
                m = _MONTH.match(run["date"])
                label = f"{m.group(1)} 年 {int(m.group(2))} 月" if m else month
                groups.append(f'<div class="lv-group"><h3 class="lv-month">{label}</h3><div class="lv-cards">')
                current = month
            groups.append(_card(run))
        groups.append("</div></div>")
        archive = (f'{feature}\n<div class="lv-filter" role="group" aria-label="依標的篩選" hidden>{buttons}</div>\n'
                   + "".join(groups))
        heading = f"全部 {len(runs)} 次展示，{len(tickers)} 檔標的"
    else:
        archive = ('<div class="call call--ink"><p>尚未有展示。排程工作流每個交易日執行一次，'
                   '第一次執行後這裡會出現結果。</p></div>')
        heading = "尚未有展示"

    if latest:
        rows = ""
        for r in latest:
            value, _ = _headline(r)
            count = sum(1 for x in runs if x["ticker"] == r["ticker"])
            rows += (f'<tr><th scope="row" style="text-align:left"><a href="{esc(r["page"])}">{esc(r["ticker"])}</a></th>'
                     f'<td style="text-align:left">{esc(r.get("name") or "—")}</td>'
                     f'<td style="text-align:left">{"ETF" if r["kind"] == "etf" else "個股"}</td>'
                     f'<td style="text-align:left">{esc(r["date"])}</td>'
                     f'<td style="text-align:left">{_signal_chip(r)}</td>'
                     f'<td style="text-align:right">{value}</td>'
                     f'<td style="text-align:right">{count}</td></tr>')
        per_ticker = f"""<section class="section"><div class="wrap">
<p class="eyebrow">依標的</p><h2>每檔標的的最近一次</h2>
<div class="tblwrap"><table class="dt dt--sm">
<thead><tr><th scope="col" style="text-align:left">標的</th><th scope="col" style="text-align:left">名稱</th>
<th scope="col" style="text-align:left">類型</th><th scope="col" style="text-align:left">最近一次</th>
<th scope="col" style="text-align:left">訊號</th><th scope="col" style="text-align:right">分數</th>
<th scope="col" style="text-align:right">累計次數</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="fignote">分數取自綜合結論的訊號框；綜合結論沒有可解析訊號框時，顯示各模組分數的未加權算術平均（頁面上會標明），並非框架的綜合評分。</p>
</div></section>"""
    else:
        per_ticker = ""

    chips = "".join(f'<span class="chip chip--ink">{esc(t)}</span>' for t in waiting) or "（全部都跑過了）"
    body = f"""<section class="rhero"><div class="wrap rhero__in">
<p class="crumb"><a href="../../index.html">InvestSkill Autopilot</a> ／ <a href="../index.html">展示櫃</a> ／ 即時展示</p>
<p class="eyebrow">live showcase · latest InvestSkill · one random ticker per run · every run kept</p>
<h1>即時展示：最新框架，隨機一檔，每次都留下</h1>
<p class="rhero__sub">每個交易日，工作流取用當時最新的 InvestSkill，從 {len(universe)} 檔標的中隨機挑一檔，
以單一 yfinance 快照跑完一組框架。每一次的結果都存成獨立的一頁（<code style="background:rgba(255,255,255,.14);border-color:rgba(255,255,255,.3);color:#fff">yyyymmdd/show_case.html</code>），不會被下一次覆蓋。</p>
</div></section>
<section class="section section--surface"><div class="wrap">
<p class="eyebrow">展示存檔</p><h2>{heading}</h2>
{archive}
</div></section>
{per_ticker}
<section class="section"><div class="wrap">
<p class="eyebrow">方法</p><h2>這些頁面是怎麼產生的</h2>
<div class="grid g2" style="margin-top:var(--s-24)">
<div class="card"><div class="card__h">1 · 同步上游</div><p>每次執行都重新 clone <a href="{IS}">InvestSkill</a> 的 <code>main</code>，
頁面上記錄當時的版本與 commit，所以每一頁都能對回產生它的框架版本。</p></div>
<div class="card"><div class="card__h">2 · 隨機挑一檔</div><p>從固定名單隨機選出，但排除最近跑過的一半，讓名單輪得完。
也可以手動指定標的。</p></div>
<div class="card"><div class="card__h">3 · 一份快照，依序執行</div><p>個股跑 <code>full-report</code> 的模組組合（預設 standard，10 個模組）；
ETF 改跑 <code>etf-analysis</code> 等 4 個模組。所有模組共用同一份資料。</p></div>
<div class="card"><div class="card__h">4 · 原樣發佈、逐次保留</div><p>分數與訊號只取自模組輸出本身。生成失敗的模組標示「未評估」，不補中性值；
成功的模組不到一半時，整次執行不發佈。發佈過的頁面不再改寫。</p></div>
</div>
<div class="call call--warn" style="margin-top:var(--s-24)"><div class="call__h">尚未輪到的標的（{len(waiting)}）</div>
<div class="chips" style="margin-top:8px">{chips}</div></div>
</div></section>"""
    return _page("即時展示存檔 — InvestSkill Autopilot 展示櫃",
                 "以最新版 InvestSkill 框架、每次隨機一檔標的自動生成的分析報告存檔，每一次執行各自保留一頁（LLM 生成、未經審閱）。",
                 body, active="live")


def write_index(manifest: dict, universe: tuple[str, ...], live_dir: Path = LIVE_DIR) -> Path:
    live_dir.mkdir(parents=True, exist_ok=True)
    write_assets(live_dir)
    path = live_dir / "index.html"
    path.write_text(render_index(manifest, universe), encoding="utf-8")
    return path


# ── landing page block ──────────────────────────────────────────────────────
def landing_block(manifest: dict, count: int = 6) -> str:
    """The "latest live showcases" tiles for docs/index.html (its own CSS)."""
    runs = sort_runs(manifest.get("runs", []))[:count]
    tiles = ""
    for run in runs:
        value, _ = _headline(run)
        ok = sum(1 for m in run["modules"] if m["status"] == "ok")
        signal = run.get("signal") or "signal not parsed"
        tiles += (f'\n      <a class="tile" href="showcase/live/{esc(run["page"])}">'
                  f'<span class="tile__count">{esc(run["date"])}</span>'
                  f'<h3>{esc(run["ticker"])}</h3>'
                  f'<p>{esc(run.get("name") or run["mode"])}</p>'
                  f'<ul class="tile__list"><li>{esc(signal)}</li><li>score {value}</li>'
                  f'<li>{ok}/{len(run["modules"])} modules</li>'
                  f'<li>InvestSkill v{esc(run.get("skill_version") or "—")}</li></ul></a>')
    total = len(manifest.get("runs", []))
    return (f'{LANDING_START}\n    <div class="tiles">{tiles}\n    </div>\n'
            f'    <p style="margin-top:var(--s-16);font-size:var(--t-14);color:var(--ink-3)">'
            f'<a href="showcase/live/index.html" style="color:var(--green-band);font-weight:600">'
            f'All {total} live showcases →</a></p>\n    {LANDING_END}')


def update_landing(manifest: dict, landing: Path = LANDING) -> bool:
    """Rewrite the marked block in docs/index.html. False if the markers are absent."""
    if not landing.exists():
        return False
    text = landing.read_text(encoding="utf-8")
    start, end = text.find(LANDING_START), text.find(LANDING_END)
    if start < 0 or end < start:
        return False
    updated = text[:start] + landing_block(manifest) + text[end + len(LANDING_END):]
    if updated != text:
        landing.write_text(updated, encoding="utf-8")
    return True
