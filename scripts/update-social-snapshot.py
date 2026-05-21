#!/usr/bin/env python3
"""Refresh the Tabiji Social Snapshot block on zonted.com/metrics/.

Uses first-party/public sources where available:
- Instagram Graph API via keychain service `instagram-access-token`
- YouTube public Shorts page via the existing metrics helper / yt-dlp
- TikTok public profile page scrape
- Pinterest API via keychain tokens when valid; otherwise preserves the last snapshot
"""
from __future__ import annotations

import datetime as dt
import html
import importlib.util
import json
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METRICS_HTML = ROOT / "metrics" / "index.html"
IG_USER_ID = "17841449394591017"
IG_TOKEN_SERVICE = "instagram-access-token"
PINTEREST_ACCESS_SERVICE = "pinterest-access-token"
PINTEREST_REFRESH_SERVICE = "pinterest-refresh-token"
PINTEREST_APP_ID_SERVICE = "pinterest-app-id"
PINTEREST_APP_SECRET_SERVICE = "pinterest-app-secret"
TIKTOK_PROFILE_URL = "https://www.tiktok.com/@tabiji1"

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36"


def keychain(service: str) -> str:
    proc = subprocess.run(["security", "find-generic-password", "-s", service, "-w"], capture_output=True, text=True)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def keychain_set(service: str, value: str, account: str = "tabijiai") -> None:
    subprocess.run(["security", "add-generic-password", "-U", "-s", service, "-a", account, "-w", value], check=True)


def fmt(n: float | int) -> str:
    return f"{int(round(float(n or 0))):,}"


def compact(n: float | int) -> str:
    n = float(n or 0)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return fmt(n)


def label_for(day: dt.date) -> str:
    return f"{day.strftime('%b')} {day.day}"


def request_json(url: str, *, headers: dict[str, str] | None = None, data: bytes | None = None) -> dict:
    req = urllib.request.Request(url, headers=headers or {}, data=data)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")[:600]
        body = re.sub(r"access_token=[^&\s]+", "access_token=<redacted>", body)
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc


def fetch_instagram() -> dict:
    token = keychain(IG_TOKEN_SERVICE)
    if not token:
        raise RuntimeError(f"missing keychain token {IG_TOKEN_SERVICE}")

    base = f"https://graph.facebook.com/v24.0/{IG_USER_ID}"

    def graph(path: str, params: dict[str, object]) -> dict:
        qs = urllib.parse.urlencode({**params, "access_token": token})
        return request_json(f"{base}{path}?{qs}")

    profile = graph("", {"fields": "username,followers_count,media_count,name"})
    today = dt.date.today()
    start = today - dt.timedelta(days=90)
    end = today

    reach_by_date: dict[dt.date, int] = {}
    totals = {"views": 0, "total_interactions": 0}
    cur = start
    while cur < end:
        nxt = min(cur + dt.timedelta(days=30), end)
        reach_payload = graph(
            "/insights",
            {"metric": "reach", "period": "day", "since": cur.isoformat(), "until": nxt.isoformat()},
        )
        for row in reach_payload.get("data", [{}])[0].get("values", []):
            day = dt.datetime.strptime(row["end_time"][:10], "%Y-%m-%d").date()
            reach_by_date[day] = int(row.get("value") or 0)

        total_payload = graph(
            "/insights",
            {
                "metric": "views,total_interactions",
                "period": "day",
                "metric_type": "total_value",
                "since": cur.isoformat(),
                "until": nxt.isoformat(),
            },
        )
        for row in total_payload.get("data", []):
            name = row.get("name")
            if name in totals:
                totals[name] += int(row.get("total_value", {}).get("value") or 0)
        cur = nxt

    labels: list[str] = []
    series: list[int] = []
    for i in range(90):
        day = start + dt.timedelta(days=i)
        labels.append(label_for(day))
        series.append(reach_by_date.get(day, 0))

    return {
        "key": "instagram",
        "name": "Instagram",
        "handle": f"@{profile.get('username') or 'tabiji.ai'}",
        "color": "#c13584",
        "total": compact(totals["views"]),
        "label": "views (90d)",
        "chartType": "line",
        "chartLabel": "Reach",
        "labels": labels,
        "series": series,
        "rows": [
            {"label": "Followers", "value": fmt(profile.get("followers_count") or 0)},
            {"label": "Reach", "value": compact(sum(series))},
            {"label": "Interactions", "value": fmt(totals["total_interactions"])},
        ],
    }


