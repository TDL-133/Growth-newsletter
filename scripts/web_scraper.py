#!/usr/bin/env python3
"""
Web Scraper - Scraper les URLs fallback quand Gmail ne trouve pas d'emails
"""

import os
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebScraper:
    """Scraper web pour récupérer le contenu des URLs fallback"""
    
    def __init__(self):
        """Initialise le scraper web"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def scrape_url(self, url: str, source_name: str) -> Optional[Dict]:
        """
        Scrape une URL et retourne le contenu
        
        Args:
            url: URL à scraper
            source_name: Nom de la source
            
        Returns:
            Dictionnaire avec le contenu scrapé
        """
        logger.info(f"🌐 Scraping URL: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parser le HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Supprimer les scripts et styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extraire le texte
            text = soup.get_text()
            
            # Nettoyer les espaces
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limiter à 15000 caractères pour éviter les tokens excessifs
            if len(text) > 15000:
                text = text[:15000]
            
            # Essayer d'extraire le titre
            title = soup.find('title')
            title_text = title.string if title else source_name
            
            return {
                'source': source_name,
                'subject': f"Web scraping: {title_text}",
                'date': datetime.now().strftime('%Y-%m-%d'),
                'from': url,
                'content': text,
                'message_id': f'web_{hash(url)}'
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"  ❌ Timeout lors du scraping de {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"  ❌ Erreur lors du scraping de {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"  ❌ Erreur inattendue: {e}")
            return None
    
    def scrape_source(self, source: Dict) -> List[Dict]:
        """
        Scrape les URLs fallback d'une source
        
        Args:
            source: Configuration de la source avec fallback_url ou fallback_urls
            
        Returns:
            Liste des contenus scrapés
        """
        results = []
        
        # Récupérer les URLs
        urls = []
        if 'fallback_url' in source and source['fallback_url']:
            urls.append(source['fallback_url'])
        if 'fallback_urls' in source and source['fallback_urls']:
            urls.extend(source['fallback_urls'])
        
        if not urls:
            logger.warning(f"  ⚠️  Aucune URL fallback pour {source['name']}")
            return results
        
        # Scraper chaque URL
        for url in urls:
            content = self.scrape_url(url, source['name'])
            if content:
                results.append(content)
                logger.info(f"  ✅ Contenu récupéré: {len(content['content'])} caractères")
        
        return results


def main():
    """Fonction de test"""
    scraper = WebScraper()
    
    test_source = {
        'name': 'Test Source',
        'fallback_url': 'https://www.lennysnewsletter.com/'
    }
    
    results = scraper.scrape_source(test_source)
    print(f"\n✅ {len(results)} contenu(s) récupéré(s)")
    
    if results:
        print(f"Premier résultat: {results[0]['subject']}")
        print(f"Taille: {len(results[0]['content'])} caractères")


if __name__ == "__main__":
    main()
