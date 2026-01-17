#!/usr/bin/env python3
"""
Build script - Reads scraped data and rebuilds index.html with fresh data.
Run this after the scrapers to update the site.
"""

import json
import os
import sqlite3
from datetime import datetime

def load_companies_from_db(db_path='fundedlist.db'):
    """Load companies from SQLite database."""
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT name, website, funding_amount, round_type, description, published_date
            FROM funding
            ORDER BY published_date DESC
            LIMIT 50
        ''')
        
        companies = []
        for row in cursor.fetchall():
            companies.append({
                'name': row[0],
                'website': row[1],
                'amount': row[2] or 'Undisclosed',
                'round': row[3] or 'Unknown',
                'tagline': row[4][:100] if row[4] else 'Building the future.',
                'date': row[5],
            })
        
        return companies
    except:
        return []
    finally:
        conn.close()


def load_companies_from_json(json_path='data/companies.json'):
    """Load companies from JSON file."""
    if not os.path.exists(json_path):
        print(f"JSON not found: {json_path}")
        return []
    
    with open(json_path) as f:
        data = json.load(f)
    
    return data.get('companies', [])


def load_vcs_from_json(json_path='data/vcs.json'):
    """Load VCs from JSON file."""
    if not os.path.exists(json_path):
        return []
    
    with open(json_path) as f:
        data = json.load(f)
    
    return data.get('vcs', [])


def generate_html(companies, vcs):
    """Generate the full HTML page with embedded data."""
    
    # Calculate days ago for each company
    today = datetime.now()
    for company in companies:
        if 'daysAgo' not in company:
            company['daysAgo'] = '1d ago'
        if 'category' not in company:
            company['category'] = 'other'
        if 'tags' not in company:
            company['tags'] = []
        if 'investors' not in company:
            company['investors'] = []
        if 'jobs' not in company:
            company['jobs'] = 10
    
    companies_json = json.dumps(companies, indent=2)
    vcs_json = json.dumps(vcs, indent=2)
    updated_date = today.strftime('%b %d, %Y')
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FundedList — Jobs at Recently Funded Startups</title>
    <meta name="description" content="Discover startups that just raised funding. Companies with fresh capital are hiring.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        :root {{
            --bg: #fafafa; --card-bg: #ffffff; --text-primary: #111111;
            --text-secondary: #666666; --text-muted: #999999; --border: #e5e5e5;
            --accent: #0066ff; --accent-light: #e6f0ff; --tag-bg: #f0f0f0;
            --green: #00a67d; --green-light: #e6f7f2;
            --purple: #7c3aed; --purple-light: #ede9fe;
        }}
        body {{ font-family: 'Inter', -apple-system, sans-serif; background: var(--bg); color: var(--text-primary); line-height: 1.5; -webkit-font-smoothing: antialiased; }}
        nav {{ position: sticky; top: 0; background: rgba(250,250,250,0.9); backdrop-filter: blur(10px); border-bottom: 1px solid var(--border); z-index: 100; }}
        .nav-inner {{ max-width: 1200px; margin: 0 auto; padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-weight: 700; font-size: 1.1rem; color: var(--text-primary); text-decoration: none; display: flex; align-items: center; gap: 8px; }}
        .logo-icon {{ width: 26px; height: 26px; background: var(--green); border-radius: 6px; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: 700; }}
        .nav-links {{ display: flex; gap: 24px; }}
        .nav-links a {{ color: var(--text-secondary); text-decoration: none; font-size: 0.875rem; font-weight: 500; cursor: pointer; }}
        .nav-links a:hover, .nav-links a.active {{ color: var(--text-primary); }}
        .tabs {{ max-width: 1200px; margin: 0 auto; padding: 20px 24px 0; display: flex; gap: 4px; border-bottom: 1px solid var(--border); }}
        .tab {{ padding: 12px 20px; font-size: 0.9rem; font-weight: 500; color: var(--text-secondary); background: none; border: none; cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px; }}
        .tab:hover {{ color: var(--text-primary); }}
        .tab.active {{ color: var(--text-primary); border-bottom-color: var(--text-primary); }}
        .hero {{ max-width: 1200px; margin: 0 auto; padding: 40px 24px 28px; }}
        .hero h1 {{ font-size: 2rem; font-weight: 700; letter-spacing: -0.03em; margin-bottom: 8px; }}
        .hero p {{ font-size: 1rem; color: var(--text-secondary); max-width: 500px; }}
        .hero-stats {{ display: flex; gap: 32px; margin-top: 24px; }}
        .hero-stat {{ display: flex; align-items: baseline; gap: 6px; }}
        .hero-stat-number {{ font-size: 1.3rem; font-weight: 700; }}
        .hero-stat-label {{ font-size: 0.85rem; color: var(--text-muted); }}
        .controls {{ max-width: 1200px; margin: 0 auto; padding: 0 24px 20px; display: flex; gap: 16px; flex-wrap: wrap; align-items: center; }}
        .search-box {{ flex: 1; min-width: 250px; max-width: 360px; position: relative; }}
        .search-box input {{ width: 100%; padding: 10px 16px 10px 40px; border: 1px solid var(--border); border-radius: 8px; font-size: 0.9rem; background: var(--card-bg); }}
        .search-box input:focus {{ outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-light); }}
        .search-box svg {{ position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-muted); width: 18px; height: 18px; }}
        .filters {{ display: flex; gap: 6px; flex-wrap: wrap; }}
        .filter-btn {{ padding: 7px 12px; border: 1px solid var(--border); border-radius: 6px; background: var(--card-bg); color: var(--text-secondary); font-size: 0.8rem; font-weight: 500; cursor: pointer; }}
        .filter-btn:hover {{ border-color: var(--text-muted); color: var(--text-primary); }}
        .filter-btn.active {{ background: var(--text-primary); border-color: var(--text-primary); color: white; }}
        .main-content {{ max-width: 1200px; margin: 0 auto; padding: 0 24px 60px; }}
        .section-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--border); }}
        .section-title {{ font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); }}
        .count-label {{ font-size: 0.8rem; color: var(--text-muted); }}
        .company-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 10px; }}
        .company-card {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 18px; transition: all 0.15s; cursor: pointer; text-decoration: none; color: inherit; display: block; }}
        .company-card:hover {{ border-color: #ccc; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.04); }}
        .company-top {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }}
        .company-name {{ font-size: 0.95rem; font-weight: 600; }}
        .funding-amount {{ background: var(--green-light); color: var(--green); padding: 2px 7px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; }}
        .company-tagline {{ color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 10px; line-height: 1.4; }}
        .company-meta {{ display: flex; gap: 10px; flex-wrap: wrap; font-size: 0.78rem; color: var(--text-muted); }}
        .meta-dot {{ width: 3px; height: 3px; background: var(--text-muted); border-radius: 50%; margin-top: 7px; }}
        .company-investors {{ display: flex; gap: 5px; flex-wrap: wrap; margin-top: 10px; }}
        .investor-badge {{ background: var(--purple-light); color: var(--purple); padding: 2px 7px; border-radius: 4px; font-size: 0.68rem; font-weight: 500; }}
        .company-tags {{ display: flex; gap: 5px; flex-wrap: wrap; margin-top: 8px; }}
        .tag {{ background: var(--tag-bg); color: var(--text-secondary); padding: 2px 7px; border-radius: 4px; font-size: 0.68rem; font-weight: 500; }}
        .vc-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 10px; }}
        .vc-card {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 18px; cursor: pointer; transition: all 0.15s; }}
        .vc-card:hover {{ border-color: #ccc; box-shadow: 0 4px 12px rgba(0,0,0,0.04); }}
        .vc-card.selected {{ border-color: var(--purple); background: var(--purple-light); }}
        .vc-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }}
        .vc-logo {{ font-size: 1.4rem; }}
        .vc-name {{ font-weight: 600; font-size: 0.95rem; }}
        .vc-stats {{ display: flex; gap: 14px; margin-bottom: 10px; font-size: 0.78rem; color: var(--text-secondary); }}
        .vc-focus {{ display: flex; gap: 5px; flex-wrap: wrap; }}
        .focus-tag {{ background: var(--tag-bg); padding: 2px 7px; border-radius: 4px; font-size: 0.68rem; color: var(--text-secondary); }}
        .vc-notable {{ margin-top: 10px; font-size: 0.72rem; color: var(--text-muted); }}
        .section {{ display: none; }}
        .section.active {{ display: block; }}
        .selected-vc-banner {{ background: var(--purple-light); border: 1px solid var(--purple); border-radius: 8px; padding: 10px 14px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }}
        .selected-vc-banner span {{ font-size: 0.85rem; color: var(--purple); font-weight: 500; }}
        .clear-vc-btn {{ background: var(--purple); color: white; border: none; padding: 5px 10px; border-radius: 4px; font-size: 0.78rem; cursor: pointer; }}
        footer {{ border-top: 1px solid var(--border); background: var(--card-bg); }}
        .footer-inner {{ max-width: 1200px; margin: 0 auto; padding: 28px 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; }}
        .footer-left {{ font-size: 0.82rem; color: var(--text-muted); }}
        .footer-links {{ display: flex; gap: 20px; }}
        .footer-links a {{ color: var(--text-secondary); text-decoration: none; font-size: 0.82rem; }}
        .empty-state {{ text-align: center; padding: 50px 20px; color: var(--text-muted); grid-column: 1 / -1; }}
        .empty-state h3 {{ font-size: 1rem; margin-bottom: 6px; color: var(--text-secondary); }}
        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 1.6rem; }}
            .company-grid, .vc-grid {{ grid-template-columns: 1fr; }}
            .nav-links {{ display: none; }}
            .controls {{ flex-direction: column; align-items: stretch; }}
            .search-box {{ max-width: none; }}
        }}
    </style>
</head>
<body>
    <nav>
        <div class="nav-inner">
            <a href="/" class="logo">
                <div class="logo-icon">F</div>
                FundedList
            </a>
            <div class="nav-links">
                <a class="active" onclick="showSection('companies')">Companies</a>
                <a onclick="showSection('vcs')">VCs</a>
                <a href="#">About</a>
            </div>
        </div>
    </nav>
    
    <div class="tabs">
        <button class="tab active" onclick="showSection('companies')">🏢 Companies</button>
        <button class="tab" onclick="showSection('vcs')">💰 VCs</button>
    </div>
    
    <section id="companies-section" class="section active">
        <div class="hero">
            <h1>Discover startups that just raised funding</h1>
            <p>Companies with fresh capital are hiring. Find your next role at a startup with runway.</p>
            <div class="hero-stats">
                <div class="hero-stat"><span class="hero-stat-number" id="stat-companies">0</span><span class="hero-stat-label">companies</span></div>
                <div class="hero-stat"><span class="hero-stat-number" id="stat-raised">$0</span><span class="hero-stat-label">raised</span></div>
                <div class="hero-stat"><span class="hero-stat-number" id="stat-jobs">0</span><span class="hero-stat-label">open roles</span></div>
            </div>
        </div>
        <div class="controls">
            <div class="search-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.35-4.35"></path></svg>
                <input type="text" id="search" placeholder="Search companies...">
            </div>
            <div class="filters" id="category-filters">
                <button class="filter-btn active" data-filter="all">All</button>
                <button class="filter-btn" data-filter="ai">AI</button>
                <button class="filter-btn" data-filter="fintech">Fintech</button>
                <button class="filter-btn" data-filter="health">Health</button>
                <button class="filter-btn" data-filter="climate">Climate</button>
                <button class="filter-btn" data-filter="dev-tools">Dev Tools</button>
            </div>
        </div>
        <main class="main-content">
            <div id="vc-filter-banner" class="selected-vc-banner" style="display: none;">
                <span>Showing companies backed by <strong id="selected-vc-name"></strong></span>
                <button class="clear-vc-btn" onclick="clearVcFilter()">Clear filter</button>
            </div>
            <div class="section-header">
                <span class="section-title">Recently Funded</span>
                <span class="count-label" id="showing-count">Showing 0 companies</span>
            </div>
            <div class="company-grid" id="company-grid"></div>
        </main>
    </section>
    
    <section id="vcs-section" class="section">
        <div class="hero">
            <h1>Top Venture Capital Firms</h1>
            <p>Browse portfolios from the world's leading VCs. Click a firm to filter companies.</p>
            <div class="hero-stats">
                <div class="hero-stat"><span class="hero-stat-number" id="vc-count">0</span><span class="hero-stat-label">VCs tracked</span></div>
                <div class="hero-stat"><span class="hero-stat-number">11,500+</span><span class="hero-stat-label">portfolio companies</span></div>
            </div>
        </div>
        <main class="main-content">
            <div class="section-header"><span class="section-title">Click a VC to filter funded companies</span></div>
            <div class="vc-grid" id="vc-grid"></div>
        </main>
    </section>
    
    <footer>
        <div class="footer-inner">
            <div class="footer-left">Updated {updated_date} · Data auto-refreshed daily</div>
            <div class="footer-links"><a href="#">Submit</a><a href="#">API</a><a href="#">About</a></div>
        </div>
    </footer>
    
    <script>
        const vcs = {vcs_json};
        const companies = {companies_json};
        
        let currentFilter = 'all';
        let selectedVc = null;
        
        function updateStats() {{
            const filtered = getFilteredCompanies();
            const totalRaised = filtered.reduce((sum, c) => {{
                const num = parseFloat((c.amount || '$0').replace(/[$BMK]/g, ''));
                const mult = (c.amount || '').includes('B') ? 1000 : 1;
                return sum + (num * mult);
            }}, 0);
            const totalJobs = filtered.reduce((sum, c) => sum + (c.jobs || 0), 0);
            document.getElementById('stat-companies').textContent = filtered.length;
            document.getElementById('stat-raised').textContent = '$' + (totalRaised/1000).toFixed(1) + 'B';
            document.getElementById('stat-jobs').textContent = totalJobs;
            document.getElementById('vc-count').textContent = vcs.length;
        }}
        
        function getFilteredCompanies() {{
            let filtered = companies;
            if (currentFilter !== 'all') filtered = filtered.filter(c => c.category === currentFilter);
            if (selectedVc) filtered = filtered.filter(c => (c.investors || []).includes(selectedVc));
            const search = document.getElementById('search').value.toLowerCase();
            if (search) filtered = filtered.filter(c => (c.name || '').toLowerCase().includes(search) || (c.tagline || '').toLowerCase().includes(search));
            return filtered;
        }}
        
        function renderCompanies() {{
            const grid = document.getElementById('company-grid');
            const filtered = getFilteredCompanies();
            document.getElementById('showing-count').textContent = 'Showing ' + filtered.length + ' companies';
            const banner = document.getElementById('vc-filter-banner');
            if (selectedVc) {{
                const vc = vcs.find(v => v.id === selectedVc);
                document.getElementById('selected-vc-name').textContent = vc ? vc.name : selectedVc;
                banner.style.display = 'flex';
            }} else {{ banner.style.display = 'none'; }}
            if (filtered.length === 0) {{ grid.innerHTML = '<div class="empty-state"><h3>No companies found</h3><p>Try adjusting your filters</p></div>'; return; }}
            grid.innerHTML = filtered.map(company => {{
                const investorBadges = (company.investors || []).map(vcId => {{
                    const vc = vcs.find(v => v.id === vcId);
                    return vc ? '<span class="investor-badge">' + vc.logo + ' ' + vc.shortName + '</span>' : '';
                }}).join('');
                return '<a href="' + (company.website || '#') + '" target="_blank" class="company-card"><div class="company-top"><span class="company-name">' + company.name + '</span><span class="funding-amount">' + (company.amount || 'Undisclosed') + '</span></div><div class="company-tagline">' + (company.tagline || '') + '</div><div class="company-meta"><span>' + (company.round || '') + '</span><span class="meta-dot"></span><span>' + (company.daysAgo || '') + '</span><span class="meta-dot"></span><span>' + (company.jobs || 0) + ' jobs</span></div><div class="company-investors">' + investorBadges + '</div><div class="company-tags">' + (company.tags || []).map(t => '<span class="tag">' + t + '</span>').join('') + '</div></a>';
            }}).join('');
            updateStats();
        }}
        
        function renderVCs() {{
            const grid = document.getElementById('vc-grid');
            grid.innerHTML = vcs.map(vc => '<div class="vc-card' + (selectedVc === vc.id ? ' selected' : '') + '" onclick="selectVc(\\'' + vc.id + '\\')"><div class="vc-header"><span class="vc-logo">' + vc.logo + '</span><span class="vc-name">' + vc.name + '</span></div><div class="vc-stats"><span>' + (vc.portfolioCount || 0).toLocaleString() + ' companies</span><span>Est. ' + vc.founded + '</span>' + (vc.aum !== 'N/A' ? '<span>' + vc.aum + '</span>' : '') + '</div><div class="vc-focus">' + (vc.focus || []).slice(0, 4).map(f => '<span class="focus-tag">' + f + '</span>').join('') + '</div><div class="vc-notable">Notable: ' + (vc.notable || []).slice(0, 4).join(', ') + '</div></div>').join('');
        }}
        
        function selectVc(vcId) {{ selectedVc = selectedVc === vcId ? null : vcId; renderVCs(); showSection('companies'); renderCompanies(); }}
        function clearVcFilter() {{ selectedVc = null; renderVCs(); renderCompanies(); }}
        function showSection(sectionId) {{
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
            document.getElementById(sectionId + '-section').classList.add('active');
            document.querySelectorAll('.tab').forEach(t => {{ if (t.textContent.toLowerCase().includes(sectionId)) t.classList.add('active'); }});
            document.querySelectorAll('.nav-links a').forEach(a => {{ if (a.textContent.toLowerCase().includes(sectionId)) a.classList.add('active'); }});
        }}
        document.querySelectorAll('#category-filters .filter-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('#category-filters .filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = btn.dataset.filter;
                renderCompanies();
            }});
        }});
        document.getElementById('search').addEventListener('input', renderCompanies);
        renderCompanies();
        renderVCs();
    </script>
</body>
</html>'''
    
    return html


