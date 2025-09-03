"""
Exemple d'utilisation du module de recherche de données électricité
Script simplifié pour tester les fonctionnalités de base
"""

from recherche_donnees_electricite import RechercheElectriciteFrance
import pandas as pd
import os

def exemple_recherche_complete():
    """
    Exemple complet de recherche de données électricité
    """
    print("🚀 EXEMPLE - Recherche de données électricité française")
    print("=" * 60)
    
    # Configuration
    rte_api_key = os.getenv('RTE_API_KEY')  # Optionnel
    if not rte_api_key:
        print("ℹ️  Variable d'environnement RTE_API_KEY non définie")
        print("   Les fonctions d'API authentifiée ne seront pas disponibles")
    
    # Initialisation du module de recherche
    recherche = RechercheElectriciteFrance(rte_api_key=rte_api_key)
    
    # Test 1: Recherche web simple
    print("\n🔍 Test 1: Recherche web sur sites spécialisés")
    print("-" * 50)
    
    terme_test = "prix spot électricité France données historiques"
    resultats_web = recherche.recherche_web_donnees_spot(terme_test)
    
    print(f"📋 Recherche effectuée pour: '{terme_test}'")
    total_resultats = 0
    
    for site, resultats in resultats_web.items():
        if isinstance(resultats, list):
            print(f"   • {site}: {len(resultats)} résultat(s)")
            total_resultats += len(resultats)
            
            # Afficher le premier résultat de chaque site
            if resultats:
                premier = resultats[0]
                print(f"     Exemple: {premier['titre'][:60]}...")
    
    print(f"✅ Total: {total_resultats} résultats trouvés")
    
    # Test 2: API RTE éCO2mix (données ouvertes)
    print("\n🔌 Test 2: API RTE éCO2mix (Open Data)")
    print("-" * 50)
    
    # Période de test réduite pour plus de rapidité
    donnees_api = recherche.recherche_api_rte_eco2mix(
        date_debut='2024-01-01',
        date_fin='2024-01-31'  # Test sur janvier 2024 seulement
    )
    
    if not donnees_api.empty:
        print(f"✅ Données récupérées: {len(donnees_api)} enregistrements")
        print(f"📊 Colonnes disponibles ({len(donnees_api.columns)}): {list(donnees_api.columns)[:5]}...")
        
        # Afficher quelques statistiques
        if 'date_heure' in donnees_api.columns:
            periode = f"de {donnees_api['date_heure'].min()} à {donnees_api['date_heure'].max()}"
            print(f"📅 Période couverte: {periode}")
    else:
        print("⚠️ Aucune donnée récupérée (normal si l'API est indisponible)")
    
    # Test 3: Analyse des résultats
    print("\n📊 Test 3: Génération du rapport d'analyse")
    print("-" * 50)
    
    rapport = recherche.analyser_resultats_complets(resultats_web, donnees_api)
    
    print("📋 Contenu du rapport:")
    print(f"   • Timestamp: {rapport['timestamp']}")
    print(f"   • Sites analysés: {rapport['recherche_web'].get('sites_analyses', [])}")
    print(f"   • Total résultats web: {rapport['recherche_web'].get('total_resultats', 0)}")
    print(f"   • Enregistrements API: {rapport['donnees_api'].get('nombre_enregistrements', 0)}")
    
    print("\n🎯 Recommandations:")
    for rec in rapport.get('recommandations', []):
        print(f"   {rec}")
    
    # Test 4: Sauvegarde
    print("\n💾 Test 4: Sauvegarde des résultats")
    print("-" * 50)
    
    recherche.sauvegarder_resultats(
        resultats_web=resultats_web,
        donnees_api=donnees_api,
        rapport=rapport,
        prefixe="test_recherche"
    )
    
    print("✅ Exemple terminé avec succès!")
    return resultats_web, donnees_api, rapport

def exemple_recherche_rapide():
    """
    Exemple rapide pour tester uniquement les fonctions de base
    """
    print("⚡ EXEMPLE RAPIDE - Test des fonctions de base")
    print("=" * 50)
    
    recherche = RechercheElectriciteFrance()
    
    # Test recherche web simple
    print("🔍 Test recherche web...")
    resultats = recherche.recherche_web_donnees_spot(
        "prix électricité France RTE EPEX"
    )
    
    nb_resultats = sum(len(r) for r in resultats.values() if isinstance(r, list))
    print(f"✅ {nb_resultats} résultats web trouvés")
    
    # Générer un petit rapport
    rapport = recherche.analyser_resultats_complets(resultats_web=resultats)
    print(f"📊 Rapport généré à {rapport['timestamp']}")
    
    return resultats, rapport

def afficher_structure_api_rte():
    """
    Affiche la structure recommandée pour les appels API RTE
    """
    print("📋 STRUCTURE RECOMMANDÉE POUR L'API RTE")
    print("=" * 50)
    
    print("🔐 API RTE éCO2mix authentifiée (nécessite clé API):")
    print("   Base URL: https://digital.iservices.rte-france.com/open_api/")
    print("   Endpoints suggérés:")
    print("   • /consumption/short-term -> Consommation prévisionnelle")
    print("   • /generation/aggregate -> Production agrégée")
    print("   • /exchange/day-ahead-prices -> Prix day-ahead")
    
    print("\n🌐 API RTE Open Data (accès libre):")
    print("   Base URL: https://odre.opendatasoft.com/api/records/1.0/")
    print("   Datasets principaux:")
    print("   • eco2mix-national-tr -> Mix énergétique temps réel")
    print("   • eco2mix-regional-tr -> Mix régional temps réel")
    
    print("\n📊 Paramètres suggérés pour votre recherche:")
    exemple_params = {
        'country': 'FR',
        'start_date': '2021-01-01',
        'end_date': '2025-07-10',
        'granularity': 'hourly',
        'power_levels': '0.5,1,2,3,4,5'
    }
    
    for param, valeur in exemple_params.items():
        print(f"   • {param}: {valeur}")
    
    print("\n🔧 Pour obtenir une clé API RTE:")
    print("   1. Créer un compte sur: https://data.rte-france.com/")
    print("   2. Demander l'accès aux API")
    print("   3. Définir la variable d'environnement: export RTE_API_KEY='votre_cle'")

if __name__ == "__main__":
    print("🎯 Choisissez un exemple à exécuter:")
    print("1. Exemple complet (recherche web + API)")
    print("2. Exemple rapide (recherche web seulement)")
    print("3. Afficher structure API RTE")
    
    choix = input("\nVotre choix (1/2/3): ").strip()
    
    if choix == "1":
        exemple_recherche_complete()
    elif choix == "2":
        exemple_recherche_rapide()
    elif choix == "3":
        afficher_structure_api_rte()
    else:
        print("Choix invalide. Exécution de l'exemple rapide par défaut...")
        exemple_recherche_rapide() 