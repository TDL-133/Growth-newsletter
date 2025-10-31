#!/usr/bin/env python3
"""
AI Processor - Traite les newsletters avec Claude (Anthropic API)
Résume, traduit et catégorise les articles
"""

import os
import logging
import json
from typing import List, Dict, Optional
from anthropic import Anthropic
import yaml
from scripts.markdown_parser import MarkdownParser
from scripts.api_metrics import APIMetrics

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIProcessor:
    """Processeur IA pour analyser et résumer les newsletters"""
    
    def __init__(self, config_path: str = "config/sources.yaml"):
        """
        Initialise le processeur IA
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config = self._load_config(config_path)
        
        # Initialiser le client Anthropic
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY doit être défini dans .env")
        
        self.client = Anthropic(api_key=api_key)
        
        # Nouveaux composants
        self.markdown_parser = MarkdownParser()
        self.metrics = APIMetrics()
        
        logger.info("✅ Client Anthropic initialisé avec markdown parser & métriques")
    
    def _load_config(self, config_path: str) -> Dict:
        """Charge la configuration depuis le fichier YAML"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def extract_articles_from_newsletter(self, email_content: str, source_name: str) -> List[Dict]:
        """
        Extrait les articles individuels d'une newsletter avec parsing intelligent
        
        Args:
            email_content: Contenu complet de l'email
            source_name: Nom de la source
            
        Returns:
            Liste d'articles extraits
        """
        logger.info(f"🤖 Extraction des articles de {source_name}...")
        
        # NOUVEAU: Détection et parsing sans IA si possible
        if self.markdown_parser.can_parse_without_ai(email_content, source_name):
            logger.info(f"  🚀 Parsing sans IA pour {source_name}")
            
            # Parser Markdown Firecrawl
            if '####' in email_content or '#####' in email_content:
                articles = self.markdown_parser.extract_articles_from_markdown(
                    email_content, source_name
                )
                if articles:
                    self.metrics.track_extraction_method('markdown_parser', len(articles))
                    return articles
            
            # Parser Substack
            if 'substack' in source_name.lower() or 'class="post-title"' in email_content:
                articles = self.markdown_parser.extract_from_substack(
                    email_content, source_name
                )
                if articles:
                    self.metrics.track_extraction_method('markdown_parser', len(articles))
                    return articles
        
        # FALLBACK: Extraction IA classique
        logger.info(f"  🤖 Extraction IA pour {source_name}")
        return self._extract_with_ai(email_content, source_name)
    
    def _extract_with_ai(self, email_content: str, source_name: str) -> List[Dict]:
        """
        Méthode d'extraction IA (renommée de l'ancienne extract_articles_from_newsletter)
        
        Args:
            email_content: Contenu complet de l'email
            source_name: Nom de la source
            
        Returns:
            Liste d'articles extraits par IA
        """
        
        prompt = f"""Tu es un expert en analyse de newsletters de growth marketing.

Analysez cette newsletter de \"{source_name}\" et extrayez tous les articles/news individuels qu'elle contient.

Pour chaque article, identifiez :
1. Le titre de l'article (1 ligne maximum - 80 caractères max)
2. Un résumé ULTRA COURT (2 lignes max = 160 caractères max)
3. L'URL COMPLÈTE et PRÉCISE de l'article (CRITIQUE: cherchez attentivement dans le contenu)
4. Le niveau d'importance (critical, important, good_to_know)

🔴 CONTRAINTE CRITIQUE - LONGUEUR DU RÉSUMÉ 🔴
- MAXIMUM 160 caractères pour le résumé (2 lignes)
- Soyez CONCIS et DIRECT
- Éliminez tout mot superflu
- Allez à l'essentiel

Newsletter à analyser :
{email_content[:10000]}

IMPORTANT pour les URLs:
- Cherchez les liens HTTP/HTTPS dans le contenu
- Préférez les URLs complètes (https://example.com/article-title)
- Si vous trouvez un lien court, utilisez-le
- Si vraiment aucun lien n'existe, mettez null

Réponds UNIQUEMENT avec un JSON valide :
{{
  "articles": [
    {{
      "title": "Titre court (max 80 car.)",
      "summary": "Résumé ultra court max 160 caractères.",
      "url": "https://example.com/article-complet",
      "category": "critical|important|good_to_know"
    }}
  ]
}}

Classe les articles par importance (critical pour les plus importants).
RAPPEL: summary MAX 160 caractères !
"""
        
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extraire le JSON de la réponse
            response_text = message.content[0].text
            
            # Nettoyer la réponse (enlever les ``` si présents)
            response_text = response_text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parser le JSON
            data = json.loads(response_text)
            articles = data.get('articles', [])
            
            # Tracker les métriques API
            self.metrics.track_anthropic_call(
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
                purpose=f"Extraction: {source_name}"
            )
            self.metrics.track_extraction_method('anthropic_ai', len(articles))
            
            logger.info(f"  ✅ {len(articles)} article(s) extrait(s) par IA")
            return articles
            
        except Exception as e:
            logger.error(f"  ❌ Erreur lors de l'extraction: {e}")
            return []
    
    def translate_to_french(self, text: str) -> str:
        """
        Traduit un texte en français
        
        Args:
            text: Texte à traduire
            
        Returns:
            Texte traduit
        """
        if not text or len(text.strip()) == 0:
            return text
        
        prompt = f"""Traduis ce texte en français de manière naturelle et fluide.
Conserve le ton professionnel du growth marketing.
Ne traduis que le texte, sans ajouter de commentaires.

Texte à traduire :
{text}
"""
        
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Erreur lors de la traduction: {e}")
            return text  # Retourner le texte original en cas d'erreur
    
    def process_all_emails(self, emails_by_source: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Traite tous les emails et extrait les articles
        
        Args:
            emails_by_source: Dictionnaire {source: [emails]}
            
        Returns:
            Liste consolidée d'articles traités
        """
        logger.info("🚀 Traitement de tous les emails avec l'IA...")
        
        all_articles = []
        
        for source_name, emails in emails_by_source.items():
            if not emails:
                continue
            
            logger.info(f"📰 Traitement de {source_name} ({len(emails)} email(s))")
            
            # Traiter chaque email
            for email in emails:
                articles = self.extract_articles_from_newsletter(
                    email['content'],
                    source_name
                )
                
                # Ajouter les métadonnées de source
                for article in articles:
                    article['source'] = source_name
                    article['email_date'] = email.get('date', '')
                    
                    # Traduire en français si nécessaire
                    if not self._is_french(article['title']):
                        article['title'] = self.translate_to_french(article['title'])
                    
                    if not self._is_french(article['summary']):
                        article['summary'] = self.translate_to_french(article['summary'])
                    
                    # VALIDATION: Tronquer le titre et le résumé s'ils sont trop longs
                    if len(article['title']) > 80:
                        article['title'] = article['title'][:77] + '...'
                        logger.warning(f"  ⚠️  Titre tronqué pour {source_name}")
                    
                    if len(article['summary']) > 160:
                        article['summary'] = article['summary'][:157] + '...'
                        logger.warning(f"  ⚠️  Résumé tronqué pour {source_name}")
                    
                    all_articles.append(article)
        
        logger.info(f"✅ Traitement terminé: {len(all_articles)} articles extraits au total")
        
        return all_articles
    
    def _is_french(self, text: str) -> bool:
        """
        Détecte si un texte est en français (heuristique simple)
        
        Args:
            text: Texte à analyser
            
        Returns:
            True si le texte semble être en français
        """
        # Mots français courants
        french_words = ['le', 'la', 'les', 'de', 'des', 'un', 'une', 'et', 'ou', 'pour', 'dans', 'sur', 'avec']
        
        text_lower = text.lower()
        french_count = sum(1 for word in french_words if f' {word} ' in f' {text_lower} ')
        
        # Si au moins 2 mots français trouvés, considérer comme français
        return french_count >= 2
    
    def rank_and_categorize(self, articles: List[Dict]) -> List[Dict]:
        """
        Classe et catégorise les articles par importance
        
        Args:
            articles: Liste des articles
            
        Returns:
            Liste des articles classés avec rang
        """
        logger.info("🎯 Classement et catégorisation des articles...")
        
        # Créer un prompt pour classer tous les articles
        articles_text = "\n\n".join([
            f"Article {i+1}:\n"
            f"Source: {art['source']}\n"
            f"Titre: {art['title']}\n"
            f"Résumé: {art['summary']}\n"
            f"Catégorie suggérée: {art.get('category', 'important')}"
            for i, art in enumerate(articles)
        ])
        
        balancing_config = self.config.get('balancing', {})
        min_total = balancing_config.get('min_articles_total', 25)
        
        # Compter les articles par source
        source_articles = {}
        for i, art in enumerate(articles):
            source = art['source']
            if source not in source_articles:
                source_articles[source] = []
            source_articles[source].append(i)
        
        sources_list = "\n".join([
            f"  - {source}: {len(indices)} articles disponibles"
            for source, indices in source_articles.items()
        ])
        
        # Calculer le nombre cible d'articles à sélectionner
        target_per_source = 2
        expected_total = min(sum(min(len(indices), target_per_source) for indices in source_articles.values()), min_total)
        
        prompt = f"""Tu es un expert en growth marketing chargé de sélectionner et classer les actualités les plus importantes pour une newsletter hebdomadaire française.

Voici {len(articles)} articles extraits de {len(source_articles)} sources différentes:
{sources_list}

🚨 CONTRAINTE ABSOLUE - ÉQUILIBRAGE STRICT PAR SOURCE 🚨

PROCÉDURE OBLIGATOIRE (à suivre dans cet ordre précis):

1️⃣ PHASE DE SÉLECTION PAR SOURCE:
   Pour CHAQUE source listée ci-dessus:
   a) Identifie les 2 meilleurs articles de cette source
   b) Si la source a moins de 2 articles, prends tous ses articles
   c) AUCUNE source ne doit être exclue de la sélection
   
