#!/usr/bin/env python3
"""
upstream_sync.py — detect what changed in InvestSkill and what this sandbox must sync.

Compares a cloned InvestSkill checkout against two baselines:

  * ``investskill.lock.json`` — the upstream commit, version, and SHA-256 of every
    prompt / system-context file as of the last reviewed sync. Differences here are
    *upstream changes*: they are safe to adopt by bumping the lock.
  * ``analysis.config`` — ``ANALYSIS_TYPES``, ``DEPTH_TIERS`` and ``ALIASES``.
    Differences here are *drift*: code in this repo needs a human edit.

The ``upstream_sync.yml`` workflow runs this on a schedule (and on a
``repository_dispatch`` from upstream), opens a PR that bumps the lock with the
change log as its body, and opens an issue when there is drift.

Usage:
  python scripts/upstream_sync.py --invest-skill-dir InvestSkill
  python scripts/upstream_sync.py --invest-skill-dir InvestSkill --report sync.md --write-lock
  python scripts/upstream_sync.py --invest-skill-dir InvestSkill --check   # exit 1 on drift

No network access: the caller clones upstream (full history, or at least back to
the locked commit, for the commit log).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from analysis.config import ALIASES, ANALYSIS_TYPES, DEPTH_TIERS, INVEST_SKILL_REPO

DEFAULT_LOCK = Path(__file__).resolve().parent.parent / "investskill.lock.json"

# Files outside prompts/ that this repo reads at run time (see PromptRepo).
CONTEXT_FILES = ("GEMINI.md", "CLAUDE.md")

_TIER_HEADING = re.compile(r"^###\s+(Quick|Standard|Comprehensive)\b", re.IGNORECASE)
_TIER_ROW = re.compile(r"^\|\s*\d+\s*\|\s*`([a-z0-9-]+)`")
_ALIAS = re.compile(r"has been (?:merged|unified) into\s+`([a-z0-9-]+)`")


# ── reading the upstream checkout ────────────────────────────────────────────

def upstream_slugs(root: Path) -> list[str]:
    return sorted(p.stem for p in (root / "prompts").glob("*.md"))


def tracked_files(root: Path) -> dict[str, str]:
    """SHA-256 of every file this repo consumes, keyed by repo-relative path."""
    paths = sorted((root / "prompts").glob("*.md")) + [root / f for f in CONTEXT_FILES]
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in paths if p.is_file()
    }


def parse_depth_tiers(full_report_md: str) -> dict[str, list[str]]:
    """Read the cumulative module sets from full-report.md § "Module Sets by Depth".

    Each tier's table lists only the modules it adds, so the result is built the
    way ``analysis.config`` builds ``DEPTH_TIERS``: quick ⊂ standard ⊂ comprehensive.
    """
    added: dict[str, list[str]] = {}
    current = None
    for line in full_report_md.splitlines():
        heading = _TIER_HEADING.match(line)
        if heading:
            current = heading.group(1).lower()
            added[current] = []
            continue
        if line.startswith("## "):
            current = None
        row = _TIER_ROW.match(line)
        if current and row:
            added[current].append(row.group(1))

    tiers: dict[str, list[str]] = {}
    running: list[str] = []
    for depth in ("quick", "standard", "comprehensive"):
        if depth in added:
            running = running + added[depth]
            tiers[depth] = running
    return tiers


def detect_aliases(root: Path) -> dict[str, str]:
    """Slugs whose prompt is a redirect card ("has been merged|unified into `<target>`")."""
    aliases = {}
    for path in sorted((root / "prompts").glob("*.md")):
        head = path.read_text(encoding="utf-8")[:1000]
        match = _ALIAS.search(head)
        if match:
            aliases[path.stem] = match.group(1)
    return aliases


def upstream_version(root: Path) -> str | None:
    try:
        return json.loads((root / "package.json").read_text(encoding="utf-8")).get("version")
    except (OSError, ValueError):
        return None


def _git(root: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                             text=True, timeout=30, check=True)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip()


def git_head(root: Path) -> str | None:
    return _git(root, "rev-parse", "HEAD") or None


def git_log(root: Path, since: str | None) -> list[dict] | None:
    """Commits in ``since..HEAD`` (newest first), or None if ``since`` is unreachable."""
    if not since or _git(root, "cat-file", "-e", f"{since}^{{commit}}") is None:
        return None
    raw = _git(root, "log", "--format=%x1e%H%x1f%ad%x1f%s", "--date=short",
               "--name-only", f"{since}..HEAD")
    if raw is None:
        return None
    commits = []
    for chunk in raw.split("\x1e"):
        if not chunk.strip():
            continue
        header, _, files = chunk.partition("\n")
        sha, date, subject = header.split("\x1f", 2)
        commits.append({"sha": sha, "date": date, "subject": subject,
                        "files": [f for f in files.splitlines() if f.strip()]})
    return commits


# ── comparison ───────────────────────────────────────────────────────────────

def load_lock(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_lock(root: Path) -> dict:
    return {
        "repo": INVEST_SKILL_REPO,
        "commit": git_head(root),
        "commit_date": _git(root, "log", "-1", "--format=%cs", "HEAD"),
        "version": upstream_version(root),
        "files": tracked_files(root),
    }


def _diff_files(old: dict[str, str], new: dict[str, str]) -> dict[str, list[str]]:
    return {
        "added": sorted(set(new) - set(old)),
        "removed": sorted(set(old) - set(new)),
        "modified": sorted(k for k in set(old) & set(new) if old[k] != new[k]),
    }


def compare(root: Path, lock: dict, *, analysis_types=None, depth_tiers=None,
            aliases=None) -> dict:
    """Return the full sync status of ``root`` against the lock and local config."""
    analysis_types = ANALYSIS_TYPES if analysis_types is None else analysis_types
    depth_tiers = DEPTH_TIERS if depth_tiers is None else depth_tiers
    aliases = ALIASES if aliases is None else aliases

    new_lock = build_lock(root)
    files = _diff_files(lock.get("files", {}), new_lock["files"])
    commit_changed = bool(new_lock["commit"]) and new_lock["commit"] != lock.get("commit")
    changed = commit_changed or any(files.values())

    slugs = upstream_slugs(root)
    full_report = root / "prompts" / "full-report.md"
    upstream_tiers = parse_depth_tiers(full_report.read_text(encoding="utf-8")) \
        if full_report.exists() else {}
    upstream_aliases = detect_aliases(root)

    drift = {
        "missing_slugs": sorted(set(slugs) - set(analysis_types)),
        "removed_slugs": sorted(set(analysis_types) - set(slugs)),
        "tier_mismatch": {
            depth: {"local": list(depth_tiers.get(depth, [])), "upstream": mods}
            for depth, mods in upstream_tiers.items()
            if list(depth_tiers.get(depth, [])) != mods
        },
        "alias_mismatch": {
            slug: {"local": aliases.get(slug), "upstream": upstream_aliases.get(slug)}
            for slug in sorted(set(aliases) | set(upstream_aliases))
            if aliases.get(slug) != upstream_aliases.get(slug)
        },
        "missing_context": [f for f in CONTEXT_FILES if not (root / f).is_file()],
    }

    return {
        "pinned": {k: lock.get(k) for k in ("commit", "version", "commit_date")},
        "upstream": {k: new_lock[k] for k in ("commit", "version", "commit_date")},
        "changed": changed,
        "files": files,
        "commits": git_log(root, lock.get("commit")) if commit_changed else [],
        "drift": drift,
        "has_drift": any(drift.values()),
        "lock": new_lock,
    }


# ── rendering ────────────────────────────────────────────────────────────────

def _short(sha: str | None) -> str:
    return sha[:7] if sha else "—"


def _commit_link(sha: str) -> str:
    base = INVEST_SKILL_REPO.removesuffix(".git")
    return f"[`{sha[:7]}`]({base}/commit/{sha})"


def render_markdown(status: dict) -> str:
    pin, up = status["pinned"], status["upstream"]
    out = [
        "## InvestSkill upstream sync",
        "",
        "| | Locked | Upstream |",
        "|---|---|---|",
        f"| Commit | `{_short(pin['commit'])}` | `{_short(up['commit'])}` |",
        f"| Version | {pin['version'] or '—'} | {up['version'] or '—'} |",
        f"| Commit date | {pin['commit_date'] or '—'} | {up['commit_date'] or '—'} |",
        "",
    ]

    drift = status["drift"]
    out += ["### Drift — needs a code change in this repo", ""]
    if not status["has_drift"]:
        out += ["None. `ANALYSIS_TYPES`, `DEPTH_TIERS` and `ALIASES` match upstream.", ""]
    else:
        if drift["missing_slugs"]:
            out.append("- [ ] **New upstream skills** — add rows to `ANALYSIS_TYPES` "
                       "(`scripts/analysis/config/__init__.py`): "
                       + ", ".join(f"`{s}`" for s in drift["missing_slugs"]))
        if drift["removed_slugs"]:
            out.append("- [ ] **Skills gone upstream** — remove from `ANALYSIS_TYPES` and any "
                       "workflow that runs them: "
                       + ", ".join(f"`{s}`" for s in drift["removed_slugs"]))
        for depth, pair in drift["tier_mismatch"].items():
            out.append(f"- [ ] **`DEPTH_TIERS[\"{depth}\"]` differs from "
                       "`prompts/full-report.md`**")
            out.append(f"  - local: {', '.join(pair['local']) or '—'}")
            out.append(f"  - upstream: {', '.join(pair['upstream']) or '—'}")
        for slug, pair in drift["alias_mismatch"].items():
            out.append(f"- [ ] **Alias `{slug}`** — local `ALIASES` says "
                       f"`{pair['local'] or 'not an alias'}`, upstream says "
                       f"`{pair['upstream'] or 'not an alias'}`")
        if drift["missing_context"]:
            out.append("- [ ] **System-context files missing upstream** (PromptRepo reads "
                       "them): " + ", ".join(f"`{f}`" for f in drift["missing_context"]))
        out.append("")

    files = status["files"]
    out += ["### Changed upstream files this repo reads", ""]
    if not any(files.values()):
        out += ["None.", ""]
    else:
        for kind in ("added", "modified", "removed"):
            if files[kind]:
                out.append(f"- **{kind}**: " + ", ".join(f"`{f}`" for f in files[kind]))
        out.append("")

    commits = status["commits"]
    out += ["### Upstream commits since the lock", ""]
    if commits is None:
        out += [f"Locked commit `{_short(pin['commit'])}` is not in the clone's history "
                "(shallow clone or force-push); see the file diff above.", ""]
    elif not commits:
        out += ["None.", ""]
    else:
        watched = {"prompts/", *CONTEXT_FILES}
        for c in commits:
            touches = [f for f in c["files"] if any(f.startswith(w) for w in watched)]
            mark = " 📝" if touches else ""
            out.append(f"- {_commit_link(c['sha'])} {c['date']} {c['subject']}{mark}")
        out += ["", "📝 = touches `prompts/` or a system-context file.", ""]
    return "\n".join(out)


def write_github_output(path: str, status: dict) -> None:
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(f"changed={str(status['changed']).lower()}\n")
        fh.write(f"drift={str(status['has_drift']).lower()}\n")
        fh.write(f"upstream_commit={status['upstream']['commit'] or ''}\n")
        fh.write(f"upstream_short={_short(status['upstream']['commit'])}\n")
        fh.write(f"upstream_version={status['upstream']['version'] or ''}\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0].strip())
    ap.add_argument("--invest-skill-dir", default="InvestSkill", type=Path,
                    help="Path to the cloned InvestSkill repo (default: InvestSkill)")
    ap.add_argument("--lock", default=DEFAULT_LOCK, type=Path,
                    help=f"Lock file (default: {DEFAULT_LOCK.name} at the repo root)")
    ap.add_argument("--report", type=Path, help="Also write the Markdown report here")
    ap.add_argument("--write-lock", action="store_true",
                    help="Rewrite the lock to the upstream checkout's current state")
    ap.add_argument("--check", action="store_true", help="Exit 1 when there is drift")
    args = ap.parse_args(argv)

    if not (args.invest_skill_dir / "prompts").is_dir():
        print(f"ERROR: {args.invest_skill_dir}/prompts not found — clone "
              f"{INVEST_SKILL_REPO} first.", file=sys.stderr)
        return 2

    status = compare(args.invest_skill_dir, load_lock(args.lock))
    report = render_markdown(status)
    print(report)
    if args.report:
        args.report.write_text(report + "\n", encoding="utf-8")
    if args.write_lock:
        args.lock.write_text(json.dumps(status["lock"], indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8")
    if os.environ.get("GITHUB_OUTPUT"):
        write_github_output(os.environ["GITHUB_OUTPUT"], status)
    return 1 if args.check and status["has_drift"] else 0


if __name__ == "__main__":
    sys.exit(main())
