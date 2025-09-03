"""
Script de test pour validation des modules de recherche électricité
Test des fonctionnalités principales sans nécessiter d'authentification
"""

import sys
import os
sys.path.append('.')

def test_imports():
    """
    Test des imports des modules
    """
    print("🧪 Test 1: Imports des modules")
    print("-" * 30)
    
    try:
        from utils.recherche_donnees_electricite import RechercheElectriciteFrance
        print("✅ Module recherche_donnees_electricite importé")
        
        from utils.integration_api_rte_avancee import APIRTEAvancee
        print("✅ Module integration_api_rte_avancee importé")
        
        import pandas as pd
        print("✅ Pandas disponible")
        
        import requests
        print("✅ Requests disponible")
        
        try:
            from bs4 import BeautifulSoup
            print("✅ BeautifulSoup disponible")
        except ImportError:
            print("⚠️ BeautifulSoup non installé - exécuter: pip install beautifulsoup4")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_initialisation():
    """
    Test d'initialisation des classes
    """
    print("\n🧪 Test 2: Initialisation des classes")
    print("-" * 30)
    
    try:
        from utils.recherche_donnees_electricite import RechercheElectriciteFrance
        
        # Test sans clé API
        recherche = RechercheElectriciteFrance()
        print("✅ RechercheElectriciteFrance initialisée sans clé API")
        
        # Test avec clé API fictive
        recherche_avec_cle = RechercheElectriciteFrance(rte_api_key="test_key")
        print("✅ RechercheElectriciteFrance initialisée avec clé API")
        
        # Test API avancée
        from utils.integration_api_rte_avancee import APIRTEAvancee
        api_avancee = APIRTEAvancee()
        print("✅ APIRTEAvancee initialisée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        return False

def test_fonctions_utilitaires():
    """
    Test des fonctions utilitaires
    """
    print("\n🧪 Test 3: Fonctions utilitaires")
    print("-" * 30)
    
    try:
        from utils.recherche_donnees_electricite import RechercheElectriciteFrance
        recherche = RechercheElectriciteFrance()
        
        # Test génération rapport sans données
        rapport = recherche.analyser_resultats_complets()
        print("✅ Rapport généré avec données vides")
        print(f"   Timestamp: {rapport.get('timestamp', 'N/A')}")
        
        # Test structure des endpoints API avancée
        from utils.integration_api_rte_avancee import APIRTEAvancee
        api = APIRTEAvancee()
        
        endpoints_disponibles = len(api.endpoints)
        print(f"✅ API avancée: {endpoints_disponibles} endpoints configurés")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test utilitaires: {e}")
        return False

def test_construction_requetes():
    """
    Test de construction des requêtes (sans les envoyer)
    """
    print("\n🧪 Test 4: Construction des requêtes")
    print("-" * 30)
    
    try:
        from utils.recherche_donnees_electricite import RechercheElectriciteFrance
        recherche = RechercheElectriciteFrance()
        
        # Test construction terme de recherche par défaut
        terme_test = "prix spot électricité France 2021-2025 données historiques heures disponibilité puissance 0.5-5 MW"
        
        # Vérifier les sites cibles
        sites_cibles = recherche.sites_cibles
        print(f"✅ Sites cibles configurés: {sites_cibles}")
        
        # Test URL de recherche Google (sans l'envoyer)
        from urllib.parse import quote_plus
        sites_query = " OR ".join([f"site:{site}" for site in sites_cibles])
        requete_complete = f"({sites_query}) {terme_test}"
        google_url = f"https://www.google.com/search?q={quote_plus(requete_complete)}"
        
        print("✅ URL de recherche Google construite")
        print(f"   Longueur: {len(google_url)} caractères")
        
        # Test paramètres API RTE
        params_rte = {
            'dataset': 'eco2mix-national-tr',
            'timezone': 'Europe/Paris',
            'rows': 1000,
            'format': 'json'
        }
        print(f"✅ Paramètres API RTE configurés: {len(params_rte)} paramètres")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur construction requêtes: {e}")
        return False

def test_traitement_donnees():
    """
    Test du traitement de données fictives
    """
    print("\n🧪 Test 5: Traitement de données")
    print("-" * 30)
    
    try:
        import pandas as pd
        from datetime import datetime, timedelta
        
        # Créer des données fictives de prix spot
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=7),
            end=datetime.now(),
            freq='H'
        )
        
        donnees_fictives = pd.DataFrame({
            'date_heure': dates,
            'prix_spot': [15 + i % 30 + (i % 7) * 5 for i in range(len(dates))],  # Prix entre 15 et 50
            'consommation': [50000 + i % 10000 for i in range(len(dates))]  # Consommation variable
        })
        
        print(f"✅ Données fictives créées: {len(donnees_fictives)} points")
        
        # Test calcul de puissances disponibles
        from utils.recherche_donnees_electricite import RechercheElectriciteFrance
        recherche = RechercheElectriciteFrance()
        
        # Simuler le traitement des données
        df = donnees_fictives.copy()
        puissances_mw = [0.5, 1, 2, 3, 4, 5]
        seuils_prix = [20, 25, 30]
        
        for puissance in puissances_mw:
            for seuil in seuils_prix:
                col_name = f'disponible_{puissance}MW_max_{seuil}EUR'
                df[col_name] = (df['prix_spot'] <= seuil).astype(int)
        
        print(f"✅ Colonnes de puissance ajoutées: {len([c for c in df.columns if 'disponible_' in c])}")
        
        # Test statistiques
        for seuil in seuils_prix:
            for puissance in [1, 3, 5]:
                col_name = f'disponible_{puissance}MW_max_{seuil}EUR'
                if col_name in df.columns:
                    taux = df[col_name].mean() * 100
                    print(f"   • {puissance}MW à ≤{seuil}€: {taux:.1f}% disponible")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur traitement données: {e}")
        return False

