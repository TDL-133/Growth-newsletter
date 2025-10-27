#!/usr/bin/env python3
"""
Gmail Scraper - Récupère les newsletters depuis Gmail
"""

import os
import pickle
import base64
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from email.mime.text import MIMEText
import re

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup
import yaml
from scripts.web_scraper import WebScraper

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Scopes Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailScraper:
    """Scraper pour récupérer les newsletters depuis Gmail"""
    
    def __init__(self, config_path: str = "config/sources.yaml"):
        """
        Initialise le scraper Gmail
        
        Args:
            config_path: Chemin vers le fichier de configuration YAML
        """
        self.config = self._load_config(config_path)
        self.service = None
        self.web_scraper = WebScraper()  # Scraper web pour les fallbacks
        self._authenticate()
    
    def _load_config(self, config_path: str) -> Dict:
        """Charge la configuration depuis le fichier YAML"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _authenticate(self):
        """Authentifie avec Gmail API"""
        creds = None
        
        # Charger le token sauvegardé si disponible
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # Si pas de credentials valides, authentifier
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Créer le client_config depuis les variables d'environnement
                client_id = os.getenv('GMAIL_CLIENT_ID')
                client_secret = os.getenv('GMAIL_CLIENT_SECRET')
                
                if not client_id or not client_secret:
                    raise ValueError("GMAIL_CLIENT_ID et GMAIL_CLIENT_SECRET doivent être définis dans .env")
                
                client_config = {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "redirect_uris": ["http://localhost:8080"],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                }
                
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                creds = flow.run_local_server(port=8080)
            
            # Sauvegarder le token
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("✅ Authentification Gmail réussie")
    
    def _build_search_query(self, source: Dict, lookback_days: int) -> str:
        """
        Construit la requête de recherche Gmail pour une source
        
        Args:
            source: Configuration de la source
            lookback_days: Nombre de jours à rechercher en arrière
            
        Returns:
            Requête de recherche Gmail
        """
        # Date de début
        after_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y/%m/%d")
        
        # Construire la requête
        query_parts = []
        
        # From
        if 'gmail_from' in source:
            query_parts.append(f"from:{source['gmail_from']}")
        
        # Subject
        if 'gmail_subject_pattern' in source:
            query_parts.append(f'subject:"{source["gmail_subject_pattern"]}"')
        
        # Date
        query_parts.append(f"after:{after_date}")
        
        # Labels
        gmail_config = self.config.get('gmail_search', {})
        labels = gmail_config.get('labels', [])
        if labels:
            query_parts.append(f"in:{labels[0].lower()}")
        
        return " ".join(query_parts)
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """
        Extrait le texte d'un contenu HTML
        
        Args:
            html_content: Contenu HTML
            
        Returns:
            Texte extrait
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Supprimer les scripts et styles
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Récupérer le texte
        text = soup.get_text()
        
        # Nettoyer les espaces
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _get_message_content(self, message_id: str) -> Optional[str]:
        """
        Récupère le contenu d'un message Gmail
        
        Args:
            message_id: ID du message Gmail
            
        Returns:
            Contenu du message (texte ou HTML converti en texte)
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Récupérer le payload
            payload = message.get('payload', {})
            
            # Fonction récursive pour extraire le contenu
            def extract_parts(parts, mime_type='text/plain'):
                for part in parts:
                    if part.get('mimeType') == mime_type:
                        data = part.get('body', {}).get('data')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    
                    # Si le part a des sous-parties, les explorer
                    if 'parts' in part:
                        result = extract_parts(part['parts'], mime_type)
                        if result:
                            return result
                return None
            
            # Essayer d'abord text/plain
            content = extract_parts([payload], 'text/plain')
            
            # Si pas de text/plain, essayer text/html
            if not content:
                html_content = extract_parts([payload], 'text/html')
                if html_content:
                    content = self._extract_text_from_html(html_content)
            
            return content
            
        except HttpError as error:
            logger.error(f"Erreur lors de la récupération du message {message_id}: {error}")
            return None
    
    def scrape_source(self, source: Dict) -> List[Dict]:
        """
        Scrape une source de newsletter
        
        Args:
            source: Configuration de la source
            
        Returns:
            Liste des emails trouvés avec leur contenu
        """
        logger.info(f"📧 Scraping source: {source['name']}")
        
        gmail_config = self.config.get('gmail_search', {})
        lookback_days = gmail_config.get('lookback_days', 7)
        max_results = gmail_config.get('max_results_per_source', 5)
        
        # Construire la requête de recherche
        query = self._build_search_query(source, lookback_days)
        logger.debug(f"Query: {query}")
        
        try:
            # Rechercher les messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                logger.info(f"  ⚠️  Aucun message trouvé pour {source['name']}")
                # Essayer le fallback web
                logger.info(f"  🌐 Tentative de scraping web...")
                web_results = self.web_scraper.scrape_source(source)
                if web_results:
                    logger.info(f"  ✅ {len(web_results)} contenu(s) récupéré(s) via web scraping")
                    return web_results
                return []
            
            logger.info(f"  ✅ {len(messages)} message(s) trouvé(s)")
            
            # Récupérer le contenu de chaque message
            emails = []
            for msg in messages:
                content = self._get_message_content(msg['id'])
                if content:
                    # Récupérer les métadonnées
                    message = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['Subject', 'Date', 'From']
                    ).execute()
                    
                    headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}
                    
                    emails.append({
                        'source': source['name'],
                        'subject': headers.get('Subject', ''),
                        'date': headers.get('Date', ''),
                        'from': headers.get('From', ''),
                        'content': content,
                        'message_id': msg['id']
                    })
            
            return emails
            
        except HttpError as error:
            logger.error(f"Erreur lors du scraping de {source['name']}: {error}")
            return []
    
    def scrape_all_sources(self) -> Dict[str, List[Dict]]:
        """
        Scrape toutes les sources configurées
        
        Returns:
            Dictionnaire {nom_source: [emails]}
        """
        logger.info("🚀 Démarrage du scraping de toutes les sources...")
        
        results = {}
        sources = self.config.get('sources', [])
        
        for source in sources:
            emails = self.scrape_source(source)
            results[source['name']] = emails
        
        total_emails = sum(len(emails) for emails in results.values())
        logger.info(f"✅ Scraping terminé: {total_emails} emails récupérés de {len(results)} sources")
        
        return results


def main():
    """Fonction principale pour tester le scraper"""
    from dotenv import load_dotenv
    load_dotenv()
    
    scraper = GmailScraper()
    results = scraper.scrape_all_sources()
    
    # Afficher un résumé
    print("\n📊 Résumé du scraping:")
    print("=" * 50)
    for source, emails in results.items():
        print(f"{source}: {len(emails)} email(s)")
        for email in emails:
            print(f"  - {email['subject'][:60]}...")


if __name__ == "__main__":
    main()
