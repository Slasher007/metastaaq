import os
import pandas as pd
from datetime import datetime, timedelta
from pvlib.iotools import get_pvgis_hourly
from entsoe import EntsoePandasClient
import numpy as np

def telecharger_donnees_pvgis_multi_annees(lat, lon, annee_debut=2020, annee_fin=2024):
    """
    Télécharge les données de production PV horaire depuis PVGIS pour plusieurs années.
    """
    print(f"Téléchargement des données PVGIS pour les années {annee_debut} à {annee_fin}...")
    
    all_data = []
    
    for annee in range(annee_debut, annee_fin + 1):
        print(f"  → Téléchargement pour l'année {annee}...")
        try:
            # Appel à l'API de PVGIS via la bibliothèque pvlib
            data, metadata, inputs = get_pvgis_hourly(
                latitude=lat,
                longitude=lon,
                start=annee,
                end=annee,
                pvcalculation=True,
                peakpower=5000,  # 5000 kWc = 5 MWc
                loss=14,         # Pertes système en %
                mountingplace='free',
                surface_tilt=35,
                surface_azimuth=0,
                outputformat='csv'
            )
            
            # Renommer les colonnes pour plus de clarté
            data.rename(columns={
                'P': 'Puissance_W',
                'G(i)': 'Irradiation_globale_plan_W_m2',
                'H_sun': 'Elevation_soleil_deg',
                'T2m': 'Temperature_air_C',
                'WS10m': 'Vitesse_vent_ms'
            }, inplace=True)

            all_data.append(data)
            print(f"  ✅ Données {annee} téléchargées avec succès")
            
        except Exception as e:
            print(f"  ❌ Erreur pour l'année {annee}: {e}")
    
    if all_data:
        # Combiner toutes les données
        combined_data = pd.concat(all_data, ignore_index=True)
        combined_data.sort_index(inplace=True)
        
        nom_fichier = f'donnees_production_pv_meaux_{annee_debut}_{annee_fin}.csv'
        combined_data.to_csv(nom_fichier)
        print(f"✅ Toutes les données PVGIS enregistrées avec succès dans '{nom_fichier}'")
        print(f"📊 Total: {len(combined_data)} points de données")
        return nom_fichier
    else:
        print("❌ Aucune donnée n'a pu être téléchargée")
        return None

