import os
import pandas as pd
from datetime import datetime, timedelta
from pvlib.iotools import get_pvgis_hourly
from entsoe import EntsoePandasClient

def telecharger_donnees_pvgis_multi_annees(lat, lon, annee_debut=2020, annee_fin=2024):
    """
    Télécharge les données de production PV horaire depuis PVGIS pour plusieurs années.
    """
    print(f"Téléchargement des données PVGIS pour les années {annee_debut} à {annee_fin}...")
    
    all_data = []
    
    for annee in range(annee_debut, annee_fin + 1):
        print(f"  → Téléchargement pour l'année {annee}...")
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

            all_data.append(data)
            print(f"  ✅ Données {annee} téléchargées avec succès")
            
        except Exception as e:
            print(f"  ❌ Erreur pour l'année {annee}: {e}")
    
    if all_data:
        # Combiner toutes les données
        combined_data = pd.concat(all_data, ignore_index=True)
        combined_data.sort_index(inplace=True)
        
        nom_fichier = f'donnees_production_pv_meaux_{annee_debut}_{annee_fin}.csv'
        combined_data.to_csv(nom_fichier)
        print(f"✅ Toutes les données PVGIS enregistrées avec succès dans '{nom_fichier}'")
        print(f"📊 Total: {len(combined_data)} points de données")
        return nom_fichier
    else:
        print("❌ Aucune donnée n'a pu être téléchargée")
        return None

def telecharger_donnees_entsoe_5_ans(api_key, pays_code='FR'):
    """
    Télécharge les prix spot Day-Ahead depuis l'API ENTSO-E pour les 5 dernières années.
    """
    print("Téléchargement des données de prix spot depuis ENTSO-E pour les 5 dernières années...")
    if not api_key or api_key == "VOTRE_CLE_API_ENTSOE_ICI":
        print("Erreur : Clé API ENTSO-E non configurée.")
        print("Veuillez suivre les instructions ici pour obtenir une clé : https://transparencyplatform.zendesk.com/hc/en-us/articles/12845911031188-How-to-get-security-token")
        return None
        
    try:
        client = EntsoePandasClient(api_key=api_key)
        
        # Définir la période : les 5 dernières années
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)  # 5 ans approximatif
        
        print(f"📅 Période de téléchargement: {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}")
        
        # Conversion au format attendu par la bibliothèque
        start_ts = pd.Timestamp(start_date.strftime('%Y%m%d'), tz='Europe/Brussels')
        end_ts = pd.Timestamp(end_date.strftime('%Y%m%d'), tz='Europe/Brussels')

        # Requête pour les prix Day-Ahead
        print("🔄 Requête en cours vers l'API ENTSO-E...")
        prices = client.query_day_ahead_prices(pays_code, start=start_ts, end=end_ts)
        
        nom_fichier = f'donnees_prix_spot_{pays_code}_{start_date.year}_{end_date.year}.csv'
        prices.to_csv(nom_fichier, header=['Prix_EUR_MWh'])
        print(f"✅ Données de prix spot enregistrées avec succès dans '{nom_fichier}'")
        print(f"📊 Total: {len(prices)} points de données")
        return nom_fichier
    except Exception as e:
        print(f"❌ Une erreur est survenue lors du téléchargement des données ENTSO-E : {e}")
        return None

# Garder les anciennes fonctions pour compatibilité
def telecharger_donnees_pvgis(lat, lon, annee=2020):
    """
    Télécharge les données de production PV horaire depuis PVGIS pour une année donnée.
    """
    return telecharger_donnees_pvgis_multi_annees(lat, lon, annee, annee)

def telecharger_donnees_entsoe(api_key, pays_code='FR'):
    """
    Télécharge les prix spot Day-Ahead depuis l'API ENTSO-E pour les 365 derniers jours.
    """
    return telecharger_donnees_entsoe_5_ans(api_key, pays_code)

if __name__ == '__main__':
    # --- PARAMETRES ---
    # Coordonnées de Meaux (77)
    LATITUDE_MEAUX = 48.96
    LONGITUDE_MEAUX = 2.88
    
    # !! IMPORTANT !!
    # Remplacez la ligne ci-dessous par votre propre clé API obtenue sur le site d'ENTSO-E
    # Instructions détaillées pour obtenir le token : https://transparencyplatform.zendesk.com/hc/en-us/articles/12845911031188-How-to-get-security-token
    ENTSOE_API_KEY = os.getenv('ENTSOE_API_TOKEN', "9d9b8840-56e2-4993-9385-47cfe2b8183f")

    print("🚀 TÉLÉCHARGEMENT DES DONNÉES - 5 DERNIÈRES ANNÉES")
    print("="*60)
    
    # 1. Récupération des données solaires (2020-2024)
    print("\n📊 1. DONNÉES SOLAIRES PVGIS")
    print("-" * 40)
    telecharger_donnees_pvgis_multi_annees(LATITUDE_MEAUX, LONGITUDE_MEAUX, 2020, 2024)
    
    print("\n💰 2. DONNÉES PRIX SPOT ENTSO-E")
    print("-" * 40)
    
    # 2. Récupération des données de marché (5 ans)
    telecharger_donnees_entsoe_5_ans(ENTSOE_API_KEY, pays_code='FR')
    
    print("\n🎉 Script terminé avec succès!") 