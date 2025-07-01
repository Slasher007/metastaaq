import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuration des graphiques
plt.style.use('seaborn-v0_8')
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 12
sns.set_palette("husl")

def charger_donnees_prix():
    """Charge et prépare les données de prix spot"""
    print("📊 Chargement des données de prix spot...")
    
    # Charger les données
    df = pd.read_csv('donnees_prix_spot_fr_2024_2025.csv', 
                     index_col=0, parse_dates=True)
    
    # Renommer la colonne si nécessaire
    if 'Prix_EUR_MWh' not in df.columns and len(df.columns) == 1:
        df.columns = ['Prix_EUR_MWh']
    
    # Ajouter des colonnes temporelles pour l'analyse
    df['Heure'] = df.index.hour
    df['JourSemaine'] = df.index.day_name()
    df['Mois'] = df.index.month_name()
    df['Date'] = df.index.date
    df['Trimestre'] = df.index.quarter
    
    print(f"✅ Données chargées: {len(df)} points de données")
    print(f"📅 Période: {df.index.min()} à {df.index.max()}")
    print(f"💰 Prix moyen: {df['Prix_EUR_MWh'].mean():.2f} €/MWh")
    print(f"📈 Prix min: {df['Prix_EUR_MWh'].min():.2f} €/MWh")
    print(f"📈 Prix max: {df['Prix_EUR_MWh'].max():.2f} €/MWh")
    
    return df

def analyser_patterns_horaires(df):
    """Analyse les patterns de prix par heure de la journée"""
    print("\n🕐 Analyse des patterns horaires...")
    
    # Statistiques par heure
    stats_horaires = df.groupby('Heure')['Prix_EUR_MWh'].agg([
        'mean', 'median', 'std', 'min', 'max', 'count'
    ]).round(2)
    
    # Pourcentage d'heures à prix négatifs par heure
    prix_negatifs = df[df['Prix_EUR_MWh'] < 0].groupby('Heure').size()
    total_heures = df.groupby('Heure').size()
    stats_horaires['pct_prix_negatifs'] = (prix_negatifs / total_heures * 100).fillna(0).round(1)
    
    # Pourcentage d'heures à moins de 15 €/MWh par heure
    prix_bas = df[df['Prix_EUR_MWh'] <= 15].groupby('Heure').size()
    stats_horaires['pct_prix_bas_15'] = (prix_bas / total_heures * 100).fillna(0).round(1)
    
    return stats_horaires

def analyser_creneaux_rentables(df, seuil_prix=15, pct_fonctionnement=40):
    """Identifie les créneaux les plus rentables selon l'objectif de fonctionnement"""
    print(f"\n🎯 Analyse des créneaux rentables (seuil: {seuil_prix} €/MWh, fonctionnement: {pct_fonctionnement}%)")
    
    # Trier par prix croissant
    df_sorted = df.sort_values('Prix_EUR_MWh')
    
    # Calculer le nombre d'heures pour le pourcentage de fonctionnement cible
    nb_heures_cible = int(len(df) * pct_fonctionnement / 100)
    
    # Sélectionner les heures les moins chères
    heures_optimales = df_sorted.head(nb_heures_cible)
    
    # Statistiques des créneaux optimaux
    cout_moyen_optimal = heures_optimales['Prix_EUR_MWh'].mean()
    cout_median_optimal = heures_optimales['Prix_EUR_MWh'].median()
    
    print(f"📊 Résultats pour {pct_fonctionnement}% de fonctionnement:")
    print(f"   • Nombre d'heures sélectionnées: {nb_heures_cible:,}")
    print(f"   • Coût moyen d'achat: {cout_moyen_optimal:.2f} €/MWh")
    print(f"   • Coût médian d'achat: {cout_median_optimal:.2f} €/MWh")
    print(f"   • Prix max dans la sélection: {heures_optimales['Prix_EUR_MWh'].max():.2f} €/MWh")
    print(f"   • Nombre d'heures à prix négatifs: {len(heures_optimales[heures_optimales['Prix_EUR_MWh'] < 0]):,}")
    
    # Analyse des patterns dans les heures optimales
    print(f"\n🕐 Répartition horaire des créneaux optimaux:")
    repartition_horaire = heures_optimales.groupby('Heure').size().sort_values(ascending=False)
    for heure, count in repartition_horaire.head(10).items():
        pct = (count / nb_heures_cible) * 100
        print(f"   • {heure:02d}h: {count:,} heures ({pct:.1f}%)")
    
    return heures_optimales, cout_moyen_optimal

