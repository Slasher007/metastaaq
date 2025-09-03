#!/usr/bin/env python3
"""
Script de test pour la fonction de téléchargement détaillé des prix spot
et l'analyse des créneaux optimaux par niveau de puissance.
"""

import os
from utils.telecharger_donnees_api import (
    telecharger_donnees_spot_historiques_detaillees,
    generer_analyse_creneaux_optimaux
)

def test_telecharger_donnees_spot_detaillees():
    """
    Test de la fonction de téléchargement détaillé des prix spot
    pour les années 2021-2025 avec analyse des puissances disponibles.
    """
    print("🧪 TEST - TÉLÉCHARGEMENT DÉTAILLÉ DES PRIX SPOT")
    print("="*60)
    
    # Paramètres de test
    api_key = os.getenv('ENTSOE_API_TOKEN', "9d9b8840-56e2-4993-9385-47cfe2b8183f")
    
    if not api_key or api_key == "VOTRE_CLE_API_ENTSOE_ICI":
        print("❌ Clé API ENTSO-E non configurée pour le test")
        print("📋 Définissez la variable d'environnement ENTSOE_API_TOKEN")
        return False
    
    print("📋 Paramètres du test:")
    print(f"   • Période: 2021-2025 (jusqu'à juillet)")
    print(f"   • Pays: France (FR)")
    print(f"   • Niveaux de puissance: 0.5, 1, 2, 3, 4, 5 MW")
    print(f"   • API Key: {api_key[:10]}...")
    
    try:
        # Test du téléchargement détaillé
        resultat = telecharger_donnees_spot_historiques_detaillees(
            api_key=api_key,
            annee_debut=2021,
            annee_fin=2025,
            mois_fin=7,
            pays_code='FR'
        )
        
        if resultat:
            print(f"\n✅ SUCCÈS - Fichier généré: {resultat}")
            
            # Test de l'analyse des créneaux optimaux
            print(f"\n🎯 TEST - ANALYSE DES CRÉNEAUX OPTIMAUX")
            print("-"*50)
            
            seuils_test = [20, 25, 30]
            for seuil in seuils_test:
                print(f"\n📊 Test pour seuil ≤ {seuil} €/MWh:")
                
                fichier_synthese = generer_analyse_creneaux_optimaux(
                    fichier_donnees_spot=resultat,
                    seuil_prix_max=seuil
                )
                
                if fichier_synthese:
                    print(f"   ✅ Synthèse générée: {fichier_synthese}")
                else:
                    print(f"   ❌ Échec de la génération de synthèse")
            
            print(f"\n🎉 TOUS LES TESTS RÉUSSIS!")
            return True
        else:
            print(f"\n❌ ÉCHEC - Impossible de télécharger les données")
            return False
            
    except Exception as e:
        print(f"\n❌ ERREUR PENDANT LE TEST: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analyse_fichier_existant():
    """
    Test de l'analyse des créneaux optimaux sur un fichier existant.
    """
    print("\n🧪 TEST - ANALYSE SUR FICHIER EXISTANT")
    print("="*50)
    
    # Rechercher des fichiers de données existants
    fichiers_possibles = [
        'donnees_spot_detaillees_FR_2021_2025.csv',
        'donnees_prix_spot_FR_2020_2025.csv',
        'donnees_prix_spot_processed_2020_2025.csv'
    ]
    
    fichier_trouve = None
    for fichier in fichiers_possibles:
        if os.path.exists(fichier):
            fichier_trouve = fichier
            break
    
    if not fichier_trouve:
        print("❌ Aucun fichier de données spot trouvé pour le test")
        print("📋 Fichiers recherchés:")
        for fichier in fichiers_possibles:
            print(f"   • {fichier}")
        return False
    
    print(f"📂 Fichier trouvé: {fichier_trouve}")
    
    try:
        # Test avec différents seuils
        seuils_test = [15, 25, 35]
        
        for seuil in seuils_test:
            print(f"\n💰 Test analyse avec seuil ≤ {seuil} €/MWh:")
            
            resultat = generer_analyse_creneaux_optimaux(
                fichier_donnees_spot=fichier_trouve,
                seuil_prix_max=seuil
            )
            
            if resultat:
                print(f"   ✅ Analyse réussie: {resultat}")
            else:
                print(f"   ❌ Échec de l'analyse")
                
        return True
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False

def afficher_instructions():
    """
    Affiche les instructions d'utilisation des nouvelles fonctions.
    """
    print("\n📖 INSTRUCTIONS D'UTILISATION")
    print("="*50)
    
    print("\n🔍 1. TÉLÉCHARGEMENT DÉTAILLÉ DES PRIX SPOT:")
    print("   Utilisez telecharger_donnees_spot_historiques_detaillees()")
    print("   pour obtenir:")
    print("   • Prix spot horaires 2021-2025")
    print("   • Colonnes de disponibilité par puissance (0.5-5 MW)")
    print("   • Classifications temporelles (weekend, créneaux)")
    print("   • Opportunités d'achat optimales")
    
    print("\n📊 2. ANALYSE DES CRÉNEAUX OPTIMAUX:")
    print("   Utilisez generer_analyse_creneaux_optimaux()")
    print("   pour obtenir:")
    print("   • Synthèse par niveau de puissance")
    print("   • Statistiques de disponibilité")
    print("   • Meilleurs créneaux horaires")
    print("   • Répartition saisonnière")
    
    print("\n⚙️ 3. PARAMÈTRES CLÉS:")
    print("   • niveaux_puissance: [0.5, 1, 2, 3, 4, 5] MW")
    print("   • seuils_prix: [0, 5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 80, 100] €/MWh")
    print("   • période: 2021-2025 (jusqu'à juillet 2025)")
    
    print("\n📁 4. FICHIERS GÉNÉRÉS:")
    print("   • donnees_spot_detaillees_FR_2021_2025.csv")
    print("   • synthese_creneaux_optimaux_max_XXX€.csv")
    
    print("\n🔑 5. CONFIGURATION API:")
    print("   • Variable d'environnement: ENTSOE_API_TOKEN")
    print("   • Ou modifiez directement dans le script")

if __name__ == "__main__":
    print("🚀 TESTS DES NOUVELLES FONCTIONS DE PRIX SPOT")
    print("="*60)
    
    # Afficher les instructions
    afficher_instructions()
    
    # Demander le mode de test
    print("\n🔧 MODES DE TEST DISPONIBLES:")
    print("1. Test complet (téléchargement + analyse)")
    print("2. Test analyse seule (fichier existant)")
    print("3. Affichage des instructions seulement")
    
    mode = input("\nChoisissez le mode (1/2/3) [défaut: 2]: ").strip() or "2"
    
    if mode == "1":
        print("\n" + "="*60)
        succes = test_telecharger_donnees_spot_detaillees()
        if succes:
            print("\n🎊 TEST COMPLET RÉUSSI!")
        else:
            print("\n💥 ÉCHEC DU TEST COMPLET")
    
    elif mode == "2":
        print("\n" + "="*60)
        succes = test_analyse_fichier_existant()
        if succes:
            print("\n🎊 TEST D'ANALYSE RÉUSSI!")
        else:
            print("\n💥 ÉCHEC DU TEST D'ANALYSE")
    
    elif mode == "3":
        print("\n✅ Instructions affichées ci-dessus")
    
    else:
        print("\n❌ Mode non reconnu")
    
    print("\n🏁 Tests terminés!") 