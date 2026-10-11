"""verify_refs.py: check every entry in refs.py against the CrossRef REST API (run on a machine with internet access).
Usage: python3 verify_refs.py
Output: output/tables/reference_verification.csv with columns key, status, similarity, crossref_title, crossref_year, doi.
Status OK = title similarity >= 0.85 and publication year within one year; REVIEW otherwise. Books and chapters
(Hannum 2007, Bound 2001, Cunha 2006, Currie 2011) can fail title matching and must be checked by hand (WorldCat or publisher page).
A REVIEW or NOT_FOUND flag means: do not cite until checked."""
import csv, difflib, json, os, re, time, urllib.parse, urllib.request
from refs import REFS

OUT = os.path.join(os.path.dirname(__file__), '..', 'output', 'tables', 'reference_verification.csv')

def split_ref(txt):
    m = re.match(r'^(.*?),\s(\d{4})\.\s(.*)$', txt)
    authors, year, rest = m.group(1), int(m.group(2)), m.group(3)
    title = rest.split('. ')[0]
    return authors, year, title

def norm(s): return re.sub(r'[^a-z0-9 ]', '', s.lower())

rows = []
for key, (label, year, txt) in REFS.items():
    authors, y, title = split_ref(txt)
    q = urllib.parse.quote(f'{title} {authors.split(",")[0]}')
    url = f'https://api.crossref.org/works?query.bibliographic={q}&rows=3&select=DOI,title,issued,container-title'
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            items = json.load(r)['message']['items']
        best = None
        for it in items:
            t = (it.get('title') or [''])[0]
            sim = difflib.SequenceMatcher(None, norm(title), norm(t)).ratio()
            yr = (it.get('issued', {}).get('date-parts') or [[None]])[0][0]
            if best is None or sim > best[0]: best = (sim, t, yr, it.get('DOI'))
        status = 'OK' if best and best[0] >= 0.85 and best[2] and abs(best[2] - y) <= 1 else 'REVIEW'
        rows.append([key, status, round(best[0], 3) if best else '', best[1] if best else '', best[2] if best else '', best[3] if best else ''])
    except Exception as e:
        rows.append([key, 'NOT_FOUND', '', str(e), '', ''])
    time.sleep(0.5)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['key', 'status', 'similarity', 'crossref_title', 'crossref_year', 'doi']); w.writerows(rows)
print(f'wrote {OUT}'); print({s: sum(r[1] == s for r in rows) for s in ('OK', 'REVIEW', 'NOT_FOUND')})
