#!/usr/bin/env python3
"""
Markdown Parser - Extrait articles du markdown structuré (Firecrawl) SANS IA
Économise les appels API Anthropic pour le contenu bien structuré
"""

import re
import logging
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MarkdownParser:
    """Parse le markdown structuré pour extraire articles sans IA"""
    
    def extract_articles_from_markdown(self, markdown_content: str, source_name: str) -> List[Dict]:
        """
        Extrait articles du markdown Firecrawl
        
        Args:
            markdown_content: Contenu markdown de Firecrawl
            source_name: Nom de la source
            
        Returns:
            Liste d'articles extraits
        """
        logger.info(f"📝 Extraction markdown pour {source_name}")
        
        articles = []
        
        # Pattern pour articles Demand Curve
        # Ex: ##### Email customer acquisition for big, once-in-a-lifetime purchases
        pattern = r'#####\s+(.+?)\n\n_Insight from.+?\n\n(.+?)(?=\n\n#####|\n\n##|\Z)'
        
        matches = re.findall(pattern, markdown_content, re.DOTALL)
        
        for title, description in matches:
            # Nettoyer le titre
            title = title.strip()
            
            # Nettoyer la description (garder 2-3 premiers paragraphes)
            desc_lines = description.split('\n\n')
            summary = ' '.join(desc_lines[:2]).strip()
            
            # Limiter à 160 caractères
            if len(summary) > 160:
                summary = summary[:157] + '...'
            
            # Extraire URLs si présentes
            url_match = re.search(r'\[.+?\]\((https?://[^\)]+)\)', description)
            url = url_match.group(1) if url_match else None
            
            articles.append({
                'title': title,
                'summary': summary,
                'url': url,
                'category': 'important',  # Par défaut, sera reclassé après
                'source': source_name,
                'extraction_method': 'markdown_parser'
            })
        
        logger.info(f"  ✅ {len(articles)} articles extraits sans IA")
        return articles
    
    def extract_from_substack(self, html_content: str, source_name: str) -> List[Dict]:
        """
        Extrait articles des newsletters Substack (structure HTML prévisible)
        
        Args:
            html_content: HTML de la newsletter Substack
            source_name: Nom de la source
            
        Returns:
            Liste d'articles extraits
        """
        logger.info(f"📧 Extraction Substack pour {source_name}")
        
        articles = []
        
        # Pattern Substack pour les titres de posts
        # <h2 class="post-title">...</h2>
        title_pattern = r'<h2[^>]*class="[^"]*post-title[^"]*"[^>]*>(.*?)</h2>'
        titles = re.findall(title_pattern, html_content, re.DOTALL)
        
        # Pattern pour les subtitles/descriptions
        subtitle_pattern = r'<p[^>]*class="[^"]*subtitle[^"]*"[^>]*>(.*?)</p>'
        subtitles = re.findall(subtitle_pattern, html_content, re.DOTALL)
        
        # Pattern pour les URLs d'articles
        url_pattern = r'<a[^>]*href="(https://[^"]+/p/[^"]+)"'
        urls = re.findall(url_pattern, html_content)
        
        # Combiner les données
        for i in range(min(len(titles), len(subtitles), len(urls))):
            title = re.sub(r'<[^>]+>', '', titles[i]).strip()
            summary = re.sub(r'<[^>]+>', '', subtitles[i]).strip()
            
            # Limiter la longueur
            if len(title) > 80:
                title = title[:77] + '...'
            if len(summary) > 160:
                summary = summary[:157] + '...'
            
            articles.append({
                'title': title,
                'summary': summary,
                'url': urls[i],
                'category': 'important',
                'source': source_name,
                'extraction_method': 'substack_parser'
            })
        
        logger.info(f"  ✅ {len(articles)} articles Substack extraits sans IA")
        return articles
    
    def can_parse_without_ai(self, content: str, source_name: str) -> bool:
        """
        Détermine si le contenu peut être parsé sans IA
        
        Args:
            content: Contenu à analyser
            source_name: Nom de la source
            
        Returns:
            True si parsing sans IA possible
        """
        # Vérifier si c'est du markdown Firecrawl
        if '####' in content or '#####' in content:
            return True
        
        # Vérifier si c'est Substack
        if 'substack.com' in source_name.lower() or 'class="post-title"' in content:
            return True
        
        return False


def main():
    """Test du parser"""
    parser = MarkdownParser()
    
    # Test avec le markdown Demand Curve de Firecrawl
    test_markdown = """
##### Email customer acquisition for big, once-in-a-lifetime purchases

_Insight from Rejoiner._

Most content on ecommerce email marketing focuses on DTC: retention, maximizing lifetime value.

But what should you do if you're a store selling $1,000+ products?

##### Four pricing psychology tactics to increase conversion

_Insight from Northern Comfort._

Shoppers don't perceive prices or buy rationally.
"""
    
    articles = parser.extract_articles_from_markdown(test_markdown, "Test Source")
    print(f"\n✅ {len(articles)} articles extraits")
    for art in articles:
        print(f"  - {art['title'][:50]}...")


if __name__ == "__main__":
    main()
