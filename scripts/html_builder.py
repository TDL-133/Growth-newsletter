#!/usr/bin/env python3
"""
HTML Builder - Génère le fichier HTML final de la newsletter
Version simplifiée sans JavaScript
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HTMLBuilder:
    """Générateur de newsletter HTML (version simple sans JS)"""
    
    def __init__(self, template_path: str = None):
        """Initialise le builder HTML"""
        pass
    
    def _get_week_date_range(self) -> str:
        """Calcule la plage de dates de la semaine passée"""
        today = datetime.now()
        end_date = today - timedelta(days=today.weekday() + 1)
        start_date = end_date - timedelta(days=6)
        
        if start_date.month == end_date.month:
            date_range = f"{start_date.day}-{end_date.day} {start_date.strftime('%B %Y')}"
        else:
            date_range = f"{start_date.strftime('%d %B')}-{end_date.strftime('%d %B %Y')}"
        
        months_fr = {
            'January': 'janvier', 'February': 'février', 'March': 'mars',
            'April': 'avril', 'May': 'mai', 'June': 'juin',
            'July': 'juillet', 'August': 'août', 'September': 'septembre',
            'October': 'octobre', 'November': 'novembre', 'December': 'décembre'
        }
        for en, fr in months_fr.items():
            date_range = date_range.replace(en, fr)
        
        return date_range
    
    def generate_html(self, articles: List[Dict], output_path: str = None) -> str:
        """Génère le fichier HTML de la newsletter"""
        logger.info("🎨 Génération du HTML de la newsletter...")
        
        # Organiser par catégorie
        by_cat = {'critical': [], 'important': [], 'good_to_know': []}
        for art in articles:
            cat = art.get('category', 'important')
            if cat in by_cat:
                by_cat[cat].append(art)
        
        # Date de la semaine
        date_range = self._get_week_date_range()
        
        # Sources uniques
        sources = sorted(set(a['source'] for a in articles))
        
        # Créer le HTML
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Growth Weekly Newsletter</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 900px; margin: 0 auto; padding: 40px 20px; line-height: 1.6; color: #111827; background: white; }}
        h1 {{ text-align: center; font-size: 2.8em; font-weight: 300; margin-bottom: 10px; }}
        .subtitle {{ text-align: center; color: #6b7280; font-style: italic; margin-bottom: 10px; font-size: 1.1em; }}
        .date {{ text-align: center; color: #9ca3af; margin-bottom: 40px; }}
        .divider {{ width: 4rem; height: 1px; background: #d1d5db; margin: 1rem auto 40px; }}
        .section {{ margin: 60px 0; }}
        .section h2 {{ font-size: 1.8em; font-weight: 400; margin-bottom: 10px; }}
        .section-divider {{ width: 3rem; height: 2px; margin-bottom: 30px; }}
        .critical h2 {{ color: #ef4444; }}
        .critical .section-divider {{ background: #ef4444; }}
        .important h2 {{ color: #f59e0b; }}
        .important .section-divider {{ background: #f59e0b; }}
        .good h2 {{ color: #10b981; }}
        .good .section-divider {{ background: #10b981; }}
        .article {{ margin: 40px 0; display: flex; gap: 24px; }}
        .article-num {{ font-size: 2em; font-weight: 300; min-width: 50px; margin-top: 4px; }}
        .critical .article-num {{ color: #ef4444; }}
        .important .article-num {{ color: #f59e0b; }}
        .good .article-num {{ color: #10b981; }}
        .article-content {{ flex: 1; }}
        .article-title {{ font-size: 1.3em; font-weight: 500; margin-bottom: 12px; line-height: 1.4; }}
        .article-title a {{ color: #111827; text-decoration: none; transition: color 0.2s; }}
        .article-title a:hover {{ color: #2563eb; }}
        .article-summary {{ color: #4b5563; margin-bottom: 12px; line-height: 1.6; }}
        .article-source {{ font-size: 0.9em; color: #9ca3af; }}
        .sources {{ margin-top: 80px; padding-top: 40px; border-top: 1px solid #e5e7eb; text-align: center; }}
        .sources-title {{ font-size: 0.95em; color: #6b7280; margin-bottom: 8px; }}
        .sources-list {{ font-size: 0.85em; color: #9ca3af; }}
        @media (max-width: 768px) {{
            body {{ padding: 20px 16px; }}
            h1 {{ font-size: 2em; }}
            .article {{ flex-direction: column; gap: 12px; }}
            .article-num {{ font-size: 1.5em; }}
            .section {{ margin: 40px 0; }}
        }}
    </style>
</head>
<body>
    <h1>Growth Weekly</h1>
    <p class="subtitle">by Dagorsey & Claude</p>
    <div class="divider"></div>
    <p class="date">{date_range}</p>
"""
        
        # Section Critical
        html += '<div class="section critical"><h2>Critical</h2><div class="section-divider"></div>\n'
        for art in by_cat['critical']:
            title = art['title'].replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
            summary = art['summary'].replace('<', '&lt;').replace('>', '&gt;')
            url = art.get('url') if art.get('url') else '#'
            html += f"""    <div class="article">
        <div class="article-num">{art['rank']:02d}</div>
        <div class="article-content">
            <div class="article-title"><a href="{url}" target="_blank">{title}</a></div>
            <div class="article-summary">{summary}</div>
            <div class="article-source">{art['source']}</div>
        </div>
    </div>\n"""
        html += '</div>\n'
        
        # Section Important
        html += '<div class="section important"><h2>Important</h2><div class="section-divider"></div>\n'
        for art in by_cat['important']:
            title = art['title'].replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
            summary = art['summary'].replace('<', '&lt;').replace('>', '&gt;')
            url = art.get('url') if art.get('url') else '#'
            html += f"""    <div class="article">
        <div class="article-num">{art['rank']:02d}</div>
        <div class="article-content">
            <div class="article-title"><a href="{url}" target="_blank">{title}</a></div>
            <div class="article-summary">{summary}</div>
            <div class="article-source">{art['source']}</div>
        </div>
    </div>\n"""
        html += '</div>\n'
        
        # Section Good to Know
        html += '<div class="section good"><h2>Good to Know</h2><div class="section-divider"></div>\n'
        for art in by_cat['good_to_know']:
            title = art['title'].replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
            summary = art['summary'].replace('<', '&lt;').replace('>', '&gt;')
            url = art.get('url') if art.get('url') else '#'
            html += f"""    <div class="article">
        <div class="article-num">{art['rank']:02d}</div>
        <div class="article-content">
            <div class="article-title"><a href="{url}" target="_blank">{title}</a></div>
            <div class="article-summary">{summary}</div>
            <div class="article-source">{art['source']}</div>
        </div>
    </div>\n"""
        html += '</div>\n'
        
        # Sources
        html += f"""    <div class="sources">
        <div class="sources-title">Sources utilisées cette semaine :</div>
        <div class="sources-list">{' • '.join(sources)}</div>
    </div>
</body>
</html>"""
        
        # Déterminer le chemin de sortie
        if not output_path:
            os.makedirs('output/newsletters', exist_ok=True)
            filename = f"growth-weekly-{datetime.now().strftime('%Y-%m-%d')}.html"
            output_path = os.path.join('output/newsletters', filename)
        
        # Sauvegarder
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"✅ Newsletter HTML générée: {output_path}")
        return output_path


def main():
    """Fonction de test"""
    test_articles = [
        {'rank': 1, 'title': 'Test Article', 'summary': 'Résumé test', 'category': 'critical', 'source': 'Test', 'url': None}
    ]
    builder = HTMLBuilder()
    output = builder.generate_html(test_articles)
    print(f"\n✅ Newsletter test: {output}")


if __name__ == "__main__":
    main()
