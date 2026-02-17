"""
Portfolio Dashboard Auto-Updater
Fetches latest stock data from Google Finance and updates index.html
Runs via GitHub Actions on a schedule (daily at 6:30 PM IST / 1:00 PM UTC)
"""

import json
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

# ============================================================
# YOUR HOLDINGS — Update this list when you buy/sell stocks
# ============================================================
HOLDINGS = [
    "ANTELOPUS", "AUBANK", "AVANTIFEED", "BANKINDIA", "BONDADA", "BSE",
    "CANBK", "EIHAHOTELS", "GKENERGY", "ICICIBANK", "ICIL", "KARURVYSYA",
    "KPEL", "KPIGREEN", "KPITTECH", "M%26M", "MOSCHIP", "MOTILALOFS",
    "NETWEB", "NH", "OBEROIRLTY", "SENCO", "SENORES", "SPORTKING",
    "SYRMA", "WAAREEENER", "WAAREERTL", "ZAGGLE"
]

# Display name mapping (URL-encoded → display)
DISPLAY_NAMES = {"M%26M": "M&M"}


def fetch_google_finance(ticker):
    """Fetch stock data from Google Finance page."""
    display_ticker = DISPLAY_NAMES.get(ticker, ticker)
    url = f"https://www.google.com/finance/quote/{ticker}:NSE"

    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        data = {"ticker": display_ticker, "updated": True}

        # Current price — look for the main price element
        price_patterns = [
            r'data-last-price="([0-9,.]+)"',
            r'class="YMlKec fxKbKc"[^>]*>₹([0-9,.]+)',
            r'class="YMlKec fxKbKc"[^>]*>([0-9,.]+)',
        ]
        for pat in price_patterns:
            m = re.search(pat, html)
            if m:
                data["ltp"] = float(m.group(1).replace(",", ""))
                break

        # Previous close
        m = re.search(r'Previous close.*?>([\d,.]+)', html, re.DOTALL)
        if m:
            data["prev_close"] = float(m.group(1).replace(",", ""))

        # 52-week range
        m = re.search(r'Year range.*?([\d,.]+)\s*-\s*([\d,.]+)', html, re.DOTALL)
        if m:
            low52 = float(m.group(1).replace(",", ""))
            high52 = float(m.group(2).replace(",", ""))
            data["high52"] = high52
            data["low52"] = low52
            if "ltp" in data and high52 > 0:
                data["down_52w"] = round((data["ltp"] - high52) / high52 * 100, 1)

        # PE ratio
        m = re.search(r'P/E ratio.*?([\d,.]+)', html, re.DOTALL)
        if m:
            data["pe"] = float(m.group(1).replace(",", ""))

        # Market cap
        m = re.search(r'Market cap.*?([\d,.]+[BMT]?)', html, re.DOTALL)
        if m:
            data["market_cap"] = m.group(1)

        # Volume
        m = re.search(r'Avg Volume.*?([\d,.]+[KMB]?)', html, re.DOTALL)
        if m:
            data["avg_volume"] = m.group(1)

        return data

    except Exception as e:
        print(f"  [WARN] Failed to fetch {display_ticker}: {e}")
        return {"ticker": display_ticker, "updated": False, "error": str(e)}


def update_html(stock_data):
    """Update the RESEARCH_DATA in index.html with fresh price/PE/52w data."""
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Build update map
    updates = {}
    for sd in stock_data:
        if not sd.get("updated"):
            continue
        ticker = sd["ticker"]
        updates[ticker] = sd

    if not updates:
        print("No updates to apply.")
        return False

    # Update individual fields in the RESEARCH_DATA JavaScript object
    for ticker, data in updates.items():
        # Escape ticker for regex (handle M&M)
        esc_ticker = re.escape(ticker)

        # Update PE
        if "pe" in data:
            pattern = rf'("{esc_ticker}":\s*\{{[^}}]*?)pe:\s*[\d.]+(\s*,)'
            replacement = rf'\g<1>pe: {data["pe"]}\2'
            html = re.sub(pattern, replacement, html, flags=re.DOTALL)

        # Update down_52w
        if "down_52w" in data:
            pattern = rf'("{esc_ticker}":\s*\{{[^}}]*?)down_52w:\s*-?[\d.]+(\s*,)'
            replacement = rf'\g<1>down_52w: {data["down_52w"]}\2'
            html = re.sub(pattern, replacement, html, flags=re.DOTALL)

    # Update the last-updated timestamp
    now = datetime.now(IST).strftime("%b %d, %Y %I:%M %p IST")
    html = re.sub(
        r'Data researched as of [^•<"]+',
        f'Data auto-updated: {now}',
        html
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Updated index.html with {len(updates)} stock(s) at {now}")
    return True


def main():
    print("=" * 60)
    print("Portfolio Dashboard Auto-Updater")
    print(f"Run time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M IST')}")
    print("=" * 60)

    results = []
    for i, ticker in enumerate(HOLDINGS):
        display = DISPLAY_NAMES.get(ticker, ticker)
        print(f"[{i+1}/{len(HOLDINGS)}] Fetching {display}...", end=" ")
        data = fetch_google_finance(ticker)
        if data.get("updated"):
            pe_str = f"PE={data.get('pe', 'N/A')}" if data.get("pe") else "PE=N/A"
            ltp_str = f"₹{data.get('ltp', 'N/A')}" if data.get("ltp") else "N/A"
            down_str = f"{data.get('down_52w', 'N/A')}%" if data.get("down_52w") else "N/A"
            print(f"OK — {ltp_str}, {pe_str}, 52W: {down_str}")
        else:
            print(f"FAILED — {data.get('error', 'unknown')}")
        results.append(data)

    success_count = sum(1 for r in results if r.get("updated"))
    print(f"\nFetched {success_count}/{len(HOLDINGS)} stocks successfully")

    if success_count > 0:
        updated = update_html(results)
        if updated:
            print("index.html updated successfully!")
        else:
            print("No changes made to index.html")
    else:
        print("No data fetched, skipping HTML update")
        sys.exit(1)

    # Write a summary JSON for GitHub Actions
    summary = {
        "run_time": datetime.now(IST).isoformat(),
        "total": len(HOLDINGS),
        "success": success_count,
        "failed": len(HOLDINGS) - success_count,
        "stocks": [{
            "ticker": r["ticker"],
            "status": "ok" if r.get("updated") else "failed",
            "ltp": r.get("ltp"),
            "pe": r.get("pe"),
            "down_52w": r.get("down_52w")
        } for r in results]
    }
    with open("update_log.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("Summary written to update_log.json")


if __name__ == "__main__":
    main()
