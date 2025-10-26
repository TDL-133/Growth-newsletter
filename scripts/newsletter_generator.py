#!/usr/bin/env python3
"""
Growth Weekly Newsletter Generator
Génère automatiquement la newsletter Growth Weekly en français

Usage:
    python newsletter_generator.py --auto
    python newsletter_generator.py --end-date 2025-10-26
    python newsletter_generator.py --dry-run
"""

import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger.remove()
logger.add(sys.stderr, level=os.getenv('LOG_LEVEL', 'INFO'))
if log_file := os.getenv('LOG_FILE'):
    logger.add(log_file, rotation="10 MB")


def load_config(config_file='config/sources.json'):
    """Charge la configuration des sources"""
    config_path = Path(__file__).parent.parent / config_file
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_week_dates(end_date=None):
    """
    Calcule les dates de début et fin de semaine
    
    Args:
        end_date: Date de fin (format YYYY-MM-DD) ou None pour semaine dernière
    
    Returns:
        tuple: (start_date, end_date) as datetime objects
    """
    if end_date:
        end = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        # Dernière semaine complète (dimanche à samedi)
        today = datetime.now()
        days_since_sunday = (today.weekday() + 1) % 7
        end = today - timedelta(days=days_since_sunday + 1)
    
    start = end - timedelta(days=6)
    return start, end


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description='Génère la newsletter Growth Weekly'
    )
    parser.add_argument(
        '--end-date',
        help='Date de fin de semaine (YYYY-MM-DD)',
        type=str
    )
    parser.add_argument(
        '--min-articles',
        help='Nombre minimum d\'articles',
        type=int,
        default=25
    )
    parser.add_argument(
        '--output',
        help='Répertoire de sortie',
        type=str,
        default='output/newsletters'
    )
    parser.add_argument(
        '--dry-run',
        help='Mode test (n\'écrit pas le fichier final)',
        action='store_true'
    )
    parser.add_argument(
        '--interactive',
        help='Mode interactif',
        action='store_true'
    )
    parser.add_argument(
        '--auto',
        help='Mode automatique (semaine dernière)',
        action='store_true'
    )
    
    args = parser.parse_args()
    
    # Mode interactif
    if args.interactive:
        logger.info("🎯 Mode interactif activé")
        end_date_str = input("Date de fin de semaine (YYYY-MM-DD) [dernière semaine]: ").strip()
        args.end_date = end_date_str if end_date_str else None
        
        min_articles_str = input(f"Nombre minimum d'articles [{args.min_articles}]: ").strip()
        args.min_articles = int(min_articles_str) if min_articles_str else args.min_articles
        
        dry_run = input("Mode test? (o/N): ").strip().lower()
        args.dry_run = dry_run == 'o'
    
    # Calcul des dates
    start_date, end_date = get_week_dates(args.end_date)
    logger.info(f"📅 Génération pour la semaine: {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}")
    
    # Chargement de la configuration
    logger.info("📥 Chargement de la configuration...")
    config = load_config()
    enabled_sources = [s for s in config['sources'] if s.get('enabled', True)]
    logger.info(f"   {len(enabled_sources)} sources activées")
    
    # ===== ÉTAPE 1: SCRAPING =====
    logger.info("\n📥 Étape 1/4: Collecte des sources...")
    logger.info("   ⚠️  IMPORTANT: Cette version utilise un exemple de données")
    logger.info("   Pour scraper réellement, vous devez:")
    logger.info("   1. Configurer votre ANTHROPIC_API_KEY dans .env")
    logger.info("   2. Implémenter le module scraper.py avec les MCP tools")
    
    # Pour l'instant, utilisons les données de la newsletter existante comme exemple
    raw_articles = []
    logger.warning("   ⚠️  Mode exemple activé - Utilisation des données pré-existantes")
    
    # ===== ÉTAPE 2: TRAITEMENT IA =====
    logger.info("\n🤖 Étape 2/4: Traitement IA...")
    logger.info("   ⚠️  Cette étape nécessite l'API Claude (voir .env.example)")
    
    # Utiliser les données de la newsletter existante
    processed_articles = []
    
    # ===== ÉTAPE 3: ÉQUILIBRAGE =====
    logger.info("\n⚖️  Étape 3/4: Équilibrage des sources...")
    
    # ===== ÉTAPE 4: GÉNÉRATION HTML =====
    logger.info("\n📰 Étape 4/4: Génération HTML...")
    
    if args.dry_run:
        logger.info("   🔍 Mode dry-run: Pas de génération de fichier")
        logger.success("\n✅ Dry-run complété avec succès!")
        logger.info(f"\n📊 Résumé:")
        logger.info(f"   • Sources configurées: {len(enabled_sources)}")
        logger.info(f"   • Semaine: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
        logger.info(f"   • Articles minimum: {args.min_articles}")
    else:
        logger.info("   🚧 Pour générer réellement la newsletter:")
        logger.info("   1. Implémentez scraper.py avec les MCP tools")
        logger.info("   2. Implémentez ai_processor.py avec l'API Claude")
        logger.info("   3. Configurez votre .env avec ANTHROPIC_API_KEY")
        logger.info("\n   📖 Consultez ARCHITECTURE.md pour plus de détails")
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Interruption par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"❌ Erreur: {e}")
        sys.exit(1)
