# Architecture d'Automatisation - Growth Weekly

## 🎯 Vue d'ensemble

Ce document décrit l'architecture complète du système d'automatisation pour générer la newsletter Growth Weekly hebdomadaire en français.

---

## 📁 Structure du Projet (Proposée)

```
Growth-newsletter/
├── 📄 ARCHITECTURE.md           # Ce fichier
├── 📄 WARP.md                   # Documentation pour Warp
├── 📄 README.md                 # Guide utilisateur
├── 📄 requirements.txt          # Dépendances Python
├── 📄 .env.example              # Template variables d'environnement
├── 📄 .gitignore                # Fichiers à ignorer
│
├── 📁 config/
│   ├── sources.json             # Configuration des 13+ sources
│   └── prompts.json             # Prompts IA pour résumé/traduction
│
├── 📁 scripts/
│   ├── newsletter_generator.py  # Script principal
│   ├── scraper.py              # Module de scraping
│   ├── ai_processor.py         # Traitement IA (résumé/traduction)
│   └── html_builder.py         # Génération HTML
│
├── 📁 templates/
│   └── newsletter_template.html # Template HTML
│
├── 📁 output/
│   └── newsletters/            # Newsletters générées (git ignored)
│
└── 📁 .github/
    └── workflows/
        └── weekly_newsletter.yml # GitHub Actions (optionnel)
```

---

## 🔄 Flux de Travail (Workflow)

### Étape 1: Collecte des Sources
```
[13+ Sources Growth] 
    ↓
[Scraper Module]
    ↓
[Données brutes JSON]
```

**Comment ça marche:**
- Le script lit `config/sources.json`
- Pour chaque source, il utilise les MCP tools disponibles:
  - `firecrawl_scrape` pour les pages web
  - `tavily-search` pour rechercher du contenu récent
  - `fetch` comme fallback
- Collecte les articles publiés dans les 7 derniers jours
- Sauvegarde en JSON: `{url, title, content, source, date}`

### Étape 2: Traitement IA
```
[Données brutes]
    ↓
[AI Processor]
    ↓
[Articles résumés + traduits + catégorisés]
```

**Comment ça marche:**
- Pour chaque article collecté:
  1. **Résumé**: Génère un résumé de 2 lignes en français
  2. **Catégorisation**: Détermine si c'est Critique/Important/Bon à Savoir
  3. **Scoring**: Attribue un score d'importance (1-10)
- Utilise des prompts optimisés pour cohérence
- Retourne un JSON structuré

### Étape 3: Curation & Équilibrage
```
[Articles traités]
    ↓
[Balance Algorithm]
    ↓
[25+ articles équilibrés par source]
```

**Comment ça marche:**
- Trie par score d'importance
- Assure représentation équilibrée des sources (algorithme de distribution)
- Sélectionne top 25+ articles
- Répartit: 8 Critique, 8 Important, 9+ Bon à Savoir

### Étape 4: Génération HTML
```
[Articles finaux]
    ↓
[HTML Builder]
    ↓
[Newsletter complète growth-weekly-YYYY-MM-DD.html]
```

**Comment ça marche:**
- Charge le template HTML
- Injecte les données dans la structure JavaScript
- Génère le footer avec les sources utilisées
- Sauvegarde dans `output/newsletters/`

---

## 🔧 Modules Détaillés

### 1️⃣ `newsletter_generator.py` (Script Principal)

```python
# Pseudo-code de fonctionnement

def main():
    # Configuration
    sources = load_config('config/sources.json')
    end_date = get_last_week_end_date()
    
    # Étape 1: Scraping
    print("📥 Collecte des sources...")
    raw_articles = scrape_all_sources(sources, days=7)
    save_json(raw_articles, 'cache/raw_articles.json')
    
    # Étape 2: Traitement IA
    print("🤖 Traitement IA...")
    processed = ai_process_articles(raw_articles)
    save_json(processed, 'cache/processed_articles.json')
    
    # Étape 3: Curation
    print("⚖️ Équilibrage des sources...")
    curated = balance_sources(processed, min_items=25)
    
    # Étape 4: Génération
    print("📰 Génération HTML...")
    html = generate_newsletter(curated, end_date)
    save_html(html, f'output/newsletters/growth-weekly-{end_date}.html')
    
    print("✅ Newsletter générée!")
    return html
```

**Arguments de ligne de commande:**
```bash
python scripts/newsletter_generator.py \
    --end-date 2025-10-26 \
    --min-articles 25 \
    --output output/newsletters/ \
    --dry-run  # Mode test sans génération finale
```

### 2️⃣ `scraper.py` (Module de Scraping)