def main():
    print("🔨 Building FundedList site...")
    
    # Try to load from JSON first, then DB
    companies = load_companies_from_json('data/companies.json')
    if not companies:
        companies = load_companies_from_db()
    
    vcs = load_vcs_from_json('data/vcs.json')
    if not vcs:
        # Default VCs if no JSON found
        vcs = [
            {"id": "yc", "name": "Y Combinator", "shortName": "YC", "logo": "🟠", "aum": "N/A", "founded": 2005, "portfolioCount": 5000, "focus": ["Early Stage"], "notable": ["Stripe", "Airbnb"]},
            {"id": "sequoia", "name": "Sequoia Capital", "shortName": "Sequoia", "logo": "🌲", "aum": "$56B", "founded": 1972, "portfolioCount": 2947, "focus": ["Consumer", "Enterprise"], "notable": ["Stripe", "DoorDash"]},
            {"id": "a16z", "name": "Andreessen Horowitz", "shortName": "a16z", "logo": "🅰️", "aum": "$46B", "founded": 2009, "portfolioCount": 1119, "focus": ["AI", "Crypto"], "notable": ["Coinbase", "GitHub"]},
        ]
    
    print(f"   Loaded {len(companies)} companies")
    print(f"   Loaded {len(vcs)} VCs")
    
    html = generate_html(companies, vcs)
    
    with open('index.html', 'w') as f:
        f.write(html)
    
    print("✅ Built index.html")


if __name__ == "__main__":
    main()
