"""
debug_visits.py
===============
Two ~5-minute diagnostics to run BEFORE the multi-hour scrape. Both write a
single text artifact (debug_out/<name>.txt) so you can confirm everything from
the GitHub UI without a long run.

Modes
-----
  --mode dom [--team arkansas --season 2025]
        Fetch a few known visits pages and dump the structure of the recruit
        list: HTTP status, container presence, li counts (header vs player),
        the OUTER HTML of the first date-header and first 2 player rows, and any
        load-more candidates found. Use this to CONFIRM the selectors in
        scrape_visits.py still match the live DOM, and to discover the real
        Load More control (the scraper currently scrolls + clicks anything whose
        text matches /load more|show more|.../, which is a best guess).

  --mode slugcheck [--season 2025]
        Hit EVERY team URL for one season and report, per team:
        HTTP status, whether ul.ri-page__list[data-js="recruit-list"] is present,
        and the player-row count. Any 404 / missing-container line is a bad slug
        in team_urls.py to fix before the big run. ~130 light fetches.

Both modes reuse the exact selectors/among helpers from scrape_visits.py so a
green debug run means the real scraper will see the same thing.
"""

import argparse
import asyncio
import os
import random

from team_urls import all_teams, is_fbs_in_year, team_url, team_slug
from scrape_visits import (
    LIST_SELECTOR, ITEM_SELECTOR, USER_AGENTS, BLOCK_SUBSTR,
    BLOCK_RESOURCE_TYPES, NAV_TIMEOUT, CONTAINER_TIMEOUT, EXTRACT_JS,
)

OUT_DIR = "debug_out"

# A handful of pages whose existence is reasonably certain, for the dom dump.
DOM_SAMPLES = [
    ("arkansas", 2025),
    ("ohio-state", 2025),
    ("alabama", 2024),
]

# In-page probe: count headers vs players, grab sample outerHTML + load-more
# candidates. Returns a JSON-able dict.
PROBE_JS = r"""
() => {
  const out = {has_container: false, header_count: 0, player_count: 0,
               first_header_html: '', sample_players_html: [],
               loadmore_candidates: []};
  const ul = document.querySelector('ul.ri-page__list[data-js="recruit-list"]');
  if (!ul) return out;
  out.has_container = true;
  const items = ul.querySelectorAll(':scope > li.ri-page__list-item');
  for (const li of items) {
    if (li.classList.contains('list-header')) {
      out.header_count++;
      if (!out.first_header_html) out.first_header_html = li.outerHTML;
    } else {
      out.player_count++;
      if (out.sample_players_html.length < 2)
        out.sample_players_html.push(li.outerHTML);
    }
  }
  const re = /load more|show more|view more|see more/i;
  const els = document.querySelectorAll('a, button, [data-js]');
  for (const el of els) {
    const t = (el.textContent || '').trim();
    if (t && re.test(t)) {
      out.loadmore_candidates.push(
        (el.tagName || '') + ' | text="' + t.slice(0, 40) + '"' +
        ' | class="' + (el.getAttribute('class') || '') + '"' +
        ' | data-js="' + (el.getAttribute('data-js') || '') + '"');
    }
  }
  return out;
}
"""


async def _new_context(browser):
    ctx = await browser.new_context(
        user_agent=random.choice(USER_AGENTS),
        viewport={"width": 1366, "height": 900},
        locale="en-US",
    )

    async def handler(route):
        try:
            req = route.request
            url = req.url.lower()
            if (req.resource_type in BLOCK_RESOURCE_TYPES
                    or any(b in url for b in BLOCK_SUBSTR)):
                await route.abort()
            else:
                await route.continue_()
        except Exception:
            try:
                await route.continue_()
            except Exception:
                pass

    await ctx.route("**/*", handler)
    return ctx


async def _slug_to_team(slug):
    for t in all_teams():
        if team_slug(t) == slug:
            return t
    return slug