```python
class NewsletterScraper:
    """
    Gère le scraping de toutes les sources configurées
    """
    
    def __init__(self, sources_config):
        self.sources = sources_config
        self.mcp_tools = initialize_mcp_tools()
    
    def scrape_source(self, source):
        """
        Scrape une source individuelle
        
        Args:
            source: {
                "name": "Kyle Poyar",
                "type": "substack",
                "url": "https://www.growthunhinged.com",
                "method": "firecrawl_scrape"
            }
        
        Returns:
            List of articles with metadata
        """
        if source['method'] == 'firecrawl_scrape':
            return self._scrape_with_firecrawl(source)
        elif source['method'] == 'tavily-search':
            return self._search_with_tavily(source)
        else:
            return self._scrape_with_fetch(source)
    
    def scrape_all_sources(self, days=7):
        """
        Scrape toutes les sources en parallèle
        """
        # Utilise ThreadPoolExecutor pour parallélisation
        # Retourne tous les articles des 7 derniers jours
```

**Stratégies par type de source:**
- **Substack** (Kyle, Elena, etc.): `firecrawl_scrape` sur page d'archive
- **Blogs** (Demand Curve): `tavily-search` avec filtres de date
- **Newsletters email**: Instructions pour intégration Gmail API (optionnel)

### 3️⃣ `ai_processor.py` (Traitement IA)

```python
class AIProcessor:
    """
    Traite les articles avec IA pour résumé, traduction et catégorisation
    """
    
    def process_article(self, article):
        """
        Traite un article individuel
        
        Input:
            {
                "url": "...",
                "title": "Your pricing is broken",
                "content": "In just the past few weeks...",
                "source": "Kyle Poyar"
            }
        
        Output:
            {
                "url": "...",
                "title_fr": "Votre pricing est cassé",
                "summary_fr": "Kyle Poyar démontre...",
                "category": "critical",
                "score": 9.2,
                "source": "Kyle Poyar / Growth Unhinged"
            }
        """
        # 1. Résumé en français (2 lignes max)
        summary = self._generate_summary(article)
        
        # 2. Traduction du titre
        title = self._translate_title(article['title'])
        
        # 3. Catégorisation
        category, score = self._categorize(article, summary)
        
        return {
            'url': article['url'],
            'title_fr': title,
            'summary_fr': summary,
            'category': category,
            'score': score,
            'source': article['source']
        }
```

**Prompts utilisés:**

```json
{
  "summarize": {
    "system": "Tu es un expert en growth marketing. Résume cet article en français en 2 lignes maximum. Capture l'insight principal et son impact pratique.",
    "template": "Article: {title}\n\nContenu: {content}\n\nRésumé en français (2 lignes):"
  },
  
  "categorize": {
    "system": "Catégorise cet article de growth marketing selon son importance.",
    "template": "Titre: {title}\nRésumé: {summary}\n\nCatégorie (critical/important/good_to_know) + Score (1-10):"
  }
}
```

### 4️⃣ `html_builder.py` (Génération HTML)

```python
def generate_newsletter(articles, week_end_date):
    """
    Génère le HTML final de la newsletter
    
    Args:
        articles: Liste d'articles catégorisés et triés
        week_end_date: Date de fin de semaine (format YYYY-MM-DD)
    
    Returns:
        HTML string complet
    """
    # 1. Charge le template
    template = load_template('templates/newsletter_template.html')
    
    # 2. Organise par catégorie
    critical = [a for a in articles if a['category'] == 'critical'][:8]
    important = [a for a in articles if a['category'] == 'important'][:8]
    good_to_know = [a for a in articles if a['category'] == 'good_to_know'][:9]
    
    # 3. Génère le JavaScript data
    news_data = {
        'critical': critical,
        'important': important,
        'goodToKnow': good_to_know
    }
    
    # 4. Injecte dans le template
    html = template.replace(
        '/* NEWS_DATA_PLACEHOLDER */',
        f'const newsData = {json.dumps(news_data, ensure_ascii=False)};'
    )
    
    # 5. Met à jour les dates
    week_start = get_week_start_date(week_end_date)
    html = html.replace('{{WEEK_START}}', week_start)
    html = html.replace('{{WEEK_END}}', week_end_date)
    
    # 6. Génère le footer des sources
    sources_used = list(set([a['source'] for a in articles]))
    sources_html = '\n'.join([f'<li>• {s}</li>' for s in sorted(sources_used)])
    html = html.replace('{{SOURCES_LIST}}', sources_html)
    
    return html
```

---

## ⚙️ Configuration: `config/sources.json`

