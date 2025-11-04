#!/usr/bin/env python3
"""
Script pour trouver les vraies adresses d'expéditeurs des newsletters dans Gmail
"""
import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from datetime import datetime, timedelta
from collections import Counter

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate():
    """Authentification Gmail"""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_id = os.getenv('GMAIL_CLIENT_ID')
            client_secret = os.getenv('GMAIL_CLIENT_SECRET')
            
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
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def search_newsletters(service, lookback_days=21):
    """Cherche les newsletters dans Gmail"""
    
    # Mots-clés à rechercher dans les sujets/expéditeurs
    keywords = [
        "growth", "marketing", "newsletter", "weekly", "substack",
        "demand curve", "elena verna", "kyle poyar", "tldr",
        "indie hackers", "sean ellis", "maja", "yann leonardi"
    ]
    
    after_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y/%m/%d")
    
    all_senders = Counter()
    emails_by_sender = {}
    
    print(f"🔍 Recherche des newsletters des {lookback_days} derniers jours...\n")
    
    for keyword in keywords:
        query = f'subject:"{keyword}" OR from:"{keyword}" after:{after_date}'
        
        try:
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=50
            ).execute()
            
            messages = results.get('messages', [])
            
            for msg in messages:
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['Subject', 'Date', 'From']
                ).execute()
                
                headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}
                from_addr = headers.get('From', '')
                subject = headers.get('Subject', '')
                
                # Extraire l'adresse email
                import re
                email_match = re.search(r'<(.+?)>', from_addr)
                if email_match:
                    email = email_match.group(1)
                else:
                    email = from_addr
                
                all_senders[email] += 1
                
                if email not in emails_by_sender:
                    emails_by_sender[email] = []
                emails_by_sender[email].append({
                    'subject': subject,
                    'date': headers.get('Date', '')
                })
        
        except Exception as e:
            continue
    
    return all_senders, emails_by_sender

def main():
    print("=" * 80)
    print("🔍 RECHERCHE DES NEWSLETTERS GROWTH MARKETING DANS GMAIL")
    print("=" * 80)
    print()
    
    service = authenticate()
    print("✅ Authentifié avec succès\n")
    
    senders, emails_by_sender = search_newsletters(service)
    
    if not senders:
        print("❌ Aucune newsletter trouvée avec les mots-clés recherchés")
        print("\n💡 Suggestions:")
        print("  - Vérifiez que vous recevez bien ces newsletters")
        print("  - Les newsletters sont peut-être dans SPAM")
        print("  - Essayez d'augmenter la période de recherche")
        return
    
    print("=" * 80)
    print(f"📊 RÉSULTATS: {len(senders)} expéditeurs uniques trouvés")
    print("=" * 80)
    print()
    
    print("📧 EXPÉDITEURS PAR FRÉQUENCE:\n")
    
    for sender, count in senders.most_common(30):
        print(f"   {count:3}x  {sender}")
        
        # Afficher quelques sujets
        if sender in emails_by_sender and len(emails_by_sender[sender]) <= 3:
            for email in emails_by_sender[sender][:3]:
                subject = email['subject'][:70]
                print(f"         └─ {subject}")
        print()
    
    print("=" * 80)
    print("💡 CONFIGURATION SUGGÉRÉE POUR sources.yaml:")
    print("=" * 80)
    print()
    print("Copiez ces adresses dans votre sources.yaml (champ gmail_from):")
    print()
    
    for sender, count in senders.most_common(20):
        if count >= 2:  # Seulement ceux qui envoient régulièrement
            print(f"gmail_from: \"{sender}\"")

if __name__ == "__main__":
    main()