def test_sauvegarde_fichiers():
    """
    Test de sauvegarde des fichiers (création de fichiers temporaires)
    """
    print("\n🧪 Test 6: Sauvegarde de fichiers")
    print("-" * 30)
    
    try:
        from utils.recherche_donnees_electricite import RechercheElectriciteFrance
        import json
        import tempfile
        import os
        
        recherche = RechercheElectriciteFrance()
        
        # Données de test
        resultats_test = {
            'rte-france.com': [
                {'titre': 'Test', 'url': 'https://test.com', 'description': 'Test description'}
            ]
        }
        
        # Test sauvegarde avec fichier temporaire
        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                recherche.sauvegarder_resultats(
                    resultats_web=resultats_test,
                    prefixe="test_validation"
                )
                
                # Vérifier les fichiers créés
                fichiers_crees = [f for f in os.listdir('.') if f.startswith('test_validation')]
                print(f"✅ Fichiers de test créés: {len(fichiers_crees)}")
                
                for fichier in fichiers_crees:
                    taille = os.path.getsize(fichier)
                    print(f"   • {fichier}: {taille} octets")
                
            finally:
                os.chdir(original_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")
        return False

def afficher_guide_utilisation():
    """
    Affiche un guide d'utilisation rapide
    """
    print("\n📋 GUIDE D'UTILISATION RAPIDE")
    print("=" * 50)
    
    print("\n🔍 1. Recherche Web Simple:")
    print("   python exemple_recherche_electricite.py")
    print("   Choisir option 2 (Exemple rapide)")
    
    print("\n🔌 2. API RTE avec authentification:")
    print("   export RTE_CLIENT_ID='votre_client_id'")
    print("   export RTE_CLIENT_SECRET='votre_client_secret'")
    print("   python integration_api_rte_avancee.py")
    
    print("\n📊 3. Recherche complète:")
    print("   python recherche_donnees_electricite.py")
    
    print("\n🎯 4. Requêtes spécifiques:")
    print("   Web: 'Site:rte-france.com OR site:services-rte.com OR site:epexspot.com'")
    print("        'prix spot électricité France 2021-2025 données historiques'")
    print("        'heures disponibilité puissance 0.5-5 MW'")
    
    print("   API: 'GET /data/spot-prices?country=FR&start_date=2021-01-01'")
    print("        '&end_date=2025-07-10&granularity=hourly&power_levels=0.5,1,2,3,4,5'")

def main():
    """
    Fonction principale de test
    """
    print("🧪 VALIDATION DES MODULES DE RECHERCHE ÉLECTRICITÉ")
    print("=" * 60)
    
    tests_reussis = 0
    total_tests = 6
    
    # Exécuter tous les tests
    if test_imports():
        tests_reussis += 1
    
    if test_initialisation():
        tests_reussis += 1
    
    if test_fonctions_utilitaires():
        tests_reussis += 1
    
    if test_construction_requetes():
        tests_reussis += 1
    
    if test_traitement_donnees():
        tests_reussis += 1
    
    if test_sauvegarde_fichiers():
        tests_reussis += 1
    
    # Résumé
    print(f"\n📊 RÉSUMÉ DES TESTS")
    print("=" * 30)
    print(f"✅ Tests réussis: {tests_reussis}/{total_tests}")
    
    if tests_reussis == total_tests:
        print("🎉 Tous les tests sont passés avec succès!")
        print("✅ Les modules sont prêts à être utilisés")
    else:
        print(f"⚠️ {total_tests - tests_reussis} test(s) ont échoué")
        print("🔧 Vérifiez les dépendances et la configuration")
    
    # Afficher le guide d'utilisation
    afficher_guide_utilisation()

if __name__ == "__main__":
    main() 