2️⃣ PHASE DE CLASSEMENT GLOBAL:
   Une fois que tu as exactement 2 articles par source (ou moins si impossible):
   a) Classe TOUS ces articles par ordre d'importance (1 = le plus important)
   b) Assigne les catégories:
      - "critical" (rangs 1-8) : News critiques, game-changing
      - "important" (rangs 9-16) : News importantes à connaître
      - "good_to_know" (rangs 17+) : News intéressantes

⚠️ VÉRIFICATIONS FINALES REQUISES:
- Tu dois avoir sélectionné environ {expected_total} articles au total
- TOUTES les {len(source_articles)} sources doivent être représentées
- Chaque source doit avoir 2 articles (sauf si elle en a moins de 2)

Articles à classer :
{articles_text[:15000]}

Réponds UNIQUEMENT avec un JSON valide :
{{
  "ranked_articles": [
    {{
      "article_index": 0,
      "rank": 1,
      "category": "critical",
      "source": "nom_de_la_source",  // OBLIGATOIRE pour vérification
      "reason": "Raison courte"
    }}
  ]
}}

ATTENTION: Si tu exclus une source de ta sélection, tu as échoué cette tâche.
"""
        
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parser la réponse
            response_text = message.content[0].text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            data = json.loads(response_text)
            ranked_data = data.get('ranked_articles', [])
            
            # Appliquer les rangs aux articles
            ranked_articles = []
            for rank_info in ranked_data:
                idx = rank_info['article_index']
                if 0 <= idx < len(articles):
                    article = articles[idx].copy()
                    article['rank'] = rank_info['rank']
                    article['category'] = rank_info['category']
                    article['ranking_reason'] = rank_info.get('reason', '')
                    ranked_articles.append(article)
            
            # Trier par rang
            ranked_articles.sort(key=lambda x: x['rank'])
            
            # VALIDATION: Forcer max 2 articles par source
            source_count = {}
            final_articles = []
            for art in ranked_articles:
                source = art['source']
                count = source_count.get(source, 0)
                if count < 2:  # Max 2 par source
                    final_articles.append(art)
                    source_count[source] = count + 1
                else:
                    logger.warning(f"  ⚠️  Article de {source} ignoré (déjà 2 articles)")
            
            # Si on a moins de min_total, compléter avec les articles ignorés
            if len(final_articles) < min_total:
                remaining = [a for a in ranked_articles if a not in final_articles]
                final_articles.extend(remaining[:min_total - len(final_articles)])
            
            logger.info(f"✅ {len(final_articles)} articles classés ({len(set(a['source'] for a in final_articles))} sources)")
            
            return final_articles
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du classement: {e}")
            # Fallback: retourner les articles avec un classement basique
            for i, article in enumerate(articles[:min_total]):
                article['rank'] = i + 1
                if i < 8:
                    article['category'] = 'critical'
                elif i < 16:
                    article['category'] = 'important'
                else:
                    article['category'] = 'good_to_know'
            
            return articles[:min_total]


def main():
    """Fonction de test"""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test avec un exemple
    processor = AIProcessor()
    
    test_email = {
        'content': """
        Top 5 Growth Tactics This Week
        
        1. New SEO Algorithm Update
        Google announced a major update to its search algorithm focusing on E-E-A-T.
        Read more: https://example.com/seo-update
        
        2. Viral Marketing Case Study
        How Duolingo increased user acquisition by 300% using TikTok.
        More info: https://example.com/duolingo
        """,
        'date': '2025-01-20'
    }
    
    articles = processor.extract_articles_from_newsletter(test_email['content'], 'Test Source')
    print(f"\n✅ Articles extraits: {len(articles)}")
    for art in articles:
        print(f"  - {art['title']}")


if __name__ == "__main__":
    main()
