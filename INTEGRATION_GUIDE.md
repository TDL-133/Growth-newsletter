# 🔧 Guide d'Intégration - Outils MCP & Optimisations

Ce guide explique comment activer toutes les optimisations développées lors des Sprints 1, 2 & 3.

## 📦 Nouveaux composants créés

```
scripts/
├── firecrawl_scraper.py    # Scraping MCP structuré (remplace web_scraper.py)
├── markdown_parser.py       # Extraction sans IA du markdown
├── tavily_searcher.py       # Recherche articles récents via Tavily
├── api_metrics.py           # Dashboard coûts & métriques
└── (existants)
    ├── gmail_scraper.py     # Scraping Gmail (déjà fonctionnel)
    ├── ai_processor.py      # Extraction & ranking IA
    ├── html_builder.py      # Génération HTML
    └── newsletter_generator.py  # Orchestrateur principal
```

---

## 🚀 ÉTAPE 1 : Activer Firecrawl MCP

### **1.1 Modifier `firecrawl_scraper.py`**

**Remplacer les placeholders** (lignes 44-57) par de vrais appels MCP :

```python
# AVANT (placeholder)
result = {
    "markdown": f"# Article from {source_name}\n\nContent placeholder...",
    "metadata": {"title": f"Article from {url}"}
}

# APRÈS (vrai appel MCP)
from warp_mcp import call_mcp_tool  # Importer le helper MCP

result = call_mcp_tool("firecrawl_scrape", {
    "url": url,
    "formats": ["markdown"],
    "onlyMainContent": True,
    "maxAge": 172800000  # Cache 48h pour performance
})
```

### **1.2 Remplacer `web_scraper` par `firecrawl_scraper`**

Dans `gmail_scraper.py` (ligne 22) :

```python
# AVANT
from scripts.web_scraper import WebScraper

# APRÈS
from scripts.firecrawl_scraper import FirecrawlScraper

# Puis ligne 47
self.web_scraper = FirecrawlScraper()  # au lieu de WebScraper()
```

---

## 🎯 ÉTAPE 2 : Intégrer le Parser Markdown

### **2.1 Modifier `ai_processor.py`**

Ajouter détection automatique du type de contenu :

```python
# Ajouter en haut du fichier
from scripts.markdown_parser import MarkdownParser

class AIProcessor:
    def __init__(self, config_path: str = "config/sources.yaml"):
        # ... existing code ...
        self.markdown_parser = MarkdownParser()  # Ajouter cette ligne
    
    def extract_articles_from_newsletter(self, email_content: str, source_name: str) -> List[Dict]:
        """Extrait les articles avec parsing intelligent"""
        
        # NOUVEAU : Détection et parsing sans IA si possible
        if self.markdown_parser.can_parse_without_ai(email_content, source_name):
            logger.info(f"  🚀 Parsing sans IA pour {source_name}")
            
            # Parser Markdown Firecrawl
            if '####' in email_content or '#####' in email_content:
                return self.markdown_parser.extract_articles_from_markdown(
                    email_content, source_name
                )
            
            # Parser Substack
            if 'substack' in source_name.lower() or 'class="post-title"' in email_content:
                return self.markdown_parser.extract_from_substack(
                    email_content, source_name
                )
        
        # FALLBACK : Extraction IA classique
        logger.info(f"  🤖 Extraction IA pour {source_name}")
        return self._extract_with_ai(email_content, source_name)
    
    def _extract_with_ai(self, email_content: str, source_name: str) -> List[Dict]:
        """Méthode existante renommée"""
        # Tout le code actuel d'extraction IA
        # (copier le contenu actuel de extract_articles_from_newsletter ici)
```

---

## 📊 ÉTAPE 3 : Activer le Tracking Métriques

### **3.1 Intégrer dans `ai_processor.py`**

```python
from scripts.api_metrics import APIMetrics

class AIProcessor:
    def __init__(self, config_path: str = "config/sources.yaml"):
        # ... existing code ...
        self.metrics = APIMetrics()  # Ajouter
    
    def extract_articles_from_newsletter(self, email_content: str, source_name: str) -> List[Dict]:
        # Après parsing sans IA
        if parsing_sans_ia_reussi:
            self.metrics.track_extraction_method('markdown_parser', len(articles))
            return articles
        
        # Après extraction IA
        articles = self._extract_with_ai(...)
        self.metrics.track_extraction_method('anthropic_ai', len(articles))
        return articles
    
    def _extract_with_ai(self, email_content: str, source_name: str) -> List[Dict]:
        message = self.client.messages.create(...)
        
        # TRACKER les tokens utilisés
        self.metrics.track_anthropic_call(
            input_tokens=message.usage.input_tokens,
            output_tokens=message.usage.output_tokens,
            purpose=f"Extraction: {source_name}"
        )
```

### **3.2 Afficher les métriques dans `newsletter_generator.py`**

À la fin du fichier :

```python
def main():
    # ... existing code ...
    
    # NOUVEAU : Afficher les métriques
    if hasattr(processor, 'metrics'):
        processor.metrics.print_summary()
        processor.metrics.save_metrics()
```

---

## 🔍 ÉTAPE 4 : Activer Tavily Search (Optionnel)

Pour enrichir les sources avec peu de contenu :

### **4.1 Modifier `tavily_searcher.py`**

Remplacer placeholder (lignes 54-82) :

