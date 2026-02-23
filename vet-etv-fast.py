import json, urllib.request, os, base64, time
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

login = os.popen('security find-generic-password -s dataforseo-login -w').read().strip()
password = os.popen('security find-generic-password -s dataforseo-password -w').read().strip()
creds = base64.b64encode(f"{login}:{password}".encode()).decode()

data = json.load(open('apis-all.json'))
cats = data['categories']

# Load any partial progress
try:
    domain_etv = json.load(open('domain-etv.json'))
    print(f"Loaded {len(domain_etv)} cached results", flush=True)
except:
    domain_etv = {}

# Extract unique domains
api_domains = []
for cat_name, apis in cats.items():
    for a in apis:
        url = a.get('url', '')
        if url:
            domain = urlparse(url).netloc.replace('www.', '')
            if domain:
                api_domains.append((cat_name, a, domain))

unique_domains = set(d for _, _, d in api_domains)
# Skip already-fetched
remaining = [d for d in unique_domains if d not in domain_etv]
print(f"Total unique: {len(unique_domains)} | Already cached: {len(domain_etv)} | Remaining: {len(remaining)}", flush=True)

errors = 0
done = 0

def fetch_etv(domain):
    payload = json.dumps([{"target": domain, "location_code": 2840, "language_code": "en"}]).encode()
    req = urllib.request.Request(
        "https://api.dataforseo.com/v3/dataforseo_labs/google/competitors_domain/live",
        data=payload,
        headers={"Authorization": f"Basic {creds}", "Content-Type": "application/json"}
    )
    try:
        resp = urllib.request.urlopen(req, timeout=20)
        result = json.loads(resp.read())
        task = result['tasks'][0]
        items = task.get('result', [{}])[0].get('items', []) if task.get('result') else []
        
        for item in items:
            if domain.split('.')[0] in item['domain']:
                return domain, item['full_domain_metrics']['organic']['etv']
        return domain, 0  # not found = tiny site
    except Exception as e:
        return domain, -1

# Run 10 concurrent
with ThreadPoolExecutor(max_workers=10) as pool:
    futures = {pool.submit(fetch_etv, d): d for d in remaining}
    for f in as_completed(futures):
        domain, etv = f.result()
        domain_etv[domain] = etv
        done += 1
        if etv == -1:
            errors += 1
        if done % 100 == 0:
            print(f"  Progress: {done}/{len(remaining)} ({errors} errors)", flush=True)
            # Save checkpoint
            with open('domain-etv.json', 'w') as fp:
                json.dump(domain_etv, fp)

print(f"\nDone: {done} fetched, {errors} errors", flush=True)

# Save final ETV lookup
with open('domain-etv.json', 'w') as f:
    json.dump(domain_etv, f, indent=2)

# Apply to APIs
vetted = 0
unvetted = 0
for cat_name, apis in cats.items():
    for a in apis:
        url = a.get('url', '')
        domain = urlparse(url).netloc.replace('www.', '') if url else ''
        etv = domain_etv.get(domain, -1)
        a['etv'] = etv
        if etv >= 0 and etv < 1000:
            a['vetted'] = False
            a['vet_reason'] = f'Low ETV ({etv:.0f})'
            unvetted += 1
        elif etv >= 1000:
            a['vetted'] = True
            vetted += 1

with open('apis-all.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"\nResults: {vetted} vetted (ETV >= 1000) | {unvetted} unvetted (ETV < 1000) | {len(api_domains) - vetted - unvetted} unknown/error", flush=True)
