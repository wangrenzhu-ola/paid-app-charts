#!/usr/bin/env python3
"""Refresh developed-market iOS paid charts into data/latest.json."""
from __future__ import annotations
import json, urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'latest.json'
COUNTRIES = ['us','gb','fr','jp','kr','au','de','ca','nl','se']
CC = {c:c.upper() for c in COUNTRIES}

UA = {'User-Agent': 'paid-app-charts/1.0'}

def get_json(url: str):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode('utf-8'))

def rss_paid(cc: str, games: bool=False):
    # genre=6014 games
    base = f'https://itunes.apple.com/{cc}/rss/toppaidapplications/limit=50'
    if games:
        base += '/genre=6014'
    url = base + '/json'
    data = get_json(url)
    entries = data.get('feed', {}).get('entry', [])
    if isinstance(entries, dict):
        entries = [entries]
    rows = []
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    for i, e in enumerate(entries, 1):
        price = e.get('im:price', {}).get('attributes', {})
        rows.append({
            'country': CC[cc],
            'rank': i,
            'list_type': 'paid_games' if games else 'overall_paid',
            'app_name': e.get('im:name', {}).get('label'),
            'developer': e.get('im:artist', {}).get('label'),
            'category': (e.get('category', {}).get('attributes') or {}).get('label'),
            'price': price.get('amount'),
            'currency': price.get('currency'),
            'app_id': (e.get('id', {}).get('attributes') or {}).get('im:id'),
            'source_url': url,
            'fetched_at': now,
        })
    return rows

def marketing_paid_apps(cc: str):
    url = f'https://itunes.apple.com/{cc}/charts/apps/top-paid/50/apps.json'
    try:
        data = get_json(url)
    except Exception as ex:
        print('marketing fail', cc, ex)
        return []
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    # structure varies; try common shapes
    apps = data.get('resultIds') or data.get('adamIds') or []
    # fallback: chart data
    chart = data.get('data') or data
    rows = []
    # If only ids, skip detail for speed and use chart results if present
    results = []
    if isinstance(chart, dict) and 'results' in chart:
        results = chart['results']
    elif isinstance(data.get('feed'), dict):
        return []
    # Alternate endpoint often returns {"adamIds":[...]} — hydrate via lookup
    ids = data.get('adamIds') or data.get('resultIds')
    if ids:
        # batch lookup
        for start in range(0, len(ids), 50):
            batch = ids[start:start+50]
            look = f"https://itunes.apple.com/lookup?id={','.join(map(str,batch))}&country={cc}"
            try:
                js = get_json(look)
            except Exception as ex:
                print('lookup fail', cc, ex)
                continue
            by_id = {str(x['trackId']): x for x in js.get('results', [])}
            for i, aid in enumerate(batch, start+1):
                x = by_id.get(str(aid))
                if not x: continue
                rows.append({
                    'country': CC[cc],
                    'rank': i,
                    'list_type': 'paid_apps',
                    'app_name': x.get('trackName'),
                    'developer': x.get('artistName'),
                    'category': (x.get('primaryGenreName')),
                    'price': x.get('price'),
                    'currency': x.get('currency'),
                    'app_id': str(x.get('trackId')),
                    'source_url': url,
                    'fetched_at': now,
                })
        return rows
    return rows

def cooccurrence(rows):
    by = defaultdict(lambda: {'countries': set(), 'category': None, 'developer': None, 'app_id': None, 'prices': []})
    for r in rows:
        if r['list_type'] != 'paid_apps':
            continue
        a = by[r['app_name']]
        a['countries'].add(r['country'])
        a['category'] = a['category'] or r.get('category')
        a['developer'] = a['developer'] or r.get('developer')
        a['app_id'] = a['app_id'] or r.get('app_id')
        if r.get('price') is not None:
            a['prices'].append({'country': r['country'], 'price': r['price'], 'currency': r.get('currency')})
    out = []
    for name, a in by.items():
        countries = sorted(a['countries'])
        out.append({
            'app_name': name,
            'developer': a['developer'],
            'category': a['category'],
            'app_id': a['app_id'],
            'countries': countries,
            'country_count': len(countries),
            'sample_price': a['prices'][0] if a['prices'] else None,
        })
    out.sort(key=lambda x: (-x['country_count'], x['app_name'].lower()))
    return out

def main():
    rows = []
    for cc in COUNTRIES:
        print('fetch', cc)
        rows += rss_paid(cc, False)
        rows += rss_paid(cc, True)
        rows += marketing_paid_apps(cc)
    prev_short = []
    if OUT.exists():
        try:
            prev_short = json.loads(OUT.read_text()).get('agent_shortlist') or []
        except Exception:
            pass
    payload = {
        'meta': {
            'title': '发达国家 iOS 付费榜 · 智能体化机会',
            'fetched_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'timezone': 'Asia/Shanghai',
            'countries': sorted({r['country'] for r in rows}),
            'list_types': sorted({r['list_type'] for r in rows}),
            'row_count': len(rows),
            'source': 'Apple iTunes RSS + Marketing Tools',
        },
        'rows': rows,
        'cooccurrence_paid_apps': cooccurrence(rows),
        'agent_shortlist': prev_short,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')))
    print('wrote', OUT, 'rows', len(rows))

if __name__ == '__main__':
    main()
