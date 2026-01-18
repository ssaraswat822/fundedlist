#!/usr/bin/env python3
"""
Build Script - Regenerates index.html with fresh data from JSON files
Run this after the scrapers to update the site.
"""

import json
import os
import re
from datetime import datetime


def load_json(path, default_key='items'):
    """Load data from JSON file."""
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {default_key: []}


def main():
    print("🔨 Building FundedList site...")
    
    # Load data from JSON files
    companies_data = load_json('data/companies.json', 'companies')
    vcs_data = load_json('data/vcs.json', 'vcs')
    jobs_data = load_json('data/jobs.json', 'jobs')
    
    companies = companies_data.get('companies', [])
    vcs = vcs_data.get('vcs', [])
    jobs = jobs_data.get('jobs', [])
    
    print(f"   Loaded {len(companies)} companies")
    print(f"   Loaded {len(vcs)} VCs")
    print(f"   Loaded {len(jobs)} jobs")
    
    # Read the template (current index.html)
    with open('index.html', 'r') as f:
        html = f.read()
    
    # Convert data to JavaScript
    companies_js = json.dumps(companies, indent=8)
    vcs_js = json.dumps(vcs, indent=8)
    jobs_js = json.dumps(jobs, indent=8)
    
    # Replace the data arrays in the HTML
    # Pattern to find and replace the companies array
    html = re.sub(
        r'const companies = \[[\s\S]*?\];',
        f'const companies = {companies_js};',
        html
    )
    
    # Pattern to find and replace the vcs array
    html = re.sub(
        r'const vcs = \[[\s\S]*?\];',
        f'const vcs = {vcs_js};',
        html
    )
    
    # Pattern to find and replace the jobs array
    html = re.sub(
        r'const jobs = \[[\s\S]*?\];',
        f'const jobs = {jobs_js};',
        html
    )
    
    # Update the footer date
    today = datetime.now().strftime('%b %d, %Y')
    html = re.sub(
        r'Updated [A-Za-z]+ \d+, \d+',
        f'Updated {today}',
        html
    )
    
    # Write the updated HTML
    with open('index.html', 'w') as f:
        f.write(html)
    
    print(f"✅ Built index.html with fresh data")
    print(f"   Updated: {today}")


if __name__ == "__main__":
    main()
