"""Rebuild data/participants.json from the latest ASTC Travel Passport PDF.

Pipeline:
  1. Download the participant-list PDF (URL changes each season; pass it in).
  2. Parse names, addresses, phones, URLs, and proof-of-residence flags.
  3. Geocode US/PR addresses with the free Census Bureau batch geocoder,
     falling back to GeoNames ZIP centroids for non-matches.
  4. Merge with data/manual_locations.json for Canada/international entries
     (different address formats; there are only ~20).

Usage:  python tools/update_data.py <pdf-url-or-path>
Deps:   pip install pypdf requests
"""
import csv
import io
import json
import re
import sys
import zipfile
from datetime import date
from pathlib import Path

import requests
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent

US_STATES = {
    'ALABAMA', 'ALASKA', 'ARIZONA', 'ARKANSAS', 'CALIFORNIA', 'COLORADO', 'CONNECTICUT',
    'DELAWARE', 'FLORIDA', 'GEORGIA', 'HAWAII', 'IDAHO', 'ILLINOIS', 'INDIANA', 'IOWA',
    'KANSAS', 'KENTUCKY', 'LOUISIANA', 'MAINE', 'MARYLAND', 'MASSACHUSETTS', 'MICHIGAN',
    'MINNESOTA', 'MISSISSIPPI', 'MISSOURI', 'MONTANA', 'NEBRASKA', 'NEVADA',
    'NEW HAMPSHIRE', 'NEW JERSEY', 'NEW MEXICO', 'NEW YORK', 'NORTH CAROLINA',
    'NORTH DAKOTA', 'OHIO', 'OKLAHOMA', 'OREGON', 'PENNSYLVANIA', 'PUERTO RICO',
    'RHODE ISLAND', 'SOUTH CAROLINA', 'SOUTH DAKOTA', 'TENNESSEE', 'TEXAS', 'UTAH',
    'VERMONT', 'VIRGINIA', 'WASHINGTON', 'WEST VIRGINIA', 'WISCONSIN', 'WYOMING',
}
INTL = {
    'AUSTRALIA', 'BERMUDA', 'CANADA', 'CZECH REPUBLIC', 'ISRAEL', 'MALAYSIA',
    'PHILIPPINES', 'SINGAPORE', 'MEXICO', 'UNITED KINGDOM',
}
VALID_HDRS = US_STATES | INTL

US_ADDR = re.compile(r'^(.*?),\s*([A-Za-z .\'-]+?),?\s+([A-Z]{2})\s+([0-9]{5}(?:-[0-9]{4})?)\s*$')
PHONE = re.compile(r'^\+?[\d(][\d() .\-+]{6,}$')
EMAIL = re.compile(r'\S+@\S+\.\S+')
URL = re.compile(r'^(https?://|www\.)\S+', re.I)
NOISE = re.compile(
    r'^(Reciprocal Membership|Individual Membership|Group Membership|Proof of Residence'
    r'|Please contact|CALL THE MUSEUM|Lost your card|.*free GENERAL ADMISSION.*|\s*)$', re.I)


def extract_text(pdf_source):
    if re.match(r'https?://', pdf_source):
        blob = requests.get(pdf_source, timeout=120).content
        reader = PdfReader(io.BytesIO(blob))
    else:
        reader = PdfReader(pdf_source)
    return '\n'.join(page.extract_text() or '' for page in reader.pages)


