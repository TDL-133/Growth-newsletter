# 🚀 Guide d'Activation GitHub Pages

## Configuration GitHub Pages pour Growth Weekly

### Étapes à suivre sur GitHub.com :

1. **Accéder aux Settings du Repository**
   - Allez sur votre repo : `https://github.com/TDL-133/Growth-newsletter`
   - Cliquez sur l'onglet `Settings` (⚙️)

2. **Configurer GitHub Pages**
   - Dans le menu latéral gauche, cliquez sur `Pages`
   - Sous "Build and deployment" :
     - **Source** : Sélectionnez `Deploy from a branch`
     - **Branch** : Sélectionnez `master` (ou `main`)
     - **Folder** : Sélectionnez `/docs`
   - Cliquez sur `Save`

3. **Attendre le Déploiement**
   - GitHub va automatiquement déployer votre site
   - Cela prend généralement 1-2 minutes
   - Une notification verte apparaîtra avec l'URL de votre site

4. **URL de Votre Site**
   - Votre newsletter sera accessible à :
   ```
   https://tdl-133.github.io/Growth-newsletter/
   ```
   
   - La dernière newsletter sera à :
   ```
   https://tdl-133.github.io/Growth-newsletter/growth-weekly-2025-10-31.html
   ```

### Structure des URLs

```
https://tdl-133.github.io/Growth-newsletter/
├── index.html                           # Page d'accueil avec archive
├── growth-weekly-2025-10-26.html       # Newsletter #1
└── growth-weekly-2025-10-31.html       # Newsletter #2 (dernière)
```

### Vérification du Déploiement

Une fois GitHub Pages activé, vous pouvez vérifier :

1. **Status du déploiement** :
   - Allez dans l'onglet `Actions` de votre repo
   - Vous verrez le workflow "pages build and deployment"
   - Un ✅ vert indique un déploiement réussi

2. **Visiter le site** :
   - Cliquez sur le lien fourni dans Settings > Pages
   - Ou visitez directement l'URL mentionnée ci-dessus

### Personnalisation (Optionnel)

#### Domaine Personnalisé

Si vous voulez utiliser votre propre domaine :

1. Dans Settings > Pages > Custom domain
2. Entrez votre domaine (ex: `growth-weekly.lopato.fr`)
3. Configurez les DNS chez votre registrar :
   ```
   Type: CNAME
   Name: growth-weekly
   Value: tdl-133.github.io
   ```

#### HTTPS

- GitHub Pages active automatiquement HTTPS
- Cochez "Enforce HTTPS" pour forcer le HTTPS

### Automatisation Future

Pour automatiser la publication de nouvelles newsletters :

1. Créez une GitHub Action qui :
   - Génère la newsletter chaque lundi
   - Met à jour `docs/index.html` avec la nouvelle édition
   - Commit et push automatiquement

2. Exemple de workflow à créer dans `.github/workflows/newsletter.yml` :

```yaml
name: Generate Weekly Newsletter

on:
  schedule:
    - cron: '0 9 * * 1'  # Tous les lundis à 9h
  workflow_dispatch:      # Déclenchement manuel

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
        run: |
          pip install -r requirements.txt
      
      - name: Generate newsletter
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GMAIL_CREDENTIALS: ${{ secrets.GMAIL_CREDENTIALS }}
        run: |
          python scripts/newsletter_generator_mcp.py
      
      - name: Commit and push
        run: |
          git config user.name "Growth Weekly Bot"
          git config user.email "bot@growthweekly.com"
          git add docs/
          git commit -m "🚀 New newsletter $(date +%Y-%m-%d)"
          git push
```

### Résolution de Problèmes

**Le site ne s'affiche pas ?**
- Vérifiez que `/docs` est bien sélectionné comme source
- Attendez 2-5 minutes après la configuration
- Vérifiez les Actions pour voir si le déploiement est réussi

**Erreur 404 ?**
- Assurez-vous que `docs/index.html` existe
- Vérifiez que les chemins des liens sont relatifs, pas absolus

**CSS/JS ne se charge pas ?**
- Utilisez des chemins relatifs dans vos HTML
- Vérifiez la console du navigateur pour les erreurs

### Maintenance

Pour ajouter une nouvelle newsletter :

```bash
# 1. Générer la newsletter
python scripts/newsletter_generator_mcp.py

# 2. Copier dans docs/
cp growth-weekly-YYYY-MM-DD.html docs/

# 3. Mettre à jour docs/index.html
# Ajouter la nouvelle newsletter en haut de la liste

# 4. Commit et push
git add docs/
git commit -m "📰 Add newsletter YYYY-MM-DD"
git push
```

### Ressources

- [Documentation GitHub Pages](https://docs.github.com/pages)
- [Guide Domaines Personnalisés](https://docs.github.com/pages/configuring-a-custom-domain-for-your-github-pages-site)
- [GitHub Actions](https://docs.github.com/actions)

---

**Note** : Une fois GitHub Pages activé, toute modification dans le dossier `docs/` et push vers `master` déclenchera automatiquement un redéploiement.
