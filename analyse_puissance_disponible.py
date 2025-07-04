import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration des graphiques
plt.style.use('seaborn-v0_8')
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 12
sns.set_palette("husl")

def charger_donnees_prix():
    """Charge et prépare les données de prix spot 2020-2025"""
    print("📊 Chargement des données de prix spot 2020-2025...")
    
    # Charger les données
    df = pd.read_csv('donnees_prix_spot_FR_2020_2025.csv', index_col=0)
    
    # Renommer la colonne si nécessaire
    if 'Prix_EUR_MWh' not in df.columns and len(df.columns) == 1:
        df.columns = ['Prix_EUR_MWh']
    
    # Convertir l'index en DatetimeIndex
    df.index = pd.to_datetime(df.index, utc=True).tz_convert('Europe/Paris').tz_localize(None)
    
    # Ajouter des colonnes temporelles
    df['Annee'] = df.index.year
    df['Mois'] = df.index.month
    df['Mois_nom'] = df.index.month_name()
    df['Heure'] = df.index.hour
    df['Date'] = df.index.date
    
    print(f"✅ Données chargées: {len(df)} points de données")
    print(f"📅 Période: {df.index.min()} à {df.index.max()}")
    print(f"🗓️ Années disponibles: {sorted(df['Annee'].unique())}")
    print(f"💰 Prix moyen global: {df['Prix_EUR_MWh'].mean():.2f} €/MWh")
    
    return df

def calculer_heures_disponibles_par_seuil(df_annee, puissances, seuils_prix):
    """
    Calcule le nombre d'heures disponibles pour chaque combinaison puissance/seuil de prix
    
    Principe: Pour une puissance donnée, on peut fonctionner si le prix est inférieur au seuil
    Plus la puissance est élevée, plus on consomme, donc plus on est sensible au prix
    """
    resultats = {}
    
    for puissance in puissances:
        resultats[f'{puissance} MW'] = {}
        
        for seuil in seuils_prix:
            # Calcul du nombre d'heures où le prix est inférieur ou égal au seuil
            heures_disponibles = len(df_annee[df_annee['Prix_EUR_MWh'] <= seuil])
            resultats[f'{puissance} MW'][f'{seuil} €/MWh'] = heures_disponibles
    
    return pd.DataFrame(resultats)

def analyser_puissance_par_annee(df):
    """Analyse la puissance disponible par année"""
    print("\n🔍 Analyse 1: Heures disponibles par coût moyen d'achat (par année)")
    print("="*70)
    
    # Définir les puissances et seuils de prix
    puissances = [0.5, 1, 2, 3, 5]
    seuils_prix = list(range(5, 45, 5))  # 5, 10, 15, ..., 40
    
    # Dictionnaire pour stocker les résultats
    resultats_annees = {}
    
    # Analyser chaque année
    for annee in sorted(df['Annee'].unique()):
        if annee >= 2020:  # S'assurer qu'on a des données complètes
            print(f"\n📅 Analyse pour l'année {annee}:")
            
            # Filtrer les données pour cette année
            df_annee = df[df['Annee'] == annee].copy()
            
            # Calculer les heures disponibles
            tableau_annee = calculer_heures_disponibles_par_seuil(df_annee, puissances, seuils_prix)
            
            # Stocker les résultats
            resultats_annees[annee] = tableau_annee
            
            # Afficher le tableau
            print(f"📊 Heures disponibles pour {annee}:")
            print(tableau_annee)
            
            # Statistiques supplémentaires
            print(f"\n📈 Statistiques {annee}:")
            print(f"   • Total d'heures dans l'année: {len(df_annee)}")
            print(f"   • Prix moyen: {df_annee['Prix_EUR_MWh'].mean():.2f} €/MWh")
            print(f"   • Prix médian: {df_annee['Prix_EUR_MWh'].median():.2f} €/MWh")
            print(f"   • Prix minimum: {df_annee['Prix_EUR_MWh'].min():.2f} €/MWh")
            print(f"   • Prix maximum: {df_annee['Prix_EUR_MWh'].max():.2f} €/MWh")
    
    return resultats_annees

