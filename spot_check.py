"""
spot_check.py
=============
Post-run sanity check on the COMBINED output. Point it at the final csv (or let
it auto-find the newest output/visits_full_*.csv). It:
  * loads the csv,
  * prints total rows + teams represented + rows-per-season,
  * flags teams with 0 rows in a season they were expected in (possible bad
    slug / missed scrape), and any duplicate (Player ID, Team, Season) keys,
  * checks the three Arkansas-2025 ground-truth recruits and prints PASS/FAIL.

Usage:
  python spot_check.py                       # newest output/visits_full_*.csv
  python spot_check.py path/to/visits.csv
"""

import csv
import glob
import os
import sys
from collections import defaultdict


GROUND_TRUTH = {
    # name(lower): (position, expect_juco, natl_contains, pos_contains,
    #               rating, status)
    "keyshawn davila": dict(position="CB", juco=True, natl="9", pos="1",
                            rating=None, status="no_or_yes"),
    "gavin garretson": dict(position="Edge", juco=False, natl=None, pos="117",
                            rating="86", status="no_or_yes"),
    "timothy merritt": dict(position="CB", juco=False, natl=None, pos=None,
                            rating=None, status="no"),
}


def _newest_csv():
    cands = sorted(glob.glob(os.path.join("output", "visits_full_*.csv")))
    if not cands:
        cands = sorted(glob.glob("visits_full_*.csv"))
    return cands[-1] if cands else None


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else _newest_csv()
    if not path or not os.path.exists(path):
        print("ERROR: no csv found. Pass a path or put it in output/.",
              file=sys.stderr)
        sys.exit(2)
    print(f"Reading {path}\n")

    with open(path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:  # strip Excel-safe leading apostrophe on Ht for display
        if r.get("Ht", "").startswith("'"):
            r["Ht"] = r["Ht"][1:]

    total = len(rows)
    per_team = defaultdict(int)
    per_season = defaultdict(int)
    per_team_season = defaultdict(int)
    keys = defaultdict(int)
    for r in rows:
        team = r.get("Team", "")
        season = r.get("High School Class", "")
        per_team[team] += 1
        per_season[season] += 1
        per_team_season[(team, season)] += 1
        pid = r.get("247 Player ID", "")
        if pid:
            keys[(pid, team, season)] += 1

    print(f"total rows         : {total}")
    print(f"teams represented  : {len(per_team)}")
    print("rows per season    :")
    for s in sorted(per_season):
        print(f"    {s}: {per_season[s]}")

    dups = {k: n for k, n in keys.items() if n > 1}
    print(f"\nduplicate (PlayerID, Team, Season) keys: {len(dups)}")
    for k, n in list(dups.items())[:20]:
        print(f"    {k} x{n}")

    # Teams that appear in SOME season but are entirely absent overall would not
    # show here; this flags thin per-season coverage worth eyeballing.
    thin = sorted([ts for ts, n in per_team_season.items() if n == 0])
    if thin:
        print(f"\nteam-seasons with 0 rows: {thin}")

    # ---- Ground truth ----
    print("\n--- Arkansas 2025 ground-truth ---")
    ark25 = [r for r in rows
             if r.get("Team") == "Arkansas"
             and str(r.get("High School Class")) == "2025"]
    by_name = {r.get("Recruit Name", "").strip().lower(): r for r in ark25}
    all_pass = True
    for name, exp in GROUND_TRUTH.items():
        r = by_name.get(name)
        if not r:
            print(f"  FAIL  {name}: NOT FOUND in Arkansas 2025")
            all_pass = False
            continue
        problems = []
        if exp["position"] and r.get("Position", "").lower() != exp["position"].lower():
            problems.append(f"position={r.get('Position')!r} != {exp['position']}")
        natl = r.get("247 Natl Rk", "")
        posn = r.get("247 HS Position Rk", "")
        if exp["juco"] and "JUCO" not in (natl + posn):
            problems.append("expected JUCO tag in ranks")
        if exp["natl"] and exp["natl"] not in natl:
            problems.append(f"natl={natl!r} missing {exp['natl']}")
        if exp["pos"] and exp["pos"] not in posn:
            problems.append(f"posrk={posn!r} missing {exp['pos']}")
        if exp["rating"] and r.get("247 HS Rating", "") != exp["rating"]:
            problems.append(f"rating={r.get('247 HS Rating')!r} != {exp['rating']}")
        if exp["status"] == "no" and r.get("Status", "") != "no":
            problems.append(f"status={r.get('Status')!r} != no")
        if problems:
            all_pass = False
            print(f"  FAIL  {name}: " + "; ".join(problems))
            print(f"        row: {{pos:{r.get('Position')}, natl:{natl}, "
                  f"pos:{posn}, rating:{r.get('247 HS Rating')}, "
                  f"status:{r.get('Status')}}}")
        else:
            print(f"  PASS  {name}")

    print("\nRESULT:", "ALL GROUND-TRUTH PASSED" if all_pass
          else "SOME CHECKS FAILED — inspect above")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
