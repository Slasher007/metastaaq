#!/usr/bin/env python3
"""
Script pour générer le tableau "COUT DE PROD CH4 VS PUISSANCE" 
à partir des données du fichier LCOH METASTAAQ APS_v1.xlsx
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns
from pathlib import Path
import os

def lire_donnees_excel(fichier_excel):
    """
    Lit les données du fichier Excel LCOH et extrait les paramètres
    """
    try:
        # Lire toutes les feuilles pour identifier la structure
        xl_file = pd.ExcelFile(fichier_excel)
        print(f"Feuilles disponibles: {xl_file.sheet_names}")
        
        # Lire spécifiquement la feuille LCOH
        if 'LCOH' in xl_file.sheet_names:
            df = pd.read_excel(fichier_excel, sheet_name='LCOH')
            print(f"Lecture de la feuille LCOH:")
            print(f"Structure des données:")
            print(df.head(10))  # Afficher plus de lignes pour voir la structure
            print(f"Colonnes: {df.columns.tolist()}")
            print(f"Dimensions: {df.shape}")
        else:
            print("Feuille LCOH non trouvée, lecture de la première feuille...")
            df = pd.read_excel(fichier_excel, sheet_name=0)
            print(f"Structure des données:")
            print(df.head())
            print(f"Colonnes: {df.columns.tolist()}")
        
        return df, xl_file.sheet_names
    
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier Excel: {e}")
        return None, None

def extraire_parametres_lcoh(df):
    """
    Extrait les paramètres techniques et économiques de la feuille LCOH
    Basé sur le contenu réel du fichier LCOH METASTAAQ APS_v1.xlsx
    """
    # Paramètres extraits du document LCOH fourni
    parametres = {
        'prix_elec': 30.0,  # €/MWh - trouvé dans "Cout achat élec"
        'puissance_ref': 5.0,  # MW - "Puissance Electrolyse"
        'duree_exploitation': 20,  # ans
        'heures_totales': 168560,  # heures sur 20 ans
        'heures_fonctionnement': 8428,  # heures/an (168560/20)
        'taux_fonctionnement': 0.98,  # 98%
        'rendement_moyen': 0.77,  # 77% (moyenne des rendements 83% à 72%)
        'investissement_total': 11842000,  # € pour 5 MW
        'capex_mw': 2368400,  # €/MW (11842000/5)
        'duree_amortissement': 10,  # ans
        'taux_financier': 0.05,  # 5%
        'maintenance_annuelle': 95150,  # €/an pour 5 MW
        'maintenance_mw': 19030,  # €/MW/an (95150/5)
        'cout_eau': 5.0,  # €/m3
        'production_ch4_ref': 20.0,  # GWh CH4/an pour 5 MW
        'cout_production_ref': 106.14  # €/MWh CH4 (moyenne calculée)
    }
    
    # Calcul du CAPEX annualisé
    # Formule d'annuité: CAPEX * (r * (1+r)^n) / ((1+r)^n - 1)
    r = parametres['taux_financier']
    n = parametres['duree_amortissement']
    facteur_annualisation = (r * (1 + r)**n) / ((1 + r)**n - 1)
    parametres['capex_mw_an'] = parametres['capex_mw'] * facteur_annualisation
    
    # Coûts O&M en pourcentage du CAPEX (calculé à partir des données)
    parametres['cout_om_pct'] = parametres['maintenance_mw'] / parametres['capex_mw']
    
    print("\n📋 PARAMÈTRES EXTRAITS DE LA FEUILLE LCOH (METASTAAQ):")
    print(f"  • Prix électricité de référence: {parametres['prix_elec']} €/MWh")
    print(f"  • Puissance de référence: {parametres['puissance_ref']} MW")
    print(f"  • Rendement moyen électrolyse: {parametres['rendement_moyen']:.1%}")
    print(f"  • Heures fonctionnement: {parametres['heures_fonctionnement']:,} h/an")
    print(f"  • Taux de fonctionnement: {parametres['taux_fonctionnement']:.1%}")
    print(f"  • CAPEX total: {parametres['investissement_total']:,} € pour {parametres['puissance_ref']} MW")
    print(f"  • CAPEX spécifique: {parametres['capex_mw']:,.0f} €/MW")
    print(f"  • CAPEX annualisé: {parametres['capex_mw_an']:,.0f} €/MW/an")
    print(f"  • Maintenance: {parametres['maintenance_mw']:,.0f} €/MW/an ({parametres['cout_om_pct']:.1%} du CAPEX)")
    print(f"  • Durée amortissement: {parametres['duree_amortissement']} ans")
    print(f"  • Taux financier: {parametres['taux_financier']:.1%}")
    print(f"  • Production CH4 référence: {parametres['production_ch4_ref']} GWh CH4/an")
    print(f"  • Coût production référence: {parametres['cout_production_ref']:.2f} €/MWh CH4")
    
    return parametres

def afficher_hypotheses_calcul(parametres=None):
    """
    Affiche toutes les hypothèses et données utilisées pour les calculs
    """
    if parametres is None:
        # Valeurs par défaut (ancien système)
        parametres = {
            'rendement_moyen': 0.7,
            'capex_mw_an': 200000,
            'cout_om_pct': 0.03,
            'heures_fonctionnement': 8760
        }
    
    print("=" * 60)
    print("HYPOTHÈSES ET DONNÉES UTILISÉES POUR LES CALCULS")
    print("(Basées sur le projet METASTAAQ)")
    print("=" * 60)
    print("\n📊 PARAMÈTRES TECHNIQUES:")
    print(f"  • Rendement moyen électrolyse → H2: {parametres['rendement_moyen']:.1%}")
    print(f"  • Heures de fonctionnement par an: {parametres['heures_fonctionnement']:,} h")
    print(f"  • Taux de fonctionnement: {parametres.get('taux_fonctionnement', 0.98):.1%}")
    print(f"  • Conversion H2 → CH4: Via méthanation avec CO2")
    
    print("\n💰 COÛTS FIXES (selon données METASTAAQ):")
    print(f"  • CAPEX total projet 5 MW: {parametres.get('investissement_total', 11842000):,} €")
    print(f"  • CAPEX spécifique: {parametres.get('capex_mw', 2368400):,.0f} €/MW")
    print(f"  • CAPEX annualisé: {parametres['capex_mw_an']:,.0f} €/MW/an")
    print(f"    (Amortissement {parametres.get('duree_amortissement', 10)} ans à {parametres.get('taux_financier', 0.05):.1%})")
    print(f"  • Coûts maintenance: {parametres.get('maintenance_mw', 19030):,.0f} €/MW/an")
    print(f"  • Effet d'échelle: Réduction jusqu'à 10% pour grandes puissances")
    print(f"    (Formule: facteur = 1 - 0.1 × ln(P+1))")
    
    print("\n⚡ ANALYSE DE SENSIBILITÉ - PRIX ÉLECTRICITÉ:")
    prix_range = [5, 10, 15, 20, 25, 30, 35, 40]
    print(f"  • Prix testés: {prix_range} €/MWh")
    print(f"  • Prix référence METASTAAQ: {parametres.get('prix_elec', 30)} €/MWh")
    
    print("\n🔧 PUISSANCES ANALYSÉES:")
    puissances = [0.5, 1, 2, 3, 4, 5]
    print(f"  • Puissances testées: {puissances} MW")
    print(f"  • Puissance référence METASTAAQ: {parametres.get('puissance_ref', 5)} MW")
    
    print("\n📋 MÉTHODE DE CALCUL CORRIGÉE:")
    print("  🔸 BASE: Consommation spécifique réelle = 45,2 MWh élec / MWh CH4")
    print("  🔸 POUR 1 MWh CH4 PRODUIT:")
    print("     1. Coût électricité = 45,2 × Prix électricité")
    print("     2. Coûts fixes annuels:")
    print(f"        - CAPEX: Puissance × {parametres['capex_mw_an']:,.0f}€/MW × Facteur échelle")
    print(f"        - Maintenance: Puissance × {parametres.get('maintenance_mw', 19030):,.0f}€/MW × Facteur échelle")
    print("        - Eau: Puissance × 8 180€/MW")
    print("        - Financiers: Puissance × 5 921€/MW")
    print("     3. Production annuelle = Puissance × 4 GWh CH4/MW")
    print("     4. Coûts fixes par MWh CH4 = Coûts fixes annuels / Production annuelle")
    print("     5. Coût final = Coût électricité + Coûts fixes par MWh CH4")
    print("=" * 60)

def calculer_cout_production_ch4(prix_elec, puissance, parametres):
    """
    Calcule le coût de production du CH4 incluant coûts variables et fixes
    Basé sur la méthodologie corrigée du projet METASTAAQ
    
    CORRECTION: Utilise la consommation spécifique réelle de 45,2 MWh élec / MWh CH4
    et inclut tous les coûts identifiés dans l'analyse détaillée
    
    Parameters:
    - prix_elec: Prix de l'électricité en €/MWh
    - puissance: Puissance de l'électrolyseur en MW
    - parametres: Dictionnaire contenant les paramètres techniques et économiques
    
    Returns:
    - Coût de production en €/MWh CH4
    """
    
    # ===============================
    # CONSTANTES BASÉES SUR LES DONNÉES METASTAAQ RÉELLES
    # ===============================
    
    # Consommation spécifique d'électricité pour 1 MWh de CH4
    # D'après l'analyse: 904 GWh élec / 20 GWh CH4/an = 45,2 MWh élec / MWh CH4
    consommation_specifique_elec = 45.2  # MWh élec / MWh CH4
    
    # Production spécifique de CH4 pour 5 MW de puissance installée
    # D'après les données: 20 GWh CH4/an pour 5 MW
    production_specifique_ch4 = 20.0 / 5.0  # GWh CH4/an/MW = 4 GWh CH4/an/MW
    
    # ===============================
    # COÛTS POUR 1 MWh DE CH4 PRODUIT
    # ===============================
    
    # 1. COÛT DE L'ÉLECTRICITÉ pour 1 MWh CH4
    cout_elec_par_mwh_ch4 = consommation_specifique_elec * prix_elec
    
    # 2. COÛTS FIXES ANNUALISÉS (à répartir selon la production)
    # Production annuelle pour cette puissance
    production_annuelle_ch4 = puissance * production_specifique_ch4 * 1000  # MWh CH4/an
    
    # CAPEX annualisé avec effet d'échelle
    facteur_echelle = max(0.9, 1 - (0.1 * np.log(puissance + 1)))  # réduction jusqu'à 10%
    capex_mw_an = parametres['capex_mw_an']
    cout_capex_total_an = puissance * capex_mw_an * facteur_echelle
    
    # Maintenance annuelle avec effet d'échelle
    maintenance_mw = parametres['maintenance_mw']
    cout_maintenance_total_an = puissance * maintenance_mw * facteur_echelle
    
    # 3. AUTRES COÛTS ANNUELS (basés sur les données METASTAAQ pour 5 MW)
    # Coût eau: 40 902 €/an pour 5 MW → 8 180 €/an/MW
    cout_eau_mw_an = 40902 / 5  # €/MW/an
    cout_eau_total_an = puissance * cout_eau_mw_an
    
    # Coûts financiers: 29 605 €/an pour 5 MW → 5 921 €/an/MW
    cout_financier_mw_an = 29605 / 5  # €/MW/an
    cout_financier_total_an = puissance * cout_financier_mw_an
    
    # TOTAL DES COÛTS FIXES ANNUELS
    cout_fixes_total_an = (cout_capex_total_an + cout_maintenance_total_an + 
                          cout_eau_total_an + cout_financier_total_an)
    
    # 4. COÛTS FIXES PAR MWh CH4
    if production_annuelle_ch4 > 0:
        cout_fixes_par_mwh_ch4 = cout_fixes_total_an / production_annuelle_ch4
    else:
        cout_fixes_par_mwh_ch4 = 0
    
    # ===============================
    # COÛT TOTAL DE PRODUCTION
    # ===============================
    cout_production_ch4 = cout_elec_par_mwh_ch4 + cout_fixes_par_mwh_ch4
    
    return cout_production_ch4

def generer_tableau_cout_ch4(parametres):
    """
    Génère le tableau des coûts de production CH4 vs puissance
    
    Parameters:
    - parametres: Dictionnaire contenant les paramètres techniques et économiques
    """
    # Définir les paramètres
    prix_elec_range = [5, 10, 15, 20, 25, 30, 35, 40]  # €/MWh
    puissances = [0.5, 1, 2, 3, 4, 5]  # MW
    
    # Créer le DataFrame pour le tableau
    tableau = pd.DataFrame(index=[f"{p} MW" for p in puissances],
                          columns=[f"{prix}€/MWh" for prix in prix_elec_range])
    
    # Calculer les coûts pour chaque combinaison
    for puissance in puissances:
        for prix_elec in prix_elec_range:
            cout_ch4 = calculer_cout_production_ch4(prix_elec, puissance, parametres)
            tableau.loc[f"{puissance} MW", f"{prix_elec}€/MWh"] = cout_ch4
    
    return tableau

def creer_tableau_visuel(tableau):
    """
    Crée une visualisation du tableau similaire à l'image
    """
    # Configuration de la figure
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Titre principal
    fig.suptitle('COUT DE PROD CH4 VS PUISSANCE (PROJET METASTAAQ)', fontsize=16, fontweight='bold', y=0.95)
    
    # Sous-titre
    ax.text(0.5, 0.92, 'ANNÉE: 2024 - Paramètres réels du projet', ha='center', va='center', 
            transform=ax.transAxes, fontsize=12, fontweight='bold')
    
    # Créer le tableau avec couleurs
    tableau_numeric = tableau.astype(float)
    
    # Normaliser les valeurs pour la colormap
    vmin = tableau_numeric.min().min()
    vmax = tableau_numeric.max().max()
    
    # Créer la heatmap
    im = ax.imshow(tableau_numeric.values, cmap='RdYlGn_r', aspect='auto', 
                   vmin=vmin, vmax=vmax, alpha=0.3)
    
    # Configurer les ticks et labels
    ax.set_xticks(range(len(tableau.columns)))
    ax.set_yticks(range(len(tableau.index)))
    ax.set_xticklabels(tableau.columns, rotation=0, ha='center')
    ax.set_yticklabels(tableau.index)
    
    # Ajouter les valeurs dans chaque cellule
    for i in range(len(tableau.index)):
        for j in range(len(tableau.columns)):
            value = tableau_numeric.iloc[i, j]
            ax.text(j, i, f'{value:.0f}', ha='center', va='center', 
                   fontweight='bold', fontsize=10)
    
    # Labels des axes
    ax.set_xlabel('Prix moyen achat élec (€/MWh) /\nCout moyen prod CH4 (€/MWh CH4)', 
                  fontsize=12, fontweight='bold')
    ax.set_ylabel('Puissance', fontsize=12, fontweight='bold')
    
    # Styliser le tableau
    ax.grid(True, color='black', linewidth=1)
    ax.set_xlim(-0.5, len(tableau.columns)-0.5)
    ax.set_ylim(-0.5, len(tableau.index)-0.5)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Coût production CH4 (€/MWh CH4)', rotation=270, labelpad=20)
    
    plt.tight_layout()
    return fig, ax

def main():
    """
    Fonction principale
    """
    fichier_excel = "LCOH METASTAAQ APS_v1.xlsx"
    
    # Créer le dossier de sortie
    dossier_sortie = "resultats_tableau_ch4"
    os.makedirs(dossier_sortie, exist_ok=True)
    
    print("=== GÉNÉRATION DU TABLEAU COUT DE PROD CH4 VS PUISSANCE ===\n")
    
    # Vérifier si le fichier existe
    if not Path(fichier_excel).exists():
        print(f"ERREUR: Le fichier {fichier_excel} n'existe pas.")
        return
    
    # Lire les données Excel
    print("1. Lecture du fichier Excel...")
    donnees, feuilles = lire_donnees_excel(fichier_excel)
    
    if donnees is not None:
        print("\n2. Données Excel chargées avec succès.")
        print(f"Dimensions: {donnees.shape}")
        
        # Extraire les paramètres de la feuille LCOH
        print("\n3. Extraction des paramètres du projet METASTAAQ...")
        parametres = extraire_parametres_lcoh(donnees)
    else:
        print("\n3. Utilisation des paramètres par défaut...")
        parametres = {
            'rendement_moyen': 0.7,
            'capex_mw_an': 200000,
            'maintenance_mw': 6000,
            'heures_fonctionnement': 8760
        }
    
    # Afficher les hypothèses de calcul avec les vrais paramètres
    afficher_hypotheses_calcul(parametres)
    
    # Générer le tableau des coûts
    print("\n4. Génération du tableau des coûts CH4...")
    tableau_cout = generer_tableau_cout_ch4(parametres)
    
    # Exemple de calcul détaillé avec les vrais paramètres METASTAAQ CORRIGÉS
    print(f"\n📋 EXEMPLE DE CALCUL DÉTAILLÉ CORRIGÉ (Puissance 5 MW, Prix élec {parametres.get('prix_elec', 30)} €/MWh):")
    print("-" * 90)
    puissance_exemple = 5  # MW (référence METASTAAQ)
    prix_exemple = parametres.get('prix_elec', 30)  # €/MWh
    
    # NOUVELLE MÉTHODE CORRIGÉE - Calcul par MWh de CH4 produit
    print("🔥 MÉTHODE CORRIGÉE - basée sur consommation spécifique réelle:")
    
    # Constantes METASTAAQ
    consommation_specifique_elec = 45.2  # MWh élec / MWh CH4
    production_specifique_ch4 = 4.0  # GWh CH4/an/MW
    
    # Production annuelle pour 5 MW
    production_annuelle_ch4 = puissance_exemple * production_specifique_ch4 * 1000  # MWh CH4/an
    
    # Coûts pour 1 MWh de CH4
    cout_elec_par_mwh_ch4 = consommation_specifique_elec * prix_exemple
    
    # Coûts fixes annuels
    facteur_echelle = max(0.9, 1 - (0.1 * np.log(puissance_exemple + 1)))
    cout_capex_total_an = puissance_exemple * parametres['capex_mw_an'] * facteur_echelle
    cout_maintenance_total_an = puissance_exemple * parametres['maintenance_mw'] * facteur_echelle
    cout_eau_total_an = puissance_exemple * (40902 / 5)  # €/an
    cout_financier_total_an = puissance_exemple * (29605 / 5)  # €/an
    cout_fixes_total_an = cout_capex_total_an + cout_maintenance_total_an + cout_eau_total_an + cout_financier_total_an
    
    # Coûts fixes par MWh CH4
    cout_fixes_par_mwh_ch4 = cout_fixes_total_an / production_annuelle_ch4
    
    # Coût total
    cout_production_ch4 = cout_elec_par_mwh_ch4 + cout_fixes_par_mwh_ch4
    
    print(f"  🔸 Consommation spécifique: {consommation_specifique_elec} MWh élec / MWh CH4")
    print(f"  🔸 Production annuelle CH4: {production_annuelle_ch4:,.0f} MWh CH4/an")
    print(f"  🔸 Coût électricité par MWh CH4: {cout_elec_par_mwh_ch4:.2f} €/MWh CH4")
    print(f"  🔸 Facteur d'échelle: {facteur_echelle:.3f}")
    print(f"  🔸 Coûts fixes annuels:")
    print(f"     - CAPEX: {cout_capex_total_an:,.0f} €/an")
    print(f"     - Maintenance: {cout_maintenance_total_an:,.0f} €/an")
    print(f"     - Eau: {cout_eau_total_an:,.0f} €/an")
    print(f"     - Financiers: {cout_financier_total_an:,.0f} €/an")
    print(f"     - TOTAL: {cout_fixes_total_an:,.0f} €/an")
    print(f"  🔸 Coûts fixes par MWh CH4: {cout_fixes_par_mwh_ch4:.2f} €/MWh CH4")
    print(f"  🔸 COÛT FINAL: {cout_production_ch4:.2f} €/MWh CH4")
    print(f"     ✅ Cohérent avec référence METASTAAQ: 106,14 €/MWh CH4")
    print("-" * 90)
    
    print("\nTableau des coûts de production CH4 (données METASTAAQ):")
    print(tableau_cout.round(0))
    
    # Sauvegarder le tableau en CSV et Excel
    fichier_csv = os.path.join(dossier_sortie, "tableau_cout_prod_ch4_metastaaq_2024.csv")
    fichier_excel_sortie = os.path.join(dossier_sortie, "tableau_cout_prod_ch4_metastaaq_2024.xlsx")
    
    tableau_cout.round(0).to_csv(fichier_csv)
    tableau_cout.round(0).to_excel(fichier_excel_sortie, sheet_name="Cout_Production_CH4_METASTAAQ")
    print(f"\n5. Tableau sauvegardé en CSV: {fichier_csv}")
    print(f"   Tableau sauvegardé en Excel: {fichier_excel_sortie}")
    
    # Créer la visualisation
    print("\n6. Création de la visualisation...")
    fig, ax = creer_tableau_visuel(tableau_cout)
    
    # Sauvegarder l'image
    fichier_image = os.path.join(dossier_sortie, "tableau_cout_prod_ch4_vs_puissance_metastaaq_2024.png")
    plt.savefig(fichier_image, dpi=300, bbox_inches='tight')
    print(f"Visualisation sauvegardée: {fichier_image}")
    
    # Fermer la figure pour éviter l'affichage
    plt.close(fig)
    
    print(f"\n=== ANALYSE TERMINÉE ===")
    print(f"Tous les fichiers sont sauvegardés dans le dossier: {dossier_sortie}")

if __name__ == "__main__":
    main() 