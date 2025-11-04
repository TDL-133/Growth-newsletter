#!/usr/bin/env python3
"""
Script pour collecter de vrais articles growth marketing avec URLs fonctionnelles
Utilise le scraping direct des sources configurées
"""

import os
import sys
import json
import yaml
import re
import logging
from datetime import datetime
from typing import List, Dict
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config():
    """Charge la config des sources"""
    with open('config/sources.yaml', 'r') as f:
        return yaml.safe_load(f)


def scrape_url_simple(url: str) -> Dict:
    """Scrape simple d'une URL pour extraire les articles"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        
        # Rechercher les liens d'articles
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Filtrer les liens valides
            if len(text) > 20 and len(text) < 150:
                if href.startswith('http') or href.startswith('/'):
                    full_url = href if href.startswith('http') else f"{urlparse(url).scheme}://{urlparse(url).netloc}{href}"
                    
                    articles.append({
                        'title': text,
                        'url': full_url,
                        'summary': ''
                    })
        
        return {'success': True, 'articles': articles[:10]}
        
    except Exception as e:
        logger.error(f"Erreur scraping {url}: {e}")
        return {'success': False, 'articles': []}


def collect_from_all_sources() -> List[Dict]:
    """Collecte les articles de toutes les sources"""
    config = load_config()
    all_articles = []
    
    sources_to_scrape = [
        {
            'name': 'TLDR Marketing',
            'url': 'https://tldr.tech/marketing'
        },
        {
            'name': 'Demand Curve',
            'url': 'https://www.demandcurve.com/blog'
        },
        {
            'name': 'Growth Unhinged',
            'url': 'https://www.growthunhinged.com/'
        },
        {
            'name': 'Indie Hackers',
            'url': 'https://www.indiehackers.com/'
        },
        {
            'name': 'Lenny\'s Newsletter',
            'url': 'https://www.lennysnewsletter.com/'
        }
    ]
    
    for source in sources_to_scrape:
        logger.info(f"Scraping {source['name']}...")
        result = scrape_url_simple(source['url'])
        
        if result['success'] and result['articles']:
            # Prendre 3 articles max par source
            for article in result['articles'][:3]:
                article['source'] = source['name']
                all_articles.append(article)
    
    logger.info(f"✅ Total: {len(all_articles)} articles collectés")
    return all_articles


def save_articles(articles: List[Dict], output_file: str = 'cache/real_articles.json'):
    """Sauvegarde les articles"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    logger.info(f"💾 Articles sauvegardés: {output_file}")


if __name__ == '__main__':
    articles = collect_from_all_sources()
    save_articles(articles)
    
    print(f"\n✅ {len(articles)} articles collectés avec URLs réelles")
    print("\nExemples:")
    for art in articles[:5]:
        print(f"  • {art['title'][:60]}...")
        print(f"    {art['url']}")
