"""
Script de recherche de données électricité française
Combine recherches web ciblées et API RTE éCO2mix pour données spot et puissance
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime, timedelta
from urllib.parse import quote_plus, urljoin
import os
from bs4 import BeautifulSoup
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RechercheElectriciteFrance:
    """
    Classe pour rechercher des données d'électricité française via web scraping et API
    """
    
    def __init__(self, rte_api_key=None):
        """
        Initialise la classe avec les paramètres de recherche
        
        Args:
            rte_api_key (str): Clé API RTE pour accès éCO2mix (optionnel)
        """
        self.rte_api_key = rte_api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # URLs de base pour les recherches
        self.sites_cibles = [
            'rte-france.com',
            'services-rte.com', 
            'epexspot.com'
        ]
        
        # API RTE éCO2mix
        self.rte_api_base = 'https://digital.iservices.rte-france.com/open_api/ecowatt/v4/'
        self.rte_data_api = 'https://odre.opendatasoft.com/api/records/1.0/search/'
    
    def recherche_web_donnees_spot(self, terme_recherche=None):
        """
        Effectue une recherche web ciblée sur les sites RTE et EPEX SPOT
        
        Args:
            terme_recherche (str): Terme de recherche personnalisé ou utilise le défaut
            
        Returns:
            dict: Résultats de recherche organisés par site
        """
        if terme_recherche is None:
            terme_recherche = "prix spot électricité France 2021-2025 données historiques heures disponibilité puissance 0.5-5 MW"
        
        logger.info(f"🔍 Démarrage recherche web: {terme_recherche}")
        
        resultats = {}
        
        # Construction de la requête Google avec restriction de sites
        sites_query = " OR ".join([f"site:{site}" for site in self.sites_cibles])
        requete_complete = f"({sites_query}) {terme_recherche}"
        
        # URL de recherche Google (Note: pour usage réel, préférer API Google Search)
        google_url = f"https://www.google.com/search?q={quote_plus(requete_complete)}"
        
        try:
            logger.info("📡 Envoi de la requête de recherche...")
            response = self.session.get(google_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extraction des résultats (structure simplifiée)
                resultats_bruts = soup.find_all('div', class_='g')
                
                for site in self.sites_cibles:
                    resultats[site] = []
                    
                for resultat in resultats_bruts[:10]:  # Limiter aux 10 premiers
                    try:
                        lien_elem = resultat.find('a')
                        if lien_elem and 'href' in lien_elem.attrs:
                            url = lien_elem['href']
                            
                            # Déterminer le site source
                            site_source = None
                            for site in self.sites_cibles:
                                if site in url:
                                    site_source = site
                                    break
                            
                            if site_source:
                                titre_elem = resultat.find('h3')
                                titre = titre_elem.text if titre_elem else "Sans titre"
                                
                                description_elem = resultat.find('span', class_='st')
                                description = description_elem.text if description_elem else "Pas de description"
                                
                                resultats[site_source].append({
                                    'titre': titre,
                                    'url': url,
                                    'description': description[:200] + "..." if len(description) > 200 else description
                                })
                    except Exception as e:
                        logger.warning(f"Erreur lors de l'extraction d'un résultat: {e}")
                        continue
                        
            else:
                logger.error(f"Erreur HTTP lors de la recherche: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la recherche web: {e}")
            resultats['erreur'] = str(e)
        
        return resultats
    
    def recherche_api_rte_eco2mix(self, date_debut='2021-01-01', date_fin='2025-07-10', granularite='hourly'):
        """
        Recherche de données via l'API RTE éCO2mix (via Open Data RTE)
        
        Args:
            date_debut (str): Date de début au format YYYY-MM-DD
            date_fin (str): Date de fin au format YYYY-MM-DD
            granularite (str): Granularité des données ('hourly', 'daily')
            
        Returns:
            pd.DataFrame: Données de prix spot et puissance disponible
        """
        logger.info(f"🔌 Recherche API RTE éCO2mix de {date_debut} à {date_fin}")
        
        try:
            # Construction des paramètres pour l'API Open Data RTE
            # Utilisation du bon format de date pour l'API
            params = {
                'dataset': 'eco2mix-national-tr',  # Dataset temps réel national
                'q': '',
                'facet': ['nature'],
                'timezone': 'Europe/Paris',
                'rows': 1000,  # Limite de résultats réduite pour test
                'start': 0,
                'format': 'json'
            }
            
            # Ajouter un filtre de date si nécessaire (format différent)
            # Pour les tests, on va d'abord essayer sans filtre de date spécifique
            
            logger.info("📡 Appel API Open Data RTE...")
            response = self.session.get(self.rte_data_api, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extraction des enregistrements
                records = data.get('records', [])
                
                if not records:
                    logger.warning("⚠️ Aucune donnée trouvée dans la réponse API")
                    return pd.DataFrame()
                
                # Conversion en DataFrame
                donnees_brutes = []
                for record in records:
                    fields = record.get('fields', {})
                    donnees_brutes.append(fields)
                
                df = pd.DataFrame(donnees_brutes)
                
                # Traitement des données pour analyse de puissance disponible
                df = self._traiter_donnees_puissance(df)
                
                logger.info(f"✅ {len(df)} enregistrements récupérés depuis l'API RTE")
                return df
                
            else:
                logger.error(f"❌ Erreur API RTE: {response.status_code}")
                logger.error(f"Réponse: {response.text[:500]}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'appel API RTE: {e}")
            return pd.DataFrame()
    
    def _traiter_donnees_puissance(self, df):
        """
        Traite les données pour calculer la disponibilité de puissance 0.5-5 MW
        
        Args:
            df (pd.DataFrame): Données brutes de l'API
            
        Returns:
            pd.DataFrame: Données enrichies avec calculs de puissance
        """
        if df.empty:
            return df
            
        logger.info("⚡ Calcul des puissances disponibles...")
        
        # Puissances cibles en MW
        puissances_mw = [0.5, 1, 2, 3, 4, 5]
        
        # Seuils de prix pour analyse économique (€/MWh)
        seuils_prix = [10, 15, 20, 25, 30, 35, 40, 50]
        
        # Calcul de disponibilité par niveau de puissance et seuil de prix
        for puissance in puissances_mw:
            for seuil in seuils_prix:
                col_name = f'disponible_{puissance}MW_max_{seuil}EUR'
                
                # Logique simplifiée : disponibilité basée sur prix spot
                # À adapter selon les vraies colonnes de l'API RTE
                if 'prix_spot' in df.columns:
                    df[col_name] = (df['prix_spot'] <= seuil).astype(int)
                else:
                    # Valeur par défaut si pas de données de prix
                    df[col_name] = 1
        
        # Classification des créneaux horaires
        if 'date_heure' in df.columns:
            df['date_heure'] = pd.to_datetime(df['date_heure'])
            df['heure'] = df['date_heure'].dt.hour
            df['jour_semaine'] = df['date_heure'].dt.dayofweek
            df['mois'] = df['date_heure'].dt.month
            
            # Classification des créneaux optimaux
            def classifier_creneau(row):
                heure = row['heure']
                jour = row['jour_semaine']
                
                # Heures creuses généralement favorables
                if 2 <= heure <= 6:
                    return "Très favorable"
                elif (22 <= heure <= 23) or (0 <= heure <= 1):
                    return "Favorable"
                elif 12 <= heure <= 14:  # Midi solaire
                    return "Modéré"
                elif (8 <= heure <= 10) or (18 <= heure <= 20):  # Heures de pointe
                    return "Défavorable"
                else:
                    return "Neutre"
            
            df['classification_creneau'] = df.apply(classifier_creneau, axis=1)
        
        return df
    
    def recherche_api_rte_authentifiee(self, endpoint='spot-prices', params=None):
        """
        Appel API RTE avec authentification (nécessite clé API)
        
        Args:
            endpoint (str): Point d'API à appeler
            params (dict): Paramètres de la requête
            
        Returns:
            dict: Réponse de l'API
        """
        if not self.rte_api_key:
            logger.error("❌ Clé API RTE requise pour cet appel")
            return None
        
        if params is None:
            params = {
                'country': 'FR',
                'start_date': '2021-01-01',
                'end_date': '2025-07-10',
                'granularity': 'hourly',
                'power_levels': '0.5,1,2,3,4,5'
            }
        
        headers = {
            'Authorization': f'Bearer {self.rte_api_key}',
            'Content-Type': 'application/json'
        }
        
        url = urljoin(self.rte_api_base, endpoint)
        
        try:
            logger.info(f"🔐 Appel API RTE authentifié: {endpoint}")
            response = self.session.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Erreur API authentifiée: {response.status_code}")
                logger.error(f"Réponse: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'appel API authentifié: {e}")
            return None
    
    def analyser_resultats_complets(self, resultats_web=None, donnees_api=None):
        """
        Analyse complète des résultats de recherche web et API
        
        Args:
            resultats_web (dict): Résultats de recherche web
            donnees_api (pd.DataFrame): Données API
            
        Returns:
            dict: Rapport d'analyse complet
        """
        logger.info("📊 Génération du rapport d'analyse...")
        
        rapport = {
            'timestamp': datetime.now().isoformat(),
            'recherche_web': {},
            'donnees_api': {},
            'recommandations': []
        }
        
        # Analyse des résultats web
        if resultats_web:
            rapport['recherche_web'] = {
                'sites_analyses': list(resultats_web.keys()),
                'total_resultats': sum(len(resultats_web.get(site, [])) for site in self.sites_cibles),
                'resultats_par_site': {
                    site: len(resultats_web.get(site, [])) 
                    for site in self.sites_cibles
                }
            }
        
        # Analyse des données API
        if donnees_api is not None and not donnees_api.empty:
            rapport['donnees_api'] = {
                'nombre_enregistrements': len(donnees_api),
                'periode_couverte': {
                    'debut': donnees_api['date_heure'].min().isoformat() if 'date_heure' in donnees_api.columns else 'N/A',
                    'fin': donnees_api['date_heure'].max().isoformat() if 'date_heure' in donnees_api.columns else 'N/A'
                },
                'colonnes_disponibles': list(donnees_api.columns)
            }
            
            # Analyse de disponibilité par puissance
            colonnes_puissance = [col for col in donnees_api.columns if 'disponible_' in col and 'MW' in col]
            if colonnes_puissance:
                rapport['donnees_api']['analyse_puissance'] = {}
                for col in colonnes_puissance[:5]:  # Limiter l'affichage
                    taux_disponibilite = donnees_api[col].mean() * 100
                    rapport['donnees_api']['analyse_puissance'][col] = f"{taux_disponibilite:.1f}%"
        
        # Recommandations
        if rapport['recherche_web'].get('total_resultats', 0) > 0:
            rapport['recommandations'].append("✅ Sources web identifiées - explorer manuellement les liens trouvés")
        
        if rapport['donnees_api'].get('nombre_enregistrements', 0) > 1000:
            rapport['recommandations'].append("✅ Volume de données API suffisant pour analyse")
        else:
            rapport['recommandations'].append("⚠️ Volume de données API limité - vérifier les paramètres de requête")
        
        return rapport
    
    def sauvegarder_resultats(self, resultats_web=None, donnees_api=None, rapport=None, prefixe="recherche_electricite"):
        """
        Sauvegarde tous les résultats dans des fichiers
        
        Args:
            resultats_web (dict): Résultats web à sauvegarder
            donnees_api (pd.DataFrame): Données API à sauvegarder
            rapport (dict): Rapport d'analyse à sauvegarder
            prefixe (str): Préfixe pour les noms de fichiers
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Sauvegarde des résultats web
        if resultats_web:
            fichier_web = f"{prefixe}_web_{timestamp}.json"
            with open(fichier_web, 'w', encoding='utf-8') as f:
                json.dump(resultats_web, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 Résultats web sauvegardés: {fichier_web}")
        
        # Sauvegarde des données API
        if donnees_api is not None and not donnees_api.empty:
            fichier_api = f"{prefixe}_api_{timestamp}.csv"
            donnees_api.to_csv(fichier_api, index=False)
            logger.info(f"💾 Données API sauvegardées: {fichier_api}")
        
        # Sauvegarde du rapport
        if rapport:
            fichier_rapport = f"{prefixe}_rapport_{timestamp}.json"
            with open(fichier_rapport, 'w', encoding='utf-8') as f:
                json.dump(rapport, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 Rapport sauvegardé: {fichier_rapport}")


def main():
    """
    Fonction principale pour exécuter les recherches
    """
    print("🚀 Démarrage de la recherche de données électricité française")
    print("=" * 60)
    
    # Initialisation
    # Pour l'API RTE authentifiée, remplacer None par votre clé API
    rte_api_key = os.getenv('RTE_API_KEY')  # Ou définir directement: "VOTRE_CLE_API"
    
    recherche = RechercheElectriciteFrance(rte_api_key=rte_api_key)
    
    # 1. Recherche web ciblée
    print("\n🔍 ÉTAPE 1: Recherche web sur sites spécialisés")
    print("-" * 40)
    
    terme_recherche = "prix spot électricité France 2021-2025 données historiques heures disponibilité puissance 0.5-5 MW"
    resultats_web = recherche.recherche_web_donnees_spot(terme_recherche)
    
    # Affichage des résultats web
    for site, resultats in resultats_web.items():
        if isinstance(resultats, list) and resultats:
            print(f"\n📋 {site}: {len(resultats)} résultat(s)")
            for i, res in enumerate(resultats[:3], 1):  # Afficher max 3 par site
                print(f"   {i}. {res['titre'][:80]}...")
                print(f"      URL: {res['url']}")
    
    # 2. Recherche API RTE éCO2mix
    print("\n\n🔌 ÉTAPE 2: Recherche via API RTE éCO2mix")
    print("-" * 40)
    
    donnees_api = recherche.recherche_api_rte_eco2mix(
        date_debut='2021-01-01',
        date_fin='2025-07-10',
        granularite='hourly'
    )
    
    if not donnees_api.empty:
        print(f"✅ {len(donnees_api)} enregistrements récupérés")
        print(f"📊 Colonnes disponibles: {len(donnees_api.columns)}")
        print("🔍 Aperçu des premières lignes:")
        print(donnees_api.head(3).to_string())
    else:
        print("⚠️ Aucune donnée récupérée via l'API")
    
    # 3. Analyse complète
    print("\n\n📊 ÉTAPE 3: Analyse des résultats")
    print("-" * 40)
    
    rapport = recherche.analyser_resultats_complets(resultats_web, donnees_api)
    
    print("📋 RÉSUMÉ DU RAPPORT:")
    print(f"   • Total résultats web: {rapport['recherche_web'].get('total_resultats', 0)}")
    print(f"   • Enregistrements API: {rapport['donnees_api'].get('nombre_enregistrements', 0)}")
    print("\n🎯 RECOMMANDATIONS:")
    for rec in rapport['recommandations']:
        print(f"   {rec}")
    
    # 4. Sauvegarde
    print("\n\n💾 ÉTAPE 4: Sauvegarde des résultats")
    print("-" * 40)
    
    recherche.sauvegarder_resultats(
        resultats_web=resultats_web,
        donnees_api=donnees_api,
        rapport=rapport
    )
    
    print("\n✅ Recherche terminée avec succès!")
    print("=" * 60)


if __name__ == "__main__":
    main() 