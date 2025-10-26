# 📰 Growth Weekly - Newsletter Automation

Newsletter hebdomadaire française automatisée sur le growth marketing et les stratégies SaaS.

## 🎯 Qu'est-ce que c'est?

Growth Weekly est une newsletter qui agrège et résume automatiquement les meilleures actualités growth marketing de 13+ sources premium:

- **Kyle Poyar** (Growth Unhinged) - Pricing, PLG, PLS
- **Elena Verna** (Growth Scoop) - Activation, rétention, B2B
- **Demand Curve** - Tactiques marketing, conversion
- **Maja Voje, Timothe Frin, Kate Syuma, Sean Ellis, Indie Hackers** et plus...

## ✨ Fonctionnalités

- ✅ **Scraping automatique** de 13+ sources growth marketing
- ✅ **Traduction IA** de l'anglais vers le français
- ✅ **Catégorisation intelligente** (Critique / Important / Bon à Savoir)
- ✅ **Équilibrage des sources** pour représentation équitable
- ✅ **Génération HTML** responsive et élégante
- ✅ **Mode interactif** et automatique

## 📁 Structure du Projet

```
Growth-newsletter/
├── config/
│   ├── sources.json          # Configuration des sources
│   └── prompts.json           # Prompts IA
├── scripts/
│   ├── newsletter_generator.py  # Script principal  
│   ├── scraper.py             # Module scraping (à implémenter)
│   ├── ai_processor.py        # Traitement IA (à implémenter)
│   └── html_builder.py        # Génération HTML (à implémenter)
├── templates/
│   └── newsletter_template.html
├── output/newsletters/        # Newsletters générées
├── cache/                     # Cache des données
├── ARCHITECTURE.md            # Documentation technique
├── WARP.md                    # Guide pour Warp AI
└── requirements.txt           # Dépendances Python
```

## 🚀 Installation

### Prérequis

- Python 3.11 ou supérieur
- pip (gestionnaire de paquets Python)
- Compte Anthropic (Claude API) pour le traitement IA

### Étape 1: Cloner le repo

```bash
git clone https://github.com/TDL-133/Growth-newsletter.git
cd Growth-newsletter
```

### Étape 2: Créer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\Scripts\activate  # Sur Windows
```

### Étape 3: Installer les dépendances

```bash
pip install -r requirements.txt
```

### Étape 4: Configuration

Copiez `.env.example` vers `.env` et ajoutez votre clé API:

```bash
cp .env.example .env
```

Éditez `.env` et ajoutez votre clé Anthropic:

```bash
ANTHROPIC_API_KEY=your_key_here
```

## 📖 Utilisation

### Mode Automatique (Recommandé)

Génère la newsletter pour la semaine dernière:

```bash
python scripts/newsletter_generator.py --auto
```

### Mode Interactif

Le script vous pose des questions:

```bash
python scripts/newsletter_generator.py --interactive
```

### Mode Personnalisé

Spécifiez la date et les options:

```bash
# Générer pour une semaine spécifique
python scripts/newsletter_generator.py --end-date 2025-10-26

# Mode dry-run (test sans génération)
python scripts/newsletter_generator.py --dry-run

# Nombre minimum d'articles
python scripts/newsletter_generator.py --min-articles 30
```

### Toutes les Options

```bash
python scripts/newsletter_generator.py --help

Options:
  --end-date DATE          Date de fin de semaine (YYYY-MM-DD)
  --min-articles N         Nombre minimum d'articles (default: 25)
  --output DIR             Répertoire de sortie
  --dry-run                Mode test (n'écrit pas le fichier)
  --interactive            Mode interactif
  --auto                   Mode automatique (semaine dernière)
```

## ⚙️ Configuration

### Ajouter une nouvelle source

Éditez `config/sources.json`:

```json
{
  "name": "Nouvelle Source",
  "display_name": "Nouvelle Source / Newsletter",
  "type": "substack",
  "url": "https://example.substack.com/archive",
  "scrape_method": "firecrawl_scrape",
  "priority": "medium",
  "tags": ["growth", "marketing"],
  "enabled": true
}
```

### Modifier les catégories

Éditez `config/sources.json` section `balance_rules`:

```json
"category_distribution": {
  "critical": 8,
  "important": 8,
  "good_to_know": 9
}
```

### Personnaliser les prompts IA

Éditez `config/prompts.json` pour ajuster les instructions de résumé, traduction et catégorisation.

## 📊 Résultat

Le script génère un fichier HTML dans `output/newsletters/`:

```
output/newsletters/growth-weekly-2025-10-26.html
```

Ouvrez-le dans votre navigateur:

```bash
open output/newsletters/growth-weekly-2025-10-26.html
```

## 🔧 Développement

### État Actuel (v0.1 - Proof of Concept)

✅ **Complété:**
- Structure du projet
- Configuration JSON
- Script principal avec arguments CLI
- Template HTML
- Documentation (README, ARCHITECTURE, WARP)

🚧 **À Implémenter:**
- Module `scraper.py` avec MCP tools
- Module `ai_processor.py` avec API Claude
- Module `html_builder.py` pour génération
- Algorithme d'équilibrage des sources
- Système de cache
- Tests unitaires

### Prochaines Étapes

1. **Implémenter le scraper** - Connecter aux MCP tools (firecrawl, tavily)
2. **Implémenter l'IA processor** - Résumés et traductions via Claude
3. **Tester end-to-end** - Générer une première newsletter complète
4. **Automatisation** - GitHub Actions pour exécution hebdomadaire
5. **Dashboard** - Interface web pour curation manuelle

### Contributing

Les contributions sont bienvenues! Pour contribuer:

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amazing-feature`)
3. Commit vos changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Architecture technique complète
- **[WARP.md](WARP.md)** - Guide pour Warp AI assistant
- **[config/sources.json](config/sources.json)** - Configuration des sources
- **[config/prompts.json](config/prompts.json)** - Prompts IA

## 🤖 Automatisation (Futur)

GitHub Actions pour générer automatiquement chaque semaine:

```yaml
# .github/workflows/weekly_newsletter.yml
on:
  schedule:
    - cron: '0 9 * * 1'  # Tous les lundis à 9h
```

Voir `ARCHITECTURE.md` pour plus de détails.

## 💡 Exemples de Newsletters

- [Growth Weekly - 20-26 Oct 2025](output/newsletters/growth-weekly-2025-10-26.html)

## ❓ FAQ

**Q: Combien coûte l'API Claude?**  
R: Environ $0.20-0.30 par newsletter (25 articles résumés).

**Q: Peut-on utiliser une autre IA?**  
R: Oui, voir `ai_processor.py` pour utiliser OpenAI ou autre.

**Q: Comment ajouter Gmail comme source?**  
R: Voir commentaires dans `.env.example` pour configuration Gmail API.

**Q: La newsletter est-elle envoyée automatiquement?**  
R: Non, génération HTML seulement. Pour envoi email, intégrez Mailchimp/SendGrid.

**Q: Puis-je personnaliser le design?**  
R: Oui, éditez `templates/newsletter_template.html`.

## 📝 License

MIT License - voir [LICENSE](LICENSE)

## 👥 Auteurs

- **Dagorsey** - Concept et curation
- **Claude (Anthropic)** - Automatisation et génération

## 🙏 Remerciements

Merci aux créateurs de contenu growth marketing dont nous agrégeons le contenu:
Kyle Poyar, Elena Verna, Demand Curve, et tous les autres contributeurs mentionnés.

---

**⭐ Si ce projet vous est utile, donnez-lui une étoile sur GitHub!**