def parse(text):
    lines = [l.strip() for l in text.split('\n')]
    entries, hdr = [], None
    for i, line in enumerate(lines):
        if line in VALID_HDRS:
            hdr = line
            continue
        m = US_ADDR.match(line)
        if not (m and hdr and hdr in US_STATES):
            continue
        street, city, st, zipc = m.group(1).strip(), m.group(2).strip(), m.group(3), m.group(4)

        # walk back for the (possibly wrapped) name
        name_parts, j = [], i - 1
        while j >= 0:
            lj = lines[j]
            if (lj in VALID_HDRS or NOISE.match(lj) or US_ADDR.match(lj) or PHONE.match(lj)
                    or EMAIL.search(lj) or URL.match(lj) or 'Membership' in lj or lj.endswith(',')):
                break
            name_parts.insert(0, lj)
            j -= 1
        name = re.sub(r'\s+', ' ', ' '.join(name_parts)).strip()
        if 'Proof of Residence Required' in name:  # previous entry's flag line leaked in
            name = name.split('Proof of Residence Required')[-1].strip()

        # walk forward for phone / url / proof flag (stops at the next address)
        phone = url = ''
        proof = False
        k = i + 1
        while k < len(lines) and k < i + 30:
            lk = lines[k]
            if US_ADDR.match(lk) or lk in VALID_HDRS:
                break
            if not phone and PHONE.match(lk):
                phone = lk
            if not url and URL.match(lk):
                url = lk
            if 'Proof of Residence Required' in lk:
                proof = True
            k += 1
        entries.append({'name': name, 'street': street, 'city': city, 'state': st,
                        'zip': zipc, 'region': hdr.title(), 'phone': phone,
                        'url': url.rstrip('.,'), 'proofOfResidence': proof})
    return entries


def geocode(entries):
    csv_buf = io.StringIO()
    for idx, e in enumerate(entries):
        csv_buf.write(f'{idx},"{e["street"]}","{e["city"]}","{e["state"]}","{e["zip"]}"\n')
    resp = requests.post(
        'https://geocoding.geo.census.gov/geocoder/locations/addressbatch',
        files={'addressFile': ('addr.csv', csv_buf.getvalue())},
        data={'benchmark': 'Public_AR_Current'}, timeout=300)
    resp.raise_for_status()

    zips = {}
    matched = 0
    for row in csv.reader(io.StringIO(resp.text)):
        if len(row) < 3:
            continue
        e = entries[int(row[0])]
        if row[2] == 'Match' and len(row) >= 6:
            lng, lat = row[5].split(',')
            e['lat'], e['lng'] = round(float(lat), 5), round(float(lng), 5)
            e['geoPrecision'] = 'exact'
            matched += 1
    print(f'census exact matches: {matched}/{len(entries)}')

    misses = [e for e in entries if 'lat' not in e]
    if misses:
        blob = requests.get('https://download.geonames.org/export/zip/US.zip', timeout=120).content
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            for line in z.read('US.txt').decode('utf-8').splitlines():
                p = line.split('\t')
                zips[p[1]] = (float(p[9]), float(p[10]))
        for e in misses:
            z5 = e['zip'][:5]
            if z5 in zips:
                e['lat'], e['lng'] = zips[z5]
                e['geoPrecision'] = 'zip-centroid'
            else:
                print('  UNRESOLVED:', e['name'], e['city'], e['state'], e['zip'])


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    text = extract_text(sys.argv[1])
    entries = parse(text)
    print(f'parsed {len(entries)} US/PR entries')
    geocode(entries)

    manual = json.loads((ROOT / 'data' / 'manual_locations.json').read_text(encoding='utf-8'))
    entries += manual['participants']

    out = []
    for e in entries:
        if 'lat' not in e:
            continue
        e.pop('zip', None)
        out.append(e)
    out.sort(key=lambda x: (x['region'], x['name']))
    payload = {
        'source': f'ASTC Travel Passport Program Participants (regenerated {date.today()})',
        'sourceUrl': sys.argv[1],
        'generated': str(date.today()),
        'count': len(out),
        'participants': out,
    }
    (ROOT / 'data' / 'participants.json').write_text(
        json.dumps(payload, indent=1, ensure_ascii=False), encoding='utf-8')
    print(f'wrote data/participants.json with {len(out)} participants — now run tools/build.py')


if __name__ == '__main__':
    main()
