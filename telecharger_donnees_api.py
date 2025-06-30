import os
import pandas as pd
from datetime import datetime, timedelta
from pvlib.iotools import get_pvgis_hourly
from entsoe import EntsoePandasClient

def telecharger_donnees_pvgis(lat, lon, annee=2020):
    """
    Télécharge les données de production PV horaire depuis PVGIS pour une année donnée.
    """
    print(f"Téléchargement des données PVGIS pour l'année {annee}...")
    try:
        # Appel à l'API de PVGIS via la bibliothèque pvlib
        data, metadata, inputs = get_pvgis_hourly(
            latitude=lat,
            longitude=lon,
            start=annee,
            end=annee,
            pvcalculation=True,
            peakpower=5000,  # 5000 kWc = 5 MWc
            loss=14,         # Pertes système en %
            mountingplace='free',
            surface_tilt=35,
            surface_azimuth=0,
            outputformat='csv'
        )
        
        # Renommer les colonnes pour plus de clarté
        data.rename(columns={
            'P': 'Puissance_W',
            'G(i)': 'Irradiation_globale_plan_W_m2',
            'H_sun': 'Elevation_soleil_deg',
            'T2m': 'Temperature_air_C',
            'WS10m': 'Vitesse_vent_ms'
        }, inplace=True)

        nom_fichier = f'donnees_pvgis_meaux_{annee}.csv'
        data.to_csv(nom_fichier)
        print(f"Données PVGIS enregistrées avec succès dans '{nom_fichier}'")
        return nom_fichier
    except Exception as e:
        print(f"Une erreur est survenue lors du téléchargement des données PVGIS : {e}")
        return None

def telecharger_donnees_entsoe(api_key, pays_code='FR'):
    """
    Télécharge les prix spot Day-Ahead depuis l'API ENTSO-E pour les 365 derniers jours.
    """
    print("Téléchargement des données de prix spot depuis ENTSO-E...")
    if not api_key or api_key == "VOTRE_CLE_API_ENTSOE_ICI":
        print("Erreur : Clé API ENTSO-E non configurée.")
        print("Veuillez vous enregistrer sur https://transparency.entsoe.eu/ pour obtenir une clé et l'ajouter dans le script.")
        return None
        
    try:
        client = EntsoePandasClient(api_key=api_key)
        
        # Définir la période : les 365 derniers jours à partir d'aujourd'hui
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # Conversion au format attendu par la bibliothèque
        start_ts = pd.Timestamp(start_date.strftime('%Y%m%d'), tz='Europe/Brussels')
        end_ts = pd.Timestamp(end_date.strftime('%Y%m%d'), tz='Europe/Brussels')

        # Requête pour les prix Day-Ahead
        prices = client.query_day_ahead_prices(pays_code, start=start_ts, end=end_ts)
        
        nom_fichier = f'donnees_prix_spot_{pays_code}_{start_date.year}_{end_date.year}.csv'
        prices.to_csv(nom_fichier, header=['Prix_EUR_MWh'])
        print(f"Données de prix spot enregistrées avec succès dans '{nom_fichier}'")
        return nom_fichier
    except Exception as e:
        print(f"Une erreur est survenue lors du téléchargement des données ENTSO-E : {e}")
        return None

if __name__ == '__main__':
    # --- PARAMETRES ---
    # Coordonnées de Meaux (77)
    LATITUDE_MEAUX = 48.96
    LONGITUDE_MEAUX = 2.88
    
    # !! IMPORTANT !!
    # Remplacez la ligne ci-dessous par votre propre clé API obtenue sur le site d'ENTSO-E
    # Vous pouvez la demander ici : https://transparency.entsoe.eu/dashboard/user-dashboard
    ENTSOE_API_KEY = os.getenv('ENTSOE_API_TOKEN', "VOTRE_CLE_API_ENTSOE_ICI")

    print("--- Lancement du script de récupération des données ---")
    
    # 1. Récupération des données solaires
    telecharger_donnees_pvgis(LATITUDE_MEAUX, LONGITUDE_MEAUX, annee=2020)
    
    print("-" * 20)
    
    # 2. Récupération des données de marché
    telecharger_donnees_entsoe(ENTSOE_API_KEY, pays_code='FR')
    
    print("--- Script terminé ---") 