def creer_graphiques_heures_disponibles(resultats_annees):
    """Crée les graphiques des heures disponibles par année"""
    print("\n📈 Création des graphiques par année...")
    
    # Créer un graphique pour chaque année
    for annee, tableau in resultats_annees.items():
        fig, axes = plt.subplots(2, 2, figsize=(20, 15))
        fig.suptitle(f'Analyse des Heures Disponibles - Année {annee}', fontsize=16, fontweight='bold')
        
        # Préparer les données pour le graphique
        # Les colonnes sont les puissances (0.5 MW, 1 MW, etc.)
        # Les index sont les seuils de prix (5 €/MWh, 10 €/MWh, etc.)
        seuils = [idx.replace(' €/MWh', '') for idx in tableau.index]
        seuils_num = [int(s) for s in seuils]
        
        # Graphique 1: Courbes par puissance
        ax1 = axes[0, 0]
        for puissance in tableau.columns:
            valeurs = tableau[puissance].values
            ax1.plot(seuils_num, valeurs, marker='o', linewidth=2, label=puissance)
        
        ax1.set_xlabel('Seuil de prix (€/MWh)')
        ax1.set_ylabel('Heures disponibles')
        ax1.set_title(f'Heures disponibles par seuil de prix - {annee}')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Graphique 2: Heatmap
        ax2 = axes[0, 1]
        im = ax2.imshow(tableau.T.values, cmap='RdYlGn', aspect='auto')
        ax2.set_xticks(range(len(seuils)))
        ax2.set_xticklabels(seuils)
        ax2.set_yticks(range(len(tableau.columns)))
        ax2.set_yticklabels(tableau.columns)
        ax2.set_xlabel('Seuil de prix (€/MWh)')
        ax2.set_ylabel('Puissance (MW)')
        ax2.set_title(f'Heatmap des heures disponibles - {annee}')
        plt.colorbar(im, ax=ax2, label='Heures disponibles')
        
        # Graphique 3: Barres groupées pour quelques seuils clés
        ax3 = axes[1, 0]
        seuils_cles = ['15 €/MWh', '20 €/MWh', '25 €/MWh', '30 €/MWh']
        x = np.arange(len(tableau.columns))
        width = 0.2
        
        for i, seuil in enumerate(seuils_cles):
            if seuil in tableau.index:
                valeurs = tableau.loc[seuil].values
                ax3.bar(x + i*width, valeurs, width, label=seuil)
        
        ax3.set_xlabel('Puissance (MW)')
        ax3.set_ylabel('Heures disponibles')
        ax3.set_title(f'Comparaison par seuils de prix - {annee}')
        ax3.set_xticks(x + width * 1.5)
        ax3.set_xticklabels(tableau.columns)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Graphique 4: Pourcentage d'heures disponibles
        ax4 = axes[1, 1]
        total_heures = 8760 if annee % 4 != 0 else 8784  # Année bissextile
        
        # Calculer les pourcentages pour le seuil de 15 €/MWh
        if '15 €/MWh' in tableau.index:
            pct_disponible = (tableau.loc['15 €/MWh'] / total_heures * 100).values
            ax4.bar(tableau.columns, pct_disponible, alpha=0.7, color='skyblue')
            ax4.set_xlabel('Puissance (MW)')
            ax4.set_ylabel('% d\'heures disponibles')
            ax4.set_title(f'Pourcentage d\'heures disponibles à 15 €/MWh - {annee}')
            ax4.grid(True, alpha=0.3)
            
            # Ajouter les valeurs sur les barres
            for i, v in enumerate(pct_disponible):
                ax4.text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(f'analyse_heures_disponibles_{annee}.png', dpi=300, bbox_inches='tight')
        plt.show()

