# SNAPSHOT — Developed Markets iOS Paid Charts

- **Local date (Asia/Shanghai):** 2026-09-17
- **Fetched at (UTC):** 2026-09-17T09:47:58Z
- **Archive root:** `/workspace/paid-charts-developed-2026-09-17/`

## Sources

| List | Source | Notes |
|------|--------|-------|
| `overall_paid` | Apple iTunes RSS `https://itunes.apple.com/{cc}/rss/toppaidapplications/limit=50/json` | Official public JSON; mixes games + apps |
| `paid_games` | Same RSS + `genre=6014` | Official Games genre paid chart |
| `paid_apps` | Apple Marketing Tools `https://rss.applemarketingtools.com/api/v2/{cc}/apps/top-paid/50/apps.json` | Apps-oriented top paid (non-game heavy); prices backfilled from RSS overall when app_id/name matched |

Prices/currency come from iTunes RSS when present. Marketing Tools feed does not include price; enrichment is best-effort.

## Coverage (Top N rows written)

| Country | overall_paid | paid_games | paid_apps |
|---------|-------------:|-----------:|----------:|
| US | 50 | 50 | 50 |
| GB | 50 | 50 | 47 |
| FR | 50 | 50 | 50 |
| JP | 50 | 50 | 49 |
| KR | 50 | 50 | 50 |
| AU | 50 | 50 | 50 |
| DE | 50 | 50 | 50 |
| CA | 50 | 50 | 50 |
| NL | 50 | 50 | 50 |
| SE | 50 | 50 | 50 |

All required markets (US, GB, FR, JP, KR, AU) and stretch markets (DE, CA, NL, SE) have **overall_paid** and **paid_games**. All ten also have **paid_apps** after AU/NL marketing-tools retry.

## Gaps / caveats

1. **No fabricated ranks/prices** — empty price cells mean enrichment miss, not invented zeros.
2. **Marketing Tools AU/NL** initially timed out; retried successfully (separate `fetched_at` on those two files may differ by ~minutes).
3. **Category labels are storefront-localized** (e.g. Jeux / ゲーム / Spiele) — see REVIEW for EN buckets.
4. **parallel-cli** not used (auth unknown; skipped per brief).
5. **anerg.com / Appfigures** used only as discovery cross-check via WebSearch; primary archive is Apple official feeds.
6. RSS caps at 50 requested (Apple feed typically max 100; we archived Top 50).
7. `paid_apps` is the Marketing Tools "top-paid apps" feed — closer to App Store **Apps** tab than Overall; not a perfect "exclude all games" filter if an edge title appears.

## Files

- `raw/{cc}-paid-overall.json` — 10 countries
- `raw/{cc}-paid-games.json` — 10 countries
- `raw/{cc}-paid-marketingtools.json` — 10 countries (= paid_apps source)
- `raw/_fetch_meta.json`, `raw/_analysis.json`
- `combined.csv`, `combined.json`
- `SNAPSHOT.md`, `REVIEW.md`
