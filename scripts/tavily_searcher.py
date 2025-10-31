#!/usr/bin/env python3
"""
Tavily Searcher - Recherche active d'articles récents via MCP Tavily
Trouve les derniers contenus pour les sources sans emails récents
"""

import os
import logging
from typing import List, Dict
from datetime import datetime
from urllib.parse import urlparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TavilySearcher:
    """Recherche d'articles récents via Tavily MCP"""
    
    def __init__(self):
        """Initialise le searcher Tavily"""
        logger.info("✅ Tavily MCP Searcher initialisé")
    
    def search_recent_articles(self, source: Dict, max_results: int = 3) -> List[Dict]:
        """
        Recherche les derniers articles d'une source
        
        Args:
            source: Configuration de la source
            max_results: Nombre maximum de résultats
            
        Returns:
            Liste d'articles trouvés avec URLs précises
        """
        source_name = source.get('name', '')
        fallback_url = source.get('fallback_url', '')
        
        if not fallback_url:
            logger.warning(f"  ⚠️  Pas d'URL pour {source_name}")
            return []
        
        # Extraire le domaine
        domain = urlparse(fallback_url).netloc
        
        # Construire requête ciblée
        query = f"site:{domain} growth marketing"
        
        logger.info(f"🔍 Tavily search: {query}")
        
        try:
            # NOTE: Appel MCP à activer en production
            # result = call_mcp_tool("tavily-search", {
            #     "query": query,
            #     "max_results": max_results,
            #     "search_depth": "basic",
            #     "include_raw_content": False
            # })
            
            # PLACEHOLDER pour développement
            # Simuler résultats basés sur le vrai retour Tavily
            articles = []
            
            # Format attendu de Tavily:
            # [{"title": "...", "url": "...", "content": "..."}]
            
            # Exemple structure:
            # for result in tavily_results:
            #     articles.append({
            #         'source': source_name,
            #         'subject': f"Tavily: {result['title']}",
            #         'date': datetime.now().strftime('%Y-%m-%d'),
            #         'from': result['url'],
            #         'content': result['content'],
            #         'url': result['url'],
            #         'message_id': f'tavily_{hash(result["url"])}'
            #     })
            
            logger.info(f"  ✅ {len(articles)} articles trouvés via Tavily")
            return articles
            
        except Exception as e:
            logger.error(f"  ❌ Erreur Tavily pour {source_name}: {e}")
            return []
    
    def enrich_source_content(self, source: Dict, existing_count: int = 0) -> List[Dict]:
        """
        Enrichit une source avec des articles récents si peu de contenu
        
        Args:
            source: Configuration de la source
            existing_count: Nombre d'articles déjà récupérés
            
        Returns:
            Liste d'articles supplémentaires
        """
        # Si on a déjà 3+ articles, pas besoin de chercher plus
        if existing_count >= 3:
            logger.info(f"  ℹ️  {source['name']}: Assez d'articles ({existing_count})")
            return []
        
        # Chercher des articles complémentaires
        needed = 3 - existing_count
        logger.info(f"  🔍 {source['name']}: Recherche de {needed} articles supplémentaires")
        
        return self.search_recent_articles(source, max_results=needed)


def main():
    """Test du searcher"""
    searcher = TavilySearcher()
    
    test_source = {
        'name': 'Demand Curve',
        'fallback_url': 'https://www.demandcurve.com/newsletter'
    }
    
    articles = searcher.search_recent_articles(test_source, max_results=3)
    print(f"\n✅ {len(articles)} articles trouvés")


if __name__ == "__main__":
    main()
