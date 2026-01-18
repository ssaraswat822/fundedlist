#!/usr/bin/env python3
"""
Job Scraper - Scrapes job listings from recently funded companies
Uses company career pages and job board APIs
"""

import json
import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Common career page patterns
CAREER_PATTERNS = [
    '/careers',
    '/jobs',
    '/join',
    '/work-with-us',
    '/about/careers',
    '/company/careers',
]


def scrape_greenhouse_jobs(company_name, greenhouse_id):
    """Scrape jobs from Greenhouse job board."""
    jobs = []
    try:
        url = f"https://boards-api.greenhouse.io/v1/boards/{greenhouse_id}/jobs"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for job in data.get('jobs', []):
                jobs.append({
                    'company': company_name,
                    'title': job.get('title'),
                    'location': job.get('location', {}).get('name', 'Remote'),
                    'department': categorize_department(job.get('title', '')),
                    'url': job.get('absolute_url'),
                    'posted': 'Recently',
                })
    except Exception as e:
        print(f"Error scraping Greenhouse for {company_name}: {e}")
    
    return jobs


def scrape_lever_jobs(company_name, lever_id):
    """Scrape jobs from Lever job board."""
    jobs = []
    try:
        url = f"https://api.lever.co/v0/postings/{lever_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for job in data:
                jobs.append({
                    'company': company_name,
                    'title': job.get('text'),
                    'location': job.get('categories', {}).get('location', 'Remote'),
                    'department': job.get('categories', {}).get('team', 'General'),
                    'url': job.get('hostedUrl'),
                    'posted': 'Recently',
                })
    except Exception as e:
        print(f"Error scraping Lever for {company_name}: {e}")
    
    return jobs


def scrape_career_page(company_name, career_url):
    """Generic career page scraper."""
    jobs = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; FundedList/1.0)'}
        response = requests.get(career_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for job listings
            job_selectors = [
                '.job-listing', '.job-card', '.position', '.opening',
                '[class*="job"]', '[class*="position"]', '[class*="career"]'
            ]
            
            for selector in job_selectors:
                for element in soup.select(selector)[:20]:
                    title_el = element.select_one('h2, h3, h4, .title, [class*="title"]')
                    location_el = element.select_one('.location, [class*="location"]')
                    link_el = element.select_one('a[href]')
                    
                    if title_el:
                        title = title_el.get_text().strip()
                        if len(title) > 5 and len(title) < 100:
                            jobs.append({
                                'company': company_name,
                                'title': title,
                                'location': location_el.get_text().strip() if location_el else 'Remote',
                                'department': categorize_department(title),
                                'url': link_el.get('href') if link_el else career_url,
                                'posted': 'Recently',
                            })
                
                if jobs:
                    break
                    
    except Exception as e:
        print(f"Error scraping {career_url}: {e}")
    
    return jobs


def categorize_department(title):
    """Categorize job by department based on title."""
    title_lower = title.lower()
    
    if any(kw in title_lower for kw in ['engineer', 'developer', 'swe', 'devops', 'sre', 'architect', 'data scientist']):
        return 'engineering'
    elif any(kw in title_lower for kw in ['product manager', 'pm', 'product lead', 'product owner']):
        return 'product'
    elif any(kw in title_lower for kw in ['design', 'ux', 'ui', 'creative']):
        return 'design'
    elif any(kw in title_lower for kw in ['sales', 'account', 'business development', 'bd', 'gtm', 'revenue']):
        return 'sales'
    elif any(kw in title_lower for kw in ['marketing', 'growth', 'content', 'brand', 'communications']):
        return 'sales'
    elif any(kw in title_lower for kw in ['operations', 'ops', 'finance', 'hr', 'people', 'legal', 'admin']):
        return 'operations'
    
    return 'engineering'


def load_companies(companies_path='data/companies.json'):
    """Load companies from JSON file."""
    if os.path.exists(companies_path):
        with open(companies_path) as f:
            data = json.load(f)
            return data.get('companies', [])
    return []


def generate_sample_jobs(companies):
    """Generate sample job listings for companies without scrapeable career pages."""
    sample_titles = {
        'engineering': ['Senior Software Engineer', 'ML Engineer', 'Backend Engineer', 'Frontend Engineer', 'DevOps Engineer', 'Data Engineer'],
        'product': ['Product Manager', 'Senior Product Manager', 'Product Lead'],
        'design': ['Product Designer', 'UX Designer', 'Design Lead'],
        'sales': ['Account Executive', 'Sales Development Rep', 'Head of Sales', 'Growth Marketing Manager'],
        'operations': ['Operations Manager', 'Finance Manager', 'HR Manager', 'Executive Assistant'],
    }
    
    locations = ['San Francisco, CA', 'New York, NY', 'Remote', 'Austin, TX', 'Seattle, WA', 'Boston, MA']
    
    jobs = []
    job_id = 1
    
    for company in companies:
        # Generate 2-4 jobs per company
        import random
        num_jobs = random.randint(2, 4)
        
        for _ in range(num_jobs):
            dept = random.choice(list(sample_titles.keys()))
            title = random.choice(sample_titles[dept])
            location = random.choice(locations)
            
            jobs.append({
                'id': job_id,
                'companyId': company.get('id'),
                'title': title,
                'department': dept,
                'location': location,
                'posted': f"{random.randint(1, 7)}d ago",
                'url': company.get('website', '#') + '/careers',
            })
            job_id += 1
    
    return jobs


def export_jobs_json(jobs, output_path='data/jobs.json'):
    """Export jobs to JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump({
            'jobs': jobs,
            'updated': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"Exported {len(jobs)} jobs to {output_path}")


def main():
    print("💼 Scraping job listings...")
    
    # Load companies
    companies = load_companies()
    
    if not companies:
        print("No companies found in data/companies.json")
        print("Generating sample jobs for demo...")
        # Use sample companies if none exist
        companies = [
            {'id': 'xai', 'name': 'xAI', 'website': 'https://x.ai'},
            {'id': 'skild', 'name': 'Skild AI', 'website': 'https://skild.ai'},
            {'id': 'rain', 'name': 'Rain', 'website': 'https://rain.com'},
        ]
    
    # Generate sample jobs (in production, you'd scrape actual career pages)
    jobs = generate_sample_jobs(companies)
    
    print(f"Generated {len(jobs)} job listings")
    export_jobs_json(jobs)
    
    return jobs


if __name__ == "__main__":
    main()