def telecharger_donnees_entsoe_5_ans(api_key, pays_code='FR'):
    """
    Télécharge les prix spot Day-Ahead depuis l'API ENTSO-E pour les 5 dernières années.
    Ajoute également les colonnes de puissances disponibles selon les seuils de prix.
    """
    print("Téléchargement des données de prix spot depuis ENTSO-E pour les 5 dernières années...")
    if not api_key or api_key == "VOTRE_CLE_API_ENTSOE_ICI":
        print("Erreur : Clé API ENTSO-E non configurée.")
        print("Veuillez suivre les instructions ici pour obtenir une clé : https://transparencyplatform.zendesk.com/hc/en-us/articles/12845911031188-How-to-get-security-token")
        return None
        
    try:
        client = EntsoePandasClient(api_key=api_key)
        
        # Définir la période : les 5 dernières années
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)  # 5 ans approximatif
        
        print(f"📅 Période de téléchargement: {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}")
        
        # Conversion au format attendu par la bibliothèque
        start_ts = pd.Timestamp(start_date.strftime('%Y%m%d'), tz='Europe/Brussels')
        end_ts = pd.Timestamp(end_date.strftime('%Y%m%d'), tz='Europe/Brussels')

        # Requête pour les prix Day-Ahead
        print("🔄 Requête en cours vers l'API ENTSO-E...")
        prices = client.query_day_ahead_prices(pays_code, start=start_ts, end=end_ts)
        
        # Convertir en DataFrame avec le nom de colonne standard
        df = pd.DataFrame(prices, columns=['Prix_EUR_MWh'])
        
        # Ajouter les colonnes de puissances disponibles
        print("⚡ Calcul des puissances disponibles par seuil de prix...")
        
        # Définir les seuils de puissance (MW) et les seuils de prix (€/MWh)
        puissances = [0.5, 1, 2, 3, 4, 5]
        seuils_prix = [5, 10, 15, 20, 25, 30, 35, 40]
        
        print(f"📊 Seuils de puissance: {puissances} MW")
        print(f"💰 Seuils de prix: {seuils_prix} €/MWh")
        
        # Pour chaque combinaison puissance/seuil, ajouter une colonne booléenne
        # indiquant si l'électrolyseur peut fonctionner à cette puissance avec ce prix
        for puissance in puissances:
            for seuil in seuils_prix:
                col_name = f'Disponible_{puissance}MW_max_{seuil}EUR_MWh'
                # L'électrolyseur peut fonctionner si le prix est inférieur ou égal au seuil
                df[col_name] = (df['Prix_EUR_MWh'] <= seuil).astype(int)
        
        # Ajouter des colonnes de synthèse pour les seuils de prix importants
        print("📈 Ajout de colonnes de synthèse...")
        
        # Colonnes indiquant le niveau de puissance maximal disponible pour chaque seuil clé
        seuils_cles = [15, 20, 25, 30]  # Seuils les plus pertinents pour le projet
        
        for seuil in seuils_cles:
            col_name = f'Puissance_max_disponible_{seuil}EUR_MWh'
            # Calculer la puissance maximale disponible pour ce prix
            df[col_name] = 0  # Initialiser à 0
            
            for puissance in puissances:
                # Si le prix permet ce niveau de puissance, mettre à jour la puissance max
                condition = df['Prix_EUR_MWh'] <= seuil
                df.loc[condition, col_name] = puissance
        
        # Ajouter des colonnes de classification du prix
        print("🏷️ Ajout de classifications de prix...")
        
        # Classification qualitative du prix
        def classifier_prix(prix):
            if prix < 0:
                return "Négatif"
            elif prix <= 10:
                return "Très bas"
            elif prix <= 20:
                return "Bas"
            elif prix <= 40:
                return "Modéré"
            elif prix <= 80:
                return "Élevé"
            else:
                return "Très élevé"
        
        df['Classification_prix'] = df['Prix_EUR_MWh'].apply(classifier_prix)
        
        # Opportunité de fonctionnement (très favorable pour l'électrolyseur)
        df['Opportunite_excellente'] = (df['Prix_EUR_MWh'] <= 5).astype(int)
        df['Opportunite_bonne'] = (df['Prix_EUR_MWh'] <= 15).astype(int)
        df['Opportunite_acceptable'] = (df['Prix_EUR_MWh'] <= 25).astype(int)
        
        # Sauvegarder le fichier enrichi
        nom_fichier = f'donnees_prix_spot_{pays_code}_{start_date.year}_{end_date.year}.csv'
        df.to_csv(nom_fichier)
        
        print(f"✅ Données de prix spot enrichies enregistrées dans '{nom_fichier}'")
        print(f"📊 Total: {len(df)} points de données")
        print(f"🔌 Colonnes ajoutées: {len(df.columns) - 1} colonnes de puissance disponible")
        
        # Afficher des statistiques de synthèse
        print(f"\n📈 STATISTIQUES DE PUISSANCES DISPONIBLES:")
        print("="*50)
        
        for seuil in seuils_cles:
            col_name = f'Puissance_max_disponible_{seuil}EUR_MWh'
            stats = df[col_name].value_counts().sort_index()
            print(f"\n💰 Répartition des puissances disponibles à ≤ {seuil} €/MWh:")
            for puissance, count in stats.items():
                pct = (count / len(df)) * 100
                print(f"   • {puissance} MW: {count:,} heures ({pct:.1f}%)")
        
        print(f"\n🎯 OPPORTUNITÉS DE FONCTIONNEMENT:")
        print("="*40)
        for opportunite in ['excellente', 'bonne', 'acceptable']:
            col_name = f'Opportunite_{opportunite}'
            count = df[col_name].sum()
            pct = (count / len(df)) * 100
            print(f"   • Opportunité {opportunite}: {count:,} heures ({pct:.1f}%)")
        
        return nom_fichier
        
    except Exception as e:
        print(f"❌ Une erreur est survenue lors du téléchargement des données ENTSO-E : {e}")
        return None

