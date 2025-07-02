import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from matplotlib.widgets import RadioButtons, Button
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
    
    # Charger les données (sans parse_dates pour éviter les problèmes de timezone)
    df = pd.read_csv('donnees_prix_spot_fr_2024_2025.csv', index_col=0)
    
    # Renommer la colonne si nécessaire
    if 'Prix_EUR_MWh' not in df.columns and len(df.columns) == 1:
        df.columns = ['Prix_EUR_MWh']
    
    # Convertir l'index en DatetimeIndex en gérant les timezone-aware datetimes
    print("🔄 Conversion de l'index en DatetimeIndex...")
    # Utiliser utc=True pour gérer les timezone-aware strings, convertir vers timezone locale, puis supprimer l'info de timezone
    df.index = pd.to_datetime(df.index, utc=True).tz_convert('Europe/Paris').tz_localize(None)
    
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

def filtrer_donnees_par_periode(df, periode_type, periode_valeur):
    """Filtre les données selon la période sélectionnée"""
    if periode_type == 'Toute la période':
        return df
    elif periode_type == 'Année':
        return df[df.index.year == int(periode_valeur)]
    elif periode_type == 'Mois':
        annee, mois = periode_valeur.split('-')
        return df[(df.index.year == int(annee)) & (df.index.month == int(mois))]
    else:
        return df

def obtenir_periodes_disponibles(df):
    """Retourne les périodes disponibles dans les données"""
    annees = sorted(df.index.year.unique())
    mois = []
    for annee in annees:
        for mois_num in sorted(df[df.index.year == annee].index.month.unique()):
            mois.append(f"{annee}-{mois_num:02d}")
    return annees, mois

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

