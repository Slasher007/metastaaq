#!/usr/bin/env python3
"""
Calcul corrigé des coûts de production CH4 vs coût moyen achat électricité 2024
Basé sur la méthodologie METASTAAQ corrigée
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

def calculer_cout_production_ch4_corrige(prix_elec, puissance):
    """
    Calcule le coût de production CH4 avec la méthodologie corrigée METASTAAQ
    
    Parameters:
    - prix_elec: Prix de l'électricité en €/MWh
    - puissance: Puissance de l'électrolyseur en MW
    
    Returns:
    - Coût de production en €/MWh CH4
    """
    
    # ===============================
    # CONSTANTES METASTAAQ RÉELLES
    # ===============================
    
    # Consommation spécifique d'électricité pour 1 MWh de CH4
    # D'après analyse détaillée: 904 GWh élec / 20 GWh CH4/an = 45,2 MWh élec / MWh CH4
    CONSOMMATION_SPECIFIQUE_ELEC = 45.2  # MWh élec / MWh CH4
    
    # Production spécifique de CH4 pour puissance installée
    # D'après données METASTAAQ: 20 GWh CH4/an pour 5 MW = 4 GWh CH4/an/MW
    PRODUCTION_SPECIFIQUE_CH4 = 4.0  # GWh CH4/an/MW
    
    # Paramètres économiques METASTAAQ
    CAPEX_MW = 2368400  # €/MW (11 842 000 € / 5 MW)
    DUREE_AMORTISSEMENT = 10  # ans
    TAUX_FINANCIER = 0.05  # 5%
    MAINTENANCE_MW = 19030  # €/MW/an (95 150 € / 5 MW)
    
    # Autres coûts annuels (basés sur données METASTAAQ pour 5 MW)
    COUT_EAU_MW = 40902 / 5  # €/MW/an = 8 180 €/MW/an
    COUT_FINANCIER_MW = 29605 / 5  # €/MW/an = 5 921 €/MW/an
    
    # ===============================
    # CALCUL DU COÛT POUR 1 MWh CH4
    # ===============================
    
    # 1. COÛT ÉLECTRICITÉ pour 1 MWh CH4
    cout_elec_par_mwh_ch4 = CONSOMMATION_SPECIFIQUE_ELEC * prix_elec
    
    # 2. PRODUCTION ANNUELLE pour cette puissance
    production_annuelle_ch4 = puissance * PRODUCTION_SPECIFIQUE_CH4 * 1000  # MWh CH4/an
    
    # 3. COÛTS FIXES ANNUELS
    
    # CAPEX annualisé (formule d'annuité)
    facteur_annualisation = (TAUX_FINANCIER * (1 + TAUX_FINANCIER)**DUREE_AMORTISSEMENT) / \
                           ((1 + TAUX_FINANCIER)**DUREE_AMORTISSEMENT - 1)
    capex_mw_an = CAPEX_MW * facteur_annualisation
    
    # Effet d'échelle (réduction des coûts fixes pour grandes puissances)
    facteur_echelle = max(0.9, 1 - (0.1 * np.log(puissance + 1)))
    
    # Coûts fixes totaux annuels
    cout_capex_total_an = puissance * capex_mw_an * facteur_echelle
    cout_maintenance_total_an = puissance * MAINTENANCE_MW * facteur_echelle
    cout_eau_total_an = puissance * COUT_EAU_MW
    cout_financier_total_an = puissance * COUT_FINANCIER_MW
    
    cout_fixes_total_an = (cout_capex_total_an + cout_maintenance_total_an + 
                          cout_eau_total_an + cout_financier_total_an)
    
    # 4. COÛTS FIXES PAR MWh CH4
    if production_annuelle_ch4 > 0:
        cout_fixes_par_mwh_ch4 = cout_fixes_total_an / production_annuelle_ch4
    else:
        cout_fixes_par_mwh_ch4 = 0
    
    # 5. COÛT TOTAL DE PRODUCTION
    cout_production_ch4 = cout_elec_par_mwh_ch4 + cout_fixes_par_mwh_ch4
    
    return cout_production_ch4, cout_elec_par_mwh_ch4, cout_fixes_par_mwh_ch4

def generer_tableau_complet_2024():
    """
    Génère le tableau complet des coûts de production CH4 vs prix électricité 2024
    """
    print("🧮 CALCUL DES COÛTS DE PRODUCTION CH4 vs COÛT MOYEN ACHAT ÉLECTRICITÉ 2024")
    print("="*80)
    
    # Paramètres d'analyse
    prix_elec_range = [5, 10, 15, 20, 25, 30, 35, 40]  # €/MWh
    puissances = [0.5, 1, 2, 3, 4, 5]  # MW
    
    # Créer le tableau principal
    tableau_cout_total = pd.DataFrame(
        index=[f"{p} MW" for p in puissances],
        columns=[f"{prix}€/MWh" for prix in prix_elec_range]
    )
    
    # Tableaux de détail
    tableau_cout_elec = pd.DataFrame(
        index=[f"{p} MW" for p in puissances],
        columns=[f"{prix}€/MWh" for prix in prix_elec_range]
    )
    
    tableau_cout_fixes = pd.DataFrame(
        index=[f"{p} MW" for p in puissances],
        columns=[f"{prix}€/MWh" for prix in prix_elec_range]
    )
    
    # Calculs pour chaque combinaison
    print("\n📊 Calcul en cours...")
    
    for i, puissance in enumerate(puissances):
        for j, prix_elec in enumerate(prix_elec_range):
            cout_total, cout_elec, cout_fixes = calculer_cout_production_ch4_corrige(prix_elec, puissance)
            
            tableau_cout_total.iloc[i, j] = cout_total
            tableau_cout_elec.iloc[i, j] = cout_elec
            tableau_cout_fixes.iloc[i, j] = cout_fixes
    
    # Conversion en float
    tableau_cout_total = tableau_cout_total.astype(float)
    tableau_cout_elec = tableau_cout_elec.astype(float)
    tableau_cout_fixes = tableau_cout_fixes.astype(float)
    
    return tableau_cout_total, tableau_cout_elec, tableau_cout_fixes

def afficher_exemple_calcul_detaille():
    """
    Affiche un exemple de calcul détaillé pour validation
    """
    print("\n" + "="*80)
    print("📋 EXEMPLE DE CALCUL DÉTAILLÉ - VALIDATION METASTAAQ")
    print("="*80)
    
    # Cas de référence METASTAAQ
    puissance_ref = 5.0  # MW
    prix_elec_ref = 30.0  # €/MWh
    
    cout_total, cout_elec, cout_fixes = calculer_cout_production_ch4_corrige(prix_elec_ref, puissance_ref)
    
    print(f"\n🎯 CAS DE RÉFÉRENCE METASTAAQ:")
    print(f"   • Puissance: {puissance_ref} MW")
    print(f"   • Prix électricité: {prix_elec_ref} €/MWh")
    print(f"\n📊 RÉSULTATS:")
    print(f"   • Coût électricité par MWh CH4: {cout_elec:.2f} €/MWh CH4")
    print(f"   • Coût fixes par MWh CH4: {cout_fixes:.2f} €/MWh CH4")
    print(f"   • COÛT TOTAL: {cout_total:.2f} €/MWh CH4")
    
    # Validation avec analyse utilisateur
    cout_attendu = 106.14
    ecart = abs(cout_total - cout_attendu)
    pourcentage_ecart = (ecart / cout_attendu) * 100
    
    print(f"\n✅ VALIDATION:")
    print(f"   • Coût calculé: {cout_total:.2f} €/MWh CH4")
    print(f"   • Coût attendu (analyse): {cout_attendu:.2f} €/MWh CH4")
    print(f"   • Écart: {ecart:.2f} €/MWh CH4 ({pourcentage_ecart:.1f}%)")
    
    if pourcentage_ecart < 5:
        print("   ✅ CALCUL VALIDÉ - Écart acceptable")
    else:
        print("   ⚠️  ÉCART SIGNIFICATIF - Vérification nécessaire")
    
    # Décomposition détaillée
    print(f"\n🔍 DÉCOMPOSITION DÉTAILLÉE:")
    
    # Constantes
    CONSOMMATION_SPECIFIQUE = 45.2
    PRODUCTION_SPECIFIQUE = 4.0
    
    # Calcul step by step
    production_annuelle = puissance_ref * PRODUCTION_SPECIFIQUE * 1000
    
    # Coûts fixes annuels
    CAPEX_MW = 2368400
    TAUX_FINANCIER = 0.05
    DUREE_AMORTISSEMENT = 10
    facteur_annualisation = (TAUX_FINANCIER * (1 + TAUX_FINANCIER)**DUREE_AMORTISSEMENT) / \
                           ((1 + TAUX_FINANCIER)**DUREE_AMORTISSEMENT - 1)
    capex_mw_an = CAPEX_MW * facteur_annualisation
    
    facteur_echelle = max(0.9, 1 - (0.1 * np.log(puissance_ref + 1)))
    
    cout_capex_an = puissance_ref * capex_mw_an * facteur_echelle
    cout_maintenance_an = puissance_ref * 19030 * facteur_echelle
    cout_eau_an = puissance_ref * (40902 / 5)
    cout_financier_an = puissance_ref * (29605 / 5)
    cout_fixes_total_an = cout_capex_an + cout_maintenance_an + cout_eau_an + cout_financier_an
    
    print(f"   • Consommation spécifique: {CONSOMMATION_SPECIFIQUE} MWh élec / MWh CH4")
    print(f"   • Production annuelle CH4: {production_annuelle:,.0f} MWh/an")
    print(f"   • Facteur d'échelle: {facteur_echelle:.3f}")
    print(f"   • CAPEX annualisé: {cout_capex_an:,.0f} €/an")
    print(f"   • Maintenance: {cout_maintenance_an:,.0f} €/an")
    print(f"   • Eau: {cout_eau_an:,.0f} €/an")
    print(f"   • Financiers: {cout_financier_an:,.0f} €/an")
    print(f"   • Total coûts fixes: {cout_fixes_total_an:,.0f} €/an")
    print(f"   • Coûts fixes unitaires: {cout_fixes:.2f} €/MWh CH4")

def creer_visualisation_avancee(tableau_cout_total, tableau_cout_elec, tableau_cout_fixes):
    """
    Crée une visualisation avancée du tableau avec décomposition des coûts
    """
    print("\n📈 Création de la visualisation avancée...")
    
    # Configuration générale
    plt.style.use('default')
    fig = plt.figure(figsize=(20, 12))
    
    # 1. Tableau principal (coûts totaux)
    ax1 = plt.subplot(2, 3, (1, 2))
    im1 = ax1.imshow(tableau_cout_total.values, cmap='RdYlGn_r', aspect='auto', 
                     vmin=tableau_cout_total.min().min(), vmax=tableau_cout_total.max().max())
    
    # Configuration du tableau principal
    ax1.set_xticks(range(len(tableau_cout_total.columns)))
    ax1.set_yticks(range(len(tableau_cout_total.index)))
    ax1.set_xticklabels(tableau_cout_total.columns, rotation=0)
    ax1.set_yticklabels(tableau_cout_total.index)
    
    # Ajouter les valeurs
    for i in range(len(tableau_cout_total.index)):
        for j in range(len(tableau_cout_total.columns)):
            value = tableau_cout_total.iloc[i, j]
            color = 'white' if value > tableau_cout_total.median().median() else 'black'
            ax1.text(j, i, f'{value:.0f}', ha='center', va='center', 
                    fontweight='bold', fontsize=10, color=color)
    
    ax1.set_title('COÛT TOTAL DE PRODUCTION CH4 (€/MWh CH4)\nProjet METASTAAQ - Année 2024', 
                  fontsize=14, fontweight='bold', pad=20)
    ax1.set_xlabel('Prix moyen achat électricité (€/MWh)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Puissance électrolyseur', fontsize=12, fontweight='bold')
    ax1.grid(True, color='black', linewidth=0.5)
    
    # Colorbar pour le tableau principal
    cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
    cbar1.set_label('Coût production CH4 (€/MWh CH4)', rotation=270, labelpad=20)
    
    # 2. Décomposition - Coûts électricité
    ax2 = plt.subplot(2, 3, 4)
    im2 = ax2.imshow(tableau_cout_elec.values, cmap='Blues', aspect='auto')
    ax2.set_title('Coûts Électricité\n(€/MWh CH4)', fontsize=11, fontweight='bold')
    ax2.set_xticks(range(len(tableau_cout_elec.columns)))
    ax2.set_xticklabels([col.split('€')[0] for col in tableau_cout_elec.columns], rotation=45)
    ax2.set_yticks(range(len(tableau_cout_elec.index)))
    ax2.set_yticklabels(tableau_cout_elec.index)
    
    for i in range(len(tableau_cout_elec.index)):
        for j in range(len(tableau_cout_elec.columns)):
            value = tableau_cout_elec.iloc[i, j]
            ax2.text(j, i, f'{value:.0f}', ha='center', va='center', fontsize=8, fontweight='bold')
    
    # 3. Décomposition - Coûts fixes
    ax3 = plt.subplot(2, 3, 5)
    im3 = ax3.imshow(tableau_cout_fixes.values, cmap='Oranges', aspect='auto')
    ax3.set_title('Coûts Fixes\n(€/MWh CH4)', fontsize=11, fontweight='bold')
    ax3.set_xticks(range(len(tableau_cout_fixes.columns)))
    ax3.set_xticklabels([col.split('€')[0] for col in tableau_cout_fixes.columns], rotation=45)
    ax3.set_yticks(range(len(tableau_cout_fixes.index)))
    ax3.set_yticklabels(tableau_cout_fixes.index)
    
    for i in range(len(tableau_cout_fixes.index)):
        for j in range(len(tableau_cout_fixes.columns)):
            value = tableau_cout_fixes.iloc[i, j]
            ax3.text(j, i, f'{value:.0f}', ha='center', va='center', fontsize=8, fontweight='bold')
    
    # 4. Analyse de sensibilité
    ax4 = plt.subplot(2, 3, (3, 6))
    
    # Courbes de sensibilité pour différentes puissances
    prix_range = [5, 10, 15, 20, 25, 30, 35, 40]
    for i, puissance in enumerate([0.5, 1, 2, 3, 4, 5]):
        couts = [tableau_cout_total.iloc[i, j] for j in range(len(prix_range))]
        ax4.plot(prix_range, couts, marker='o', linewidth=2, 
                label=f'{puissance} MW', markersize=6)
    
    # Ligne de référence à 106.14 €/MWh
    ax4.axhline(y=106.14, color='red', linestyle='--', linewidth=2, 
                label='Référence METASTAAQ (106.14 €/MWh)')
    
    ax4.set_xlabel('Prix achat électricité (€/MWh)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Coût production CH4 (€/MWh)', fontsize=12, fontweight='bold')
    ax4.set_title('Analyse de Sensibilité\nCoût CH4 vs Prix Électricité', 
                  fontsize=12, fontweight='bold')
    ax4.legend(loc='upper left', fontsize=10)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def sauvegarder_resultats(tableau_cout_total, tableau_cout_elec, tableau_cout_fixes):
    """
    Sauvegarde tous les résultats
    """
    # Créer le dossier de sortie
    dossier_sortie = "resultats_tableau_ch4_2024"
    os.makedirs(dossier_sortie, exist_ok=True)
    
    print(f"\n💾 Sauvegarde des résultats dans {dossier_sortie}/")
    
    # Sauvegarder les tableaux
    with pd.ExcelWriter(os.path.join(dossier_sortie, "analyse_complete_ch4_2024.xlsx")) as writer:
        tableau_cout_total.round(2).to_excel(writer, sheet_name="Cout_Total_CH4")
        tableau_cout_elec.round(2).to_excel(writer, sheet_name="Cout_Electricite")
        tableau_cout_fixes.round(2).to_excel(writer, sheet_name="Cout_Fixes")
    
    # CSV principal
    tableau_cout_total.round(2).to_csv(os.path.join(dossier_sortie, "tableau_cout_ch4_2024_corrige.csv"))
    
    print("   ✅ Tableaux Excel et CSV sauvegardés")
    
    return dossier_sortie

def main():
    """
    Fonction principale
    """
    print("🚀 ANALYSE DES COÛTS DE PRODUCTION CH4 vs COÛT MOYEN ACHAT ÉLECTRICITÉ 2024")
    print("Méthodologie METASTAAQ corrigée")
    print("="*80)
    
    # Afficher l'exemple de calcul détaillé
    afficher_exemple_calcul_detaille()
    
    # Générer les tableaux complets
    print("\n" + "="*80)
    print("📊 GÉNÉRATION DES TABLEAUX COMPLETS")
    print("="*80)
    
    tableau_cout_total, tableau_cout_elec, tableau_cout_fixes = generer_tableau_complet_2024()
    
    # Afficher les résultats
    print("\n📋 TABLEAU PRINCIPAL - COÛT TOTAL DE PRODUCTION CH4 (€/MWh CH4):")
    print("-"*70)
    print(tableau_cout_total.round(1))
    
    print("\n💡 ANALYSE RAPIDE:")
    prix_optimal = tableau_cout_total.min().min()
    idx_optimal = tableau_cout_total.stack().idxmin()
    print(f"   • Coût minimum: {prix_optimal:.1f} €/MWh CH4")
    print(f"   • Configuration optimale: {idx_optimal[0]} à {idx_optimal[1]}")
    print(f"   • Coût maximum: {tableau_cout_total.max().max():.1f} €/MWh CH4")
    
    # Créer la visualisation
    print("\n📈 CRÉATION DE LA VISUALISATION...")
    fig = creer_visualisation_avancee(tableau_cout_total, tableau_cout_elec, tableau_cout_fixes)
    
    # Sauvegarder les résultats
    dossier_sortie = sauvegarder_resultats(tableau_cout_total, tableau_cout_elec, tableau_cout_fixes)
    
    # Sauvegarder la visualisation
    fichier_image = os.path.join(dossier_sortie, "analyse_complete_ch4_vs_electricite_2024.png")
    fig.savefig(fichier_image, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"   ✅ Visualisation sauvegardée: {fichier_image}")
    
    print(f"\n🎉 ANALYSE TERMINÉE")
    print(f"📁 Tous les fichiers sont dans: {dossier_sortie}/")
    print("="*80)

if __name__ == "__main__":
    main() 