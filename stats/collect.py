#!/usr/bin/env python3
"""
Snapshots how ScreenInk is being downloaded, and writes the result into stats/.

Why this exists
---------------
GitHub answers two different questions, and forgets one of them quickly:

  * Release asset download counts are cumulative and permanent-ish, but they are
    attached to the release. Delete a release and its history is gone for good.
  * Traffic (views, clones, referrers) is a *fourteen day rolling window*. Nobody
    is watching it on day fifteen, so unless something writes it down it is lost.

So this runs daily and appends to CSVs that live in the repository. Fourteen days
of overlap means a missed run - or a fortnight of them - costs nothing: the next
run backfills every day it can still see.

What it deliberately does not do
--------------------------------
There is no country data here, because GitHub does not expose any. Downloads are
served straight from GitHub's CDN and we never see the request. Measuring
location needs something sitting in front of the download; see stats/README.md.

Usage
-----
    GITHUB_TOKEN=... python stats/collect.py [--repo owner/name] [--dry-run]

The token needs push access: the traffic endpoints refuse anything less.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"
HERE = Path(__file__).resolve().parent


def get(path: str, token: str):
    """One GitHub API call, returning parsed JSON, or None if the endpoint is forbidden."""
    request = urllib.request.Request(
        f"{API}{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "screenink-stats",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        # Traffic needs push access. Say so plainly rather than dying, because the
        # download counts are still worth collecting without it.
        if error.code in (403, 404):
            print(f"  ! {path} returned {error.code} - skipping", file=sys.stderr)
            return None
        raise


def read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def merge(path: Path, fieldnames: list[str], fresh: list[dict], key: tuple[str, ...]) -> int:
    """
    Folds fresh rows into whatever is already on disk, keyed by `key`.

    Fresh rows win. That matters because GitHub's numbers for the last day or two
    are still settling, so a row written yesterday may be an undercount today.
    """
    existing = {tuple(row[k] for k in key): row for row in read_rows(path)}
    added = 0
    for row in fresh:
        identity = tuple(str(row[k]) for k in key)
        if identity not in existing:
            added += 1
        existing[identity] = {k: str(row[k]) for k in fieldnames}

    ordered = sorted(existing.values(), key=lambda row: tuple(row[k] for k in key))
    write_rows(path, fieldnames, ordered)
    return added


def day(timestamp: str) -> str:
    """GitHub hands back ISO timestamps; we only ever care about the date."""
    return timestamp[:10]


def collect_downloads(repo: str, token: str, today: str) -> list[dict]:
    """Cumulative download count per release asset, as of now."""
    rows = []
    page = 1
    while True:
        releases = get(f"/repos/{repo}/releases?per_page=100&page={page}", token) or []
        if not releases:
            break
        for release in releases:
            for asset in release.get("assets", []):
                rows.append(
                    {
                        "date": today,
                        "tag": release["tag_name"],
                        "published": day(release.get("published_at") or release["created_at"]),
                        "asset": asset["name"],
                        "downloads": asset["download_count"],
                    }
                )
        page += 1
    return rows


def collect_traffic(repo: str, token: str) -> list[dict]:
    """Views and clones, per day, for as far back as GitHub will admit."""
    views = get(f"/repos/{repo}/traffic/views", token) or {}
    clones = get(f"/repos/{repo}/traffic/clones", token) or {}

    by_date: dict[str, dict] = {}
    for entry in views.get("views", []):
        by_date.setdefault(day(entry["timestamp"]), {})["views"] = entry["count"]
        by_date[day(entry["timestamp"])]["unique_visitors"] = entry["uniques"]
    for entry in clones.get("clones", []):
        row = by_date.setdefault(day(entry["timestamp"]), {})
        row["clones"] = entry["count"]
        row["unique_cloners"] = entry["uniques"]

    return [
        {
            "date": date,
            "views": row.get("views", 0),
            "unique_visitors": row.get("unique_visitors", 0),
            "clones": row.get("clones", 0),
            "unique_cloners": row.get("unique_cloners", 0),
        }
        for date, row in sorted(by_date.items())
    ]


def collect_referrers(repo: str, token: str, today: str) -> list[dict]:
    """
    Where visitors arrived from. This is the closest thing GitHub offers to
    'where are people coming from', and it is about sites, not places.
    """
    referrers = get(f"/repos/{repo}/traffic/popular/referrers", token) or []
    return [
        {
            "date": today,
            "referrer": entry["referrer"],
            "views": entry["count"],
            "unique_visitors": entry["uniques"],
        }
        for entry in referrers
    ]


def write_summary(path: Path) -> None:
    """
    A short, readable report, so the numbers are usable without opening a
    spreadsheet. Everything here is derived from the CSVs, never from the API,
    which means the report covers the whole recorded history rather than just
    whatever GitHub still remembers today.
    """
    downloads = read_rows(HERE / "downloads.csv")
    traffic = read_rows(HERE / "traffic.csv")
    referrers = read_rows(HERE / "referrers.csv")

    lines = ["# ScreenInk download statistics", ""]
    lines.append(f"Generated {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC. ")
    lines.append("Updated daily by `.github/workflows/stats.yml`.")
    lines.append("")

    # --- downloads, latest snapshot per release -----------------------------
    latest: dict[tuple[str, str], dict] = {}
    for row in downloads:
        key = (row["tag"], row["asset"])
        if key not in latest or row["date"] > latest[key]["date"]:
            latest[key] = row

    if latest:
        as_of = max(row["date"] for row in latest.values())
        total = sum(int(row["downloads"]) for row in latest.values())
        lines += [
            "## Downloads",
            "",
            f"**{total} download{'' if total == 1 else 's'}** in total, as of {as_of}.",
            "",
            "| Release | Published | Downloads |",
            "|---|---|---|",
        ]
        for (tag, _asset), row in sorted(latest.items(), key=lambda item: item[1]["published"], reverse=True):
            lines.append(f"| {tag} | {row['published']} | {row['downloads']} |")
        lines.append("")

        # Day-on-day movement is the interesting bit, and it only exists because
        # we have been writing the cumulative number down.
        by_date: dict[str, int] = {}
        for row in downloads:
            by_date[row["date"]] = by_date.get(row["date"], 0) + int(row["downloads"])
        dates = sorted(by_date)
        if len(dates) > 1:
            lines += ["### New downloads per day", "", "| Date | New |", "|---|---|"]
            for previous, current in zip(dates, dates[1:]):
                lines.append(f"| {current} | {by_date[current] - by_date[previous]:+d} |")
            lines.append("")
            lines.append(
                "_A negative number means a release was deleted. Deleting a release "
                "destroys its download count permanently, so don't._"
            )
            lines.append("")

    # --- traffic ------------------------------------------------------------
    if traffic:
        recent = traffic[-30:]
        lines += [
            "## Repository traffic",
            "",
            f"Recorded from {traffic[0]['date']} to {traffic[-1]['date']}.",
            "",
            f"- **{sum(int(r['views']) for r in traffic)}** page views "
            f"from **{sum(int(r['unique_visitors']) for r in traffic)}** unique visitors",
            f"- **{sum(int(r['clones']) for r in traffic)}** clones "
            f"from **{sum(int(r['unique_cloners']) for r in traffic)}** unique cloners",
            "",
            "### Last 30 recorded days",
            "",
            "| Date | Views | Visitors | Clones |",
            "|---|---|---|---|",
        ]
        for row in recent:
            lines.append(f"| {row['date']} | {row['views']} | {row['unique_visitors']} | {row['clones']} |")
        lines.append("")

    # --- referrers ----------------------------------------------------------
    if referrers:
        totals: dict[str, int] = {}
        for row in referrers:
            # Referrer rows are a 14-day rolling total, so summing every snapshot
            # would count the same visit many times over. The peak is honest.
            totals[row["referrer"]] = max(totals.get(row["referrer"], 0), int(row["views"]))
        lines += [
            "## Where visitors came from",
            "",
            "Referring sites, at their highest recorded fortnightly total. This is",
            "the only 'where from' GitHub exposes, and it is about sites rather than",
            "places - see the note on geography in `stats/README.md`.",
            "",
            "| Source | Views |",
            "|---|---|",
        ]
        for source, views in sorted(totals.items(), key=lambda item: item[1], reverse=True):
            lines.append(f"| {source} | {views} |")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=os.environ.get("STATS_REPO", "alexusa75/ScreenInk-releases"))
    parser.add_argument("--dry-run", action="store_true", help="Print what would be written and stop.")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("No GITHUB_TOKEN. Nothing to do.", file=sys.stderr)
        return 1

    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    print(f"Snapshotting {args.repo} for {today}")

    downloads = collect_downloads(args.repo, token, today)
    traffic = collect_traffic(args.repo, token)
    referrers = collect_referrers(args.repo, token, today)

    total = sum(int(row["downloads"]) for row in downloads)
    print(f"  {len(downloads)} asset(s), {total} download(s) all told")
    print(f"  {len(traffic)} day(s) of traffic, {len(referrers)} referrer(s)")

    if args.dry_run:
        print(json.dumps({"downloads": downloads, "traffic": traffic, "referrers": referrers}, indent=2))
        return 0

    merge(HERE / "downloads.csv", ["date", "tag", "published", "asset", "downloads"], downloads,
          key=("date", "tag", "asset"))
    merge(HERE / "traffic.csv", ["date", "views", "unique_visitors", "clones", "unique_cloners"], traffic,
          key=("date",))
    merge(HERE / "referrers.csv", ["date", "referrer", "views", "unique_visitors"], referrers,
          key=("date", "referrer"))

    write_summary(HERE / "SUMMARY.md")
    print("  wrote downloads.csv, traffic.csv, referrers.csv and SUMMARY.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
