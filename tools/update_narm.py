"""Rebuild data/narm.json from the NARM member-list PDF.

NARM publishes a quarterly PDF (e.g. NARM_SUMMER_2026.pdf) with entries grouped
by country/state as "City, Institution Name<symbols>, phone". There are no
street addresses, so geocoding is city-level: GeoNames US ZIP centroids
averaged per (city, state), plus hand-maintained tables for Canada and the
Caribbean/Bermuda.

Restriction symbols (kept in the data and surfaced in the UI):
  *    restricted for concerts/lectures/special exhibitions/ticketed events
  **   no benefit if your home museum is within 15 miles
  ***  both of the above
  #    no benefit if your home museum is within 50 miles
  ##   privileges do not apply to the Pacific Film Archive
  ^    not extended to members of institutions that restrict this institution

Usage:  python tools/update_narm.py <pdf-url-or-path>
Deps:   pip install pypdf requests   (+ data/geonames US.zip download)
"""
import io
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import requests
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent

US_STATES = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
    'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
    'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
    'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN',
    'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
    'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
}
COUNTRIES = {'Bermuda', 'Canada', 'Cayman Islands', 'Puerto Rico', 'United States',
             'Mexico', 'El Salvador'}
NOISE = re.compile(
    r"^(Preferred Services|North American Reciprocal|.*NARM (privileges|identification).*"
    r"|https?://|.?2026 North American|\d+\s*$|\d+\s+Restrictions|Restrictions$"
    r"|All rights reserved)", re.I)
PHONE = re.compile(r'(\+?[\d]{3}[-.)( ][\d\-.();, ]{7,})\s*$')
SYMS = re.compile(r'\s*(\*{1,3}|#{1,2}|\^|\*\^)+\s*$')

CANADA_CITIES = {
    'edmonton': (53.546, -113.494), 'kamloops': (50.676, -120.341), 'kelowna': (49.888, -119.496),
    'vernon': (50.267, -119.272), 'victoria': (48.428, -123.365), 'brandon': (49.848, -99.950),
    'winnipeg': (49.895, -97.138), 'fredericton': (45.963, -66.643), 'halifax': (44.649, -63.575),
    'delhi': (42.853, -80.500), 'hamilton': (43.256, -79.871), 'kleinburg': (43.844, -79.628),
    'mississauga': (43.589, -79.644), 'ottawa': (45.421, -75.697), 'sarnia': (42.975, -82.404),
    'sudbury': (46.492, -80.991), 'waterford': (42.933, -80.288), 'waterloo': (43.464, -80.520),
    'montreal': (45.502, -73.567), 'toronto': (43.653, -79.383), 'london': (42.984, -81.246),
    'kingston': (44.231, -76.486), 'windsor': (42.317, -83.026), 'calgary': (51.045, -114.057),
    'saskatoon': (52.134, -106.647), 'regina': (50.445, -104.618), 'quebec city': (46.813, -71.208),
    "st. john's": (47.561, -52.712), 'charlottetown': (46.238, -63.129), 'moncton': (46.088, -64.778),
    'guelph': (43.544, -80.248), 'oshawa': (43.897, -78.865), 'owen sound': (44.567, -80.943),
    'peterborough': (44.305, -78.320), 'stratford': (43.370, -80.982), 'burnaby': (49.249, -122.980),
    'kenora': (49.767, -94.489), 'simcoe': (42.837, -80.304),
}
MANUAL = {
    ('devonshire', 'Bermuda'): (32.3038, -64.7620), ('hamilton', 'Bermuda'): (32.2949, -64.7830),
    ('george town', 'Cayman Islands'): (19.2866, -81.3744),
    ('san juan', 'Puerto Rico'): (18.4655, -66.1057),
    ('balboa island', 'CA'): (33.6061, -117.8953), ('kensington', 'CT'): (41.6354, -72.7712),
    ('storrs', 'CT'): (41.8084, -72.2495), ('davie', 'FL'): (26.0814, -80.2806),
    ('north miami', 'FL'): (25.8901, -80.1867), ('sanibel island', 'FL'): (26.4489, -82.1221),
    ('tequesta', 'FL'): (26.9681, -80.1014), ('johns creek', 'GA'): (34.0289, -84.1986),
    ('milton', 'GA'): (34.1321, -84.3002), ("colton's point", 'MD'): (38.2193, -76.7619),
    ("st. mary's city", 'MD'): (38.1868, -76.4336), ('farmington hills', 'MI'): (42.4853, -83.3771),
    ('rochester hills', 'MI'): (42.6584, -83.1499), ('ho-ho-kus', 'NJ'): (40.9962, -74.1013),
    ('loveladies', 'NJ'): (39.6351, -74.1879), ('bonito river', 'NM'): (33.4961, -105.5230),
    ('setauket', 'NY'): (40.9454, -73.1012), ('staatsburgh', 'NY'): (41.8468, -73.9290),
    ('kirtland', 'OH'): (41.6289, -81.3612), ('put-in-bay', 'OH'): (41.6517, -82.8213),
    ('shaker heights', 'OH'): (41.4739, -81.5370), ('worthington', 'OH'): (40.0931, -83.0180),
    ('media', 'PA'): (39.9168, -75.3879), ('brownington', 'VT'): (44.8351, -72.1743),
    ('fife', 'WA'): (47.2393, -122.3571),
}


