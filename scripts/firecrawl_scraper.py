#!/usr/bin/env python3
"""
Firecrawl MCP Scraper - Scraper avancé utilisant l'outil MCP Firecrawl
Remplace web_scraper.py avec une solution plus robuste et structurée
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FirecrawlScraper:
    """Scraper utilisant Firecrawl MCP pour un contenu web structuré"""
    
    def __init__(self):
        """Initialise le scraper Firecrawl"""
        logger.info("✅ Firecrawl MCP Scraper initialisé")
    
    def scrape_url(self, url: str, source_name: str) -> Optional[Dict]:
        """
        Scrape une URL avec Firecrawl MCP
        
        Args:
            url: URL à scraper
            source_name: Nom de la source
            
        Returns:
            Dictionnaire avec le contenu scrapé en markdown structuré
        """
        logger.info(f"🔥 Firecrawl scraping: {url}")
        
        try:
            # Appel MCP Firecrawl activé
            import sys
            sys.path.append('/Users/lopato/Documents/DAGORSEY/Geek/test-new-stuff/Revue de presse growth fr')
            from warp_mcp_helper import call_mcp
            
            result = call_mcp("firecrawl_scrape", {
                "url": url,
                "formats": ["markdown"],
                "onlyMainContent": True,
                "maxAge": 172800000  # 48h cache pour performance
            })
            
            if result and "markdown" in result:
                content = result["markdown"]
                title = result.get("metadata", {}).get("title", source_name)
                
                logger.info(f"  ✅ Contenu structuré récupéré: {len(content)} caractères")
                
                return {
                    'source': source_name,
                    'subject': f"Firecrawl: {title}",
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'from': url,
                    'content': content,
                    'content_type': 'markdown',
                    'message_id': f'firecrawl_{hash(url)}'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"  ❌ Erreur Firecrawl pour {url}: {e}")
            return None
    
    def scrape_source(self, source: Dict) -> List[Dict]:
        """
        Scrape les URLs fallback d'une source avec Firecrawl
        
        Args:
            source: Configuration de la source
            
        Returns:
            Liste des contenus scrapés en markdown structuré
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
        
        # Scraper chaque URL avec Firecrawl
        for url in urls:
            content = self.scrape_url(url, source['name'])
            if content:
                results.append(content)
        
        return results
    
    def search_recent_articles(self, source: Dict, days: int = 7) -> List[Dict]:
        """
        Recherche active des derniers articles d'une source (nouveau!)
        
        Args:
            source: Configuration de la source
            days: Nombre de jours à rechercher en arrière
            
        Returns:
            Liste d'articles récents trouvés
        """
        logger.info(f"🔍 Recherche d'articles récents pour {source['name']}")
        
        try:
            # Construire requête de recherche ciblée
            fallback_url = source.get('fallback_url', '')
            if not fallback_url:
                return []
            
            # Extraire le domaine
            from urllib.parse import urlparse
            domain = urlparse(fallback_url).netloc
            
            # Requête ciblée
            query = f"site:{domain} growth marketing"
            
            # NOTE: Appel MCP à activer
            # results = call_mcp_tool("firecrawl_search", {
            #     "query": query,
            #     "limit": 5,
            #     "scrapeOptions": {
            #         "formats": ["markdown"],
            #         "onlyMainContent": True
            #     }
            # })
            
            # PLACEHOLDER
            results = []
            
            logger.info(f"  ✅ {len(results)} articles récents trouvés")
            return results
            
        except Exception as e:
            logger.error(f"  ❌ Erreur recherche pour {source['name']}: {e}")
            return []


def main():
    """Fonction de test"""
    scraper = FirecrawlScraper()
    
    test_source = {
        'name': 'Test Source',
        'fallback_url': 'https://www.demandcurve.com/newsletter'
    }
    
    results = scraper.scrape_source(test_source)
    print(f"\n✅ {len(results)} contenu(s) récupéré(s)")
    
    if results:
        print(f"Type de contenu: {results[0].get('content_type')}")
        print(f"Taille: {len(results[0]['content'])} caractères")


if __name__ == "__main__":
    main()
