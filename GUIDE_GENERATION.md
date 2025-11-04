# Guide de Génération - Growth Weekly

## 🎯 Objectif
Générer une newsletter Growth Weekly professionnelle avec **vrais liens fonctionnels** et contenu réel.

## 📋 Prérequis

### Option 1 : Génération MCP (Recommandé - Liens Réels)
```bash
# Depuis Warp Terminal avec MCP activé
python3 scripts/newsletter_generator_mcp.py --clear-cache
```

**Avantages** :
- ✅ Liens 100% fonctionnels
- ✅ Contenu réel scraped via Firecrawl
- ✅ Recherche intelligente via Tavily
- ✅ Coût $0 (pas d'API Anthropic)

### Option 2 : Génération Manuelle (Contenu Curé)
Le fichier actuel `growth-weekly-2025-10-31-curated.html` contient :
- ✅ Structure professionnelle
- ✅ 25 articles bien rédigés
- ⚠️  URLs d'exemple (non fonctionnelles)

## 🔧 Pour obtenir de vrais liens

### Méthode 1 : Utiliser Warp MCP (Automatique)

Depuis Warp Terminal, demandez :
```
"Génère une Growth Weekly avec vrais liens en utilisant Firecrawl et Tavily"
```

L'agent Warp va :
1. Appeler `firecrawl_scrape` sur chaque source
2. Parser le markdown pour extraire les articles
3. Utiliser `tavily-search` pour compléter
4. Générer le HTML avec URLs réelles

### Méthode 2 : Scraping Python Direct

```bash
# Installer dépendances
pip install requests beautifulsoup4 lxml

# Collecter les articles réels
python3 scripts/collect_real_articles.py

# Générer la newsletter avec ces articles
python3 scripts/build_newsletter_from_real.py
```

### Méthode 3 : Curation Manuelle

1. Visitez manuellement les sources :
   - https://tldr.tech/marketing
   - https://www.demandcurve.com/blog
   - https://www.growthunhinged.com/
   - https://www.lennysnewsletter.com/
   - https://www.indiehackers.com/

2. Copiez les vrais liens d'articles

3. Éditez `output/newsletters/growth-weekly-2025-10-31-curated.html`

4. Remplacez les URLs d'exemple par les vraies

## 📊 Structure des Sources

### Sources Principales (avec URLs réelles)

| Source | URL Base | Fréquence |
|--------|----------|-----------|
| TLDR Marketing | https://tldr.tech/marketing | Daily |
| Demand Curve | https://www.demandcurve.com/blog | Weekly |
| Kyle Poyar | https://www.growthunhinged.com/ | Weekly |
| Elena Verna | https://elenaverna.substack.com/ | Weekly |
| Indie Hackers | https://www.indiehackers.com/ | Daily |
| Lenny's Newsletter | https://www.lennysnewsletter.com/ | Weekly |
| Maja Voje | https://maja.substack.com/ | Weekly |
| Yann Leonardi | https://lagrowthsemaine.substack.com/ | Weekly |

## 🚀 Workflow Recommandé

### Génération Hebdomadaire

```bash
# 1. Vider le cache
rm -rf cache/mcp_*.json

# 2. Lancer la génération MCP depuis Warp
# (l'agent fait les vrais appels Firecrawl/Tavily)

# 3. Vérifier le résultat
open output/newsletters/growth-weekly-$(date +%Y-%m-%d).html

# 4. Publier
# - Envoyer par email
# - Publier sur le site
# - Partager sur réseaux sociaux
```

## 🐛 Troubleshooting

### "Les liens ne fonctionnent pas"
**Cause** : Vous utilisez la version curée avec URLs d'exemple.
**Solution** : Lancez `newsletter_generator_mcp.py` depuis Warp avec MCP activé.

### "MCP tools not available"
**Cause** : Script lancé hors de Warp ou MCP non configuré.
**Solution** : 
1. Ouvrir Warp Terminal
2. Vérifier configuration MCP : `warp config mcp`
3. Relancer depuis Warp

### "Transport closed" errors
**Cause** : Outils MCP indisponibles en mode local.
**Solution** : Le script bascule automatiquement en mode simulation pour les tests locaux.

## 📝 Notes

- **Version Actuelle** : Template curé avec contenu professionnel mais liens d'exemple
- **Prochaine Étape** : Intégration complète avec vrais appels MCP pour URLs réelles
- **Alternative** : Utiliser `collect_real_articles.py` + édition manuelle du HTML

## 🎨 Personnalisation

Pour modifier le style :
```css
/* Fichier : output/newsletters/growth-weekly-*.html */
/* Section <style> en tête du HTML */

/* Couleurs des catégories */
.section-title { color: #d32f2f; }  /* Critique - Rouge */
.section-title.important { color: #f57c00; }  /* Important - Orange */
.section-title.good { color: #388e3c; }  /* Good to Know - Vert */
```

## 📧 Contact

Pour questions ou support :
- **Email** : [votre email]
- **GitHub** : [votre repo]

---

**Growth Weekly** · Généré avec ❤️ par Dagorsey & Claude