def telecharger_donnees_spot_historiques_detaillees(api_key, annee_debut=2021, annee_fin=2025, mois_fin=9, pays_code='FR'):
    """
    Télécharge les données historiques des prix spot de l'électricité pour analyse détaillée
    des puissances disponibles par tranche horaire (2021-2025).
    
    Args:
        api_key: Clé API ENTSO-E
        annee_debut: Année de début (défaut: 2021)
        annee_fin: Année de fin (défaut: 2025)
        mois_fin: Mois de fin pour la dernière année (défaut: 7 pour juillet)
        pays_code: Code pays (défaut: 'FR')
    
    Returns:
        str: Nom du fichier CSV généré avec les analyses détaillées
    """
    print(f"🔍 TÉLÉCHARGEMENT DÉTAILLÉ DES PRIX SPOT HISTORIQUES")
    print(f"📅 Période: {annee_debut} - {mois_fin:02d}/{annee_fin}")
    print("="*60)
    
    if not api_key or api_key == "VOTRE_CLE_API_ENTSOE_ICI":
        print("❌ Erreur : Clé API ENTSO-E non configurée.")
        print("📋 Instructions : https://transparencyplatform.zendesk.com/hc/en-us/articles/12845911031188-How-to-get-security-token")
        return None
    
    try:
        client = EntsoePandasClient(api_key=api_key)
        
        # Définir les dates précises
        start_date = datetime(annee_debut, 1, 1)
        if annee_fin == datetime.now().year and mois_fin <= datetime.now().month:
            end_date = datetime(annee_fin, mois_fin, 31)
        else:
            end_date = datetime(annee_fin, mois_fin, 31)
        
        print(f"📅 Période exacte: {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}")
        
        # Conversion au format ENTSO-E
        start_ts = pd.Timestamp(start_date, tz='Europe/Brussels')
        end_ts = pd.Timestamp(end_date, tz='Europe/Brussels')
        
        print("🔄 Téléchargement des prix spot depuis ENTSO-E...")
        prices = client.query_day_ahead_prices(pays_code, start=start_ts, end=end_ts)
        
        # Créer le DataFrame principal
        df = pd.DataFrame(prices, columns=['Prix_EUR_MWh'])
        df.index.name = 'DateTime'
        
        print(f"✅ {len(df):,} points de données téléchargés")
        
        # Ajouter des informations temporelles
        print("📊 Ajout des informations temporelles...")
        df['Annee'] = df.index.year
        df['Mois'] = df.index.month
        df['Jour'] = df.index.day
        df['Heure'] = df.index.hour
        df['Jour_semaine'] = df.index.dayofweek  # 0=Lundi, 6=Dimanche
        df['Est_weekend'] = (df['Jour_semaine'] >= 5).astype(int)
        
        # Noms des jours et mois en français
        jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        mois_fr = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                   'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        
        df['Nom_jour'] = df['Jour_semaine'].map(lambda x: jours_fr[x])
        df['Nom_mois'] = df['Mois'].map(lambda x: mois_fr[x])
        
        # Classification des créneaux horaires
        def classifier_creneau(heure):
            if 2 <= heure <= 5:
                return "Nuit profonde"
            elif 6 <= heure <= 8:
                return "Matin"
            elif 9 <= heure <= 11:
                return "Matinée"
            elif 12 <= heure <= 14:
                return "Midi"
            elif 15 <= heure <= 18:
                return "Après-midi"
            elif 19 <= heure <= 21:
                return "Soirée"
            else:
                return "Nuit"
        
        df['Creneau_horaire'] = df['Heure'].apply(classifier_creneau)
        
        # ANALYSE DES PUISSANCES DISPONIBLES
        print("⚡ Analyse détaillée des puissances disponibles...")
        
        # Niveaux de puissance à analyser (MW)
        niveaux_puissance = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0]
        
        # Seuils de prix stratégiques (€/MWh)
        seuils_prix = [0, 5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 80, 100]
        
        print(f"🔌 Niveaux de puissance analysés: {niveaux_puissance} MW")
        print(f"💰 Seuils de prix analysés: {seuils_prix} €/MWh")
        
        # Pour chaque niveau de puissance et chaque seuil de prix
        for puissance in niveaux_puissance:
            for seuil in seuils_prix:
                col_name = f'Disponible_{puissance}MW_max_{seuil}EUR'
                df[col_name] = (df['Prix_EUR_MWh'] <= seuil).astype(int)
        
        # Calcul de la puissance maximale disponible pour chaque heure
        print("📈 Calcul des puissances maximales disponibles...")
        
        def calculer_puissance_max(prix, seuil_max=50):
            """Calcule la puissance maximale disponible pour un prix donné"""
            if prix <= seuil_max:
                for puissance in reversed(niveaux_puissance):  # Commencer par la plus haute
                    if prix <= seuil_max:  # Condition simplifiée - peut être ajustée
                        return puissance
            return 0
        
        # Puissance maximale pour différents budgets
        for budget in [15, 20, 25, 30, 40, 50]:
            df[f'Puissance_max_{budget}EUR'] = df['Prix_EUR_MWh'].apply(
                lambda x: max([p for p in niveaux_puissance if x <= budget], default=0)
            )
        
        # CLASSIFICATION AVANCÉE DES PRIX
        print("🏷️ Classification avancée des prix...")
        
        def classifier_prix_detaille(prix):
            if prix < 0:
                return "Négatif"
            elif prix <= 5:
                return "Très favorable"
            elif prix <= 15:
                return "Favorable"
            elif prix <= 25:
                return "Acceptable"
            elif prix <= 40:
                return "Modéré"
            elif prix <= 60:
                return "Élevé"
            elif prix <= 100:
                return "Très élevé"
            else:
                return "Excessif"
        
        df['Classification_prix'] = df['Prix_EUR_MWh'].apply(classifier_prix_detaille)
        
        # Opportunités stratégiques par niveau de puissance
        for puissance in niveaux_puissance:
            # Opportunité excellente: prix très bas permettant fonctionnement économique
            df[f'Opportunite_excellente_{puissance}MW'] = (df['Prix_EUR_MWh'] <= 10).astype(int)
            # Opportunité bonne: prix raisonnable
            df[f'Opportunite_bonne_{puissance}MW'] = (df['Prix_EUR_MWh'] <= 25).astype(int)
            # Opportunité acceptable: prix limite
            df[f'Opportunite_acceptable_{puissance}MW'] = (df['Prix_EUR_MWh'] <= 40).astype(int)
        
        # HEURES D'UTILISATION OPTIMALES
        print("⏰ Calcul des heures d'utilisation optimales...")
        
        # Créer des colonnes pour les tranches de prix les plus intéressantes
        tranches_prix = [
            (0, 10, "Prix_0_10EUR"),
            (10, 20, "Prix_10_20EUR"), 
            (20, 30, "Prix_20_30EUR"),
            (30, 40, "Prix_30_40EUR"),
            (40, 60, "Prix_40_60EUR"),
            (60, float('inf'), "Prix_plus_60EUR")
        ]
        
        for min_prix, max_prix, nom_col in tranches_prix:
            if max_prix == float('inf'):
                df[nom_col] = (df['Prix_EUR_MWh'] >= min_prix).astype(int)
            else:
                df[nom_col] = ((df['Prix_EUR_MWh'] >= min_prix) & 
                              (df['Prix_EUR_MWh'] < max_prix)).astype(int)
        
        # Sauvegarder le fichier enrichi
        nom_fichier = f'donnees_spot_detaillees_{pays_code}_{annee_debut}_{annee_fin}.csv'
        df.to_csv(nom_fichier)
        
        print(f"✅ Données enrichies sauvegardées: '{nom_fichier}'")
        print(f"📊 Nombre total de colonnes: {len(df.columns)}")
        
        # GÉNÉRATION DU RAPPORT D'ANALYSE
        print(f"\n📈 RAPPORT D'ANALYSE DÉTAILLÉ")
        print("="*70)
        
        # Statistiques générales
        print(f"\n🔢 STATISTIQUES GÉNÉRALES:")
        print(f"   • Période analysée: {len(df):,} heures")
        print(f"   • Prix moyen: {df['Prix_EUR_MWh'].mean():.2f} €/MWh")
        print(f"   • Prix médian: {df['Prix_EUR_MWh'].median():.2f} €/MWh")
        print(f"   • Prix minimum: {df['Prix_EUR_MWh'].min():.2f} €/MWh")
        print(f"   • Prix maximum: {df['Prix_EUR_MWh'].max():.2f} €/MWh")
        
        # Analyse par année
        print(f"\n📅 ÉVOLUTION ANNUELLE:")
        stats_annuelles = df.groupby('Annee')['Prix_EUR_MWh'].agg(['mean', 'median', 'min', 'max', 'count'])
        for annee, stats in stats_annuelles.iterrows():
            print(f"   • {annee}: Moy={stats['mean']:.1f}€ | Méd={stats['median']:.1f}€ | " +
                  f"Min={stats['min']:.1f}€ | Max={stats['max']:.1f}€ | {stats['count']:,}h")
        
        # Heures disponibles par niveau de puissance
        print(f"\n⚡ HEURES DISPONIBLES PAR PUISSANCE (≤ 25€/MWh):")
        for puissance in niveaux_puissance:
            heures_dispo = df[f'Disponible_{puissance}MW_max_25EUR'].sum()
            pourcentage = (heures_dispo / len(df)) * 100
            print(f"   • {puissance:3.1f} MW: {heures_dispo:,} heures ({pourcentage:.1f}%)")
        
        # Analyse par créneau horaire
        print(f"\n⏰ PRIX MOYEN PAR CRÉNEAU HORAIRE:")
        prix_par_creneau = df.groupby('Creneau_horaire')['Prix_EUR_MWh'].mean().sort_values()
        for creneau, prix_moy in prix_par_creneau.items():
            print(f"   • {creneau:12}: {prix_moy:.1f} €/MWh")
        
        # Opportunités par tranche de prix
        print(f"\n💰 RÉPARTITION DES HEURES PAR TRANCHE DE PRIX:")
        for min_prix, max_prix, nom_col in tranches_prix:
            heures = df[nom_col].sum()
            pourcentage = (heures / len(df)) * 100
            if max_prix == float('inf'):
                print(f"   • ≥ {min_prix:2.0f} €/MWh: {heures:,} heures ({pourcentage:.1f}%)")
            else:
                print(f"   • {min_prix:2.0f}-{max_prix:2.0f} €/MWh: {heures:,} heures ({pourcentage:.1f}%)")
        
        # Analyse weekend vs semaine
        print(f"\n📊 COMPARAISON WEEKEND/SEMAINE:")
        prix_semaine = df[df['Est_weekend'] == 0]['Prix_EUR_MWh'].mean()
        prix_weekend = df[df['Est_weekend'] == 1]['Prix_EUR_MWh'].mean()
        print(f"   • Prix moyen semaine: {prix_semaine:.1f} €/MWh")
        print(f"   • Prix moyen weekend: {prix_weekend:.1f} €/MWh")
        print(f"   • Différence: {prix_weekend - prix_semaine:+.1f} €/MWh")
        
        return nom_fichier
        
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement: {e}")
        import traceback
        traceback.print_exc()
        return None


