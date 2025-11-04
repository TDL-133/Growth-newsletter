#!/usr/bin/env python3
"""
MCP Content Aggregator - Agrégation de contenu via outils MCP
Utilise Firecrawl et Tavily pour collecter les articles SANS appels API Anthropic
"""

import os
import sys
import json
import logging
import yaml
from datetime import datetime, timedelta
from typing import Dict, List
import re

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from warp_mcp_helper import call_mcp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MCPContentAggregator:
    """Agrégateur de contenu utilisant uniquement les outils MCP"""
    
    def __init__(self, config_path: str = "config/sources.yaml"):
        """
        Initialise l'agrégateur MCP
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config = self._load_config(config_path)
        self.articles_cache = []
        logger.info("✅ MCPContentAggregator initialisé (MCP-only, pas d'API Anthropic)")
    
    def _load_config(self, config_path: str) -> Dict:
        """Charge la configuration depuis le fichier YAML"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def collect_all_sources(self) -> List[Dict]:
        """
        Collecte les articles de toutes les sources via MCP
        
        Returns:
            Liste d'articles avec métadonnées
        """
        logger.info("🚀 Collecte des articles via outils MCP...")
        
        all_articles = []
        sources = self.config.get('sources', [])
        
        for source in sources:
            source_name = source['name']
            logger.info(f"\n📰 Traitement de {source_name}...")
            
            # Stratégie 1: Scraper les URLs de fallback avec Firecrawl
            articles = self._scrape_source_with_firecrawl(source)
            
            # Stratégie 2 (fallback): Recherche Tavily si pas assez d'articles
            if len(articles) < 2:
                logger.info(f"  🔍 Recherche Tavily pour compléter {source_name}...")
                tavily_articles = self._search_with_tavily(source)
                articles.extend(tavily_articles)
            
            # Limiter à 3 articles par source max
            articles = articles[:3]
            
            for article in articles:
                article['source'] = source_name
                article['collected_at'] = datetime.now().isoformat()
            
            all_articles.extend(articles)
            logger.info(f"  ✅ {len(articles)} articles collectés pour {source_name}")
        
        logger.info(f"\n✅ Total: {len(all_articles)} articles collectés de {len(sources)} sources")
        return all_articles
    
    def _scrape_source_with_firecrawl(self, source: Dict) -> List[Dict]:
        """
        Scrape une source avec Firecrawl MCP
        
        Args:
            source: Configuration de la source
            
        Returns:
            Liste d'articles extraits
        """
        urls = source.get('fallback_urls', [])
        if not urls:
            return []
        
        articles = []
        
        for url in urls[:2]:  # Limiter à 2 URLs par source
            try:
                logger.info(f"  🔥 Firecrawl scraping: {url}")
                
                # Appel MCP Firecrawl
                result = call_mcp('firecrawl_scrape', {
                    'url': url,
                    'formats': ['markdown'],
                    'onlyMainContent': True
                })
                
                if result.get('success') and result.get('content'):
                    markdown_content = result['content'][0].get('markdown', '')
                    
                    # Parser le markdown pour extraire les articles
                    extracted = self._parse_markdown_content(markdown_content, url)
                    articles.extend(extracted)
                    
            except Exception as e:
                logger.error(f"  ❌ Erreur Firecrawl pour {url}: {e}")
        
        return articles
    
    def _search_with_tavily(self, source: Dict) -> List[Dict]:
        """
        Recherche des articles récents avec Tavily Search
        
        Args:
            source: Configuration de la source
            
        Returns:
            Liste d'articles trouvés
        """
        source_name = source['name']
        query = f"{source_name} growth marketing newsletter this week"
        
        articles = []
        
        try:
            logger.info(f"  🔎 Tavily search: {query}")
            
            # Appel MCP Tavily
            result = call_mcp('tavily-search', {
                'query': query,
                'max_results': 5,
                'search_depth': 'basic',
                'include_raw_content': False
            })
            
            if result.get('success') and result.get('results'):
                for item in result['results'][:3]:
                    article = {
                        'title': item.get('title', ''),
                        'summary': item.get('content', '')[:160],
                        'url': item.get('url', ''),
                        'category': 'important'
                    }
                    articles.append(article)
                    
        except Exception as e:
            logger.error(f"  ❌ Erreur Tavily pour {source_name}: {e}")
        
        return articles
    
    def _parse_markdown_content(self, markdown: str, source_url: str) -> List[Dict]:
        """
        Parse le contenu markdown pour extraire les articles
        
        Args:
            markdown: Contenu en markdown
            source_url: URL source
            
        Returns:
            Liste d'articles extraits
        """
        articles = []
        
        # Rechercher des patterns d'articles dans le markdown
        # Pattern 1: Titres avec liens (#### ou #####)
        pattern = r'####\s+\[(.+?)\]\((.+?)\)\s*\n(.+?)(?=####|\Z)'
        matches = re.findall(pattern, markdown, re.DOTALL)
        
        for match in matches[:5]:  # Max 5 articles par page
            title = match[0].strip()[:80]
            url = match[1].strip()
            content = match[2].strip()
            
            # Nettoyer et extraire le résumé
            summary_lines = [line.strip() for line in content.split('\n') if line.strip()]
            summary = ' '.join(summary_lines[:2])[:160]
            
            article = {
                'title': title,
                'summary': summary,
                'url': url if url.startswith('http') else source_url,
                'category': 'important'
            }
            articles.append(article)
        
        # Pattern 2: Paragraphes avec liens
        if not articles:
            pattern2 = r'\[(.+?)\]\((.+?)\)'
            matches2 = re.findall(pattern2, markdown)
            
            for title, url in matches2[:3]:
                if len(title) > 20 and url.startswith('http'):
                    article = {
                        'title': title[:80],
                        'summary': 'Article extrait automatiquement',
                        'url': url,
                        'category': 'good_to_know'
                    }
                    articles.append(article)
        
        return articles
    
    def rank_and_categorize(self, articles: List[Dict]) -> List[Dict]:
        """
        Classe et catégorise les articles par importance (sans IA)
        
        Args:
            articles: Liste des articles
            
        Returns:
            Liste des articles classés avec rang
        """
        logger.info("🎯 Classement et catégorisation des articles (sans IA)...")
        
        # Équilibrage: max 2-3 articles par source
        source_counts = {}
        balanced_articles = []
        
        for article in articles:
            source = article.get('source', 'Unknown')
            count = source_counts.get(source, 0)
            
            if count < 3:  # Max 3 par source
                balanced_articles.append(article)
                source_counts[source] = count + 1
        
        # Mélanger pour diversifier
        import random
        random.shuffle(balanced_articles)
        
        # Assigner rangs et catégories
        total = len(balanced_articles)
        for i, article in enumerate(balanced_articles):
            article['rank'] = i + 1
            
            # Catégorisation par tiers
            if i < total // 3:
                article['category'] = 'critical'
            elif i < 2 * total // 3:
                article['category'] = 'important'
            else:
                article['category'] = 'good_to_know'
        
        logger.info(f"✅ {len(balanced_articles)} articles classés ({len(source_counts)} sources)")
        
        return balanced_articles


def main():
    """Fonction de test"""
    aggregator = MCPContentAggregator()
    
    # Collecter les articles
    articles = aggregator.collect_all_sources()
    
    # Classer et catégoriser
    ranked = aggregator.rank_and_categorize(articles)
    
    print(f"\n✅ Articles collectés et classés: {len(ranked)}")
    for art in ranked[:5]:
        print(f"  {art['rank']}. [{art['category']}] {art['title']}")


if __name__ == "__main__":
    main()