def analyser_saisonnalite(df):
    """Analyse la saisonnalité pour 2023 et 2024 à 15 €/MWh"""
    print("\n🌍 Analyse 2: Saisonnalité de la puissance disponible (2023 & 2024)")
    print("="*70)
    
    puissances = [0.5, 1, 2, 3, 5]
    prix_cible = 15  # €/MWh
    
    resultats_saisonnalite = {}
    
    for annee in [2023, 2024]:
        if annee in df['Annee'].unique():
            print(f"\n📅 Analyse saisonnalité pour {annee}:")
            
            # Filtrer les données pour cette année
            df_annee = df[df['Annee'] == annee].copy()
            
            # Calculer les heures disponibles par mois pour chaque puissance
            tableau_mois = {}
            
            for puissance in puissances:
                tableau_mois[f'{puissance} MW'] = {}
                
                for mois in range(1, 13):
                    df_mois = df_annee[df_annee['Mois'] == mois]
                    heures_disponibles = len(df_mois[df_mois['Prix_EUR_MWh'] <= prix_cible])
                    nom_mois = df_mois['Mois_nom'].iloc[0] if len(df_mois) > 0 else f'Mois_{mois}'
                    tableau_mois[f'{puissance} MW'][nom_mois] = heures_disponibles
            
            # Convertir en DataFrame
            tableau_saisonnalite = pd.DataFrame(tableau_mois)
            resultats_saisonnalite[annee] = tableau_saisonnalite
            
            print(f"📊 Heures disponibles par mois à {prix_cible} €/MWh pour {annee}:")
            print(tableau_saisonnalite)
            
            # Statistiques mensuelles
            print(f"\n📈 Statistiques mensuelles {annee}:")
            for mois in range(1, 13):
                df_mois = df_annee[df_annee['Mois'] == mois]
                if len(df_mois) > 0:
                    nom_mois = df_mois['Mois_nom'].iloc[0]
                    prix_moyen = df_mois['Prix_EUR_MWh'].mean()
                    heures_favorables = len(df_mois[df_mois['Prix_EUR_MWh'] <= prix_cible])
                    print(f"   • {nom_mois}: {prix_moyen:.2f} €/MWh moyen, {heures_favorables} heures ≤ {prix_cible} €/MWh")
    
    return resultats_saisonnalite

