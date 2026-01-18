#!/usr/bin/env python3
"""
VC Portfolio Scraper - Scrapes portfolio pages from major VC firms
"""

import json
import os
from datetime import datetime

# VC Data - manually maintained since portfolio pages are hard to scrape reliably
VCS = [
    {
        "id": "yc",
        "name": "Y Combinator",
        "shortName": "YC",
        "logo": "🟠",
        "website": "https://ycombinator.com",
        "portfolio_url": "https://ycombinator.com/companies",
        "aum": "N/A",
        "founded": 2005,
        "portfolioCount": 5000,
        "focus": ["Early Stage", "All Sectors"],
        "notable": ["Stripe", "Airbnb", "Dropbox", "Reddit", "Coinbase", "DoorDash"]
    },
    {
        "id": "sequoia",
        "name": "Sequoia Capital",
        "shortName": "Sequoia",
        "logo": "🌲",
        "website": "https://sequoiacap.com",
        "portfolio_url": "https://sequoiacap.com/our-companies",
        "aum": "$56B",
        "founded": 1972,
        "portfolioCount": 2947,
        "focus": ["Consumer", "Enterprise", "Fintech", "Healthcare"],
        "notable": ["Stripe", "Airbnb", "DoorDash", "Linear", "Zoom", "Snowflake"]
    },
    {
        "id": "a16z",
        "name": "Andreessen Horowitz",
        "shortName": "a16z",
        "logo": "🅰️",
        "website": "https://a16z.com",
        "portfolio_url": "https://a16z.com/portfolio/",
        "aum": "$46B",
        "founded": 2009,
        "portfolioCount": 1119,
        "focus": ["AI", "Crypto", "Fintech", "Bio", "Games"],
        "notable": ["Coinbase", "GitHub", "Roblox", "Figma", "Instacart", "Lyft"]
    },
    {
        "id": "accel",
        "name": "Accel",
        "shortName": "Accel",
        "logo": "⚡",
        "website": "https://accel.com",
        "portfolio_url": "https://accel.com/portfolio",
        "aum": "$50B",
        "founded": 1983,
        "portfolioCount": 500,
        "focus": ["Enterprise", "Consumer", "Fintech"],
        "notable": ["Facebook", "Slack", "Spotify", "Dropbox", "Atlassian"]
    },
    {
        "id": "greylock",
        "name": "Greylock Partners",
        "shortName": "Greylock",
        "logo": "🔷",
        "website": "https://greylock.com",
        "portfolio_url": "https://greylock.com/portfolio",
        "aum": "$5B",
        "founded": 1965,
        "portfolioCount": 476,
        "focus": ["Enterprise", "Consumer", "AI"],
        "notable": ["Discord", "Figma", "LinkedIn", "Airbnb", "Roblox"]
    },
    {
        "id": "founders-fund",
        "name": "Founders Fund",
        "shortName": "FF",
        "logo": "🚀",
        "website": "https://foundersfund.com",
        "portfolio_url": "https://foundersfund.com/portfolio",
        "aum": "$17B",
        "founded": 2005,
        "portfolioCount": 200,
        "focus": ["Deep Tech", "Defense", "Space", "Bio"],
        "notable": ["SpaceX", "Palantir", "Anduril", "Stripe", "Airbnb"]
    },
    {
        "id": "lightspeed",
        "name": "Lightspeed Venture Partners",
        "shortName": "Lightspeed",
        "logo": "💡",
        "website": "https://lsvp.com",
        "portfolio_url": "https://lsvp.com/portfolio",
        "aum": "$18B",
        "founded": 2000,
        "portfolioCount": 400,
        "focus": ["Enterprise", "Consumer", "Crypto"],
        "notable": ["Snap", "Affirm", "Carta", "Epic Games", "Mulesoft"]
    },
    {
        "id": "benchmark",
        "name": "Benchmark",
        "shortName": "Benchmark",
        "logo": "📊",
        "website": "https://benchmark.com",
        "portfolio_url": "https://benchmark.com/portfolio",
        "aum": "$4B",
        "founded": 1995,
        "portfolioCount": 150,
        "focus": ["Consumer", "Enterprise", "Marketplaces"],
        "notable": ["eBay", "Twitter", "Uber", "Discord", "Snapchat"]
    },
    {
        "id": "khosla",
        "name": "Khosla Ventures",
        "shortName": "Khosla",
        "logo": "🔬",
        "website": "https://khoslaventures.com",
        "portfolio_url": "https://khoslaventures.com/portfolio",
        "aum": "$15B",
        "founded": 2004,
        "portfolioCount": 300,
        "focus": ["Climate", "Health", "AI", "Enterprise"],
        "notable": ["DoorDash", "Instacart", "Impossible Foods", "OpenAI"]
    },
    {
        "id": "nea",
        "name": "New Enterprise Associates",
        "shortName": "NEA",
        "logo": "🌐",
        "website": "https://nea.com",
        "portfolio_url": "https://nea.com/portfolio",
        "aum": "$25B",
        "founded": 1977,
        "portfolioCount": 1000,
        "focus": ["Healthcare", "Enterprise", "Consumer"],
        "notable": ["Salesforce", "Coursera", "Robinhood", "Plaid"]
    }
]


def export_vcs_json(output_path='data/vcs.json'):
    """Export VC data to JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump({
            'vcs': VCS,
            'updated': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"Exported {len(VCS)} VCs to {output_path}")


def main():
    print("📊 Exporting VC data...")
    export_vcs_json()
    print(f"✅ Done! {len(VCS)} VCs exported")


if __name__ == "__main__":
    main()