```python
from warp_mcp import call_mcp_tool

result = call_mcp_tool("tavily-search", {
    "query": query,
    "max_results": max_results,
    "search_depth": "basic",
    "include_raw_content": False
})

articles = []
for tavily_result in result.get('results', []):
    articles.append({
        'source': source_name,
        'subject': f"Tavily: {tavily_result['title']}",
        'date': datetime.now().strftime('%Y-%m-%d'),
        'from': tavily_result['url'],
        'content': tavily_result['content'],
        'url': tavily_result['url'],
        'message_id': f'tavily_{hash(tavily_result["url"])}'
    })
```

### **4.2 Intégrer dans `newsletter_generator.py`**

```python
from scripts.tavily_searcher import TavilySearcher

# Après scraping Gmail/Web
tavily = TavilySearcher()

for source_name, emails in results.items():
    if len(emails) < 2:  # Source avec peu de contenu
        logger.info(f"🔍 Enrichissement {source_name} via Tavily")
        source_config = next(s for s in config['sources'] if s['name'] == source_name)
        additional = tavily.enrich_source_content(source_config, len(emails))
        results[source_name].extend(additional)
```

---

## 🎯 ÉTAPE 5 : Batching API Anthropic

Pour réduire de 70% les appels :

### **5.1 Modifier `ai_processor.py` - `process_all_emails()`**

**Remplacer** (lignes 190-218) :

```python
# AVANT : 1 appel par email
for email in emails:
    articles = self.extract_articles_from_newsletter(
        email['content'],
        source_name
    )

# APRÈS : 1 appel par source
all_emails_content = "\n\n=== EMAIL SEPARATOR ===\n\n".join([
    f"Email from {email.get('date', 'N/A')}:\n{email['content']}"
    for email in emails
])

articles = self.extract_articles_from_newsletter(
    all_emails_content,
    source_name
)
```

---

## ✅ ÉTAPE 6 : Test Complet

### **6.1 Commande de test**

```bash
cd "/Users/lopato/Documents/DAGORSEY/Geek/test-new-stuff/Revue de presse growth fr"
source venv/bin/activate

# Nettoyer le cache
rm cache/articles.json cache/ranked_articles.json

# Générer avec nouveaux outils
python scripts/newsletter_generator.py --use-cache
```

### **6.2 Vérifier les métriques**

```bash
# Afficher les métriques sauvegardées
python -c "
import json
with open('metrics/api_costs.json', 'r') as f:
    metrics = json.load(f)[-1]  # Dernière session

print(f\"Coût total: \${metrics['costs']['total_cost']:.4f}\")
print(f\"Optimisation: {metrics['optimization']['optimization_rate']:.1f}% sans IA\")
"
```

---

## 📊 Résultats Attendus

### **Avant optimisation**
```
📊 MÉTRIQUES:
- Appels API Anthropic: 10-12
- Coût: ~$0.038/newsletter
- Extraction: 100% via IA
```

### **Après optimisation**
```
📊 MÉTRIQUES:
- Appels API Anthropic: 2-3
- Coût: ~$0.007/newsletter (-82%)
- Extraction: 60-70% sans IA
```

---

## 🐛 Troubleshooting

### **Erreur : Module 'warp_mcp' not found**

Si l'import MCP ne fonctionne pas, utiliser directement dans Warp :
```python
# Les outils MCP sont déjà disponibles dans l'environnement Warp
# Pas besoin d'import spécial
```

### **Firecrawl retourne du contenu vide**

Vérifier que l'URL est accessible :
```python
result = call_mcp_tool("firecrawl_scrape", {
    "url": url,
    "formats": ["markdown", "html"],  # Essayer les deux formats
    "onlyMainContent": False  # Désactiver le filtrage si problème
})
```

### **Markdown parser ne trouve rien**

Ajuster les regex dans `markdown_parser.py` selon la structure réelle :
```python
# Logger le contenu pour debug
logger.debug(f"Content structure: {markdown_content[:500]}")
```

---

## 🎯 Ordre d'Implémentation Recommandé

1. **Étape 3** (Métriques) - Pour mesurer l'impact
2. **Étape 1** (Firecrawl) - Plus grosse amélioration qualité
3. **Étape 2** (Parser) - Économie API immédiate
4. **Étape 5** (Batching) - Optimisation supplémentaire
5. **Étape 4** (Tavily) - Bonus si besoin

---

## 📝 Checklist d'Intégration

- [ ] Firecrawl MCP activé dans `firecrawl_scraper.py`
- [ ] `web_scraper` remplacé par `firecrawl_scraper`
- [ ] Markdown parser intégré dans `ai_processor.py`
- [ ] Métriques API tracking activé
- [ ] Batching API implémenté
- [ ] Test complet de génération
- [ ] Vérification des coûts dans `metrics/api_costs.json`
- [ ] Commit sur GitHub

---

## 💡 Notes Importantes

- **Les outils MCP sont déjà disponibles dans Warp** - Pas besoin d'installation
- **Firecrawl inclut cache automatique** - Pas de surcoût pour re-scrapings
- **Le markdown parser est 100% local** - Zéro coût API
- **Les métriques sont sauvegardées** - Historique complet des optimisations

---

## 🚀 Next Steps

Après intégration complète :

1. **Tester sur 2-3 générations** pour valider les économies
2. **Ajuster les regex** du markdown parser si nécessaire
3. **Documenter les patterns** de sources problématiques
4. **Automatiser** la génération hebdomadaire

---

**Questions ? Besoin d'aide pour une étape spécifique ?**