```json
{
  "sources": [
    {
      "name": "Kyle Poyar",
      "display_name": "Kyle Poyar / Growth Unhinged",
      "type": "substack",
      "url": "https://www.growthunhinged.com/archive",
      "scrape_method": "firecrawl_scrape",
      "priority": "high",
      "tags": ["pricing", "plg", "pls", "benchmarks"]
    },
    {
      "name": "Elena Verna",
      "display_name": "Elena Verna / Growth Scoop",
      "type": "substack",
      "url": "https://www.elenaverna.com/archive",
      "scrape_method": "firecrawl_scrape",
      "priority": "high",
      "tags": ["activation", "retention", "plg", "b2b"]
    },
    {
      "name": "Demand Curve",
      "display_name": "Demand Curve",
      "type": "blog",
      "url": "https://www.demandcurve.com/blog",
      "scrape_method": "firecrawl_scrape",
      "priority": "high",
      "tags": ["marketing", "growth-tactics", "conversion"]
    }
    // ... 10+ autres sources
  ],
  
  "scraping_config": {
    "lookback_days": 7,
    "max_articles_per_source": 5,
    "min_article_length": 500,
    "language_filter": ["en", "fr"]
  },
  
  "balance_rules": {
    "min_sources_represented": 10,
    "max_articles_per_source": 3,
    "total_articles": 25
  }
}
```

---

## 🔐 Variables d'Environnement: `.env`

```bash
# APIs pour scraping (MCP tools sont déjà configurés dans Warp)
ANTHROPIC_API_KEY=your_key_here  # Pour traitement IA via Claude

# Optionnel: Gmail API (pour scraper emails directement)
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_secret

# Configuration
OUTPUT_DIR=./output/newsletters
CACHE_DIR=./cache
LOG_LEVEL=INFO
```

---

## 🚀 Utilisation

### Mode Interactif (Recommandé pour débuter)
```bash
# Installation
pip install -r requirements.txt

# Génération interactive
python scripts/newsletter_generator.py --interactive

# Le script vous demandera:
# 1. Date de fin de semaine? [2025-10-26]
# 2. Nombre minimum d'articles? [25]
# 3. Mode test ou production? [test]
```

### Mode Automatique
```bash
# Génération pour la semaine dernière
python scripts/newsletter_generator.py --auto

# Génération avec date spécifique
python scripts/newsletter_generator.py --end-date 2025-10-26

# Mode dry-run (affiche résultats sans générer HTML)
python scripts/newsletter_generator.py --dry-run
```

### Sortie du script
```
📥 Collecte des sources (13 sources configurées)...
  ✓ Kyle Poyar: 3 articles trouvés
  ✓ Elena Verna: 2 articles trouvés
  ✓ Demand Curve: 4 articles trouvés
  ✓ Maja Voje: 2 articles trouvés
  ... (9+ autres sources)
  
  Total: 47 articles collectés

🤖 Traitement IA (résumé, traduction, catégorisation)...
  ⏳ Traitement de 47 articles... [████████████████] 100%
  ✓ 47/47 articles traités

⚖️ Équilibrage des sources...
  • Algorithme de distribution appliqué
  • 12 sources représentées
  • Maximum 3 articles par source respecté
  
  Sélection finale:
    - Critique: 8 articles
    - Important: 8 articles  
    - Bon à Savoir: 9 articles
  Total: 25 articles

📰 Génération HTML...
  ✓ Template chargé
  ✓ Données injectées
  ✓ Footer généré
  
  Fichier créé: output/newsletters/growth-weekly-2025-10-26.html

✅ Newsletter générée avec succès!

📊 Statistiques:
  - Articles collectés: 47
  - Articles utilisés: 25
  - Sources représentées: 12/13
  - Durée totale: 2m 34s
```

---

## 🎨 Algorithme d'Équilibrage des Sources

```python
def balance_sources(articles, min_items=25, max_per_source=3):
    """
    Assure une représentation équilibrée de toutes les sources
    
    Algorithme:
    1. Trie tous les articles par score (décroissant)
    2. Groupe par source
    3. Round-robin selection:
       - Pour chaque source (dans l'ordre de priorité)
       - Prend le meilleur article non encore sélectionné
       - Continue jusqu'à avoir min_items articles
    4. Respecte la contrainte max_per_source
    """
    selected = []
    source_counts = defaultdict(int)
    
    # Trie par score
    sorted_articles = sorted(articles, key=lambda x: x['score'], reverse=True)
    
    # Round-robin par source
    source_pool = group_by_source(sorted_articles)
    
    while len(selected) < min_items:
        for source in source_pool:
            if source_counts[source] < max_per_source:
                if article := get_next_article(source_pool[source]):
                    selected.append(article)
                    source_counts[source] += 1
    
    return selected
```

