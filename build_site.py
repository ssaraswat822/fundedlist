#!/usr/bin/env python3
"""
Build Script - Regenerates index.html with fresh data from JSON files
Run this after the scrapers to update the site.
"""

import json
import os
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
    
    # Convert data to JavaScript strings
    companies_js = json.dumps(companies, indent=8, ensure_ascii=False)
    vcs_js = json.dumps(vcs, indent=8, ensure_ascii=False)
    jobs_js = json.dumps(jobs, indent=8, ensure_ascii=False)
    
    # Find and replace data arrays using string operations (not regex)
    # This avoids issues with special characters in the JSON
    
    # Replace companies array
    start_marker = 'const companies = ['
    start_idx = html.find(start_marker)
    if start_idx != -1:
        # Find the closing ];
        bracket_count = 0
        end_idx = start_idx + len(start_marker) - 1
        for i in range(start_idx + len(start_marker) - 1, len(html)):
            if html[i] == '[':
                bracket_count += 1
            elif html[i] == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    end_idx = i + 1
                    break
        html = html[:start_idx] + 'const companies = ' + companies_js + ';' + html[end_idx+1:]
    
    # Replace vcs array
    start_marker = 'const vcs = ['
    start_idx = html.find(start_marker)
    if start_idx != -1:
        bracket_count = 0
        end_idx = start_idx + len(start_marker) - 1
        for i in range(start_idx + len(start_marker) - 1, len(html)):
            if html[i] == '[':
                bracket_count += 1
            elif html[i] == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    end_idx = i + 1
                    break
        html = html[:start_idx] + 'const vcs = ' + vcs_js + ';' + html[end_idx+1:]
    
    # Replace jobs array
    start_marker = 'const jobs = ['
    start_idx = html.find(start_marker)
    if start_idx != -1:
        bracket_count = 0
        end_idx = start_idx + len(start_marker) - 1
        for i in range(start_idx + len(start_marker) - 1, len(html)):
            if html[i] == '[':
                bracket_count += 1
            elif html[i] == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    end_idx = i + 1
                    break
        html = html[:start_idx] + 'const jobs = ' + jobs_js + ';' + html[end_idx+1:]
    
    # Update the footer date
    today = datetime.now().strftime('%b %d, %Y')
    html = html.replace('Updated Jan 17, 2026', f'Updated {today}')
    
    # Write the updated HTML
    with open('index.html', 'w') as f:
        f.write(html)
    
    print(f"✅ Built index.html with fresh data")
    print(f"   Updated: {today}")


if __name__ == "__main__":
    main()
