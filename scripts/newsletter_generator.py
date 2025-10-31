#!/usr/bin/env python3
"""
Newsletter Generator - Script principal
Orchestre tout le workflow de génération de la newsletter Growth Weekly
"""

import os
import sys
import logging
import json
from datetime import datetime
from dotenv import load_dotenv

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.gmail_scraper import GmailScraper
from scripts.ai_processor import AIProcessor
from scripts.html_builder import HTMLBuilder

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
log_file = os.getenv('LOG_FILE', 'logs/newsletter_generator.log')

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


class NewsletterGenerator:
    """Générateur de newsletter Growth Weekly"""
    
    def __init__(self):
        """Initialise le générateur"""
        logger.info("=" * 80)
        logger.info("🚀 DÉMARRAGE DU GÉNÉRATEUR DE NEWSLETTER GROWTH WEEKLY")
        logger.info("=" * 80)
        
        self.scraper = None
        self.ai_processor = None
        self.html_builder = None
        
        # Créer le dossier cache si nécessaire
        cache_dir = os.getenv('CACHE_DIR', 'cache')
        os.makedirs(cache_dir, exist_ok=True)
    
    def run(self, use_cache: bool = False):
        """
        Exécute le workflow complet de génération
        
        Args:
            use_cache: Utiliser les données en cache si disponibles
        """
        try:
            # Étape 1: Scraping Gmail
            emails_by_source = self._step_1_scrape_emails(use_cache)
            
            # Étape 2: Traitement IA
            all_articles = self._step_2_process_with_ai(emails_by_source, use_cache)
            
            # Étape 3: Classement et catégorisation
            ranked_articles = self._step_3_rank_and_categorize(all_articles, use_cache)
            
            # Étape 4: Génération HTML
            output_path = self._step_4_generate_html(ranked_articles)
            
            # Résumé final
            self._print_summary(ranked_articles, output_path)
            
            logger.info("=" * 80)
            logger.info("✅ GÉNÉRATION TERMINÉE AVEC SUCCÈS")
            logger.info("=" * 80)
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ ERREUR LORS DE LA GÉNÉRATION: {e}", exc_info=True)
            raise
    
    def _step_1_scrape_emails(self, use_cache: bool = False) -> dict:
        """Étape 1: Scraping des emails depuis Gmail"""
        logger.info("\n" + "=" * 80)
        logger.info("ÉTAPE 1/4: SCRAPING DES EMAILS GMAIL")
        logger.info("=" * 80)
        
        cache_file = 'cache/emails.json'
        
        if use_cache and os.path.exists(cache_file):
            logger.info(f"📦 Chargement des emails depuis le cache: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Initialiser le scraper
        self.scraper = GmailScraper()
        
        # Scraper toutes les sources
        emails_by_source = self.scraper.scrape_all_sources()
        
        # Sauvegarder en cache
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(emails_by_source, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Emails sauvegardés en cache: {cache_file}")
        
        return emails_by_source
    
    def _step_2_process_with_ai(self, emails_by_source: dict, use_cache: bool = False) -> list:
        """Étape 2: Traitement avec l'IA"""
        logger.info("\n" + "=" * 80)
        logger.info("ÉTAPE 2/4: TRAITEMENT AVEC L'IA (EXTRACTION & TRADUCTION)")
        logger.info("=" * 80)
        
        cache_file = 'cache/articles.json'
        
        if use_cache and os.path.exists(cache_file):
            logger.info(f"📦 Chargement des articles depuis le cache: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Initialiser le processeur IA
        self.ai_processor = AIProcessor()
        
        # Traiter tous les emails
        all_articles = self.ai_processor.process_all_emails(emails_by_source)
        
        # Sauvegarder en cache
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Articles sauvegardés en cache: {cache_file}")
        
        return all_articles
    
    def _step_3_rank_and_categorize(self, all_articles: list, use_cache: bool = False) -> list:
        """Étape 3: Classement et catégorisation"""
        logger.info("\n" + "=" * 80)
        logger.info("ÉTAPE 3/4: CLASSEMENT ET CATÉGORISATION")
        logger.info("=" * 80)
        
        cache_file = 'cache/ranked_articles.json'
        
        if use_cache and os.path.exists(cache_file):
            logger.info(f"📦 Chargement des articles classés depuis le cache: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Utiliser le même processeur IA pour le classement
        if not self.ai_processor:
            self.ai_processor = AIProcessor()
        
        # Classer les articles
        ranked_articles = self.ai_processor.rank_and_categorize(all_articles)
        
        # Sauvegarder en cache
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(ranked_articles, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Articles classés sauvegardés en cache: {cache_file}")
        
        return ranked_articles
    
    def _step_4_generate_html(self, ranked_articles: list) -> str:
        """Étape 4: Génération du HTML"""
        logger.info("\n" + "=" * 80)
        logger.info("ÉTAPE 4/4: GÉNÉRATION DU HTML")
        logger.info("=" * 80)
        
        # Initialiser le builder HTML
        self.html_builder = HTMLBuilder()
        
        # Générer le HTML
        output_path = self.html_builder.generate_html(ranked_articles)
        
        return output_path
    
    def _print_summary(self, ranked_articles: list, output_path: str):
        """Affiche un résumé de la génération"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 RÉSUMÉ DE LA GÉNÉRATION")
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
        
        # Afficher les métriques API si disponibles
        if self.ai_processor and hasattr(self.ai_processor, 'metrics'):
            logger.info("\n" + "=" * 80)
            logger.info("📊 MÉTRIQUES API & OPTIMISATIONS")
            logger.info("=" * 80)
            self.ai_processor.metrics.print_summary()
            self.ai_processor.metrics.save_metrics()
        
        logger.info(f"\n📄 Fichier généré: {output_path}")
        logger.info(f"🌐 Ouvrir dans le navigateur: file://{os.path.abspath(output_path)}")


def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Générateur de newsletter Growth Weekly')
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
            shutil.rmtree(cache_dir)
            logger.info("🗑️  Cache effacé")
        os.makedirs(cache_dir, exist_ok=True)
    
    # Générer la newsletter
    generator = NewsletterGenerator()
    output_path = generator.run(use_cache=args.use_cache)
    
    print(f"\n✅ Newsletter générée avec succès!")
    print(f"📄 Fichier: {output_path}")
    print(f"🌐 Ouvrir: file://{os.path.abspath(output_path)}")


if __name__ == "__main__":
    main()
