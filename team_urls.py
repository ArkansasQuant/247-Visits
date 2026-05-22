"""
team_urls.py
============
Full FBS team list (2018-2026 window) with 247Sports slugs and helpers.

URL pattern (verified shape):
    https://247sports.com/college/{slug}/season/{season}-football/visits/

IMPORTANT — SLUG VERIFICATION:
  247 slugs are NOT all known with certainty. Every slug I am unsure about is
  marked `# VERIFY`. Before the full run, run debug_visits.py in `slugcheck`
  mode (see debug workflow) for one season -> it hits every URL and reports
  HTTP status + whether the recruit-list container is present. Any 404 / missing
  container = a bad slug to fix here. This is a ~few-minute job that de-risks the
  whole multi-hour run.

FBS-entry years: teams that JOINED FBS inside the window are listed in
FBS_ENTRY; they are excluded for seasons before their entry year. Everyone else
defaults to FBS for the entire 2018-2026 window. Idaho is intentionally OMITTED
(it dropped back to FCS starting 2018, so it is not FBS anywhere in this window).
"""

# Display name -> 247 slug.
SLUGS = {
    # ---------------- SEC ----------------
    "Alabama": "alabama",
    "Arkansas": "arkansas",
    "Auburn": "auburn",
    "Florida": "florida",
    "Georgia": "georgia",
    "Kentucky": "kentucky",
    "LSU": "lsu",
    "Mississippi State": "mississippi-state",
    "Missouri": "missouri",
    "Oklahoma": "oklahoma",
    "Ole Miss": "ole-miss",
    "South Carolina": "south-carolina",
    "Tennessee": "tennessee",
    "Texas": "texas",
    "Texas A&M": "texas-am",
    "Vanderbilt": "vanderbilt",

    # ---------------- Big Ten ----------------
    "Illinois": "illinois",
    "Indiana": "indiana",
    "Iowa": "iowa",
    "Maryland": "maryland",
    "Michigan": "michigan",
    "Michigan State": "michigan-state",
    "Minnesota": "minnesota",
    "Nebraska": "nebraska",
    "Northwestern": "northwestern",
    "Ohio State": "ohio-state",
    "Oregon": "oregon",
    "Penn State": "penn-state",
    "Purdue": "purdue",
    "Rutgers": "rutgers",
    "UCLA": "ucla",
    "USC": "usc",
    "Washington": "washington",
    "Wisconsin": "wisconsin",

    # ---------------- Big 12 ----------------
    "Arizona": "arizona",
    "Arizona State": "arizona-state",
    "Baylor": "baylor",
    "BYU": "byu",
    "Cincinnati": "cincinnati",
    "Colorado": "colorado",
    "Houston": "houston",
    "Iowa State": "iowa-state",
    "Kansas": "kansas",
    "Kansas State": "kansas-state",
    "Oklahoma State": "oklahoma-state",
    "TCU": "tcu",
    "Texas Tech": "texas-tech",
    "UCF": "ucf",                       # VERIFY (could be central-florida)
    "Utah": "utah",
    "West Virginia": "west-virginia",

    # ---------------- ACC ----------------
    "Boston College": "boston-college",
    "California": "california",
    "Clemson": "clemson",
    "Duke": "duke",
    "Florida State": "florida-state",
    "Georgia Tech": "georgia-tech",
    "Louisville": "louisville",
    "Miami": "miami",                   # VERIFY (Miami FL; 247 may use miami-fl)
    "NC State": "nc-state",             # VERIFY (could be north-carolina-state)
    "North Carolina": "north-carolina",
    "Pittsburgh": "pittsburgh",         # VERIFY (could be pitt)
    "SMU": "smu",
    "Stanford": "stanford",
    "Syracuse": "syracuse",
    "Virginia": "virginia",
    "Virginia Tech": "virginia-tech",
    "Wake Forest": "wake-forest",

    # ---------------- Pac-12 (2-team era 2024; rebuilding 2026) ----------------
    "Oregon State": "oregon-state",
    "Washington State": "washington-state",

    # ---------------- American (AAC) ----------------
    "Army": "army",                     # VERIFY (could be army-west-point)
    "Charlotte": "charlotte",
    "East Carolina": "east-carolina",
    "Florida Atlantic": "florida-atlantic",
    "Memphis": "memphis",
    "Navy": "navy",
    "North Texas": "north-texas",
    "Rice": "rice",
    "South Florida": "south-florida",
    "Temple": "temple",
    "Tulane": "tulane",
    "Tulsa": "tulsa",
    "UAB": "uab",                       # VERIFY (could be alabama-birmingham)
    "UTSA": "texas-san-antonio",        # VERIFY (could be utsa)

    # ---------------- Conference USA ----------------
    "Delaware": "delaware",             # FBS 2025
    "Florida International": "florida-international",  # VERIFY (could be fiu)
    "Jacksonville State": "jacksonville-state",       # FBS 2023
    "Kennesaw State": "kennesaw-state",               # FBS 2024
    "Liberty": "liberty",               # FBS reclass began 2018 (window start)
    "Louisiana Tech": "louisiana-tech",
    "Middle Tennessee": "middle-tennessee",  # VERIFY (could be middle-tennessee-state)
    "Missouri State": "missouri-state", # FBS 2025
    "New Mexico State": "new-mexico-state",
    "Sam Houston": "sam-houston-state", # FBS 2023 # VERIFY (could be sam-houston)
    "UTEP": "texas-el-paso",            # VERIFY (could be utep)
    "Western Kentucky": "western-kentucky",

    # ---------------- MAC ----------------
    "Akron": "akron",
    "Ball State": "ball-state",
    "Bowling Green": "bowling-green",
    "Buffalo": "buffalo",
    "Central Michigan": "central-michigan",
    "Eastern Michigan": "eastern-michigan",
    "Kent State": "kent-state",
    "Miami (OH)": "miami-oh",
    "Northern Illinois": "northern-illinois",
    "Ohio": "ohio",
    "Toledo": "toledo",
    "Western Michigan": "western-michigan",
    "UMass": "massachusetts",           # VERIFY (could be umass); FBS whole window

    # ---------------- Mountain West ----------------
    "Air Force": "air-force",
    "Boise State": "boise-state",
    "Colorado State": "colorado-state",
    "Fresno State": "fresno-state",
    "Hawaii": "hawaii",
    "Nevada": "nevada",
    "New Mexico": "new-mexico",
    "San Diego State": "san-diego-state",
    "San Jose State": "san-jose-state",
    "UNLV": "unlv",                     # VERIFY (could be nevada-las-vegas)
    "Utah State": "utah-state",
    "Wyoming": "wyoming",

    # ---------------- Sun Belt ----------------
    "Appalachian State": "appalachian-state",
    "Arkansas State": "arkansas-state",
    "Coastal Carolina": "coastal-carolina",
    "Georgia Southern": "georgia-southern",
    "Georgia State": "georgia-state",
    "James Madison": "james-madison",   # FBS 2022
    "Louisiana": "louisiana",           # VERIFY (Ragin' Cajuns; could be louisiana-lafayette)
    "UL Monroe": "louisiana-monroe",    # VERIFY (could be ul-monroe)
    "Marshall": "marshall",
    "Old Dominion": "old-dominion",
    "South Alabama": "south-alabama",
    "Southern Miss": "southern-miss",   # VERIFY (could be southern-mississippi)
    "Texas State": "texas-state",
    "Troy": "troy",

    # ---------------- Independents ----------------
    "Notre Dame": "notre-dame",
    "UConn": "connecticut",             # VERIFY (could be uconn)
}

