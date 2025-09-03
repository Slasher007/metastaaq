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
    from utils.telecharger_donnees_api import telecharger_donnees_pvgis_multi_annees, telecharger_donnees_entsoe_5_ans
    from process_prix_spot_data import main as process_prix_spot
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Assurez-vous que les fichiers 'telecharger_donnees_api.py' et 'process_prix_spot_data.py' sont présents")
    sys.exit(1)

def main():
    """Fonction principale qui orchestre le téléchargement et le processing"""
    print("🚀 METASTAAQ - TÉLÉCHARGEMENT ET TRAITEMENT DES DONNÉES")
    print("="*70)
    print(f"⏰ Début du traitement: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # --- PARAMETRES ---
    # Coordonnées de Meaux (77)
    LATITUDE_MEAUX = 48.96
    LONGITUDE_MEAUX = 2.88
    
    # Clé API ENTSO-E
    ENTSOE_API_KEY = os.getenv('ENTSOE_API_TOKEN', "9d9b8840-56e2-4993-9385-47cfe2b8183f")
    
    # Années à télécharger
    ANNEE_DEBUT = 2020
    ANNEE_FIN = 2024
    
    print(f"📍 Localisation: Meaux (Lat: {LATITUDE_MEAUX}, Lon: {LONGITUDE_MEAUX})")
    print(f"📅 Période: {ANNEE_DEBUT} - {ANNEE_FIN} (5 années)")
    
    # Variables pour suivre le succès des opérations
    fichier_pv = None
    fichier_prix = None
    fichier_prix_processed = None
    
    # ================================
    # ÉTAPE 1: TÉLÉCHARGEMENT DES DONNÉES SOLAIRES
    # ================================
    print("\n" + "="*50)
    print("📊 ÉTAPE 1: DONNÉES SOLAIRES PVGIS")
    print("="*50)
    
    try:
        fichier_pv = telecharger_donnees_pvgis_multi_annees(
            LATITUDE_MEAUX, 
            LONGITUDE_MEAUX, 
            ANNEE_DEBUT, 
            ANNEE_FIN
        )
        if fichier_pv:
            print(f"✅ Données solaires téléchargées: {fichier_pv}")
        else:
            print("❌ Échec du téléchargement des données solaires")
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement des données solaires: {e}")
    
    # ================================
    # ÉTAPE 2: TÉLÉCHARGEMENT DES PRIX SPOT
    # ================================
    print("\n" + "="*50)
    print("💰 ÉTAPE 2: DONNÉES PRIX SPOT ENTSO-E")
    print("="*50)
    
    try:
        fichier_prix = telecharger_donnees_entsoe_5_ans(ENTSOE_API_KEY, pays_code='FR')
        if fichier_prix:
            print(f"✅ Données prix spot téléchargées: {fichier_prix}")
        else:
            print("❌ Échec du téléchargement des données prix spot")
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement des données prix spot: {e}")
    
    # ================================
    # ÉTAPE 3: TRAITEMENT DES DONNÉES PRIX SPOT
    # ================================
    print("\n" + "="*50)
    print("🔄 ÉTAPE 3: TRAITEMENT DES DONNÉES PRIX SPOT")
    print("="*50)
    
    if fichier_prix:
        try:
            df_processed, fichier_prix_processed = process_prix_spot(fichier_prix)
            if df_processed is not None:
                print(f"✅ Données prix spot traitées: {fichier_prix_processed}")
            else:
                print("❌ Échec du traitement des données prix spot")
        except Exception as e:
            print(f"❌ Erreur lors du traitement des données prix spot: {e}")
    else:
        print("⚠️  Pas de fichier prix spot à traiter")
    
    # ================================
    # RÉSUMÉ FINAL
    # ================================
    print("\n" + "="*70)
    print("📋 RÉSUMÉ FINAL")
    print("="*70)
    
    print(f"⏰ Fin du traitement: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📁 Fichiers générés:")
    
    if fichier_pv:
        print(f"   ✅ Données solaires: {fichier_pv}")
    else:
        print(f"   ❌ Données solaires: Échec")
    
    if fichier_prix:
        print(f"   ✅ Données prix spot brutes: {fichier_prix}")
    else:
        print(f"   ❌ Données prix spot brutes: Échec")
    
    if fichier_prix_processed:
        print(f"   ✅ Données prix spot traitées: {fichier_prix_processed}")
    else:
        print(f"   ❌ Données prix spot traitées: Échec")
    
    # Vérifier si tout s'est bien passé
    succes_total = all([fichier_pv, fichier_prix, fichier_prix_processed])
    
    if succes_total:
        print("\n🎉 SUCCÈS: Toutes les données ont été téléchargées et traitées avec succès!")
        print("👉 Vous pouvez maintenant utiliser les fichiers CSV générés pour vos analyses")
    else:
        print("\n⚠️  SUCCÈS PARTIEL: Certaines opérations ont échoué")
        print("👉 Vérifiez les messages d'erreur ci-dessus")
    
    print("\n" + "="*70)
    
    return succes_total

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("🏁 Script terminé avec succès!")
            sys.exit(0)
        else:
            print("🏁 Script terminé avec des erreurs")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        sys.exit(1) 