def fetch_youtube() -> dict:
    helper = ROOT / "scripts" / "update-metrics-cron.py"
    spec = importlib.util.spec_from_file_location("zonted_metrics_helper", helper)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not import YouTube metrics helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    youtube = module.fetch_youtube_metrics()
    series = youtube.get("timeSeries", {})
    return {
        "key": "youtube",
        "name": "YouTube Shorts",
        "handle": youtube.get("handle") or "@tabijiai",
        "color": "#cc0000",
        "total": fmt(youtube.get("totalViews") or 0),
        "label": "channel views",
        "chartType": "line",
        "chartLabel": "Views by publish date",
        "labels": series.get("labels") or [],
        "series": series.get("series") or [],
        "tension": 0.35,
        "pointRadius": 0,
        "chartRange": series.get("range") or "",
        "rows": [
            {"label": "Subscribers", "value": fmt(youtube.get("subscribers") or 0)},
            {"label": "Videos", "value": fmt(youtube.get("videos") or 0)},
            {"label": "Tracked views", "value": compact(youtube.get("trackedViews") or 0)},
        ],
    }


def fetch_tiktok() -> dict:
    req = urllib.request.Request(TIKTOK_PROFILE_URL, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    page = urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "ignore")
    values: dict[str, int] = {}
    for key in ("followerCount", "followingCount", "heartCount", "videoCount"):
        match = re.search(rf'"{key}":(\d+)', page)
        if not match:
            raise RuntimeError(f"could not find TikTok {key}")
        values[key] = int(match.group(1))
    return {
        "key": "tiktok",
        "name": "TikTok",
        "handle": "@tabiji1",
        "color": "#111111",
        "total": fmt(values["heartCount"]),
        "label": "total likes",
        "chartType": "bar",
        "chartLabel": "Profile metrics",
        "labels": ["Followers", "Likes", "Videos"],
        "series": [values["followerCount"], values["heartCount"], values["videoCount"]],
        "rows": [
            {"label": "Followers", "value": fmt(values["followerCount"])},
            {"label": "Videos", "value": fmt(values["videoCount"])},
            {"label": "Following", "value": fmt(values["followingCount"])},
        ],
    }


def refresh_pinterest_token() -> None:
    app_id = keychain(PINTEREST_APP_ID_SERVICE)
    app_secret = keychain(PINTEREST_APP_SECRET_SERVICE)
    refresh = keychain(PINTEREST_REFRESH_SERVICE)
    if not all([app_id, app_secret, refresh]):
        return
    body = urllib.parse.urlencode({"grant_type": "refresh_token", "refresh_token": refresh}).encode()
    auth = __import__("base64").b64encode(f"{app_id}:{app_secret}".encode()).decode()
    payload = request_json(
        "https://api.pinterest.com/v5/oauth/token",
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"},
        data=body,
    )
    if payload.get("access_token"):
        keychain_set(PINTEREST_ACCESS_SERVICE, payload["access_token"])
    if payload.get("refresh_token"):
        keychain_set(PINTEREST_REFRESH_SERVICE, payload["refresh_token"])


