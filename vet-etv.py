import json, urllib.request, os, base64, time, sys
from urllib.parse import urlparse

login = os.popen('security find-generic-password -s dataforseo-login -w').read().strip()
password = os.popen('security find-generic-password -s dataforseo-password -w').read().strip()
creds = base64.b64encode(f"{login}:{password}".encode()).decode()

data = json.load(open('apis-all.json'))
cats = data['categories']

# Extract unique domains
api_domains = []
for cat_name, apis in cats.items():
    for a in apis:
        url = a.get('url', '')
        if url:
            domain = urlparse(url).netloc.replace('www.', '')
            if domain:
                api_domains.append((cat_name, a, domain))

print(f"Total APIs to check: {len(api_domains)}", flush=True)

# Dedupe domains to avoid redundant calls
unique_domains = {}
for cat, api, domain in api_domains:
    if domain not in unique_domains:
        unique_domains[domain] = []
    unique_domains[domain].append((cat, api))

print(f"Unique domains: {len(unique_domains)}", flush=True)

# Fetch ETV for each unique domain
domain_etv = {}
errors = 0
for i, domain in enumerate(unique_domains.keys()):
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
        
        # Find self in items
        etv = None
        for item in items:
            if domain.split('.')[0] in item['domain']:
                etv = item['full_domain_metrics']['organic']['etv']
                break
        
        if etv is None and items:
            # Self not found — domain might be too small to appear. ETV = 0
            etv = 0
        elif etv is None:
            etv = 0
            
        domain_etv[domain] = etv
    except Exception as e:
        domain_etv[domain] = -1  # error
        errors += 1
    
    if (i + 1) % 50 == 0:
        print(f"  Progress: {i+1}/{len(unique_domains)} domains checked ({errors} errors)", flush=True)
    
    time.sleep(0.2)  # rate limit

print(f"\nDone fetching. {len(domain_etv)} domains, {errors} errors.", flush=True)

# Apply ETV to APIs and mark unvetted
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

# Save ETV lookup for reference
with open('domain-etv.json', 'w') as f:
    json.dump(domain_etv, f, indent=2)

print(f"\nResults: {vetted} vetted (ETV >= 1000) | {unvetted} unvetted (ETV < 1000) | {len(api_domains) - vetted - unvetted} unknown/error", flush=True)