def creer_interface_interactive(df_original):
    """Crée une interface interactive pour l'analyse des prix spot"""
    print("\n🎮 Création de l'interface interactive...")
    
    # Obtenir les périodes disponibles
    annees, mois = obtenir_periodes_disponibles(df_original)
    
    # Créer les options pour les radio buttons
    options_radio = ['Toutes les données']
    # Ajouter seulement les mois (format: 2024-07)
    for mois in mois:
        annee, mois_num = mois.split('-')
        nom_mois = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                   'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'][int(mois_num)-1]
        options_radio.append(f"{nom_mois} {annee}")
    
    # Variables globales pour l'état de l'interface
    state = {
        'selection_actuelle': 'Toutes les données',
        'df_filtre': df_original.copy(),
        'options': options_radio,
        'annees': annees,
        'mois': mois
    }
    
    # Créer la figure principale
    fig = plt.figure(figsize=(20, 15))
    
    # Zone pour les graphiques (laisser de l'espace pour les contrôles)
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3, 
                         left=0.22, right=0.95, top=0.92, bottom=0.05)
    
    # Axes pour les graphiques
    ax1 = fig.add_subplot(gs[0, 0])  # Distribution des prix
    ax2 = fig.add_subplot(gs[0, 1])  # Prix moyens par heure
    ax3 = fig.add_subplot(gs[0, 2])  # Opportunités par heure
    ax4 = fig.add_subplot(gs[1, 0])  # Évolution temporelle
    ax5 = fig.add_subplot(gs[1, 1:3])  # Heatmap
    ax6 = fig.add_subplot(gs[2, 0])  # Créneaux optimaux
    ax7 = fig.add_subplot(gs[2, 1])  # Prix par mois/année
    ax8 = fig.add_subplot(gs[2, 2:])  # Statistiques textuelles
    
    axes = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]
    
    # Zone pour les contrôles (côté gauche) - radio buttons pour sélection
    ax_radio = fig.add_axes([0.02, 0.1, 0.18, 0.8])
    radio = RadioButtons(ax_radio, options_radio)
    radio.set_active(0)  # "Toutes les données" par défaut
    
    # Titre pour les contrôles
    fig.text(0.02, 0.95, 'Sélectionnez la période:', fontsize=12, fontweight='bold')
    
    def mettre_a_jour_graphiques():
        """Met à jour tous les graphiques avec les données filtrées"""
        df_data = state['df_filtre']
        
        if len(df_data) == 0:
            for ax in axes:
                ax.clear()
                ax.text(0.5, 0.5, 'Aucune donnée\npour cette période', 
                       ha='center', va='center', transform=ax.transAxes)
            return
        
        # Recalculer les statistiques pour toutes les données
        stats_horaires = df_data.groupby('Heure')['Prix_EUR_MWh'].agg([
            'mean', 'median', 'std', 'min', 'max', 'count'
        ]).round(2)
        
        # Pourcentages
        prix_negatifs = df_data[df_data['Prix_EUR_MWh'] < 0].groupby('Heure').size()
        total_heures = df_data.groupby('Heure').size()
        stats_horaires['pct_prix_negatifs'] = (prix_negatifs / total_heures * 100).fillna(0).round(1)
        
        prix_bas = df_data[df_data['Prix_EUR_MWh'] <= 15].groupby('Heure').size()
        stats_horaires['pct_prix_bas_15'] = (prix_bas / total_heures * 100).fillna(0).round(1)
        
        # Créneaux optimaux pour toutes les données
        nb_heures_cible = int(len(df_data) * 40 / 100)
        heures_optimales = df_data.nsmallest(nb_heures_cible, 'Prix_EUR_MWh')
        
        # Effacer tous les axes
        for ax in axes:
            ax.clear()
        
        # 1. Distribution des prix
        ax1.hist(df_data['Prix_EUR_MWh'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.axvline(df_data['Prix_EUR_MWh'].mean(), color='red', linestyle='--', 
                   label=f'Moyenne: {df_data["Prix_EUR_MWh"].mean():.1f} €/MWh')
        ax1.axvline(15, color='green', linestyle='--', label='Objectif: 15 €/MWh')
        ax1.set_xlabel('Prix (€/MWh)')
        ax1.set_ylabel('Fréquence')
        ax1.set_title('Distribution des Prix')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Prix moyens par heure
        ax2.bar(stats_horaires.index, stats_horaires['mean'], alpha=0.7, color='coral')
        ax2.axhline(15, color='green', linestyle='--', label='Objectif: 15 €/MWh')
        ax2.set_xlabel('Heure')
        ax2.set_ylabel('Prix moyen (€/MWh)')
        ax2.set_title('Prix Moyen par Heure')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Opportunités par heure
        ax3.bar(stats_horaires.index, stats_horaires['pct_prix_bas_15'], 
               alpha=0.7, color='lightgreen')
        ax3.set_xlabel('Heure')
        ax3.set_ylabel('% heures ≤ 15 €/MWh')
        ax3.set_title('Opportunités par Heure (≤ 15 €/MWh)')
        ax3.grid(True, alpha=0.3)
        
        # 4. Évolution temporelle adaptative
        is_monthly_view = (state['selection_actuelle'] != 'Toutes les données')
        
        if len(df_data) > 1:
            if is_monthly_view:
                # Vue mensuelle : évolution journalière
                df_temporal = df_data.resample('D')['Prix_EUR_MWh'].mean()
                ax4.plot(df_temporal.index, df_temporal.values, marker='o', linewidth=2, color='navy')
                ax4.set_xlabel('Jour')
                ax4.set_title('Évolution Journalière')
            else:
                # Vue globale ou annuelle : évolution mensuelle
                df_temporal = df_data.resample('M')['Prix_EUR_MWh'].mean()
                ax4.plot(df_temporal.index, df_temporal.values, marker='o', linewidth=2, color='navy')
                ax4.set_xlabel('Mois')
                ax4.set_title('Évolution Mensuelle')
            
            ax4.axhline(15, color='green', linestyle='--', label='Objectif: 15 €/MWh')
            ax4.set_ylabel('Prix moyen (€/MWh)')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            ax4.tick_params(axis='x', rotation=45)
        
        # 5. Heatmap prix par heure et jour de la semaine
        jours_ordre = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot_data = df_data.pivot_table(values='Prix_EUR_MWh', index='JourSemaine', 
                                       columns='Heure', aggfunc='mean')
        pivot_data = pivot_data.reindex(jours_ordre)
        
        im = ax5.imshow(pivot_data.values, cmap='RdYlGn_r', aspect='auto')
        ax5.set_xticks(range(24))
        ax5.set_xticklabels(range(24))
        ax5.set_yticks(range(len(pivot_data)))
        ax5.set_yticklabels(['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'])
        ax5.set_xlabel('Heure')
        ax5.set_ylabel('Jour de la semaine')
        ax5.set_title('Heatmap Prix par Heure et Jour')
        plt.colorbar(im, ax=ax5, label='Prix (€/MWh)')
        
        # 6. Créneaux optimaux
        repartition_optimale = heures_optimales.groupby('Heure').size()
        ax6.bar(repartition_optimale.index, repartition_optimale.values, alpha=0.7, color='gold')
        ax6.set_xlabel('Heure')
        ax6.set_ylabel('Heures sélectionnées')
        ax6.set_title('Créneaux Optimaux (40%)')
        ax6.grid(True, alpha=0.3)
        
        # 7. Comparaison adaptative selon le filtre sélectionné
        if state['selection_actuelle'] == 'Toutes les données':
            # Vue globale : comparer par année si plusieurs années, sinon par mois
            if len(state['annees']) > 1:
                # Prix moyens par année
                prix_annees = []
                for annee in state['annees']:
                    df_annee = df_original[df_original.index.year == annee]
                    prix_annees.append(df_annee['Prix_EUR_MWh'].mean())
                
                ax7.bar([str(a) for a in state['annees']], prix_annees, alpha=0.7, color='purple')
                ax7.set_xlabel('Année')
                ax7.set_title('Comparaison par Année')
            else:
                # Prix par mois de l'année
                prix_mois = df_original.groupby(df_original.index.month)['Prix_EUR_MWh'].mean()
                mois_noms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                            'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
                ax7.bar([mois_noms[i-1] for i in prix_mois.index], prix_mois.values, alpha=0.7, color='orange')
                ax7.set_xlabel('Mois')
                ax7.set_title('Comparaison par Mois')
                ax7.tick_params(axis='x', rotation=45)
        else:
            # Vue mensuelle spécifique : comparer ce mois avec les autres mois ou montrer la répartition hebdomadaire
            mois_selectionne = state['selection_actuelle'].split(' ')
            mois_nom = mois_selectionne[0]
            annee_selectionnee = int(mois_selectionne[1])
            
            # Mapping des noms de mois
            mois_mapping = {'Jan': 1, 'Fév': 2, 'Mar': 3, 'Avr': 4, 'Mai': 5, 'Jun': 6,
                           'Jul': 7, 'Aoû': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Déc': 12}
            mois_num = mois_mapping[mois_nom]
            
            # Option 1: Comparer ce mois avec les mêmes mois des autres années (si disponible)
            memes_mois_autres_annees = []
            annees_disponibles = []
            for annee in state['annees']:
                df_meme_mois = df_original[(df_original.index.year == annee) & (df_original.index.month == mois_num)]
                if len(df_meme_mois) > 0:
                    memes_mois_autres_annees.append(df_meme_mois['Prix_EUR_MWh'].mean())
                    annees_disponibles.append(annee)
            
            if len(annees_disponibles) > 1:
                # Comparer le même mois sur différentes années
                colors = ['red' if a == annee_selectionnee else 'lightblue' for a in annees_disponibles]
                bars = ax7.bar([str(a) for a in annees_disponibles], memes_mois_autres_annees, 
                              alpha=0.7, color=colors)
                ax7.set_xlabel('Année')
                ax7.set_title(f'Comparaison {mois_nom} sur Différentes Années')
                
                # Mettre en évidence l'année sélectionnée
                for i, annee in enumerate(annees_disponibles):
                    if annee == annee_selectionnee:
                        bars[i].set_edgecolor('darkred')
                        bars[i].set_linewidth(2)
            else:
                # Pas d'autres années disponibles : montrer la répartition par semaine du mois
                df_semaines = df_data.groupby(df_data.index.isocalendar().week)['Prix_EUR_MWh'].mean()
                semaines_labels = [f"S{int(s)}" for s in df_semaines.index]
                ax7.bar(semaines_labels, df_semaines.values, alpha=0.7, color='green')
                ax7.set_xlabel('Semaine')
                ax7.set_title(f'Prix Moyen par Semaine - {mois_nom} {annee_selectionnee}')
        
        # Ligne de référence et mise en forme commune
        ax7.axhline(15, color='green', linestyle='--', label='Objectif: 15 €/MWh')
        ax7.set_ylabel('Prix moyen (€/MWh)')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # 8. Statistiques détaillées
        ax8.axis('off')
        if state['selection_actuelle'] == 'Toutes les données':
            titre_stats = "ANALYSE COMPLÈTE DES PRIX SPOT ÉLECTRICITÉ"
            duree_desc = f"{len(state['annees'])} année(s), {len(state['mois'])} mois"
        else:
            titre_stats = f"ANALYSE MENSUELLE {state['selection_actuelle']}"
            duree_desc = "1 mois complet"
        
        stats_text = f"""
📊 {titre_stats} - METASTAAQ

🔢 Données de la période:
• Nombre de points: {len(df_data):,} heures
• Période: {df_data.index.min().strftime('%d/%m/%Y')} au {df_data.index.max().strftime('%d/%m/%Y')}
• Durée: {duree_desc}

💰 Statistiques des prix:
• Prix moyen: {df_data['Prix_EUR_MWh'].mean():.2f} €/MWh
• Prix médian: {df_data['Prix_EUR_MWh'].median():.2f} €/MWh
• Écart-type: {df_data['Prix_EUR_MWh'].std():.2f} €/MWh
• Prix minimum: {df_data['Prix_EUR_MWh'].min():.2f} €/MWh
• Prix maximum: {df_data['Prix_EUR_MWh'].max():.2f} €/MWh

🎯 Analyse de l'objectif (≤ 15 €/MWh):
• Heures favorables: {len(df_data[df_data['Prix_EUR_MWh'] <= 15]):,} ({len(df_data[df_data['Prix_EUR_MWh'] <= 15])/len(df_data)*100:.1f}%)
• Heures à prix négatifs: {len(df_data[df_data['Prix_EUR_MWh'] < 0]):,} ({len(df_data[df_data['Prix_EUR_MWh'] < 0])/len(df_data)*100:.1f}%)

⚡ Stratégie optimisée (40% de fonctionnement):
• Coût d'achat moyen optimal: {heures_optimales['Prix_EUR_MWh'].mean():.2f} €/MWh
• Prix seuil maximum: {heures_optimales['Prix_EUR_MWh'].max():.2f} €/MWh
• Économie vs prix moyen: {df_data['Prix_EUR_MWh'].mean() - heures_optimales['Prix_EUR_MWh'].mean():.2f} €/MWh
• Objectif 15€/MWh: {'✅ ATTEINT' if heures_optimales['Prix_EUR_MWh'].mean() <= 15 else '❌ NON ATTEINT'}

🕐 Meilleurs créneaux horaires:
"""
        
        # Ajouter le top 5 des meilleures heures
        top_heures = stats_horaires.nsmallest(5, 'mean')
        for heure, row in top_heures.iterrows():
            stats_text += f"• {heure:02d}h: {row['mean']:.1f} €/MWh\n"
        
        ax8.text(0.02, 0.98, stats_text, transform=ax8.transAxes, fontsize=9,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
        
        # Mettre à jour le titre principal
        fig.suptitle(f'Analyse Prix Spot - METASTAAQ ({state["selection_actuelle"]})', 
                    fontsize=16, fontweight='bold')
        
        plt.draw()
    
    def on_radio_clicked(label):
        """Gestionnaire pour les boutons radio"""
        state['selection_actuelle'] = label
        
        if label == 'Toutes les données':
            state['df_filtre'] = df_original.copy()
        else:
            # C'est un mois (format: "Jul 2024")
            mois_nom, annee = label.split(' ')
            mois_mapping = {'Jan': '01', 'Fév': '02', 'Mar': '03', 'Avr': '04', 'Mai': '05', 'Jun': '06',
                           'Jul': '07', 'Aoû': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Déc': '12'}
            mois_num = mois_mapping[mois_nom]
            periode_valeur = f"{annee}-{mois_num}"
            state['df_filtre'] = filtrer_donnees_par_periode(df_original, 'Mois', periode_valeur)
        
        mettre_a_jour_graphiques()
    
    # Connecter les événements
    radio.on_clicked(on_radio_clicked)
    
    # Affichage initial avec toutes les données
    mettre_a_jour_graphiques()
    
    plt.show()
    
    return fig

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
    
    # Créer l'interface interactive
    print("\n🎮 Lancement de l'interface interactive...")
    print("📊 Filtres disponibles:")
    print("   • Toutes les données: Vue d'ensemble complète")
    print("   • Par mois: Analyse détaillée d'un mois spécifique")
    print("\n⚠️  Fermez la fenêtre graphique pour continuer le script.")
    
    fig_interactive = creer_interface_interactive(df)
    
    # Sauvegarder les résultats de base
    print(f"\n💾 Sauvegarde des résultats...")
    stats_horaires.to_csv('analyse_prix_horaires.csv')
    scenarios.to_csv('scenarios_fonctionnement.csv', index=False)
    heures_optimales.to_csv('creneaux_optimaux_40pct.csv')
    print("✅ Fichiers sauvegardés: analyse_prix_horaires.csv, scenarios_fonctionnement.csv, creneaux_optimaux_40pct.csv")
    
    print("\n✅ Analyse terminée!")

if __name__ == "__main__":
    main() 