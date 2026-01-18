#!/usr/bin/env python3
"""
Funding Scraper - Pulls clean startup data from the free YC API
Source: https://github.com/yc-oss/api (updated daily, no auth required)
"""

import json
import os
import random
from datetime import datetime
import requests


YC_API_URL = "https://yc-oss.github.io/api/companies/all.json"


def fetch_yc_companies():
    """Fetch all YC companies from the free API."""
    print("📡 Fetching YC companies from API...")
    
    try:
        response = requests.get(YC_API_URL, timeout=30)
        response.raise_for_status()
        companies = response.json()
        print(f"   Found {len(companies)} total YC companies")
        return companies
    except Exception as e:
        print(f"   Error fetching YC API: {e}")
        return []


def categorize_company(company):
    """Determine category from industry/tags."""
    industry = (company.get('industry') or '').lower()
    subindustry = (company.get('subindustry') or '').lower()
    tags = ' '.join([t.lower() for t in (company.get('tags') or [])])
    combined = f"{industry} {subindustry} {tags}"
    
    if any(kw in combined for kw in ['artificial intelligence', 'machine learning', 'ai', 'nlp', 'computer vision', 'deep learning']):
        return 'ai'
    elif any(kw in combined for kw in ['fintech', 'financial', 'banking', 'payments', 'crypto', 'insurance', 'lending']):
        return 'fintech'
    elif any(kw in combined for kw in ['health', 'medical', 'biotech', 'healthcare', 'drug', 'clinical', 'therapeutics']):
        return 'health'
    elif any(kw in combined for kw in ['climate', 'energy', 'sustainability', 'clean', 'solar', 'carbon']):
        return 'climate'
    elif any(kw in combined for kw in ['developer', 'devops', 'infrastructure', 'b2b', 'saas', 'enterprise', 'api', 'security']):
        return 'dev-tools'
    return 'other'


def filter_and_rank_companies(companies, limit=30):
    """Filter to hiring/active companies and rank by relevance."""
    
    scored = []
    for c in companies:
        if not c.get('name'):
            continue
        
        # Skip dead/inactive
        status = (c.get('status') or '').lower()
        if status in ['dead', 'inactive', 'acquired']:
            continue
        
        # Calculate relevance score
        score = 0
        if c.get('isHiring'):
            score += 20  # Prioritize hiring companies
        if c.get('top_company'):
            score += 10
        
        team_size = c.get('team_size') or 0
        if team_size >= 100:
            score += 5
        elif team_size >= 20:
            score += 3
        elif team_size >= 5:
            score += 1
        
        stage = (c.get('stage') or '').lower()
        if 'series' in stage or 'growth' in stage:
            score += 5
        
        # Boost recent batches
        batch = c.get('batch') or ''
        if batch:
            try:
                year = int(batch[1:3]) if len(batch) >= 3 else 0
                if year >= 23:
                    score += 3
                elif year >= 20:
                    score += 1
            except:
                pass
        
        c['_score'] = score
        scored.append(c)
    
    # Sort by score, take top N
    scored.sort(key=lambda x: x['_score'], reverse=True)
    return scored[:limit]


def format_company(company):
    """Format a YC company for our frontend."""
    
    category = categorize_company(company)
    
    # Create ID from slug or name
    slug = company.get('slug') or company.get('name', 'unknown').lower().replace(' ', '-').replace('.', '')
    
    # Get display tags
    display_tags = []
    if company.get('industry'):
        display_tags.append(company['industry'])
    for tag in (company.get('tags') or [])[:2]:
        if tag not in display_tags:
            display_tags.append(tag)
    
    # Funding stage
    stage = company.get('stage') or 'Seed'
    if not stage or stage == 'Unknown':
        stage = 'YC Backed'
    
    # Days ago (use batch info)
    batch = company.get('batch') or ''
    days_ago = f"Batch {batch}" if batch else "YC Company"
    
    return {
        'id': slug,
        'name': company.get('name', 'Unknown'),
        'tagline': company.get('one_liner') or (company.get('long_description') or '')[:120] or 'Building something great.',
        'amount': 'YC Backed',
        'round': stage,
        'daysAgo': days_ago,
        'category': category,
        'tags': display_tags[:3] if display_tags else [category.title()],
        'investors': ['yc'],
        'website': company.get('website') or f"https://ycombinator.com/companies/{slug}",
        'isHiring': company.get('isHiring', False),
        'teamSize': company.get('team_size') or 0,
    }


def generate_jobs(companies):
    """Generate job listings for companies."""
    
    titles = {
        'engineering': ['Software Engineer', 'Senior Engineer', 'Full Stack Developer', 'Backend Engineer', 'Frontend Engineer', 'ML Engineer', 'DevOps Engineer'],
        'product': ['Product Manager', 'Senior PM', 'Product Lead'],
        'design': ['Product Designer', 'UX Designer', 'UI Designer'],
        'sales': ['Account Executive', 'Sales Lead', 'Growth Manager', 'BD Manager'],
        'operations': ['Operations Manager', 'Chief of Staff', 'People Ops'],
    }
    
    locations = ['San Francisco, CA', 'New York, NY', 'Remote', 'Austin, TX', 'Seattle, WA', 'Los Angeles, CA', 'Boston, MA']
    
    jobs = []
    job_id = 1
    
    random.seed(42)  # Consistent output
    
    for company in companies:
        # More jobs for hiring companies
        num_jobs = random.randint(3, 5) if company.get('isHiring') else random.randint(1, 2)
        
        used_titles = set()
        for _ in range(num_jobs):
            dept = random.choice(list(titles.keys()))
            title = random.choice(titles[dept])
            
            # Avoid duplicate titles per company
            if title in used_titles:
                continue
            used_titles.add(title)
            
            jobs.append({
                'id': job_id,
                'companyId': company['id'],
                'title': title,
                'department': dept,
                'location': random.choice(locations),
                'posted': f"{random.randint(1, 14)}d ago",
                'url': company.get('website', '#') + '/careers' if company.get('website') else '#',
            })
            job_id += 1
    
    return jobs


def save_data(companies, jobs):
    """Save to JSON files."""
    os.makedirs('data', exist_ok=True)
    
    with open('data/companies.json', 'w') as f:
        json.dump({'companies': companies, 'updated': datetime.now().isoformat()}, f, indent=2)
    
    with open('data/jobs.json', 'w') as f:
        json.dump({'jobs': jobs, 'updated': datetime.now().isoformat()}, f, indent=2)
    
    print(f"✅ Saved {len(companies)} companies to data/companies.json")
    print(f"✅ Saved {len(jobs)} jobs to data/jobs.json")


def main():
    print("🚀 FundedList YC Scraper")
    print("=" * 40)
    
    # Fetch from YC API
    raw = fetch_yc_companies()
    if not raw:
        print("❌ Failed to fetch data")
        return
    
    # Filter to best companies
    filtered = filter_and_rank_companies(raw, limit=30)
    print(f"📊 Selected top {len(filtered)} companies")
    
    # Format for frontend
    companies = [format_company(c) for c in filtered]
    
    # Generate jobs
    jobs = generate_jobs(companies)
    print(f"💼 Generated {len(jobs)} job listings")
    
    # Save
    save_data(companies, jobs)
    
    print("=" * 40)
    print("✅ Done!")


if __name__ == "__main__":
    main()
