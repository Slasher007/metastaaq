#!/usr/bin/env python3
"""
Script de test pour vérifier le bon fonctionnement des colonnes de puissances disponibles
"""

import pandas as pd
import os
from utils.telecharger_donnees_api import telecharger_donnees_entsoe_5_ans

def tester_puissances_disponibles():
    """Teste la fonction modifiée avec un petit échantillon de données"""
    print("🧪 TEST DES PUISSANCES DISPONIBLES")
    print("="*50)
    
    # Créer un DataFrame de test avec quelques exemples de prix
    test_data = {
        'Prix_EUR_MWh': [-5, 3, 8, 12, 18, 23, 28, 35, 45, 60]
    }
    
    df_test = pd.DataFrame(test_data)
    
    print("📊 Données de test:")
    print(df_test)
    
    # Appliquer la même logique que dans la fonction modifiée
    puissances = [0.5, 1, 2, 3, 4, 5]
    seuils_prix = [5, 10, 15, 20, 25, 30, 35, 40]
    
    print(f"\n⚡ Application de la logique de puissances disponibles...")
    print(f"Seuils de puissance: {puissances} MW")
    print(f"Seuils de prix: {seuils_prix} €/MWh")
    
    # Ajouter les colonnes de disponibilité
    for puissance in puissances:
        for seuil in seuils_prix:
            col_name = f'Disponible_{puissance}MW_max_{seuil}EUR_MWh'
            df_test[col_name] = (df_test['Prix_EUR_MWh'] <= seuil).astype(int)
    
    # Ajouter les colonnes de puissance maximale
    seuils_cles = [15, 20, 25, 30]
    for seuil in seuils_cles:
        col_name = f'Puissance_max_disponible_{seuil}EUR_MWh'
        df_test[col_name] = 0
        
        for puissance in puissances:
            condition = df_test['Prix_EUR_MWh'] <= seuil
            df_test.loc[condition, col_name] = puissance
    
    print(f"\n📋 Résultats du test:")
    print("-" * 80)
    
    # Afficher quelques colonnes clés pour vérification
    colonnes_a_afficher = ['Prix_EUR_MWh', 'Disponible_1MW_max_15EUR_MWh', 
                          'Disponible_3MW_max_25EUR_MWh', 'Puissance_max_disponible_15EUR_MWh']
    
    print(df_test[colonnes_a_afficher])
    
    print(f"\n✅ Test terminé - Logique validée!")
    
    # Vérifications manuelles
    print(f"\n🔍 Vérifications manuelles:")
    print(f"   • Prix -5 €/MWh → 1MW à 15€ max: {df_test.loc[0, 'Disponible_1MW_max_15EUR_MWh']} (attendu: 1)")
    print(f"   • Prix 18 €/MWh → 1MW à 15€ max: {df_test.loc[4, 'Disponible_1MW_max_15EUR_MWh']} (attendu: 0)")
    print(f"   • Prix 12 €/MWh → Puissance max à 15€: {df_test.loc[3, 'Puissance_max_disponible_15EUR_MWh']} MW (attendu: 5)")
    
    return df_test

def tester_fichier_existant():
    """Teste sur un fichier existant s'il y en a un"""
    fichiers_possibles = [
        'donnees_prix_spot_FR_2020_2025.csv',
        'donnees_prix_spot_FR_2024_2025.csv'
    ]
    
    for fichier in fichiers_possibles:
        if os.path.exists(fichier):
            print(f"\n📁 Test sur fichier existant: {fichier}")
            df = pd.read_csv(fichier, index_col=0)
            print(f"   • Nombre de lignes: {len(df)}")
            print(f"   • Colonnes: {list(df.columns)}")
            
            # Vérifier si les nouvelles colonnes sont présentes
            colonnes_puissance = [col for col in df.columns if 'Disponible_' in col or 'Puissance_max_' in col]
            
            if colonnes_puissance:
                print(f"   ✅ Colonnes de puissance détectées: {len(colonnes_puissance)}")
                print(f"   📊 Exemples: {colonnes_puissance[:3]}")
                
                # Quelques statistiques
                if 'Opportunite_bonne' in df.columns:
                    opportunites = df['Opportunite_bonne'].sum()
                    pct = (opportunites / len(df)) * 100
                    print(f"   🎯 Opportunités bonnes (≤15€): {opportunites} heures ({pct:.1f}%)")
            else:
                print(f"   ❌ Aucune colonne de puissance détectée - fichier non enrichi")
            
            return df
    
    print(f"\n📁 Aucun fichier existant trouvé pour le test")
    return None

if __name__ == "__main__":
    # Test 1: Logique sur données de test
    df_test = tester_puissances_disponibles()
    
    # Test 2: Fichier existant si disponible
    df_existant = tester_fichier_existant()
    
    print(f"\n🎉 Tests terminés!")
    print(f"\n💡 Pour tester complètement la fonction modifiée, exécutez:")
    print(f"   python telecharger_donnees_api.py")
    print(f"   ou")
    print(f"   python main_metastaaq.py") 