def extract_text(pdf_source):
    if re.match(r'https?://', pdf_source):
        blob = requests.get(pdf_source, timeout=120).content
        reader = PdfReader(io.BytesIO(blob))
    else:
        reader = PdfReader(pdf_source)
    text = '\n'.join(page.extract_text() or '' for page in reader.pages)
    return text.replace('’', "'").replace('�', "'")


def parse(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    entries = []
    ctx = {'country': None, 'state': None, 'dc': False}

    def flush(buf):
        if not buf:
            return
        l = buf.strip().rstrip(',')
        pm = PHONE.search(l)
        phone = pm.group(1).strip().rstrip(';,') if pm else ''
        body = l[:pm.start()].rstrip(' ,') if pm else l
        if ctx['dc']:
            city, name, st = 'Washington', body, 'DC'
        elif ctx['country'] == 'Canada':
            m = re.match(r'^([A-Z]{2}), ([^,]+), (.+)$', body)
            if not m:
                return
            st, city, name = m.group(1), m.group(2), m.group(3)
        else:
            m = re.match(r'^([^,]+), (.+)$', body)
            if not m:
                return
            city, name = m.group(1), m.group(2)
            st = ctx['state'] if ctx['country'] == 'United States' else ''
        sm = SYMS.search(name)
        syms = sm.group(0).strip() if sm else ''
        if sm:
            name = name[:sm.start()].strip()
        name = name.rstrip(',').strip()
        if len(name) < 3 or len(city) > 40:
            return
        entries.append({'name': name, 'city': city, 'state': st,
                        'country': ctx['country'], 'phone': phone, 'symbols': syms})

    buf = ''
    for l in lines:
        if l in COUNTRIES:
            flush(buf); buf = ''
            ctx.update(country=l, state=None, dc=False)
            continue
        if l in US_STATES:
            flush(buf); buf = ''
            ctx.update(country='United States', state=US_STATES[l], dc=False)
            continue
        if l == 'District of Columbia, Washington':
            flush(buf); buf = ''
            ctx.update(country='United States', state='DC', dc=True)
            continue
        if NOISE.match(l) or ctx['country'] is None:
            continue
        buf = (buf + ' ' + l).strip() if buf else l
        if PHONE.search(buf):
            flush(buf); buf = ''
    flush(buf)
    return entries


def geocode(entries, us_zip_path):
    us = defaultdict(list)
    if str(us_zip_path).endswith('.zip'):
        with zipfile.ZipFile(us_zip_path) as z:
            raw = z.read('US.txt').decode('utf-8')
    else:
        raw = Path(us_zip_path).read_text(encoding='utf-8')
    for line in raw.splitlines():
        p = line.split('\t')
        if len(p) < 11:
            continue
        us[(p[2].lower(), p[4])].append((float(p[9]), float(p[10])))
    US = {k: (sum(a for a, _ in v) / len(v), sum(b for _, b in v) / len(v))
          for k, v in us.items()}

    misses = []
    for e in entries:
        city = re.sub(r'\s*\(.*\)$', '', e['city']).lower()
        key = (city, e['state'])
        got = None
        if e['country'] in ('United States', 'Puerto Rico'):
            got = US.get(key)
            if not got:
                alt = key[0].replace('st.', 'saint').replace('mt.', 'mount')
                got = US.get((alt, e['state']))
            if not got:
                got = MANUAL.get(key) or MANUAL.get((e['city'].lower(), e['country']))
        elif e['country'] == 'Canada':
            got = CANADA_CITIES.get(e['city'].lower())
        else:
            got = MANUAL.get((e['city'].lower(), e['country']))
        if got:
            e['lat'], e['lng'] = round(got[0], 4), round(got[1], 4)
        else:
            misses.append(e)
    return misses


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    text = extract_text(sys.argv[1])
    entries = parse(text)
    print(f'parsed {len(entries)} entries')
    print(Counter(e['country'] for e in entries))
    print('symbols:', Counter(e['symbols'] for e in entries if e['symbols']))

    us_zips = sys.argv[2] if len(sys.argv) > 2 else 'US.txt'
    misses = geocode(entries, us_zips)
    print(f'geocoded {len(entries) - len(misses)}, missing {len(misses)}')
    for e in misses:
        print('  MISS:', e['country'], e['state'], repr(e['city']), '|', e['name'][:60])

    ok = [e for e in entries if 'lat' in e]
    ok.sort(key=lambda x: (x['country'], x['state'], x['city'], x['name']))
    payload = {
        'source': 'NARM member list',
        'sourceUrl': sys.argv[1],
        'generated': str(date.today()),
        'count': len(ok),
        'participants': ok,
    }
    (ROOT / 'data' / 'narm.json').write_text(
        json.dumps(payload, indent=1, ensure_ascii=False), encoding='utf-8')
    print(f'wrote data/narm.json with {len(ok)} members')


if __name__ == '__main__':
    main()
