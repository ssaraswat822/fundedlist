#!/usr/bin/env python3
"""
Funding News Scraper - Scrapes recent startup funding announcements
Sources: startups.gallery, vcnewsdaily.com RSS feeds
"""

import json
import os
import re
import sqlite3
from datetime import datetime, timedelta
import feedparser
import requests
from bs4 import BeautifulSoup

# RSS Feeds for funding news
RSS_FEEDS = [
    "https://vcnewsdaily.com/feed/",
    "https://techcrunch.com/category/venture/feed/",
]

def init_database(db_path='fundedlist.db'):
    """Initialize SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS funding (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            website TEXT,
            funding_amount TEXT,
            round_type TEXT,
            description TEXT,
            category TEXT,
            investors TEXT,
            published_date TEXT,
            source TEXT,
            scraped_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            title TEXT NOT NULL,
            department TEXT,
            location TEXT,
            url TEXT,
            posted_date TEXT,
            scraped_at TEXT
        )
    ''')
    
    conn.commit()
    return conn


def parse_funding_amount(text):
    """Extract funding amount from text."""
    patterns = [
        r'\$(\d+(?:\.\d+)?)\s*(billion|B)\b',
        r'\$(\d+(?:\.\d+)?)\s*(million|M)\b',
        r'\$(\d+(?:\.\d+)?)\s*(thousand|K)\b',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            num = float(match.group(1))
            unit = match.group(2).lower()
            if unit in ['billion', 'b']:
                return f"${num}B"
            elif unit in ['million', 'm']:
                return f"${num}M"
            elif unit in ['thousand', 'k']:
                return f"${num}K"
    
    return None


def parse_round_type(text):
    """Extract funding round type from text."""
    rounds = ['Seed', 'Pre-Seed', 'Series A', 'Series B', 'Series C', 'Series D', 'Series E', 'Series F', 'Growth', 'IPO']
    text_lower = text.lower()
    
    for round_type in rounds:
        if round_type.lower() in text_lower:
            return round_type
    
    return "Funding"


def categorize_company(text):
    """Categorize company based on description."""
    text_lower = text.lower()
    
    categories = {
        'ai': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'llm', 'gpt', 'neural', 'deep learning'],
        'fintech': ['fintech', 'payment', 'banking', 'financial', 'crypto', 'blockchain', 'defi', 'lending'],
        'health': ['health', 'medical', 'biotech', 'pharma', 'clinical', 'patient', 'healthcare', 'drug'],
        'climate': ['climate', 'energy', 'solar', 'wind', 'carbon', 'sustainable', 'green', 'ev', 'battery'],
        'dev-tools': ['developer', 'devops', 'api', 'infrastructure', 'cloud', 'security', 'software', 'saas'],
    }
    
    for category, keywords in categories.items():
        if any(kw in text_lower for kw in keywords):
            return category
    
    return 'other'


def scrape_rss_feeds():
    """Scrape RSS feeds for funding news."""
    companies = []
    
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:20]:  # Last 20 entries
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                link = entry.get('link', '')
                published = entry.get('published', '')
                
                # Check if it's funding related
                funding_keywords = ['raise', 'funding', 'series', 'seed', 'million', 'billion', 'investment', 'round']
                if not any(kw in title.lower() or kw in summary.lower() for kw in funding_keywords):
                    continue
                
                # Extract company name (usually first part of title)
                name_match = re.match(r'^([A-Za-z0-9\s\.]+)', title)
                company_name = name_match.group(1).strip() if name_match else title[:30]
                
                amount = parse_funding_amount(title + ' ' + summary)
                round_type = parse_round_type(title + ' ' + summary)
                category = categorize_company(summary)
                
                companies.append({
                    'name': company_name,
                    'amount': amount or 'Undisclosed',
                    'round': round_type,
                    'tagline': summary[:150] if summary else '',
                    'category': category,
                    'source': feed_url,
                    'link': link,
                    'published': published,
                })
                
        except Exception as e:
            print(f"Error scraping {feed_url}: {e}")
    
    return companies


def scrape_startups_gallery():
    """Scrape startups.gallery for structured funding data."""
    companies = []
    
    try:
        url = "https://startups.gallery/news"
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; FundedList/1.0)'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for funding entries
            for row in soup.select('tr, .funding-row, .startup-card'):
                text = row.get_text()
                
                if '$' in text and ('million' in text.lower() or 'billion' in text.lower() or 'M' in text or 'B' in text):
                    amount = parse_funding_amount(text)
                    round_type = parse_round_type(text)
                    
                    # Try to extract company name
                    links = row.select('a')
                    name = links[0].get_text().strip() if links else text[:30]
                    
                    companies.append({
                        'name': name,
                        'amount': amount or 'Undisclosed',
                        'round': round_type,
                        'tagline': '',
                        'category': categorize_company(text),
                        'source': 'startups.gallery',
                    })
                    
    except Exception as e:
        print(f"Error scraping startups.gallery: {e}")
    
    return companies


def save_to_database(companies, db_path='fundedlist.db'):
    """Save scraped companies to database."""
    conn = init_database(db_path)
    cursor = conn.cursor()
    
    for company in companies:
        cursor.execute('''
            INSERT INTO funding (name, funding_amount, round_type, description, category, source, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            company['name'],
            company.get('amount'),
            company.get('round'),
            company.get('tagline'),
            company.get('category'),
            company.get('source'),
            datetime.now().isoformat()
        ))
    
    conn.commit()
    conn.close()
    print(f"Saved {len(companies)} companies to database")


def export_to_json(companies, output_path='data/companies.json'):
    """Export companies to JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Add IDs and format for frontend
    for i, company in enumerate(companies):
        company['id'] = company.get('id') or f"company-{i+1}"
        company['daysAgo'] = '1d ago'  # Simplified
        company['tags'] = [company.get('category', 'other').replace('-', ' ').title()]
        company['investors'] = company.get('investors', [])
    
    with open(output_path, 'w') as f:
        json.dump({'companies': companies, 'updated': datetime.now().isoformat()}, f, indent=2)
    
    print(f"Exported {len(companies)} companies to {output_path}")


def main():
    print("🔍 Scraping funding news...")
    
    # Scrape from multiple sources
    companies = []
    companies.extend(scrape_rss_feeds())
    companies.extend(scrape_startups_gallery())
    
    # Deduplicate by name
    seen = set()
    unique_companies = []
    for company in companies:
        name_lower = company['name'].lower()
        if name_lower not in seen:
            seen.add(name_lower)
            unique_companies.append(company)
    
    print(f"Found {len(unique_companies)} unique companies")
    
    # Save to database and JSON
    if unique_companies:
        save_to_database(unique_companies)
        export_to_json(unique_companies)
    
    return unique_companies


if __name__ == "__main__":
    main()
