# 🚀 FundedList

A curated job board for recently funded startups. Find roles at companies with fresh capital and runway to grow.

**Live at:** [your-site.netlify.app](https://your-site.netlify.app)

---

## Features

- 🏢 **Companies** — Browse startups that just raised funding
- 💼 **Jobs** — Open roles at funded companies
- 💰 **VCs** — Filter by investor portfolio
- 🔄 **Auto-updates** — Data refreshes daily via GitHub Actions

---

## Quick Setup

### 1. Upload to GitHub

Upload all these files to your GitHub repository.

**Important:** For the `.github/workflows/update-data.yml` file:
- Click "Add file" → "Create new file"
- Name it `.github/workflows/update-data.yml`
- Paste the contents

### 2. Connect to Netlify

1. Go to [netlify.com](https://netlify.com)
2. Click "Add new site" → "Import an existing project"
3. Select your GitHub repo
4. Leave build command **blank**
5. Set publish directory to `.`
6. Click Deploy

### 3. Enable Auto-Updates

The GitHub Action runs automatically every day at 6am UTC. To run manually:
1. Go to your repo → **Actions** tab
2. Click **"Update Funding Data"**
3. Click **"Run workflow"**

---

## How It Works

```
Daily @ 6am UTC
      │
      ▼
┌─────────────────────────────┐
│     GitHub Actions          │
│  • scraper_v2.py (funding)  │
│  • vc_scraper.py (VCs)      │
│  • job_scraper.py (jobs)    │
│  • build_site.py (rebuild)  │
└─────────────────────────────┘
      │
      ▼
┌─────────────────────────────┐
│     Netlify                 │
│  Auto-deploys on push       │
└─────────────────────────────┘
```

---

## Files

| File | Purpose |
|------|---------|
| `index.html` | The main site |
| `scraper_v2.py` | Scrapes funding news from RSS feeds |
| `vc_scraper.py` | Exports VC data |
| `job_scraper.py` | Generates/scrapes job listings |
| `build_site.py` | Rebuilds HTML with fresh data |
| `requirements.txt` | Python dependencies |
| `netlify.toml` | Netlify config |
| `.github/workflows/update-data.yml` | Daily automation |

---

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run scrapers
python scraper_v2.py
python vc_scraper.py
python job_scraper.py

# Rebuild site
python build_site.py

# Preview locally
python -m http.server 8000
# Open http://localhost:8000
```

---

## Cost

| Service | Cost |
|---------|------|
| Netlify | Free |
| GitHub Actions | Free |
| **Total** | **$0/month** |

---

## Customization

### Add more VCs
Edit `vc_scraper.py` and add to the `VCS` list.

### Add more data sources
Edit `scraper_v2.py` and add RSS feeds to `RSS_FEEDS`.

### Change schedule
Edit `.github/workflows/update-data.yml`:
```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
```

---

## License

MIT