def fetch_pinterest(existing: dict) -> dict:
    """Best effort. If Pinterest auth is stale/revoked, preserve the previous analytics card."""
    try:
        refresh_pinterest_token()
        token = keychain(PINTEREST_ACCESS_SERVICE)
        if not token:
            raise RuntimeError("missing Pinterest access token")
        today = dt.date.today()
        start = today - dt.timedelta(days=90)
        end = today - dt.timedelta(days=1)
        params = urllib.parse.urlencode(
            {
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "metric_types": ["IMPRESSION", "SAVE", "OUTBOUND_CLICK"],
                "split_field": "NO_SPLIT",
            },
            doseq=True,
        )
        payload = request_json(
            f"https://api.pinterest.com/v5/user_account/analytics?{params}",
            headers={"Authorization": f"Bearer {token}"},
        )
        # Pinterest response shapes have varied. Support the documented daily_metrics
        # list while falling back safely if the token/app cannot read analytics.
        daily = None
        if isinstance(payload.get("all"), dict):
            daily = payload["all"].get("daily_metrics")
        if daily is None:
            daily = payload.get("daily_metrics")
        if not isinstance(daily, list):
            raise RuntimeError("Pinterest analytics response did not include daily metrics")
        labels: list[str] = []
        series: list[int] = []
        saves = 0
        outbound = 0
        for row in sorted(daily, key=lambda r: r.get("date", "")):
            day = dt.date.fromisoformat(row.get("date"))
            metrics = row.get("metrics", row)
            labels.append(label_for(day))
            series.append(int(metrics.get("IMPRESSION") or metrics.get("impression") or 0))
            saves += int(metrics.get("SAVE") or metrics.get("save") or 0)
            outbound += int(metrics.get("OUTBOUND_CLICK") or metrics.get("outbound_click") or 0)
        card = dict(existing)
        card.update(
            {
                "total": fmt(sum(series)),
                "labels": labels,
                "series": series,
                "rows": [
                    existing.get("rows", [{"label": "Monthly views", "value": "—"}])[0],
                    {"label": "Saves", "value": fmt(saves)},
                    {"label": "Outbound", "value": fmt(outbound)},
                ],
            }
        )
        return card
    except Exception as exc:
        print(f"warning: Pinterest snapshot preserved ({exc})")
        return existing


def social_section(cards: list[dict]) -> str:
    blocks: list[str] = []
    for card in cards:
        rows = "\n".join(
            f'                        <li class="channel-item"><span>{html.escape(row.get("label", ""))}</span><strong>{html.escape(row.get("value", ""))}</strong></li>'
            for row in card.get("rows", [])
        )
        kicker = ""
        if card.get("key") == "youtube" and card.get("chartRange"):
            kicker = f'                    <div class="chart-kicker">Views by publish date · {html.escape(card["chartRange"])}</div>\n'
        blocks.append(
            f'''                <article class="property-card social-card">
                    <div class="property-card-header">
                        <div>
                            <h3>{html.escape(card["name"])}</h3>
                            <span class="property-domain">{html.escape(card["handle"])}</span>
                        </div>
                        <div class="property-total">
                            <strong>{html.escape(card["total"])}</strong>
                            <span>{html.escape(card["label"])}</span>
                        </div>
                    </div>
{kicker}                    <div class="property-mini-chart"><canvas id="{html.escape(card['key'])}SocialChart"></canvas></div>
                    <div class="subsection-label">Signals</div>
                    <ol class="channel-list">
{rows}
                    </ol>
                </article>'''
        )
    body = "\n".join(blocks)
    return f'''        <!-- Tabiji Social Snapshot -->
        <section class="portfolio-section social-snapshot-section" aria-labelledby="social-snapshot-heading">
            <h2 id="social-snapshot-heading"><span class="icon">🌐</span> Tabiji Social Snapshot</h2>
            <p class="section-desc">Four-platform snapshot for Tabiji’s social engine: Instagram, YouTube Shorts, Pinterest, and TikTok.</p>
            <div class="property-grid social-grid">
{body}
            </div>
        </section>
'''


def main() -> int:
    text = METRICS_HTML.read_text()
    chart_match = re.search(r"const chartData = (.*?);", text, re.S)
    if not chart_match:
        raise RuntimeError("could not find chartData")
    chart = json.loads(chart_match.group(1))
    existing_cards = {card["key"]: card for card in chart.get("socialSnapshot", {}).get("cards", [])}

    cards = [
        fetch_instagram(),
        fetch_youtube(),
        fetch_pinterest(existing_cards.get("pinterest", {})),
        fetch_tiktok(),
    ]
    chart["socialSnapshot"] = {"cards": cards}

    text = text[: chart_match.start(1)] + json.dumps(chart, separators=(",", ":")) + text[chart_match.end(1) :]
    text = re.sub(
        r"        <!-- Tabiji Social Snapshot -->.*?(?=\n    </div>\n    </main>)",
        social_section(cards),
        text,
        flags=re.S,
    )
    METRICS_HTML.write_text(text)

    summary = {card["key"]: {"total": card["total"], "rows": card.get("rows", [])} for card in cards}
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
