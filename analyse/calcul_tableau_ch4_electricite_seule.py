#!/usr/bin/env python3
"""
Calcul simplifié des coûts de production CH4 - ÉLECTRICITÉ SEULE
Basé sur la consommation spécifique METASTAAQ : 45,2 MWh élec / MWh CH4
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

def calculer_cout_production_ch4_electricite_seule(prix_elec):
    """
    Calcule le coût de production CH4 en ne considérant que l'électricité
    
    Parameters:
    - prix_elec: Prix de l'électricité en €/MWh
    
    Returns:
    - Coût de production en €/MWh CH4 (électricité seule)
    """
    
    # Consommation spécifique d'électricité pour 1 MWh de CH4
    # D'après analyse METASTAAQ : 904 GWh élec / 20 GWh CH4/an = 45,2 MWh élec / MWh CH4
    CONSOMMATION_SPECIFIQUE_ELEC = 45.2  # MWh élec / MWh CH4
    
    # Calcul direct : coût électricité pour produire 1 MWh de CH4
    cout_production_ch4 = CONSOMMATION_SPECIFIQUE_ELEC * prix_elec
    
    return cout_production_ch4

def generer_tableau_electricite_seule():
    """
    Génère le tableau des coûts CH4 basé uniquement sur l'électricité
    """
    print("⚡ CALCUL DES COÛTS CH4 - ÉLECTRICITÉ SEULE")
    print("Consommation spécifique METASTAAQ : 45,2 MWh élec / MWh CH4")
    print("="*70)
    
    # Prix d'électricité à analyser
    prix_elec_range = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]  # €/MWh
    
    # Calcul des coûts CH4 correspondants
    couts_ch4 = []
    
    print("\n📊 CALCULS :")
    print("-"*50)
    print("Prix élec (€/MWh) | Coût CH4 (€/MWh)")
    print("-"*50)
    
    for prix_elec in prix_elec_range:
        cout_ch4 = calculer_cout_production_ch4_electricite_seule(prix_elec)
        couts_ch4.append(cout_ch4)
        print(f"{prix_elec:>8} €/MWh     |  {cout_ch4:>8.1f} €/MWh")
    
    print("-"*50)
    
    # Créer un DataFrame pour faciliter l'analyse
    df_resultats = pd.DataFrame({
        'Prix_Electricite_EUR_MWh': prix_elec_range,
        'Cout_CH4_EUR_MWh': couts_ch4
    })
    
    return df_resultats

def creer_tableau_matriciel():
    """
    Crée un tableau matriciel similaire au format original
    mais avec différentes plages de prix
    """
    print("\n📋 CRÉATION DU TABLEAU MATRICIEL")
    print("="*50)
    
    # Prix d'électricité (plus de granularité)
    prix_elec_range = [5, 10, 15, 20, 25, 30, 35, 40]  # €/MWh
    
    # Différents scénarios (par exemple différentes années ou conditions)
    scenarios = [
        "Scénario Optimal",
        "Scénario Moyen", 
        "Scénario Défavorable",
        "Prix Spot Bas",
        "Prix Spot Élevé"
    ]
    
    # Créer le tableau matriciel
    tableau = pd.DataFrame(
        index=scenarios,
        columns=[f"{prix}€/MWh" for prix in prix_elec_range]
    )
    
    # Remplir le tableau (même calcul pour tous les scénarios car on ne considère que l'électricité)
    for i, scenario in enumerate(scenarios):
        for j, prix_elec in enumerate(prix_elec_range):
            cout_ch4 = calculer_cout_production_ch4_electricite_seule(prix_elec)
            tableau.iloc[i, j] = cout_ch4
    
    return tableau.astype(float)

def creer_visualisation_electricite_seule(df_resultats, tableau_matriciel):
    """
    Crée une visualisation des coûts CH4 vs prix électricité
    """
    print("\n📈 Création des visualisations...")
    
    # Configuration générale
    plt.style.use('default')
    fig = plt.figure(figsize=(16, 10))
    
    # 1. Graphique linéaire principal
    ax1 = plt.subplot(2, 2, 1)
    ax1.plot(df_resultats['Prix_Electricite_EUR_MWh'], df_resultats['Cout_CH4_EUR_MWh'], 
             marker='o', linewidth=3, markersize=8, color='blue', label='Coût CH4')
    
    # Ligne de référence METASTAAQ
    prix_ref = 30
    cout_ref_elec_seule = calculer_cout_production_ch4_electricite_seule(prix_ref)
    ax1.axhline(y=cout_ref_elec_seule, color='red', linestyle='--', linewidth=2, 
                label=f'Référence METASTAAQ ({prix_ref}€/MWh élec)')
    ax1.axvline(x=prix_ref, color='red', linestyle='--', linewidth=2, alpha=0.5)
    
    ax1.set_xlabel('Prix électricité (€/MWh)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Coût production CH4 (€/MWh)', fontsize=12, fontweight='bold')
    ax1.set_title('Coût Production CH4 vs Prix Électricité\n(Électricité seule - 45,2 MWh élec/MWh CH4)', 
                  fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Annotations
    ax1.annotate(f'{cout_ref_elec_seule:.0f} €/MWh CH4', 
                xy=(prix_ref, cout_ref_elec_seule), 
                xytext=(prix_ref+5, cout_ref_elec_seule+50),
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=10, fontweight='bold', color='red')
    
    # 2. Tableau matriciel (heatmap)
    ax2 = plt.subplot(2, 2, (2, 4))
    im = ax2.imshow(tableau_matriciel.values, cmap='RdYlGn_r', aspect='auto')
    
    # Configuration du tableau
    ax2.set_xticks(range(len(tableau_matriciel.columns)))
    ax2.set_yticks(range(len(tableau_matriciel.index)))
    ax2.set_xticklabels(tableau_matriciel.columns, rotation=0)
    ax2.set_yticklabels(tableau_matriciel.index)
    
    # Ajouter les valeurs dans chaque cellule
    for i in range(len(tableau_matriciel.index)):
        for j in range(len(tableau_matriciel.columns)):
            value = tableau_matriciel.iloc[i, j]
            color = 'white' if value > tableau_matriciel.median().median() else 'black'
            ax2.text(j, i, f'{value:.0f}', ha='center', va='center', 
                    fontweight='bold', fontsize=10, color=color)
    
    ax2.set_title('Tableau Coûts CH4 (€/MWh)\nÉlectricité Seule - Différents Scénarios', 
                  fontsize=13, fontweight='bold', pad=20)
    ax2.set_xlabel('Prix électricité (€/MWh)', fontsize=12, fontweight='bold')
    ax2.grid(True, color='black', linewidth=0.5)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax2, shrink=0.8)
    cbar.set_label('Coût CH4 (€/MWh)', rotation=270, labelpad=20)
    
    # 3. Graphique de comparaison avec objectifs
    ax3 = plt.subplot(2, 2, 3)
    
    # Objectifs de coût CH4
    objectif_competitif = 30  # €/MWh CH4 (objectif METASTAAQ)
    objectif_acceptable = 50  # €/MWh CH4
    
    ax3.plot(df_resultats['Prix_Electricite_EUR_MWh'], df_resultats['Cout_CH4_EUR_MWh'], 
             marker='o', linewidth=3, markersize=6, color='blue', label='Coût CH4 calculé')
    
    ax3.axhline(y=objectif_competitif, color='green', linestyle='-', linewidth=2, 
                label=f'Objectif compétitif ({objectif_competitif}€/MWh)')
    ax3.axhline(y=objectif_acceptable, color='orange', linestyle='-', linewidth=2, 
                label=f'Objectif acceptable ({objectif_acceptable}€/MWh)')
    
    # Zone de compétitivité
    ax3.fill_between(df_resultats['Prix_Electricite_EUR_MWh'], 0, objectif_competitif, 
                     alpha=0.2, color='green', label='Zone compétitive')
    ax3.fill_between(df_resultats['Prix_Electricite_EUR_MWh'], objectif_competitif, objectif_acceptable, 
                     alpha=0.2, color='orange', label='Zone acceptable')
    
    # Calcul du prix électricité pour atteindre les objectifs
    prix_elec_objectif_competitif = objectif_competitif / 45.2
    prix_elec_objectif_acceptable = objectif_acceptable / 45.2
    
    ax3.axvline(x=prix_elec_objectif_competitif, color='green', linestyle='--', alpha=0.7)
    ax3.axvline(x=prix_elec_objectif_acceptable, color='orange', linestyle='--', alpha=0.7)
    
    ax3.set_xlabel('Prix électricité (€/MWh)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Coût CH4 (€/MWh)', fontsize=12, fontweight='bold')
    ax3.set_title('Analyse de Compétitivité\nObjectifs vs Coûts Calculés', 
                  fontsize=13, fontweight='bold')
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)
    
    # Annotations pour les seuils
    ax3.annotate(f'Prix élec max\n{prix_elec_objectif_competitif:.1f}€/MWh', 
                xy=(prix_elec_objectif_competitif, objectif_competitif), 
                xytext=(prix_elec_objectif_competitif+3, objectif_competitif+30),
                arrowprops=dict(arrowstyle='->', color='green'),
                fontsize=9, fontweight='bold', color='green')
    
    plt.tight_layout()
    return fig

def analyser_resultats(df_resultats):
    """
    Analyse les résultats et fournit des insights
    """
    print("\n" + "="*70)
    print("📊 ANALYSE DES RÉSULTATS - ÉLECTRICITÉ SEULE")
    print("="*70)
    
    # Facteur de conversion
    facteur_conversion = 45.2
    print(f"\n🔍 FACTEUR DE CONVERSION METASTAAQ:")
    print(f"   • {facteur_conversion} MWh électricité → 1 MWh CH4")
    print(f"   • Formule : Coût CH4 = Prix élec × {facteur_conversion}")
    
    # Calculs pour objectifs
    objectif_competitif = 30  # €/MWh CH4
    objectif_acceptable = 50  # €/MWh CH4
    
    prix_elec_max_competitif = objectif_competitif / facteur_conversion
    prix_elec_max_acceptable = objectif_acceptable / facteur_conversion
    
    print(f"\n🎯 POUR ATTEINDRE LES OBJECTIFS :")
    print(f"   • Objectif compétitif (30€/MWh CH4) : Prix élec ≤ {prix_elec_max_competitif:.1f}€/MWh")
    print(f"   • Objectif acceptable (50€/MWh CH4) : Prix élec ≤ {prix_elec_max_acceptable:.1f}€/MWh")
    
    # Cas de référence METASTAAQ
    prix_ref = 30
    cout_ref = calculer_cout_production_ch4_electricite_seule(prix_ref)
    print(f"\n📋 CAS DE RÉFÉRENCE METASTAAQ :")
    print(f"   • Prix électricité : {prix_ref}€/MWh")
    print(f"   • Coût CH4 (élec seule) : {cout_ref:.1f}€/MWh")
    print(f"   • Part électricité dans coût total (106.14€) : {cout_ref/106.14*100:.1f}%")
    
    # Exemples pratiques
    print(f"\n💡 EXEMPLES PRATIQUES :")
    prix_exemples = [5, 10, 15, 20, 25]
    for prix in prix_exemples:
        cout = calculer_cout_production_ch4_electricite_seule(prix)
        economie = cout_ref - cout
        pourcentage = (economie / cout_ref) * 100
        print(f"   • À {prix}€/MWh : CH4 à {cout:.1f}€/MWh (économie {economie:.1f}€/MWh = {pourcentage:.0f}%)")

def sauvegarder_resultats_electricite_seule(df_resultats, tableau_matriciel):
    """
    Sauvegarde les résultats de l'analyse électricité seule
    """
    # Créer le dossier de sortie
    dossier_sortie = "resultats_ch4_electricite_seule"
    os.makedirs(dossier_sortie, exist_ok=True)
    
    print(f"\n💾 Sauvegarde dans {dossier_sortie}/")
    
    # Sauvegarder en Excel
    with pd.ExcelWriter(os.path.join(dossier_sortie, "analyse_ch4_electricite_seule.xlsx")) as writer:
        df_resultats.to_excel(writer, sheet_name="Resultats_Lineaires", index=False)
        tableau_matriciel.to_excel(writer, sheet_name="Tableau_Matriciel")
    
    # CSV pour faciliter l'import
    df_resultats.to_csv(os.path.join(dossier_sortie, "couts_ch4_electricite_seule.csv"), index=False)
    
    print("   ✅ Fichiers Excel et CSV sauvegardés")
    
    return dossier_sortie

def main():
    """
    Fonction principale
    """
    print("⚡ ANALYSE COÛTS CH4 - ÉLECTRICITÉ SEULE")
    print("Méthodologie simplifiée basée sur METASTAAQ")
    print("="*60)
    
    # Générer les résultats
    df_resultats = generer_tableau_electricite_seule()
    
    # Créer le tableau matriciel
    tableau_matriciel = creer_tableau_matriciel()
    
    print("\n📋 TABLEAU MATRICIEL :")
    print(tableau_matriciel.round(1))
    
    # Analyser les résultats
    analyser_resultats(df_resultats)
    
    # Créer la visualisation
    print("\n📈 CRÉATION DES VISUALISATIONS...")
    fig = creer_visualisation_electricite_seule(df_resultats, tableau_matriciel)
    
    # Sauvegarder les résultats
    dossier_sortie = sauvegarder_resultats_electricite_seule(df_resultats, tableau_matriciel)
    
    # Sauvegarder la visualisation
    fichier_image = os.path.join(dossier_sortie, "analyse_ch4_electricite_seule.png")
    fig.savefig(fichier_image, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"   ✅ Visualisation sauvegardée : {fichier_image}")
    
    print(f"\n🎉 ANALYSE TERMINÉE")
    print(f"📁 Résultats dans : {dossier_sortie}/")
    print("="*60)

if __name__ == "__main__":
    main() 