def creer_graphiques_saisonnalite(resultats_saisonnalite):
    """Crée les graphiques de saisonnalité"""
    print("\n📈 Création des graphiques de saisonnalité...")
    
    for annee, tableau in resultats_saisonnalite.items():
        fig, axes = plt.subplots(2, 2, figsize=(20, 15))
        fig.suptitle(f'Saisonnalité de la Puissance Disponible - Année {annee} (15 €/MWh)', 
                    fontsize=16, fontweight='bold')
        
        # Préparer les données
        mois = tableau.index
        mois_num = range(1, len(mois) + 1)
        
        # Graphique 1: Courbes par puissance
        ax1 = axes[0, 0]
        for puissance in tableau.columns:
            valeurs = tableau[puissance].values
            ax1.plot(mois_num, valeurs, marker='o', linewidth=2, label=puissance)
        
        ax1.set_xlabel('Mois')
        ax1.set_ylabel('Heures disponibles')
        ax1.set_title(f'Évolution mensuelle par puissance - {annee}')
        ax1.set_xticks(mois_num)
        ax1.set_xticklabels([m[:3] for m in mois], rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Graphique 2: Heatmap
        ax2 = axes[0, 1]
        im = ax2.imshow(tableau.T.values, cmap='RdYlGn', aspect='auto')
        ax2.set_xticks(range(len(mois)))
        ax2.set_xticklabels([m[:3] for m in mois], rotation=45)
        ax2.set_yticks(range(len(tableau.columns)))
        ax2.set_yticklabels(tableau.columns)
        ax2.set_xlabel('Mois')
        ax2.set_ylabel('Puissance (MW)')
        ax2.set_title(f'Heatmap saisonnalité - {annee}')
        plt.colorbar(im, ax=ax2, label='Heures disponibles')
        
        # Graphique 3: Barres groupées pour quelques puissances
        ax3 = axes[1, 0]
        puissances_cles = ['1 MW', '2 MW', '3 MW', '5 MW']
        x = np.arange(len(mois))
        width = 0.2
        
        for i, puissance in enumerate(puissances_cles):
            if puissance in tableau.columns:
                valeurs = tableau[puissance].values
                ax3.bar(x + i*width, valeurs, width, label=puissance)
        
        ax3.set_xlabel('Mois')
        ax3.set_ylabel('Heures disponibles')
        ax3.set_title(f'Comparaison par puissance - {annee}')
        ax3.set_xticks(x + width * 1.5)
        ax3.set_xticklabels([m[:3] for m in mois], rotation=45)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Graphique 4: Moyenne mobile
        ax4 = axes[1, 1]
        # Calculer la moyenne des heures disponibles toutes puissances confondues
        moyenne_mensuelle = tableau.mean(axis=1)
        ax4.plot(mois_num, moyenne_mensuelle, marker='o', linewidth=3, color='red', label='Moyenne')
        ax4.fill_between(mois_num, moyenne_mensuelle, alpha=0.3, color='red')
        
        ax4.set_xlabel('Mois')
        ax4.set_ylabel('Heures disponibles moyennes')
        ax4.set_title(f'Moyenne mensuelle toutes puissances - {annee}')
        ax4.set_xticks(mois_num)
        ax4.set_xticklabels([m[:3] for m in mois], rotation=45)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # Ajouter les valeurs sur la courbe
        for i, v in enumerate(moyenne_mensuelle):
            ax4.text(i+1, v + 5, f'{v:.0f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(f'analyse_saisonnalite_{annee}.png', dpi=300, bbox_inches='tight')
        plt.show()

def sauvegarder_resultats_excel(resultats_annees, resultats_saisonnalite):
    """Sauvegarde tous les résultats dans des fichiers Excel"""
    print("\n💾 Sauvegarde des résultats en Excel...")
    
    # 1. Sauvegarder les analyses par année
    with pd.ExcelWriter('analyse_heures_disponibles_par_annee.xlsx') as writer:
        for annee, tableau in resultats_annees.items():
            tableau.to_excel(writer, sheet_name=f'Annee_{annee}')
        
        # Ajouter une feuille de synthèse
        synthese = pd.DataFrame()
        for annee, tableau in resultats_annees.items():
            # Extraire les données pour 15 €/MWh
            if '15 €/MWh' in tableau.index:
                synthese[f'{annee}'] = tableau.loc['15 €/MWh']
        
        synthese.to_excel(writer, sheet_name='Synthese_15_EUR_MWh')
    
    # 2. Sauvegarder les analyses de saisonnalité
    with pd.ExcelWriter('analyse_saisonnalite_2023_2024.xlsx') as writer:
        for annee, tableau in resultats_saisonnalite.items():
            tableau.to_excel(writer, sheet_name=f'Saisonnalite_{annee}')
        
        # Comparaison 2023 vs 2024
        if 2023 in resultats_saisonnalite and 2024 in resultats_saisonnalite:
            comparaison = pd.DataFrame()
            for puissance in resultats_saisonnalite[2023].columns:
                comparaison[f'{puissance}_2023'] = resultats_saisonnalite[2023][puissance]
                if puissance in resultats_saisonnalite[2024].columns:
                    comparaison[f'{puissance}_2024'] = resultats_saisonnalite[2024][puissance]
            
            comparaison.to_excel(writer, sheet_name='Comparaison_2023_vs_2024')
    
    print("✅ Fichiers Excel créés:")
    print("   • analyse_heures_disponibles_par_annee.xlsx")
    print("   • analyse_saisonnalite_2023_2024.xlsx")

def generer_rapport_synthese(df, resultats_annees, resultats_saisonnalite):
    """Génère un rapport de synthèse"""
    print("\n📋 RAPPORT DE SYNTHÈSE - ANALYSE PUISSANCE DISPONIBLE")
    print("="*70)
    
    # Synthèse globale
    print(f"\n🔍 DONNÉES ANALYSÉES:")
    print(f"   • Période: {df.index.min().strftime('%Y-%m-%d')} à {df.index.max().strftime('%Y-%m-%d')}")
    print(f"   • Total d'heures: {len(df):,}")
    print(f"   • Années complètes: {len(resultats_annees)}")
    
    # Synthèse par année pour 15 €/MWh
    print(f"\n⚡ HEURES DISPONIBLES À 15 €/MWh PAR ANNÉE:")
    for annee in sorted(resultats_annees.keys()):
        tableau = resultats_annees[annee]
        if '15 €/MWh' in tableau.index:
            print(f"   • {annee}:")
            for puissance in tableau.columns:
                heures = tableau.loc['15 €/MWh', puissance]
                total_heures = 8760 if annee % 4 != 0 else 8784
                pct = (heures / total_heures) * 100
                print(f"     - {puissance}: {heures:,} heures ({pct:.1f}%)")
    
    # Analyse de tendance
    print(f"\n📈 TENDANCES:")
    if len(resultats_annees) >= 2:
        annees = sorted(resultats_annees.keys())
        premiere_annee = annees[0]
        derniere_annee = annees[-1]
        
        for puissance in resultats_annees[premiere_annee].columns:
            if '15 €/MWh' in resultats_annees[premiere_annee].index and '15 €/MWh' in resultats_annees[derniere_annee].index:
                heures_debut = resultats_annees[premiere_annee].loc['15 €/MWh', puissance]
                heures_fin = resultats_annees[derniere_annee].loc['15 €/MWh', puissance]
                evolution = ((heures_fin - heures_debut) / heures_debut) * 100
                tendance = "↗️" if evolution > 0 else "↘️" if evolution < 0 else "➡️"
                print(f"   • {puissance}: {evolution:+.1f}% ({premiere_annee} → {derniere_annee}) {tendance}")
    
    # Synthèse saisonnalité
    if resultats_saisonnalite:
        print(f"\n🌍 SAISONNALITÉ (15 €/MWh):")
        for annee in sorted(resultats_saisonnalite.keys()):
            tableau = resultats_saisonnalite[annee]
            print(f"   • {annee}:")
            
            # Meilleurs et pires mois
            moyenne_mensuelle = tableau.mean(axis=1)
            meilleur_mois = moyenne_mensuelle.idxmax()
            pire_mois = moyenne_mensuelle.idxmin()
            
            print(f"     - Meilleur mois: {meilleur_mois} ({moyenne_mensuelle[meilleur_mois]:.0f} h moy.)")
            print(f"     - Pire mois: {pire_mois} ({moyenne_mensuelle[pire_mois]:.0f} h moy.)")
            
            # Amplitude saisonnière
            amplitude = moyenne_mensuelle.max() - moyenne_mensuelle.min()
            print(f"     - Amplitude saisonnière: {amplitude:.0f} heures")

def main():
    """Fonction principale"""
    print("🚀 ANALYSE PUISSANCE DISPONIBLE METASTAAQ 2020-2025")
    print("="*60)
    
    # Charger les données
    df = charger_donnees_prix()
    
    # Analyse 1: Heures disponibles par année et par seuil de prix
    resultats_annees = analyser_puissance_par_annee(df)
    
    # Créer les graphiques par année
    creer_graphiques_heures_disponibles(resultats_annees)
    
    # Analyse 2: Saisonnalité pour 2023 et 2024
    resultats_saisonnalite = analyser_saisonnalite(df)
    
    # Créer les graphiques de saisonnalité
    creer_graphiques_saisonnalite(resultats_saisonnalite)
    
    # Sauvegarder en Excel
    sauvegarder_resultats_excel(resultats_annees, resultats_saisonnalite)
    
    # Générer le rapport de synthèse
    generer_rapport_synthese(df, resultats_annees, resultats_saisonnalite)
    
    print("\n✅ Analyse terminée!")
    print("\n📁 Fichiers générés:")
    print("   📊 Graphiques: analyse_heures_disponibles_XXXX.png")
    print("   📊 Graphiques: analyse_saisonnalite_XXXX.png")
    print("   📋 Excel: analyse_heures_disponibles_par_annee.xlsx")
    print("   📋 Excel: analyse_saisonnalite_2023_2024.xlsx")

if __name__ == "__main__":
    main() 