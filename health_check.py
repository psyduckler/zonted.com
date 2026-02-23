#!/usr/bin/env python3
"""Health check all API URLs from apis-raw.json and apis-zapier.json"""

import json
import time
import requests
import concurrent.futures
from datetime import datetime, timezone
from urllib.parse import urlparse
import re

# Parked/generic domain patterns (redirect targets that indicate dead APIs)
PARKED_PATTERNS = [
    r'sedo\.com', r'godaddy\.com/domainforsale', r'dan\.com',
    r'parking', r'domainmarket', r'buydomains', r'hugedomains',
    r'afternic', r'undeveloped\.com', r'brandpa\.com',
    r'namecheap\.com/domains/registration', r'networksolutions',
    r'register\.com', r'domain\.com/domains',
    r'domainsbyproxy', r'squarespace\.com/domain',
    r'web\.com/domains', r'bluehost\.com/domains',
    r'hostgator\.com/domains', r'dreamhost\.com/domains',
    r'namebright\.com', r'bodis\.com',
    r'above\.com', r'parkingcrew\.net',
]

PARKED_RE = re.compile('|'.join(PARKED_PATTERNS), re.IGNORECASE)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; APIHealthChecker/1.0)',
    'Accept': 'text/html,application/xhtml+xml,application/json,*/*',
}

def is_parked(url):
    return bool(PARKED_RE.search(url))

def check_url(url):
    checked_at = datetime.now(timezone.utc).isoformat()
    result = {
        'url': url,
        'status': None,
        'http_code': None,
        'final_url': url,
        'response_time_ms': None,
        'error': None,
        'checked_at': checked_at,
    }

    session = requests.Session()
    session.max_redirects = 5

    start = time.time()
    try:
        # Try HEAD first
        resp = session.head(url, headers=HEADERS, timeout=10, allow_redirects=True)
        elapsed = (time.time() - start) * 1000
        
        # If HEAD returns 405 or 400, fall back to GET
        if resp.status_code in (405, 400, 403, 501) or resp.status_code >= 500:
            start2 = time.time()
            try:
                resp2 = session.get(url, headers=HEADERS, timeout=10, allow_redirects=True, stream=True)
                # Read just a tiny bit to confirm connection
                resp2.raw.read(256)
                resp2.close()
                elapsed = (time.time() - start2) * 1000
                # Use GET result if it's better
                if resp2.status_code < resp.status_code or resp.status_code in (405, 501):
                    resp = resp2
            except Exception:
                pass  # Stick with HEAD result

        code = resp.status_code
        final = resp.url

        result['http_code'] = code
        result['final_url'] = final
        result['response_time_ms'] = round(elapsed)

        # Check if redirected to a parked page
        if is_parked(final):
            result['status'] = 'deprecated'
            result['error'] = f'Redirects to parked/domain-sale page: {final}'
        elif 200 <= code <= 299:
            result['status'] = 'alive'
        elif code in (301, 302, 303, 307, 308):
            # Final URL was followed by requests, so if we're here the final is alive
            result['status'] = 'redirect'
        elif code in (403, 429):
            result['status'] = 'warning'
        elif code == 404 or code == 410:
            result['status'] = 'deprecated'
        elif code >= 500:
            result['status'] = 'deprecated'
        elif code in (401, 402):
            # Auth required — API exists but needs key
            result['status'] = 'warning'
        else:
            result['status'] = 'warning'

    except requests.exceptions.SSLError as e:
        elapsed = (time.time() - start) * 1000
        result['response_time_ms'] = round(elapsed)
        result['status'] = 'deprecated'
        result['error'] = f'SSL error: {str(e)[:200]}'
    except requests.exceptions.ConnectionError as e:
        elapsed = (time.time() - start) * 1000
        result['response_time_ms'] = round(elapsed)
        result['status'] = 'deprecated'
        result['error'] = f'Connection error: {str(e)[:200]}'
    except requests.exceptions.Timeout:
        elapsed = (time.time() - start) * 1000
        result['response_time_ms'] = round(elapsed)
        result['status'] = 'deprecated'
        result['error'] = 'Timeout (10s)'
    except requests.exceptions.TooManyRedirects:
        elapsed = (time.time() - start) * 1000
        result['response_time_ms'] = round(elapsed)
        result['status'] = 'deprecated'
        result['error'] = 'Too many redirects'
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        result['response_time_ms'] = round(elapsed)
        result['status'] = 'deprecated'
        result['error'] = f'Error: {str(e)[:200]}'

    return result


