"""CLI for the live showcase.

    python scripts/run_showcase_live.py                    # random ticker, standard depth
    python scripts/run_showcase_live.py --ticker NVDA --depth quick
    python scripts/run_showcase_live.py --from-report output/full_report/msft/<file>.md
    python scripts/run_showcase_live.py --rebuild-index    # re-render index.html only

A normal run needs the InvestSkill clone and an API key (GEMINI_API_KEY by
default). ``--from-report`` and ``--rebuild-index`` need neither.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from analysis.config import (
    ANALYSIS_TYPES,
    DEFAULT_INVEST_SKILL_DIR,
    DEFAULT_PROVIDER,
    SUPPORTED_PROVIDERS,
    TODAY,
    analysis_meta,
    depth_skills,
    provider_default,
)
from analysis.exceptions import AnalysisError
from analysis.pipeline import generate_full_report
from analysis.prompts import PromptRepo
from analysis.publish import save_full_report

from . import site
from .universe import ETF_SKILLS, UNIVERSE, pick

LIVE_DEPTHS = ("quick", "standard", "comprehensive")
DEFAULT_LIVE_DEPTH = "standard"
MIN_OK_SHARE = 0.5          # publish only if at least half the modules produced output


# ── upstream provenance ─────────────────────────────────────────────────────
def skill_version(invest_skill_dir: Path, commit: str | None = None) -> str | None:
    """InvestSkill's package.json version — at ``commit`` if given, else the checkout's."""
    raw = None
    if commit:
        try:
            raw = subprocess.run(
                ["git", "-C", str(invest_skill_dir), "show", f"{commit}:package.json"],
                capture_output=True, text=True, timeout=10, check=True).stdout
        except (OSError, subprocess.SubprocessError):
            raw = None
    if raw is None:
        path = Path(invest_skill_dir) / "package.json"
        if not path.exists():
            return None
        raw = path.read_text(encoding="utf-8")
    try:
        version = json.loads(raw).get("version")
    except ValueError:
        return None
    return version if isinstance(version, str) else None


def quote_profile(ticker: str) -> tuple[str, str | None]:
    """('etf' | 'stock', long name) from yfinance; a lookup failure means 'stock'."""
    try:
        import yfinance as yf
        info = yf.Ticker(ticker).info or {}
    except Exception:                      # network, missing package, delisted symbol
        return "stock", None
    kind = "etf" if str(info.get("quoteType", "")).upper() in ("ETF", "MUTUALFUND") else "stock"
    return kind, info.get("longName") or info.get("shortName")


# ── building a run record ───────────────────────────────────────────────────
def build_run(ticker: str, *, kind: str, name: str | None, mode: str, requested: list[str],
              ran: list[str], sections: list[tuple[str, str]], synthesis: str, provider: str,
              model: str, date: str, version: str | None, commit: str | None,
              source_md: str | None) -> dict:
    by_slug = dict(zip(ran, sections))
    modules = []
    for slug in requested:
        if slug in by_slug:
            label, content = by_slug[slug]
            modules.append(site.module_record(slug, label, content))
        else:
            modules.append({"slug": slug, "label": analysis_meta(slug)["label"],
                            "status": "missing"})
    run = {
        "ticker": ticker, "name": name, "kind": kind, "mode": mode, "date": date,
        "provider": provider, "model": model,
        "skill_version": version, "skill_commit": commit,
        "page": None, "source_md": source_md,          # page is assigned on publish
        "modules": modules,
    }
    headline = site.parse_signal(synthesis)
    run.update({k: v for k, v in headline.items() if k != "source"})
    run["mean_score"], run["mean_n"] = site.mean_score(modules)
    return run


def publish(run: dict, sections: list[tuple[str, str]], synthesis: str,
            live_dir: Path, universe: tuple[str, ...] = UNIVERSE, *,
            landing: Path | None = None) -> Path:
    """Write the run's own page, then the manifest, the index and the landing block.

    Earlier runs are never rewritten: every showcase keeps its directory.
    """
    manifest = site.load_manifest(live_dir)
    others = [r for r in manifest.get("runs", [])
              if not (r["ticker"] == run["ticker"] and r["date"] == run["date"])]
    run["page"] = site.page_for(manifest.get("runs", []), run["ticker"], run["date"])
    manifest["runs"] = site.sort_runs([run] + others)
    position = manifest["runs"].index(run)
    older = manifest["runs"][position + 1] if position + 1 < len(manifest["runs"]) else None

    page = live_dir / run["page"]
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(site.render_report(run, sections, synthesis, older), encoding="utf-8")
    site.save_manifest(manifest, live_dir)
    site.write_index(manifest, universe, live_dir)
    if landing is not None:
        site.update_landing(manifest, landing)
    return page


# ── importing an existing full-report Markdown file ─────────────────────────
_LABEL_TO_SLUG = {meta["label"]: slug for slug, meta in ANALYSIS_TYPES.items()}
_SECTION = re.compile(r"^### (\d+)\. (.+)$", re.M)


def parse_report(text: str) -> tuple[dict, str, list[tuple[str, str]]]:
    """Split a ``save_full_report`` file into (frontmatter, synthesis, sections)."""
    meta: dict[str, str] = {}
    if text.startswith("---\n"):
        head, _, text = text[4:].partition("\n---\n")
        for line in head.splitlines():
            key, sep, value = line.partition(":")
            if sep:
                meta[key.strip()] = value.strip().strip('"')
    verdict_mark, modules_mark = "## 🎯 綜合結論", "## 📑 各模組分析"
    start = text.find(verdict_mark)
    split = text.find(modules_mark)
    if start < 0 or split < 0:
        raise ValueError("not a full-report file: verdict / module headings not found")
    synthesis = text[text.index("\n", start) + 1:split].strip().rstrip("-").strip()
    body = text[text.index("\n", split) + 1:]

    # The writer numbers its own sections 1..N in order; a module's own
    # "### 1. …" heading must not be mistaken for the next section.
    sections: list[tuple[str, str]] = []
    marks = []
    expected = 1
    for m in _SECTION.finditer(body):
        if int(m.group(1)) == expected and m.group(2).strip() in _LABEL_TO_SLUG:
            marks.append(m)
            expected += 1
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        content = body[m.end():end].strip()
        content = re.sub(r"\n-{3,}\s*$", "", content).strip()
        sections.append((m.group(2).strip(), content))
    return meta, synthesis, sections


def import_report(path: Path, live_dir: Path, invest_skill_dir: Path,
                  landing: Path | None = None,
                  profiles: dict[str, tuple[str, str | None]] | None = None) -> Path:
    meta, synthesis, sections = parse_report(path.read_text(encoding="utf-8"))
    if not sections:
        raise ValueError(f"no module sections found in {path}")
    ticker = meta.get("ticker", "").upper()
    if not ticker:
        raise ValueError(f"no ticker in the frontmatter of {path}")
    ran = [_LABEL_TO_SLUG[label] for label, _ in sections]
    commit = meta.get("skill_commit") or None
    try:
        source = str(path.resolve().relative_to(site.REPO))
    except ValueError:
        source = path.name
    if profiles is None:
        kind, name = "stock", None
    else:                                   # one lookup per ticker across a batch
        if ticker not in profiles:
            profiles[ticker] = quote_profile(ticker)
        kind, name = profiles[ticker]
    run = build_run(
        ticker, kind=kind, name=name, mode=f"full-report · {len(ran)} modules",
        requested=ran, ran=ran, sections=sections, synthesis=synthesis,
        provider=meta.get("provider", "—"), model=meta.get("model", "—"),
        date=meta.get("date", TODAY),
        version=skill_version(invest_skill_dir, commit) if commit else None,
        commit=commit, source_md=source)
    return publish(run, sections, synthesis, live_dir, landing=landing)


# ── main ────────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ticker", default=None,
                    help="ticker to run (default: a random one from the universe)")
    ap.add_argument("--depth", default=DEFAULT_LIVE_DEPTH, choices=LIVE_DEPTHS,
                    help=f"full-report module set for a stock (default: {DEFAULT_LIVE_DEPTH})")
    ap.add_argument("--provider", default=DEFAULT_PROVIDER, choices=SUPPORTED_PROVIDERS)
    ap.add_argument("--model", default=None)
    ap.add_argument("--max-tokens", type=int, default=None)
    ap.add_argument("--sleep", type=float, default=1.0, help="seconds between module calls")
    ap.add_argument("--invest-skill-dir", default=str(DEFAULT_INVEST_SKILL_DIR))
    ap.add_argument("--live-dir", default=str(site.LIVE_DIR), help="where the pages are written")
    ap.add_argument("--output-dir", default=None,
                    help="where the Markdown is archived (default: output/showcase_live/<ticker>)")
    ap.add_argument("--from-report", default=None, metavar="FILE", nargs="+",
                    help="publish existing full-report Markdown files instead of generating")
    ap.add_argument("--landing", default=None,
                    help="landing page whose live-runs block is refreshed "
                         "(default: docs/index.html when --live-dir is the default)")
    ap.add_argument("--rebuild-index", action="store_true",
                    help="re-render index.html from runs.json and exit")
    ap.add_argument("--print-pick", action="store_true",
                    help="print the ticker that would be run and exit")
    args = ap.parse_args(argv)

    live_dir = Path(args.live_dir)
    invest_skill_dir = Path(args.invest_skill_dir)
    if args.landing:
        landing = Path(args.landing)
    else:
        landing = site.LANDING if live_dir.resolve() == site.LIVE_DIR.resolve() else None

    if args.rebuild_index:
        manifest = site.load_manifest(live_dir)
        path = site.write_index(manifest, UNIVERSE, live_dir)
        if landing is not None:
            site.update_landing(manifest, landing)
        print(f"✅ Index written to {path}")
        return 0

    if args.from_report:
        failures = 0
        profiles: dict[str, tuple[str, str | None]] = {}
        for source in args.from_report:
            try:
                page = import_report(Path(source), live_dir, invest_skill_dir, landing, profiles)
            except (OSError, ValueError) as exc:
                print(f"ERROR: {source}: {exc}", file=sys.stderr)
                failures += 1
                continue
            print(f"✅ Imported → {page}")
        return 1 if failures else 0

    recent = [r["ticker"] for r in site.load_manifest(live_dir).get("runs", [])]
    ticker = (args.ticker or pick(recent)).upper()
    if args.print_pick:
        print(ticker)
        return 0

    model = args.model or provider_default(args.provider, "default_model")
    max_tokens = args.max_tokens or provider_default(args.provider, "default_tokens")
    kind, name = quote_profile(ticker)
    if kind == "etf":
        requested, mode = list(ETF_SKILLS), f"etf-analysis · {len(ETF_SKILLS)} modules"
    else:
        requested = depth_skills(args.depth)
        mode = f"full-report · depth {args.depth}"
    print(f"Live showcase: {ticker} ({kind}) — {mode}, {len(requested)} modules via "
          f"{args.provider}/{model}")

    try:
        result = generate_full_report(
            ticker, provider=args.provider, model=model, max_tokens=max_tokens,
            invest_skill_dir=invest_skill_dir, skills=requested, language="zh-TW",
            sleep=args.sleep)
    except AnalysisError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    sections, ran = result["sections"], result["skills"]
    ok = sum(1 for _, content in sections
             if not content.lstrip().startswith(site.FAILED_PREFIX))
    if ok < max(1, len(requested) * MIN_OK_SHARE):
        print(f"ERROR: only {ok} of {len(requested)} modules produced output — not publishing.",
              file=sys.stderr)
        return 1

    repo = PromptRepo(invest_skill_dir)
    commit = repo.revision()
    out_dir = Path(args.output_dir) if args.output_dir else \
        Path("output") / "showcase_live" / ticker.lower()
    md_path = save_full_report(ticker, sections, result["synthesis"], out_dir,
                               args.provider, model, skill_commit=commit)
    run = build_run(
        ticker, kind=kind, name=name, mode=mode, requested=requested, ran=ran,
        sections=sections, synthesis=result["synthesis"], provider=args.provider, model=model,
        date=TODAY, version=skill_version(invest_skill_dir), commit=commit,
        source_md=str(md_path))
    page = publish(run, sections, result["synthesis"], live_dir, landing=landing)
    print(f"✅ {ticker}: {ok}/{len(requested)} modules → {page}  (Markdown: {md_path})")
    return 0
