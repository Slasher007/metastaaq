#!/usr/bin/env python3
"""
Script principal pour MetaSTAAQ - Téléchargement et traitement des données
Télécharge les données PVGIS et ENTSO-E sur 5 ans et les traite
"""

import os
import sys
from datetime import datetime

# Import des modules locaux
try:
    from utils.spot_price_download import download_spot_price_data
    from utils.spot_price_data_processing import process_prix_spot
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    sys.exit(1)


    


if __name__ == "__main__":

    # Coordonnées de Meaux (77)
    LATITUDE_MEAUX = 48.96
    LONGITUDE_MEAUX = 2.88
    #print(f"📍 Localisation: Meaux (Lat: {LATITUDE_MEAUX}, Lon: {LONGITUDE_MEAUX})")
    
    # Téléchargement des données de prix spot
    #api_key = os.getenv('ENTSOE_API_TOKEN', "9d9b8840-56e2-4993-9385-47cfe2b8183f")
    #annee_debut = 2021
    #annee_fin = 2025
    #mois_fin = 8
   #pays_code = 'FR'
   #download_spot_price_data(api_key, annee_debut, annee_fin, mois_fin, pays_code)
