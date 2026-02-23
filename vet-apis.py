import json, os, time, urllib.request, urllib.parse

SERPAPI_KEY = os.popen('security find-generic-password -s serpapi-key -w').read().strip()
data = json.load(open('apis-all.json'))

# Flatten first 50
apis_flat = []
for cat_name, apis in data['categories'].items():
    for a in apis:
        apis_flat.append((cat_name, a))
        if len(apis_flat) >= 50:
            break
    if len(apis_flat) >= 50:
        break

doc_keywords = ['api', 'docs', 'documentation', 'reference', 'developer', 'swagger', 'openapi', 
                'endpoints', 'sdk', 'integration', 'guide', 'getting started']

results = []
for i, (cat, api) in enumerate(apis_flat):
    name = api['name']
    query = f"{name} API documentation"
    params = urllib.parse.urlencode({'q': query, 'api_key': SERPAPI_KEY, 'engine': 'google', 'num': 5})
    url = f"https://serpapi.com/search.json?{params}"
    
    try:
        resp = urllib.request.urlopen(url, timeout=15)
        search = json.loads(resp.read())
        organic = search.get('organic_results', [])
        
        # Check if any result looks like real API docs
        doc_url = None
        doc_evidence = []
        for r in organic[:5]:
            title = (r.get('title', '') + ' ' + r.get('snippet', '')).lower()
            link = r.get('link', '')
            matches = [kw for kw in doc_keywords if kw in title]
            if len(matches) >= 2 or 'documentation' in title or '/docs' in link.lower() or '/api' in link.lower():
                doc_url = link
                doc_evidence = matches
                break
        
        vetted = doc_url is not None
        result = {
            'name': name,
            'category': cat,
            'vetted': vetted,
            'docs_url': doc_url,
            'top_results': len(organic)
        }
        results.append(result)
        
        status = "✅" if vetted else "❌"
        print(f"{i+1}/50 {status} {name} — {doc_url or 'no docs found'}")
        
        # Update the API in the main data
        api['vetted'] = vetted
        if doc_url:
            api['docs_url'] = doc_url
            
    except Exception as e:
        print(f"{i+1}/50 ⚠️  {name} — error: {e}")
        results.append({'name': name, 'category': cat, 'vetted': False, 'error': str(e)})
    
    time.sleep(0.5)  # rate limit

# Save updated data
with open('apis-all.json', 'w') as f:
    json.dump(data, f, indent=2)

# Save vet results
with open('vet-results-batch1.json', 'w') as f:
    json.dump(results, f, indent=2)

vetted_count = sum(1 for r in results if r.get('vetted'))
print(f"\n--- Results: {vetted_count}/50 vetted (docs found) ---")
