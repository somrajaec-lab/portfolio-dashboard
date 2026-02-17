# Portfolio Dashboard — GitHub Pages Setup Guide

## What You Get
- A **live dashboard** at `https://YOUR-USERNAME.github.io/portfolio-dashboard/`
- **Auto-updates daily** at 6:30 PM IST (after market close) via GitHub Actions
- PE ratio, 52-week high data refreshed automatically
- Upload a new Kite CSV anytime to update holdings
- **Free** — no hosting costs, runs on GitHub's free tier

---

## Step-by-Step Setup (10 minutes)

### Step 1: Create a GitHub Account (skip if you have one)
1. Go to [github.com](https://github.com)
2. Sign up with your email
3. Verify your email address

### Step 2: Create a New Repository
1. Click the **+** button (top right) → **New repository**
2. Name it: `portfolio-dashboard`
3. Set it to **Private** (important — this has your financial data)
4. Check **"Add a README file"**
5. Click **Create repository**

### Step 3: Upload the Dashboard Files
1. In your new repo, click **Add file** → **Upload files**
2. Drag and drop ALL of these files from the `portfolio-dashboard` folder:
   - `index.html` (the dashboard)
   - `update_data.py` (the auto-updater script)
   - `SETUP_GUIDE.md` (this file)
3. Also upload the `.github` folder:
   - Click **Add file** → **Create new file**
   - In the filename box, type: `.github/workflows/update-dashboard.yml`
   - Copy-paste the contents of `.github/workflows/update-dashboard.yml` into the editor
   - Click **Commit new file**

### Step 4: Enable GitHub Pages
1. Go to your repo → **Settings** (tab at top)
2. In the left sidebar, click **Pages**
3. Under "Source", select **Deploy from a branch**
4. Branch: select **main**, folder: **/ (root)**
5. Click **Save**
6. Wait 2-3 minutes, then visit: `https://YOUR-USERNAME.github.io/portfolio-dashboard/`

### Step 5: Enable GitHub Actions
1. Go to your repo → **Actions** (tab at top)
2. You should see the "Update Portfolio Dashboard" workflow
3. If prompted, click **"I understand my workflows, go ahead and enable them"**
4. Click on the workflow → **Run workflow** → **Run workflow** (to test it manually)
5. Wait for it to complete (takes ~2 minutes)
6. Refresh your dashboard page — you should see updated timestamps

---

## How Auto-Update Works

```
Every weekday at 6:30 PM IST (after market close):
  1. GitHub Actions triggers the workflow
  2. update_data.py fetches latest data from Google Finance
  3. PE ratios and 52-week high data are updated in index.html
  4. Changes are committed and pushed automatically
  5. GitHub Pages rebuilds the site (~1 minute)
  6. Your dashboard shows fresh data
```

---

## How to Update Holdings (When You Buy/Sell)

### Method 1: Upload New CSV (easiest)
1. Visit your dashboard URL
2. Click **"Upload Kite CSV"**
3. The dashboard updates instantly in your browser

### Method 2: Update the Python Script (for persistent changes)
1. Edit `update_data.py` in GitHub
2. Update the `HOLDINGS` list to add/remove tickers
3. Commit the change
4. The next auto-update will use the new list

### Method 3: Ask Claude
Come back with a fresh Kite CSV export, and I'll regenerate the entire dashboard with fresh qualitative research (quarterly results, news, FII/DII trends, leadership, govt themes).

---

## Refreshing Qualitative Data

The auto-updater refreshes **quantitative data** (prices, PE, 52-week data).

For **qualitative data** (quarterly results, news, FII/DII, leadership, govt themes), come back to me:
- **Every quarter** — after results season (Feb, May, Aug, Nov)
- **On major news events** — if something big happens to one of your holdings

I'll regenerate the full `index.html` with fresh research.

---

## Troubleshooting

### Dashboard not loading?
- Check Settings → Pages → make sure it says "Your site is published at..."
- Clear browser cache (Ctrl+Shift+R)
- Wait 5 minutes after the first deploy

### Auto-update not running?
- Go to Actions tab → check if the workflow ran
- If it failed, click on the run to see error logs
- Google Finance sometimes blocks automated requests — the script handles this gracefully

### Want to change update frequency?
Edit `.github/workflows/update-dashboard.yml`:
```yaml
# Every 2 hours during market hours (IST 9:15 AM - 3:30 PM = UTC 3:45 AM - 10:00 AM)
- cron: '0 4,6,8,10 * * 1-5'

# Twice daily (morning + evening)
- cron: '0 4,13 * * 1-5'

# Only on weekday evenings
- cron: '0 13 * * 1-5'  # (current default)
```

### Want to add password protection?
Since the repo is private, only you can see the source code. But GitHub Pages for private repos requires GitHub Pro ($4/month). Alternative: use Cloudflare Pages (free) with access policies.

---

## File Structure
```
portfolio-dashboard/
├── index.html                           # The dashboard (main file)
├── update_data.py                       # Auto-updater script
├── update_log.json                      # Generated — last update summary
├── SETUP_GUIDE.md                       # This file
└── .github/
    └── workflows/
        └── update-dashboard.yml         # GitHub Actions schedule
```

---

## Limits (GitHub Free Tier)
- **GitHub Actions**: 2,000 minutes/month free (each run takes ~1 min, so ~60 runs/month is fine)
- **GitHub Pages**: Private repos need GitHub Pro. For free, make the repo public OR use Cloudflare Pages
- **Google Finance scraping**: May occasionally fail — the script retries gracefully

---

*Generated by Claude • Feb 2026*