# Garder les anciennes fonctions pour compatibilité
def telecharger_donnees_pvgis(lat, lon, annee=2020):
    """
    Télécharge les données de production PV horaire depuis PVGIS pour une année donnée.
    """
    return telecharger_donnees_pvgis_multi_annees(lat, lon, annee, annee)

def telecharger_donnees_entsoe(api_key, pays_code='FR'):
    """
    Télécharge les prix spot Day-Ahead depuis l'API ENTSO-E pour les 365 derniers jours.
    """
    return telecharger_donnees_entsoe_5_ans(api_key, pays_code)

if __name__ == '__main__':
    # --- PARAMETRES ---
    # Coordonnées de Meaux (77)
    LATITUDE_MEAUX = 48.96
    LONGITUDE_MEAUX = 2.88
    
    # !! IMPORTANT !!
    # Remplacez la ligne ci-dessous par votre propre clé API obtenue sur le site d'ENTSO-E
    # Instructions détaillées pour obtenir le token : https://transparencyplatform.zendesk.com/hc/en-us/articles/12845911031188-How-to-get-security-token
    ENTSOE_API_KEY = os.getenv('ENTSOE_API_TOKEN', "9d9b8840-56e2-4993-9385-47cfe2b8183f")

    print("🚀 TÉLÉCHARGEMENT DES DONNÉES - ANALYSE COMPLÈTE")
    print("="*60)
    
    # Choix du mode d'analyse
    print("\n🔧 MODES DISPONIBLES:")
    print("1. Analyse standard (5 dernières années)")
    print("2. Analyse détaillée des prix spot (2021-2025)")
    print("3. Les deux analyses")
    
    mode = input("\nChoisissez le mode (1/2/3) [défaut: 2]: ").strip() or "2"
    
    if mode in ["1", "3"]:
        # 1. Récupération des données solaires (2020-2024)
        print("\n📊 1. DONNÉES SOLAIRES PVGIS")
        print("-" * 40)
        telecharger_donnees_pvgis_multi_annees(LATITUDE_MEAUX, LONGITUDE_MEAUX, 2020, 2024)
        
        print("\n💰 2. DONNÉES PRIX SPOT ENTSO-E (Mode standard)")
        print("-" * 50)
        telecharger_donnees_entsoe_5_ans(ENTSOE_API_KEY, pays_code='FR')
    
    if mode in ["2", "3"]:
        print("\n🔍 ANALYSE DÉTAILLÉE DES PRIX SPOT HISTORIQUES")
        print("-" * 55)
        
        # Paramètres pour l'analyse détaillée
        print("📋 Paramètres de l'analyse détaillée:")
        print("   • Années: 2021-2025 (jusqu'à juillet)")
        print("   • Niveaux de puissance: 0.5, 1, 2, 3, 4, 5 MW")
        print("   • Analyse horaire avec créneaux optimaux")
        
        confirmer = input("\nLancer l'analyse détaillée ? (O/n): ").strip().lower()
        if confirmer != 'n':
            resultat = telecharger_donnees_spot_historiques_detaillees(
                api_key=ENTSOE_API_KEY,
                annee_debut=2021,
                annee_fin=2025,
                mois_fin=7,  # Jusqu'à juillet 2025
                pays_code='FR'
            )
            
            if resultat:
                print(f"\n🎯 ANALYSE TERMINÉE!")
                print(f"📁 Fichier généré: {resultat}")
                print("📊 Ce fichier contient:")
                print("   • Prix spot horaires détaillés")
                print("   • Disponibilités par niveau de puissance")
                print("   • Classifications temporelles")
                print("   • Opportunités d'achat optimales")
                print("   • Statistiques complètes")
                
                # Générer l'analyse des créneaux optimaux
                print("\n🔍 Génération de l'analyse des créneaux optimaux...")
                seuils_analyses = [25, 30, 40]  # Différents seuils de prix
                
                for seuil in seuils_analyses:
                    print(f"\n   → Analyse pour seuil ≤ {seuil} €/MWh")
                    fichier_synthese = generer_analyse_creneaux_optimaux(
                        fichier_donnees_spot=resultat,
                        seuil_prix_max=seuil
                    )
                    if fichier_synthese:
                        print(f"   ✅ Synthèse générée: {fichier_synthese}")
    
    print("\n🎉 Script terminé avec succès!") 