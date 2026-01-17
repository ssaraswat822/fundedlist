# 🚀 FundedList

A curated directory of startups that just raised funding — with links to their open jobs.

**Live updates daily** via GitHub Actions → Netlify auto-deploy.

---

## Quick Deploy to Netlify

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fundedlist.git
git push -u origin main
```

### Step 2: Connect to Netlify

1. Go to [netlify.com](https://netlify.com) → Log in
2. Click **"Add new site"** → **"Import an existing project"**
3. Connect your GitHub repo
4. Settings:
   - **Build command:** (leave blank)
   - **Publish directory:** `.`
5. Click **Deploy**

Your site is now live! 🎉

### Step 3: Enable Auto-Updates

Go to your GitHub repo → **Actions** tab → workflows will run daily at 6am UTC.

To run manually: **Actions** → **"Update Funding Data"** → **"Run workflow"**

---

## How It Works

```
Daily @ 6am UTC
      │
      ▼
┌─────────────────────────────┐
│     GitHub Actions          │
│  • Run funding scraper      │
│  • Run VC portfolio scraper │
│  • Rebuild index.html       │
│  • Commit & push            │
└─────────────────────────────┘
      │
      ▼
┌─────────────────────────────┐
│     Netlify                 │
│  Auto-deploys on push       │
└─────────────────────────────┘
```

---

## Project Structure

```
fundedlist/
├── index.html              # Main site (auto-generated)
├── data/
│   ├── companies.json      # Funded companies
│   └── vcs.json            # VC firms
├── scraper_v2.py           # Funding news scraper
├── vc_scraper.py           # VC portfolio scraper
├── job_scraper.py          # Job listings scraper
├── build_site.py           # Site generator
├── netlify.toml            # Netlify config
└── .github/workflows/
    └── update-data.yml     # Daily automation
```

---

## Data Sources

| Source | Data |
|--------|------|
| startups.gallery | Structured funding rounds |
| vcnewsdaily.com | Press releases |
| a16z.com/portfolio | a16z companies |
| sequoiacap.com/our-companies | Sequoia companies |
| ycombinator.com/companies | YC companies |

---

## Local Development

```bash
pip install -r requirements.txt

# Run scrapers
python scraper_v2.py
python vc_scraper.py

# Build site
python build_site.py

# Preview
python -m http.server 8000
```

---

## Cost: $0/month

- Netlify: Free tier (100GB bandwidth)
- GitHub Actions: Free tier (2,000 mins/month)