# Teams that JOINED FBS within the window: {display: first_fbs_season}.
# For seasons before the entry year, is_fbs_in_year() returns False so we don't
# waste requests. (A wrong slug or pre-entry season would 404 anyway and be
# logged as NOPAGE, so this is an optimization, not the only safety net.)
FBS_ENTRY = {
    "James Madison": 2022,
    "Jacksonville State": 2023,
    "Sam Houston": 2023,
    "Kennesaw State": 2024,
    "Delaware": 2025,
    "Missouri State": 2025,
    # Liberty technically reclassified starting 2018 (window start) -> no entry
    # gate needed. Coastal Carolina/App State/Charlotte/etc. were already FBS
    # before 2018.
}

# Sane default window (inclusive).
DEFAULT_SEASONS = list(range(2018, 2027))  # 2018..2026


def all_teams():
    """All teams, sorted by display name."""
    return sorted(SLUGS.keys())


def team_slug(team):
    """247 slug for a display name (or '' if unknown)."""
    return SLUGS.get(team, "")


def is_fbs_in_year(team, season):
    """True if `team` should have an FBS visits page for `season`."""
    if team not in SLUGS:
        return False
    entry = FBS_ENTRY.get(team)
    if entry is not None and season < entry:
        return False
    return True


def team_url(team, season):
    """Visits-list URL for a team-season."""
    slug = SLUGS[team]
    return f"https://247sports.com/college/{slug}/season/{season}-football/visits/"