**Exemple de distribution:**
```
Kyle Poyar: ███ (3 articles)
Elena Verna: ███ (3 articles)
Demand Curve: ██ (2 articles)
Maja Voje: ██ (2 articles)
TLDR Marketing: ██ (2 articles)
Indie Hackers: ██ (2 articles)
Userpilot: ██ (2 articles)
... (autres sources)
```

---

## 🔄 Workflow Hebdomadaire Automatisé (Optionnel)

### GitHub Actions: `.github/workflows/weekly_newsletter.yml`

```yaml
name: Generate Weekly Newsletter

on:
  schedule:
    # Tous les lundis à 9h00 UTC (10h Paris)
    - cron: '0 9 * * 1'
  workflow_dispatch:  # Permet déclenchement manuel

jobs:
  generate:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Generate newsletter
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/newsletter_generator.py --auto
      
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: 'Newsletter: Growth Weekly for week ending ${{ env.WEEK_END }}'
          branch: newsletter/auto-${{ env.WEEK_END }}
          title: '📰 Growth Weekly - ${{ env.WEEK_END }}'
          body: |
            Newsletter générée automatiquement pour la semaine se terminant le ${{ env.WEEK_END }}.
            
            📊 Statistiques:
            - Articles collectés: ${{ env.STATS_COLLECTED }}
            - Articles sélectionnés: ${{ env.STATS_SELECTED }}
            - Sources représentées: ${{ env.STATS_SOURCES }}
            
            Merci de reviewer avant merge!
```

**Avantages:**
- ✅ Exécution automatique chaque lundi
- ✅ Crée une PR pour review avant publication
- ✅ Historique complet dans GitHub
- ✅ Peut être déclenché manuellement si besoin

---

## 📈 Améliorations Futures

### Phase 1 (Court terme)
- ✅ Cache intelligent (évite re-scraping)
- ✅ Logs détaillés avec timestamps
- ✅ Mode dry-run pour tests
- ✅ Validation des données avant génération

### Phase 2 (Moyen terme)
- 🔄 Dashboard web pour curation manuelle
- 🔄 Intégration Gmail API pour newsletters email
- 🔄 A/B testing des catégorisations
- 🔄 Analytics: tracking des clics/lectures

### Phase 3 (Long terme)
- 🚀 ML model pour catégorisation automatique
- 🚀 Détection automatique de nouvelles sources
- 🚀 Envoi email automatique (Mailchimp/SendGrid)
- 🚀 Archive publique avec search

---

## 🛠️ Dépendances: `requirements.txt`

```txt
# Core
python>=3.11

# Web scraping
requests>=2.31.0
beautifulsoup4>=4.12.0

# APIs
anthropic>=0.18.0  # Pour Claude API (résumés/traductions)
openai>=1.12.0     # Alternative si préféré

# Data processing
pandas>=2.2.0
python-dateutil>=2.8.2

# Configuration
python-dotenv>=1.0.0
pyyaml>=6.0.1

# Utils
tqdm>=4.66.0       # Progress bars
loguru>=0.7.0      # Better logging
```

---

## 🎓 Comment Commencer

1. **Lisez ce document** (vous y êtes ✅)
2. **Validez l'approche** - Est-ce que ça correspond à vos besoins?
3. **Je crée les fichiers** - Scripts Python + config + template
4. **Vous testez** - Génération de la première newsletter automatiquement
5. **Itérations** - On ajuste selon vos retours
6. **Automatisation** - GitHub Actions si souhaité

---

## 💡 Avantages de cette Architecture

✅ **Modulaire**: Chaque composant est indépendant  
✅ **Testable**: Mode dry-run pour valider avant génération  
✅ **Extensible**: Facile d'ajouter de nouvelles sources  
✅ **Maintenable**: Configuration centralisée en JSON  
✅ **Automatisable**: GitHub Actions ready  
✅ **Transparent**: Logs détaillés à chaque étape  

---

## ❓ Questions Fréquentes

**Q: Combien de temps prend la génération?**  
R: ~2-3 minutes pour scraper 13 sources et traiter 25 articles.

**Q: Ça coûte combien en API calls?**  
R: ~$0.20-0.30 par newsletter (coût Claude API pour résumés).

**Q: Peut-on personnaliser les catégories?**  
R: Oui, facilement dans `config/prompts.json`.

**Q: Comment ajouter une nouvelle source?**  
R: Un seul ajout dans `config/sources.json`.

**Q: Ça marche sans les MCP tools?**  
R: Oui, fallback sur `requests` + `BeautifulSoup` si besoin.

---

**Prêt pour que je crée tous les fichiers? 🚀**
