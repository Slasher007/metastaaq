"""
Intégration avancée avec les API RTE pour données électricité
Script complémentaire avec authentification OAuth2 et endpoints spécialisés
"""

import requests
import json
import base64
import pandas as pd
from datetime import datetime, timedelta
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIRTEAvancee:
    """
    Classe avancée pour l'accès aux API RTE avec authentification OAuth2
    Basée sur la documentation officielle RTE
    """
    
    def __init__(self, client_id=None, client_secret=None):
        """
        Initialise l'API RTE avec authentification OAuth2
        
        Args:
            client_id (str): Client ID de l'application RTE
            client_secret (str): Client Secret de l'application RTE
        """
        self.client_id = client_id or os.getenv('RTE_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('RTE_CLIENT_SECRET')
        
        # URLs de base pour les API RTE
        self.auth_base_url = 'https://digital.iservices.rte-france.com/token/oauth/'
        self.api_base_url = 'https://digital.iservices.rte-france.com/open_api/'
        
        # Session HTTP avec configuration
        self.session = requests.Session()
        self.access_token = None
        self.token_expires_at = None
        
        # Endpoints disponibles pour les données électricité
        self.endpoints = {
            'consumption': 'consumption/v1.2/short_term',
            'generation_forecast': 'generation/v2.1/forecasts_made_of',
            'actual_generation': 'generation/v2.1/actual_generations_per_production_type',
            'unavailability': 'unavailability/v4.8/generation_units',
            'exchange': 'exchange/v1.0/physical_flows',
            'balancing': 'balancing/v1.0/imbalance_prices'
        }
    
    def authentifier(self):
        """
        Effectue l'authentification OAuth2 avec l'API RTE
        
        Returns:
            bool: True si authentification réussie, False sinon
        """
        if not self.client_id or not self.client_secret:
            logger.error("❌ Client ID et Client Secret requis pour l'authentification")
            logger.info("📋 Pour obtenir vos identifiants:")
            logger.info("   1. Créer un compte sur https://data.rte-france.com/")
            logger.info("   2. Créer une application")
            logger.info("   3. Associer les API nécessaires")
            logger.info("   4. Définir les variables: RTE_CLIENT_ID et RTE_CLIENT_SECRET")
            return False
        
        try:
            # Préparer les credentials en base64
            credentials = f"{self.client_id}:{self.client_secret}"
            credentials_b64 = base64.b64encode(credentials.encode()).decode()
            
            # Headers pour l'authentification
            headers = {
                'Authorization': f'Basic {credentials_b64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Corps de la requête OAuth2
            data = {
                'grant_type': 'client_credentials'
            }
            
            logger.info("🔐 Authentification OAuth2 en cours...")
            response = self.session.post(
                self.auth_base_url,
                headers=headers,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                expires_in = token_data.get('expires_in', 3600)  # Défaut 1h
                
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                # Configurer les headers pour les futures requêtes
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                })
                
                logger.info("✅ Authentification réussie")
                logger.info(f"⏰ Token expire à: {self.token_expires_at}")
                return True
            else:
                logger.error(f"❌ Erreur d'authentification: {response.status_code}")
                logger.error(f"Réponse: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'authentification: {e}")
            return False
    
    def verifier_token(self):
        """
        Vérifie si le token est encore valide et le renouvelle si nécessaire
        
        Returns:
            bool: True si token valide, False sinon
        """
        if not self.access_token or not self.token_expires_at:
            return self.authentifier()
        
        # Vérifier si le token expire dans moins de 5 minutes
        if datetime.now() >= (self.token_expires_at - timedelta(minutes=5)):
            logger.info("🔄 Renouvellement du token nécessaire")
            return self.authentifier()
        
        return True
    
    def obtenir_donnees_consommation(self, date_debut, date_fin, type_donnee='REALISED'):
        """
        Récupère les données de consommation française
        
        Args:
            date_debut (str): Date de début (YYYY-MM-DDTHH:MM)
            date_fin (str): Date de fin (YYYY-MM-DDTHH:MM)
            type_donnee (str): 'REALISED' ou 'FORECAST'
            
        Returns:
            pd.DataFrame: Données de consommation
        """
        if not self.verifier_token():
            return pd.DataFrame()
        
        params = {
            'start_date': date_debut,
            'end_date': date_fin,
            'type': type_donnee
        }
        
        return self._faire_requete_api('consumption', params)
    
    def obtenir_prix_spot_day_ahead(self, date_debut, date_fin):
        """
        Récupère les prix day-ahead (cette fonction nécessite l'endpoint correct)
        
        Args:
            date_debut (str): Date de début
            date_fin (str): Date de fin
            
        Returns:
            pd.DataFrame: Données de prix
        """
        if not self.verifier_token():
            return pd.DataFrame()
        
        # Note: Cet endpoint peut nécessiter un accès spécialisé
        params = {
            'start_date': date_debut,
            'end_date': date_fin
        }
        
        logger.warning("⚠️ Endpoint prix day-ahead non confirmé - vérifier la documentation RTE")
        return self._faire_requete_api('balancing', params)
    
    def obtenir_production_previsions(self, date_debut, date_fin, type_production='WIND'):
        """
        Récupère les prévisions de production par filière
        
        Args:
            date_debut (str): Date de début
            date_fin (str): Date de fin
            type_production (str): Type de production (WIND, SOLAR, etc.)
            
        Returns:
            pd.DataFrame: Prévisions de production
        """
        if not self.verifier_token():
            return pd.DataFrame()
        
        params = {
            'start_date': date_debut,
            'end_date': date_fin,
            'production_type': type_production
        }
        
        return self._faire_requete_api('generation_forecast', params)
    
    def obtenir_production_reelle(self, date_debut, date_fin):
        """
        Récupère la production réelle par filière
        
        Args:
            date_debut (str): Date de début
            date_fin (str): Date de fin
            
        Returns:
            pd.DataFrame: Production réelle
        """
        if not self.verifier_token():
            return pd.DataFrame()
        
        params = {
            'start_date': date_debut,
            'end_date': date_fin
        }
        
        return self._faire_requete_api('actual_generation', params)
    
    def analyser_creneaux_optimaux_puissance(self, donnees_consommation, seuils_puissance=[0.5, 1, 2, 3, 4, 5]):
        """
        Analyse les créneaux optimaux pour différents niveaux de puissance
        Basé sur la consommation et les patterns historiques
        
        Args:
            donnees_consommation (pd.DataFrame): Données de consommation
            seuils_puissance (list): Seuils de puissance en MW
            
        Returns:
            pd.DataFrame: Analyse des créneaux optimaux
        """
        if donnees_consommation.empty:
            return pd.DataFrame()
        
        logger.info("⚡ Analyse des créneaux optimaux de puissance...")
        
        # Copier les données pour traitement
        df = donnees_consommation.copy()
        
        # Ajouter des colonnes temporelles si pas déjà présentes
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
            df['heure'] = df['datetime'].dt.hour
            df['jour_semaine'] = df['datetime'].dt.dayofweek
            df['mois'] = df['datetime'].dt.month
        
        # Classification des créneaux par consommation (proxy pour prix)
        # Logique: consommation élevée = prix élevé, consommation faible = prix bas
        if 'value' in df.columns:
            # Calculer les quantiles de consommation
            quantiles = df['value'].quantile([0.2, 0.4, 0.6, 0.8])
            
            def classifier_creneau_consommation(valeur):
                if valeur <= quantiles[0.2]:
                    return "Très favorable"  # Consommation très faible
                elif valeur <= quantiles[0.4]:
                    return "Favorable"
                elif valeur <= quantiles[0.6]:
                    return "Modéré"
                elif valeur <= quantiles[0.8]:
                    return "Défavorable"
                else:
                    return "Très défavorable"  # Consommation très élevée
            
            df['classification_creneau'] = df['value'].apply(classifier_creneau_consommation)
            
            # Calcul de disponibilité par puissance (logique simplifiée)
            for puissance in seuils_puissance:
                # Plus la puissance est élevée, plus le seuil de consommation doit être bas
                seuil_consommation = quantiles[0.8] * (1 - (puissance / max(seuils_puissance)) * 0.5)
                
                col_name = f'disponible_{puissance}MW'
                df[col_name] = (df['value'] <= seuil_consommation).astype(int)
        
        return df
    
    def _faire_requete_api(self, endpoint_key, params):
        """
        Effectue une requête vers un endpoint de l'API RTE
        
        Args:
            endpoint_key (str): Clé de l'endpoint dans self.endpoints
            params (dict): Paramètres de la requête
            
        Returns:
            pd.DataFrame: Données retournées par l'API
        """
        if endpoint_key not in self.endpoints:
            logger.error(f"❌ Endpoint '{endpoint_key}' non reconnu")
            return pd.DataFrame()
        
        endpoint = self.endpoints[endpoint_key]
        url = f"{self.api_base_url}{endpoint}"
        
        try:
            logger.info(f"📡 Requête API: {endpoint}")
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Traitement des données selon la structure RTE
                if isinstance(data, dict) and 'values' in data:
                    df = pd.DataFrame(data['values'])
                elif isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    df = pd.DataFrame([data])
                
                logger.info(f"✅ {len(df)} enregistrements récupérés")
                return df
                
            else:
                logger.error(f"❌ Erreur API {endpoint}: {response.status_code}")
                logger.error(f"Réponse: {response.text[:500]}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la requête {endpoint}: {e}")
            return pd.DataFrame()
    
    def generer_rapport_complet_puissance(self, date_debut, date_fin, puissances=[0.5, 1, 2, 3, 4, 5]):
        """
        Génère un rapport complet d'analyse de puissance disponible
        
        Args:
            date_debut (str): Date de début
            date_fin (str): Date de fin
            puissances (list): Niveaux de puissance à analyser
            
        Returns:
            dict: Rapport complet avec toutes les analyses
        """
        logger.info("📊 Génération du rapport complet de puissance...")
        
        rapport = {
            'periode': {'debut': date_debut, 'fin': date_fin},
            'puissances_analysees': puissances,
            'timestamp': datetime.now().isoformat(),
            'donnees': {},
            'analyses': {},
            'recommandations': []
        }
        
        # 1. Récupérer les données de consommation
        logger.info("📈 Récupération des données de consommation...")
        donnees_conso = self.obtenir_donnees_consommation(date_debut, date_fin)
        if not donnees_conso.empty:
            rapport['donnees']['consommation'] = len(donnees_conso)
            
            # Analyser les créneaux optimaux
            analyse_creneaux = self.analyser_creneaux_optimaux_puissance(donnees_conso, puissances)
            if not analyse_creneaux.empty:
                rapport['analyses']['creneaux_optimaux'] = {}
                
                for puissance in puissances:
                    col_name = f'disponible_{puissance}MW'
                    if col_name in analyse_creneaux.columns:
                        taux_dispo = analyse_creneaux[col_name].mean() * 100
                        rapport['analyses']['creneaux_optimaux'][f'{puissance}MW'] = f"{taux_dispo:.1f}%"
        
        # 2. Récupérer les prévisions de production (si disponible)
        logger.info("🔋 Récupération des prévisions de production...")
        for type_prod in ['WIND', 'SOLAR']:
            donnees_prod = self.obtenir_production_previsions(date_debut, date_fin, type_prod)
            if not donnees_prod.empty:
                rapport['donnees'][f'production_{type_prod.lower()}'] = len(donnees_prod)
        
        # 3. Générer des recommandations
        if rapport['analyses'].get('creneaux_optimaux'):
            meilleures_puissances = []
            for puissance, taux in rapport['analyses']['creneaux_optimaux'].items():
                taux_val = float(taux.replace('%', ''))
                if taux_val > 50:
                    meilleures_puissances.append(f"{puissance} (disponible {taux} du temps)")
            
            if meilleures_puissances:
                rapport['recommandations'].append(f"✅ Puissances recommandées: {', '.join(meilleures_puissances)}")
            else:
                rapport['recommandations'].append("⚠️ Aucune puissance disponible > 50% du temps - revoir les seuils")
        
        return rapport


def exemple_utilisation_api_rte_avancee():
    """
    Exemple d'utilisation de l'API RTE avancée
    """
    print("🚀 EXEMPLE - API RTE Avancée")
    print("=" * 50)
    
    # Vérifier les variables d'environnement
    client_id = os.getenv('RTE_CLIENT_ID')
    client_secret = os.getenv('RTE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("⚠️  Variables d'environnement non définies:")
        print("   export RTE_CLIENT_ID='votre_client_id'")
        print("   export RTE_CLIENT_SECRET='votre_client_secret'")
        print("\n📋 Pour obtenir ces identifiants:")
        print("   1. Créer un compte sur https://data.rte-france.com/")
        print("   2. Créer une application pour 'Web Server'")
        print("   3. Associer les API nécessaires à votre application")
        print("   4. Noter le Client ID et Client Secret")
        return
    
    # Initialiser l'API
    api = APIRTEAvancee(client_id, client_secret)
    
    # Test d'authentification
    if api.authentifier():
        print("✅ Authentification réussie!")
        
        # Définir une période de test
        date_debut = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%dT00:00')
        date_fin = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT23:59')
        
        print(f"📅 Période de test: {date_debut} à {date_fin}")
        
        # Test récupération de données
        print("\n📊 Test des données de consommation...")
        donnees_conso = api.obtenir_donnees_consommation(date_debut, date_fin)
        
        if not donnees_conso.empty:
            print(f"✅ {len(donnees_conso)} points de consommation récupérés")
            
            # Analyse des créneaux optimaux
            print("\n⚡ Analyse des créneaux optimaux...")
            analyse = api.analyser_creneaux_optimaux_puissance(donnees_conso)
            
            if not analyse.empty:
                # Afficher quelques statistiques
                for puissance in [0.5, 1, 2, 3, 4, 5]:
                    col_name = f'disponible_{puissance}MW'
                    if col_name in analyse.columns:
                        taux = analyse[col_name].mean() * 100
                        print(f"   • {puissance} MW: {taux:.1f}% du temps")
        
        # Générer un rapport complet
        print("\n📋 Génération du rapport complet...")
        rapport = api.generer_rapport_complet_puissance(date_debut, date_fin)
        
        print("🎯 Recommandations:")
        for rec in rapport.get('recommandations', []):
            print(f"   {rec}")
    
    else:
        print("❌ Échec de l'authentification")


if __name__ == "__main__":
    exemple_utilisation_api_rte_avancee() 