async def mode_dom(lines):
    from playwright.async_api import async_playwright, TimeoutError as PWTimeout

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage",
                  "--disable-blink-features=AutomationControlled"],
        )
        try:
            for slug, season in DOM_SAMPLES:
                url = (f"https://247sports.com/college/{slug}/season/"
                       f"{season}-football/visits/")
                lines.append("=" * 78)
                lines.append(f"DOM DUMP: {slug} {season}")
                lines.append(f"URL: {url}")
                ctx = await _new_context(browser)
                try:
                    page = await ctx.new_page()
                    resp = await page.goto(url, wait_until="domcontentloaded",
                                           timeout=NAV_TIMEOUT)
                    code = resp.status if resp else 0
                    lines.append(f"HTTP status: {code}")
                    try:
                        await page.wait_for_selector(
                            LIST_SELECTOR, timeout=CONTAINER_TIMEOUT)
                    except PWTimeout:
                        lines.append("!! list container NOT found within timeout")
                    # Let lazy rows settle a touch (no full load-more here).
                    await page.evaluate(
                        "window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(1500)

                    probe = await page.evaluate(PROBE_JS)
                    lines.append(f"has_container : {probe.get('has_container')}")
                    lines.append(f"header_count : {probe.get('header_count')}")
                    lines.append(f"player_count : {probe.get('player_count')}")
                    lines.append("")
                    lines.append("-- first date-header outerHTML --")
                    lines.append(probe.get("first_header_html", "")[:2500] or "(none)")
                    lines.append("")
                    lines.append("-- first 2 player-row outerHTML --")
                    for i, h in enumerate(probe.get("sample_players_html", []), 1):
                        lines.append(f"[player {i}]")
                        lines.append(h[:3000])
                        lines.append("")
                    lines.append("-- load-more candidates (tag/text/class/data-js) --")
                    cands = probe.get("loadmore_candidates", [])
                    if cands:
                        for c in cands[:20]:
                            lines.append("  " + c)
                    else:
                        lines.append("  (none found by text match — "
                                     "list may be fully server-rendered)")
                    lines.append("")

                    # Sanity: run the REAL extractor and show first 3 parsed rows.
                    data = await page.evaluate(EXTRACT_JS)
                    rows = data.get("rows", []) if isinstance(data, dict) else []
                    lines.append(f"EXTRACT_JS parsed rows: {len(rows)} "
                                 f"(error={data.get('error') if isinstance(data, dict) else 'n/a'})")
                    for r in rows[:3]:
                        lines.append("  " + str({k: r.get(k) for k in (
                            "name", "href", "meta", "metrics", "stars", "score",
                            "natrank", "posrank", "juco", "position",
                            "committed_school", "has_checkmark",
                            "visit_date_raw")}))
                    lines.append("")
                except Exception as e:
                    lines.append(f"!! ERROR: {e}")
                finally:
                    await ctx.close()
        finally:
            await browser.close()


async def mode_slugcheck(season, lines):
    from playwright.async_api import async_playwright, TimeoutError as PWTimeout

    teams = [t for t in all_teams() if is_fbs_in_year(t, season)]
    lines.append("=" * 78)
    lines.append(f"SLUGCHECK season {season}: {len(teams)} teams")
    lines.append("status  container  players  team  ->  url")
    lines.append("-" * 78)

    bad = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage",
                  "--disable-blink-features=AutomationControlled"],
        )
        try:
            sem = asyncio.Semaphore(3)  # gentle; this is a light probe

            async def check(team):
                async with sem:
                    url = team_url(team, season)
                    ctx = await _new_context(browser)
                    code, has, nplayers = 0, False, 0
                    try:
                        page = await ctx.new_page()
                        resp = await page.goto(url, wait_until="domcontentloaded",
                                               timeout=NAV_TIMEOUT)
                        code = resp.status if resp else 0
                        try:
                            await page.wait_for_selector(
                                LIST_SELECTOR, timeout=CONTAINER_TIMEOUT)
                            has = True
                        except PWTimeout:
                            has = False
                        if has:
                            await page.evaluate(
                                "window.scrollTo(0, document.body.scrollHeight)")
                            await page.wait_for_timeout(800)
                            nplayers = await page.locator(ITEM_SELECTOR).count()
                    except Exception as e:
                        code = code or -1
                        return (team, code, has, nplayers, str(e)[:60])
                    finally:
                        await ctx.close()
                    return (team, code, has, nplayers, "")

            res = await asyncio.gather(*[check(t) for t in teams])
        finally:
            await browser.close()

    for team, code, has, nplayers, err in sorted(res, key=lambda x: x[0]):
        flag = "" if (code == 200 and has) else "  <-- CHECK"
        if flag:
            bad.append(team)
        line = (f"{str(code):>5}  {str(has):>9}  {str(nplayers):>7}  "
                f"{team}  ->  {team_url(team, season)}{flag}")
        if err:
            line += f"   ERR={err}"
        lines.append(line)

    lines.append("-" * 78)
    if bad:
        lines.append(f"TEAMS TO CHECK ({len(bad)}): {bad}")
        lines.append("Fix their slug in team_urls.py (or confirm they are not "
                     "FBS in this season / had no visits page).")
    else:
        lines.append("All teams returned 200 + container. Slugs look good.")


def main():
    ap = argparse.ArgumentParser(description="247 visits debug diagnostics")
    ap.add_argument("--mode", choices=["dom", "slugcheck"], required=True)
    ap.add_argument("--team", default="arkansas",
                    help="(dom mode) ignored unless you edit DOM_SAMPLES")
    ap.add_argument("--season", type=int, default=2025)
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    lines = []
    if args.mode == "dom":
        asyncio.run(mode_dom(lines))
        out = os.path.join(OUT_DIR, "dom_dump.txt")
    else:
        asyncio.run(mode_slugcheck(args.season, lines))
        out = os.path.join(OUT_DIR, f"slugcheck_{args.season}.txt")

    text = "\n".join(lines) + "\n"
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