def main():
    print("Loading source files...")
    with open('apis-raw.json') as f:
        raw_data = json.load(f)
    with open('apis-zapier.json') as f:
        zapier_data = json.load(f)

    # Build URL -> API name mapping for both files
    url_to_apis = {}  # url -> list of (name, source)

    for cat, apis in raw_data['categories'].items():
        for api in apis:
            u = api.get('url')
            if u:
                url_to_apis.setdefault(u, []).append((api['name'], 'raw'))

    for api in zapier_data:
        u = api.get('url')
        if u:
            url_to_apis.setdefault(u, []).append((api['name'], 'zapier'))

    all_urls = list(url_to_apis.keys())
    total = len(all_urls)
    print(f"Total unique URLs to check: {total}")

    results = []
    done = 0
    BATCH = 50
    WORKERS = 50

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        # Submit in batches
        for batch_start in range(0, total, BATCH):
            batch = all_urls[batch_start:batch_start + BATCH]
            futures = {executor.submit(check_url, url): url for url in batch}
            for fut in concurrent.futures.as_completed(futures):
                res = fut.result()
                results.append(res)
                done += 1
                if done % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = done / elapsed
                    eta = (total - done) / rate if rate > 0 else 0
                    print(f"  [{done}/{total}] {elapsed:.0f}s elapsed, ETA ~{eta:.0f}s")
            # Polite delay between batches
            if batch_start + BATCH < total:
                time.sleep(0.1)

    total_time = time.time() - start_time
    print(f"\nCompleted {total} URLs in {total_time:.1f}s")

    # Save results
    print("Saving url-health-check.json...")
    with open('url-health-check.json', 'w') as f:
        json.dump(results, f, indent=2)

    # --- Summary stats ---
    alive = [r for r in results if r['status'] == 'alive']
    redirect = [r for r in results if r['status'] == 'redirect']
    deprecated = [r for r in results if r['status'] == 'deprecated']
    warning = [r for r in results if r['status'] == 'warning']

    print(f"\nResults:")
    print(f"  Alive:      {len(alive)}")
    print(f"  Redirect:   {len(redirect)}")
    print(f"  Deprecated: {len(deprecated)}")
    print(f"  Warning:    {len(warning)}")

    # Build URL -> result lookup
    url_result = {r['url']: r for r in results}
    deprecated_urls = {r['url'] for r in deprecated}
    warning_urls = {r['url'] for r in warning}

    # --- Write summary markdown ---
    print("Saving health-check-summary.md...")
    lines = [
        "# API URL Health Check Summary",
        f"\n**Checked:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Total URLs checked:** {total}",
        f"**Alive:** {len(alive)}  ",
        f"**Redirect (alive final):** {len(redirect)}  ",
        f"**Deprecated:** {len(deprecated)}  ",
        f"**Warning (auth/unusual):** {len(warning)}  ",
        "",
        "---",
        "",
        "## Deprecated URLs",
        "",
        "| API Name | Source | URL | HTTP Code | Error |",
        "|----------|--------|-----|-----------|-------|",
    ]

    for r in sorted(deprecated, key=lambda x: x['url']):
        u = r['url']
        names = url_to_apis.get(u, [('Unknown', '?')])
        for name, source in names:
            code = r['http_code'] or 'N/A'
            err = (r['error'] or '').replace('|', '/').replace('\n', ' ')[:80]
            lines.append(f"| {name} | {source} | {u} | {code} | {err} |")

    lines += [
        "",
        "---",
        "",
        "## Warning URLs (403/429/Auth Required)",
        "",
        "| API Name | Source | URL | HTTP Code |",
        "|----------|--------|-----|-----------|",
    ]

    for r in sorted(warning, key=lambda x: x['url']):
        u = r['url']
        names = url_to_apis.get(u, [('Unknown', '?')])
        for name, source in names:
            code = r['http_code'] or 'N/A'
            lines.append(f"| {name} | {source} | {u} | {code} |")

    with open('health-check-summary.md', 'w') as f:
        f.write('\n'.join(lines))

    # --- Update apis-raw.json ---
    print("Updating apis-raw.json with deprecated status...")
    updated_raw = 0
    for cat, apis in raw_data['categories'].items():
        for api in apis:
            u = api.get('url')
            if u and u in deprecated_urls:
                api['status'] = 'deprecated'
                updated_raw += 1
            elif 'status' in api and api['status'] == 'deprecated' and u not in deprecated_urls:
                # Remove stale deprecated if it's now alive
                del api['status']
    print(f"  Marked {updated_raw} entries deprecated in apis-raw.json")

    with open('apis-raw.json', 'w') as f:
        json.dump(raw_data, f, indent=2)

    # --- Update apis-zapier.json ---
    print("Updating apis-zapier.json with deprecated status...")
    updated_zapier = 0
    for api in zapier_data:
        u = api.get('url')
        if u and u in deprecated_urls:
            api['status'] = 'deprecated'
            updated_zapier += 1
        elif 'status' in api and api['status'] == 'deprecated' and u not in deprecated_urls:
            del api['status']
    print(f"  Marked {updated_zapier} entries deprecated in apis-zapier.json")

    with open('apis-zapier.json', 'w') as f:
        json.dump(zapier_data, f, indent=2)

    print("\nAll done!")
    print(f"  url-health-check.json — {total} results")
    print(f"  health-check-summary.md — summary")
    print(f"  apis-raw.json — {updated_raw} deprecated marked")
    print(f"  apis-zapier.json — {updated_zapier} deprecated marked")


if __name__ == '__main__':
    main()
