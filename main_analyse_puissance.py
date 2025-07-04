#!/usr/bin/env python3
"""
Script principal pour l'analyse de puissance disponible METASTAAQ
Analyse les heures disponibles en fonction du coût d'achat d'électricité
"""

import sys
import os
from analyse_prix_spot import analyse_puissance_disponible

def main():
    """Fonction principale pour lancer l'analyse de puissance disponible"""
    
    print("🚀 LANCEMENT DE L'ANALYSE DE PUISSANCE DISPONIBLE")
    print("="*60)
    print("📋 Cette analyse va générer:")
    print("   • 5 tableaux par année (2020-2024) avec les heures disponibles")
    print("   • 5 graphiques par année")
    print("   • 2 analyses de saisonnalité (2023 & 2024)")
    print("   • 2 graphiques de saisonnalité")
    print("   • 2 fichiers Excel avec tous les résultats")
    print("="*60)
    
    # Vérifier que les données sont disponibles
    if not os.path.exists('donnees_prix_spot_FR_2020_2025.csv'):
        print("❌ Fichier 'donnees_prix_spot_FR_2020_2025.csv' non trouvé!")
        print("💡 Veuillez vous assurer que le fichier est dans le répertoire courant.")
        sys.exit(1)
    
    # Créer le dossier de résultats s'il n'existe pas
    os.makedirs('analyse_data_2024_2025', exist_ok=True)
    print("📁 Dossier 'analyse_data_2024_2025' créé/vérifié")
    
    try:
        # Lancer l'analyse
        analyse_puissance_disponible()
        
        print("\n🎉 ANALYSE TERMINÉE AVEC SUCCÈS!")
        print("\n📊 Résultats disponibles dans:")
        print("   • analyse_data_2024_2025/analyse_heures_disponibles_par_annee.xlsx")
        print("   • analyse_data_2024_2025/analyse_saisonnalite_2023_2024.xlsx")
        print("   • analyse_data_2024_2025/analyse_heures_disponibles_XXXX.png")
        print("   • analyse_data_2024_2025/analyse_saisonnalite_XXXX.png")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        print(f"💡 Vérifiez que toutes les dépendances sont installées:")
        print("   pip install pandas matplotlib seaborn openpyxl")
        sys.exit(1)

if __name__ == "__main__":
    main() 