def creer_graphiques_analyse(df, stats_horaires, heures_optimales):
    """Crée les graphiques d'analyse des prix spot"""
    print("\n📈 Création des graphiques d'analyse...")
    
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle('Analyse des Prix Spot - Optimisation METASTAAQ', fontsize=16, fontweight='bold')
    
    # 1. Distribution des prix
    axes[0, 0].hist(df['Prix_EUR_MWh'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0, 0].axvline(df['Prix_EUR_MWh'].mean(), color='red', linestyle='--', 
                       label=f'Moyenne: {df["Prix_EUR_MWh"].mean():.1f} €/MWh')
    axes[0, 0].axvline(15, color='green', linestyle='--', label='Objectif: 15 €/MWh')
    axes[0, 0].set_xlabel('Prix (€/MWh)')
    axes[0, 0].set_ylabel('Fréquence')
    axes[0, 0].set_title('Distribution des Prix Spot')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Prix moyens par heure
    axes[0, 1].bar(stats_horaires.index, stats_horaires['mean'], alpha=0.7, color='coral')
    axes[0, 1].axhline(15, color='green', linestyle='--', label='Objectif: 15 €/MWh')
    axes[0, 1].set_xlabel('Heure de la journée')
    axes[0, 1].set_ylabel('Prix moyen (€/MWh)')
    axes[0, 1].set_title('Prix Moyen par Heure')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Pourcentage d'heures à prix bas par heure
    axes[0, 2].bar(stats_horaires.index, stats_horaires['pct_prix_bas_15'], alpha=0.7, color='lightgreen')
    axes[0, 2].set_xlabel('Heure de la journée')
    axes[0, 2].set_ylabel('% heures ≤ 15 €/MWh')
    axes[0, 2].set_title('Opportunités par Heure (≤ 15 €/MWh)')
    axes[0, 2].grid(True, alpha=0.3)
    
    # 4. Évolution des prix dans le temps
    df_monthly = df.resample('M')['Prix_EUR_MWh'].mean()
    axes[1, 0].plot(df_monthly.index, df_monthly.values, marker='o', linewidth=2, color='navy')
    axes[1, 0].axhline(15, color='green', linestyle='--', label='Objectif: 15 €/MWh')
    axes[1, 0].set_xlabel('Mois')
    axes[1, 0].set_ylabel('Prix moyen (€/MWh)')
    axes[1, 0].set_title('Évolution Mensuelle des Prix')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # 5. Heatmap prix par heure et jour de la semaine
    jours_ordre = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_data = df.pivot_table(values='Prix_EUR_MWh', index='JourSemaine', columns='Heure', aggfunc='mean')
    pivot_data = pivot_data.reindex(jours_ordre)
    
    im = axes[1, 1].imshow(pivot_data.values, cmap='RdYlGn_r', aspect='auto')
    axes[1, 1].set_xticks(range(24))
    axes[1, 1].set_xticklabels(range(24))
    axes[1, 1].set_yticks(range(7))
    axes[1, 1].set_yticklabels(['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'])
    axes[1, 1].set_xlabel('Heure')
    axes[1, 1].set_ylabel('Jour de la semaine')
    axes[1, 1].set_title('Heatmap Prix par Heure et Jour')
    plt.colorbar(im, ax=axes[1, 1], label='Prix (€/MWh)')
    
    # 6. Analyse des créneaux optimaux
    repartition_optimale = heures_optimales.groupby('Heure').size()
    axes[1, 2].bar(repartition_optimale.index, repartition_optimale.values, alpha=0.7, color='gold')
    axes[1, 2].set_xlabel('Heure de la journée')
    axes[1, 2].set_ylabel('Nombre d\'heures sélectionnées')
    axes[1, 2].set_title('Répartition des Créneaux Optimaux')
    axes[1, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('analyse_prix_spot_metastaaq.png', dpi=300, bbox_inches='tight')
    plt.show()

def analyser_scenarios_fonctionnement(df):
    """Analyse différents scénarios de pourcentage de fonctionnement"""
    print("\n🔄 Analyse de scénarios de fonctionnement...")
    
    scenarios = [20, 30, 40, 50, 60]
    resultats = []
    
    for pct in scenarios:
        nb_heures = int(len(df) * pct / 100)
        heures_optimales = df.nsmallest(nb_heures, 'Prix_EUR_MWh')
        cout_moyen = heures_optimales['Prix_EUR_MWh'].mean()
        prix_max = heures_optimales['Prix_EUR_MWh'].max()
        heures_negatives = len(heures_optimales[heures_optimales['Prix_EUR_MWh'] < 0])
        
        resultats.append({
            'Fonctionnement (%)': pct,
            'Coût moyen (€/MWh)': cout_moyen,
            'Prix max seuil (€/MWh)': prix_max,
            'Heures à prix négatifs': heures_negatives,
            'Objectif 15€ atteint': '✅' if cout_moyen <= 15 else '❌'
        })
    
    df_scenarios = pd.DataFrame(resultats)
    print("\n📊 Comparaison des scénarios:")
    print(df_scenarios.to_string(index=False))
    
    return df_scenarios

def recommandations_strategiques(df, stats_horaires, heures_optimales, cout_optimal):
    """Génère les recommandations stratégiques"""
    print("\n" + "="*60)
    print("🎯 RECOMMANDATIONS STRATÉGIQUES - METASTAAQ")
    print("="*60)
    
    # Top 5 des meilleures heures
    top_heures = stats_horaires.nsmallest(5, 'mean')
    print("\n🕐 TOP 5 des créneaux horaires les plus rentables:")
    for heure, row in top_heures.iterrows():
        print(f"   • {heure:02d}h: {row['mean']:.1f} €/MWh (médiane: {row['median']:.1f} €/MWh)")
    
    # Analyse saisonnière
    prix_par_mois = df.groupby('Mois')['Prix_EUR_MWh'].mean().sort_values()
    print(f"\n📅 Meilleurs mois pour l'achat d'électricité:")
    for mois, prix in prix_par_mois.head(3).items():
        print(f"   • {mois}: {prix:.1f} €/MWh")
    
    # Stratégie recommandée
    print(f"\n💡 STRATÉGIE RECOMMANDÉE:")
    print(f"   • Fonctionnement optimal: 40% du temps ({len(heures_optimales):,} heures/an)")
    print(f"   • Coût d'achat moyen: {cout_optimal:.2f} €/MWh")
    print(f"   • Objectif 15 €/MWh: {'✅ ATTEINT' if cout_optimal <= 15 else '❌ NON ATTEINT'}")
    
    if cout_optimal <= 15:
        print(f"   • Marge sur objectif: {15 - cout_optimal:.2f} €/MWh")
    else:
        print(f"   • Écart à l'objectif: +{cout_optimal - 15:.2f} €/MWh")
    
    # Créneaux préférentiels
    heures_preferentielles = heures_optimales.groupby('Heure').size().sort_values(ascending=False).head(8)
    print(f"\n🎯 Créneaux horaires préférentiels (par ordre de priorité):")
    for heure, count in heures_preferentielles.items():
        pct = (count / len(heures_optimales)) * 100
        print(f"   • {heure:02d}h: {pct:.1f}% des heures optimales")

def main():
    """Fonction principale d'analyse"""
    print("🚀 ANALYSE DES PRIX SPOT POUR METASTAAQ")
    print("="*50)
    
    # Charger les données
    df = charger_donnees_prix()
    
    # Analyser les patterns horaires
    stats_horaires = analyser_patterns_horaires(df)
    
    # Identifier les créneaux rentables
    heures_optimales, cout_optimal = analyser_creneaux_rentables(df, seuil_prix=15, pct_fonctionnement=40)
    
    # Analyser différents scénarios
    scenarios = analyser_scenarios_fonctionnement(df)
    
    # Créer les graphiques
    creer_graphiques_analyse(df, stats_horaires, heures_optimales)
    
    # Recommandations
    recommandations_strategiques(df, stats_horaires, heures_optimales, cout_optimal)
    
    # Sauvegarder les résultats
    print(f"\n💾 Sauvegarde des résultats...")
    stats_horaires.to_csv('analyse_prix_horaires.csv')
    scenarios.to_csv('scenarios_fonctionnement.csv', index=False)
    heures_optimales.to_csv('creneaux_optimaux_40pct.csv')
    print("✅ Fichiers sauvegardés: analyse_prix_horaires.csv, scenarios_fonctionnement.csv, creneaux_optimaux_40pct.csv")

if __name__ == "__main__":
    main() 