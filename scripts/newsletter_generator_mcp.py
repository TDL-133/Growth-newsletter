#!/usr/bin/env python3
"""
Newsletter Generator MCP-Only - Version sans appels API Anthropic
Utilise uniquement les outils MCP (Firecrawl, Tavily) pour générer la newsletter
"""

import os
import sys
import logging
import json
from datetime import datetime
from dotenv import load_dotenv

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.mcp_content_aggregator import MCPContentAggregator
from scripts.html_builder import HTMLBuilder

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
log_file = os.getenv('LOG_FILE', 'logs/newsletter_generator_mcp.log')

os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NewsletterGeneratorMCP:
    """Générateur de newsletter Growth Weekly (MCP-only)"""
    
    def __init__(self):
        """Initialise le générateur MCP"""
        logger.info("=" * 80)
        logger.info("🚀 DÉMARRAGE DU GÉNÉRATEUR GROWTH WEEKLY (MCP-ONLY)")
        logger.info("=" * 80)
        
        self.aggregator = None
        self.html_builder = None
        
        # Créer les dossiers nécessaires
        os.makedirs('cache', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
    
    def run(self, use_cache: bool = False):
        """
        Exécute le workflow complet de génération
        
        Args:
            use_cache: Utiliser les données en cache si disponibles
        """
        try:
            # Étape 1: Collecte des articles via MCP
            all_articles = self._step_1_collect_articles(use_cache)
            
            # Étape 2: Classement et catégorisation (sans IA)
            ranked_articles = self._step_2_rank_articles(all_articles, use_cache)
            
            # Étape 3: Génération HTML
            output_path = self._step_3_generate_html(ranked_articles)
            
            # Résumé final
            self._print_summary(ranked_articles, output_path)
            
            logger.info("=" * 80)
            logger.info("✅ GÉNÉRATION TERMINÉE AVEC SUCCÈS (MCP-ONLY)")
            logger.info("=" * 80)
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ ERREUR LORS DE LA GÉNÉRATION: {e}", exc_info=True)
            raise
    
    def _step_1_collect_articles(self, use_cache: bool = False) -> list:
        """Étape 1: Collecte des articles via MCP"""
        logger.info("\n" + "=" * 80)
        logger.info("ÉTAPE 1/3: COLLECTE DES ARTICLES VIA MCP (Firecrawl + Tavily)")
        logger.info("=" * 80)
        
        cache_file = 'cache/mcp_articles.json'
        
        if use_cache and os.path.exists(cache_file):
            logger.info(f"📦 Chargement des articles depuis le cache: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Initialiser l'agrégateur MCP
        self.aggregator = MCPContentAggregator()
        
        # Collecter tous les articles
        all_articles = self.aggregator.collect_all_sources()
        
        # Sauvegarder en cache
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Articles sauvegardés en cache: {cache_file}")
        
        return all_articles
    
    def _step_2_rank_articles(self, all_articles: list, use_cache: bool = False) -> list:
        """Étape 2: Classement et catégorisation sans IA"""
        logger.info("\n" + "=" * 80)
        logger.info("ÉTAPE 2/3: CLASSEMENT ET CATÉGORISATION (SANS IA)")
        logger.info("=" * 80)
        
        cache_file = 'cache/mcp_ranked_articles.json'
        
        if use_cache and os.path.exists(cache_file):
            logger.info(f"📦 Chargement des articles classés depuis le cache: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Utiliser le même agrégateur pour le classement
        if not self.aggregator:
            self.aggregator = MCPContentAggregator()
        
        # Classer les articles
        ranked_articles = self.aggregator.rank_and_categorize(all_articles)
        
        # Sauvegarder en cache
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(ranked_articles, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Articles classés sauvegardés en cache: {cache_file}")
        
        return ranked_articles
    
    def _step_3_generate_html(self, ranked_articles: list) -> str:
        """Étape 3: Génération du HTML"""
        logger.info("\n" + "=" * 80)
        logger.info("ÉTAPE 3/3: GÉNÉRATION DU HTML")
        logger.info("=" * 80)
        
        # Initialiser le builder HTML
        self.html_builder = HTMLBuilder()
        
        # Générer le HTML
        output_path = self.html_builder.generate_html(ranked_articles)
        
        return output_path
    
    def _print_summary(self, ranked_articles: list, output_path: str):
        """Affiche un résumé de la génération"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 RÉSUMÉ DE LA GÉNÉRATION (MCP-ONLY)")
        logger.info("=" * 80)
        
        # Compter les articles par catégorie
        categories_count = {
            'critical': 0,
            'important': 0,
            'good_to_know': 0
        }
        
        sources_count = {}
        
        for article in ranked_articles:
            cat = article.get('category', 'important')
            if cat in categories_count:
                categories_count[cat] += 1
            
            source = article.get('source', 'Unknown')
            sources_count[source] = sources_count.get(source, 0) + 1
        
        logger.info(f"📰 Total d'articles: {len(ranked_articles)}")
        logger.info(f"   🔴 Critical: {categories_count['critical']}")
        logger.info(f"   🟡 Important: {categories_count['important']}")
        logger.info(f"   🟢 Good to Know: {categories_count['good_to_know']}")
        
        logger.info(f"\n📊 Répartition par source:")
        for source, count in sorted(sources_count.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"   {source}: {count} article(s)")
        
        logger.info(f"\n💰 COÛT API: $0.00 (MCP-only, pas d'appels Anthropic)")
        logger.info(f"📄 Fichier généré: {output_path}")
        logger.info(f"🌐 Ouvrir dans le navigateur: file://{os.path.abspath(output_path)}")


def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Générateur de newsletter Growth Weekly (MCP-only)')
    parser.add_argument('--use-cache', action='store_true', 
                       help='Utiliser les données en cache si disponibles')
    parser.add_argument('--clear-cache', action='store_true',
                       help='Effacer le cache avant de commencer')
    
    args = parser.parse_args()
    
    # Effacer le cache si demandé
    if args.clear_cache:
        import shutil
        cache_dir = 'cache'
        if os.path.exists(cache_dir):
            # Supprimer uniquement les fichiers MCP
            for f in ['mcp_articles.json', 'mcp_ranked_articles.json']:
                path = os.path.join(cache_dir, f)
                if os.path.exists(path):
                    os.remove(path)
                    logger.info(f"🗑️  Cache MCP effacé: {f}")
    
    # Générer la newsletter
    generator = NewsletterGeneratorMCP()
    output_path = generator.run(use_cache=args.use_cache)
    
    print(f"\n✅ Newsletter générée avec succès (MCP-only)!")
    print(f"📄 Fichier: {output_path}")
    print(f"🌐 Ouvrir: file://{os.path.abspath(output_path)}")
    print(f"💰 Coût API: $0.00 (pas d'appels Anthropic)")


if __name__ == "__main__":
    main()
