# 🔌 Module de Recherche de Données Électricité France

Ce module permet d'effectuer des recherches web ciblées et d'accéder aux API pour récupérer des données sur les prix spot de l'électricité et la disponibilité de puissance en France.

## 📋 Fonctionnalités

### 🔍 Recherche Web Ciblée
- Recherche sur `rte-france.com`, `services-rte.com`, `epexspot.com`
- Requête optimisée : `"Site:rte-france.com OR site:services-rte.com OR site:epexspot.com prix spot électricité France 2021-2025 données historiques heures disponibilité puissance 0.5-5 MW"`
- Extraction et organisation automatique des résultats

### 🔌 API RTE éCO2mix
- Accès aux données ouvertes RTE
- Requête type : `GET /data/spot-prices?country=FR&start_date=2021-01-01&end_date=2025-07-10&granularity=hourly&power_levels=0.5,1,2,3,4,5`
- Calcul automatique des puissances disponibles par seuil de prix

## 🚀 Installation

1. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

2. **Dépendances requises** :
- `pandas` - Traitement des données
- `requests` - Requêtes HTTP
- `beautifulsoup4` - Parsing HTML
- `numpy` - Calculs numériques

## 💻 Utilisation

### 🎯 Utilisation Simple

```python
from recherche_donnees_electricite import RechercheElectriciteFrance

# Initialisation
recherche = RechercheElectriciteFrance()

# Recherche web ciblée
resultats_web = recherche.recherche_web_donnees_spot()

# Recherche via API RTE (données ouvertes)
donnees_api = recherche.recherche_api_rte_eco2mix(
    date_debut='2024-01-01',
    date_fin='2024-12-31'
)
```

### 📊 Exemple Complet

Exécutez le script d'exemple :

```bash
python exemple_recherche_electricite.py
```

Options disponibles :
1. **Exemple complet** - Recherche web + API + analyse
2. **Exemple rapide** - Test de base des fonctions
3. **Structure API RTE** - Affichage de la documentation API

### 🔐 Configuration API Authentifiée (Optionnel)

Pour accéder aux API RTE authentifiées :

1. Créer un compte sur https://data.rte-france.com/
2. Obtenir une clé API
3. Définir la variable d'environnement :

```bash
# Windows
set RTE_API_KEY=votre_cle_api

# Linux/Mac
export RTE_API_KEY=votre_cle_api
```

4. Utiliser avec authentification :

```python
recherche = RechercheElectriciteFrance(rte_api_key="votre_cle")
donnees_auth = recherche.recherche_api_rte_authentifiee()
```

## 📊 Structure des Données

### Recherche Web
```json
{
  "rte-france.com": [
    {
      "titre": "Données de prix spot",
      "url": "https://...",
      "description": "..."
    }
  ],
  "services-rte.com": [...],
  "epexspot.com": [...]
}
```

### Données API
```csv
date_heure,prix_spot,disponible_0.5MW_max_20EUR,classification_creneau,...
2024-01-01 00:00,15.5,1,"Très favorable",...
```

## 🎯 Cas d'Usage Typiques

### 1. Analyse des Prix Spot
```python
# Récupérer les données de prix
donnees = recherche.recherche_api_rte_eco2mix(
    date_debut='2021-01-01',
    date_fin='2025-07-10'
)

# Analyser les créneaux favorables
creneaux_favorables = donnees[donnees['classification_creneau'] == 'Très favorable']
```

### 2. Disponibilité de Puissance
```python
# Calculer la disponibilité pour 2 MW à max 25 €/MWh
disponibilite_2MW = donnees['disponible_2MW_max_25EUR'].mean() * 100
print(f"Disponibilité 2 MW: {disponibilite_2MW:.1f}%")
```

### 3. Recherche de Sources
```python
# Trouver des sources de données spécialisées
sources = recherche.recherche_web_donnees_spot(
    "données historiques prix électricité granularité horaire"
)
```

## 📁 Fichiers Générés

Le module génère automatiquement :
- `recherche_electricite_web_YYYYMMDD_HHMMSS.json` - Résultats de recherche web
- `recherche_electricite_api_YYYYMMDD_HHMMSS.csv` - Données API
- `recherche_electricite_rapport_YYYYMMDD_HHMMSS.json` - Rapport d'analyse

## 🔧 Paramètres Configurables

### Recherche Web
- `terme_recherche` : Personnaliser la requête de recherche
- `sites_cibles` : Modifier les sites à cibler

### API RTE
- `date_debut/date_fin` : Période d'analyse
- `granularite` : 'hourly', 'daily', etc.
- `power_levels` : Niveaux de puissance à analyser

### Analyse de Puissance
- Seuils de prix : 10, 15, 20, 25, 30, 35, 40, 50 €/MWh
- Puissances : 0.5, 1, 2, 3, 4, 5 MW

## ⚠️ Notes Importantes

1. **Respect des API** : Respectez les limites de taux des API
2. **Recherche Web** : Google peut bloquer les requêtes automatisées
3. **Données RTE** : Vérifiez la documentation officielle pour les paramètres exacts
4. **Performance** : Les requêtes sur de longues périodes peuvent être lentes

## 🆘 Dépannage

### Erreur "Aucune donnée trouvée"
- Vérifiez les paramètres de date
- Consultez la documentation API RTE
- Testez avec une période plus courte

### Erreur de recherche web
- Vérifiez votre connexion internet
- Google peut limiter les requêtes automatisées
- Utilisez des délais entre les requêtes

### Erreur d'authentification API
- Vérifiez votre clé API RTE
- Assurez-vous que la variable d'environnement est définie
- Consultez le statut de l'API RTE

## 🔗 Ressources Utiles

- [Documentation API RTE](https://data.rte-france.com/)
- [Open Data RTE](https://odre.opendatasoft.com/)
- [EPEX SPOT](https://www.epexspot.com/)
- [Transparency Platform ENTSO-E](https://transparency.entsoe.eu/)

## 📞 Support

Pour toute question ou problème :
1. Vérifiez ce README
2. Consultez les logs d'erreur détaillés
3. Testez avec l'exemple simple d'abord 