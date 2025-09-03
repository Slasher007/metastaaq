import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime

def trouver_fichier_prix_spot():
    """Trouve automatiquement le fichier de prix spot le plus récent"""
    # Chercher tous les fichiers de prix spot
    fichiers_prix = glob.glob('donnees_prix_spot_*.csv')
    
    if not fichiers_prix:
        # Si aucun fichier avec le nouveau format, chercher l'ancien format
        if os.path.exists('donnees_prix_spot_fr_2024_2025.csv'):
            return 'donnees_prix_spot_fr_2024_2025.csv'
        else:
            raise FileNotFoundError("Aucun fichier de prix spot trouvé")
    
    # Retourner le fichier le plus récent (par nom de fichier)
    fichier_recent = sorted(fichiers_prix)[-1]
    print(f"📁 Fichier de prix spot détecté: {fichier_recent}")
    return fichier_recent

def charger_donnees_prix(fichier_prix=None):
    """Charge et prépare les données de prix spot"""
    print("📊 Chargement des données de prix spot...")
    
    if fichier_prix is None:
        fichier_prix = trouver_fichier_prix_spot()
    
    # Charger les données sans utiliser la première colonne comme index
    df = pd.read_csv(fichier_prix)
    
    # Renommer les colonnes si nécessaire
    if len(df.columns) == 2:
        df.columns = ['Timestamp', 'Prix_EUR_MWh']
    
    # Convertir la colonne timestamp en datetime
    print("🔄 Conversion de la colonne timestamp...")
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], utc=True).dt.tz_convert('Europe/Paris').dt.tz_localize(None)
    
    # Vérifier et gérer les doublons dans les timestamps
    if df['Timestamp'].duplicated().any():
        print(f"⚠️  Doublons détectés: {df['Timestamp'].duplicated().sum()} lignes")
        print("🔧 Suppression des doublons...")
        df = df.drop_duplicates(subset=['Timestamp'], keep='first')
        print(f"✅ Données après suppression des doublons: {len(df)} lignes")
    
    # Ajouter des colonnes temporelles pour l'analyse
    df['Heure'] = df['Timestamp'].dt.hour
    df['JourSemaine'] = df['Timestamp'].dt.day_name()
    df['Mois'] = df['Timestamp'].dt.month_name()
    df['Date'] = df['Timestamp'].dt.date
    df['Trimestre'] = df['Timestamp'].dt.quarter
    df['Annee'] = df['Timestamp'].dt.year
    
    print(f"✅ Données chargées: {len(df)} points de données")
    print(f"📅 Période: {df['Timestamp'].min()} à {df['Timestamp'].max()}")
    print(f"🗓️ Années couvertes: {sorted(df['Annee'].unique())}")
    
    return df

def processder_donnees_pour_export(df):
    """Traite les données selon le format demandé"""
    print("\n🔄 Traitement des données pour export...")
    
    # Créer un nouveau DataFrame avec les colonnes dans l'ordre demandé
    df_processed = pd.DataFrame()
    
    # Ajouter les colonnes dans l'ordre requis: Date, Heure, Mois, Jours, Prix
    df_processed['Date'] = df['Date']            # Première colonne: date seulement
    df_processed['Heure'] = df['Heure']
    df_processed['Mois'] = df['Mois']
    df_processed['Jours'] = df['JourSemaine']    # Jour de la semaine
    df_processed['Prix'] = df['Prix_EUR_MWh']
    df_processed['Annee'] = df['Annee']          # Ajouter l'année pour faciliter les analyses
    
    print(f"✅ Données traitées: {len(df_processed)} lignes")
    print(f"📝 Colonnes: {list(df_processed.columns)}")
    print(f"📊 Aperçu des premières lignes:")
    print(df_processed.head())
    
    return df_processed

def main(fichier_prix=None):
    """Fonction principale pour traiter et sauvegarder les données"""
    print("🚀 TRAITEMENT DES DONNÉES PRIX SPOT")
    print("="*50)
    
    try:
        # Charger les données originales
        df_original = charger_donnees_prix(fichier_prix)
        
        # Traiter les données selon le format demandé
        df_processed = processder_donnees_pour_export(df_original)
        
        # Nom du fichier de sortie basé sur la période des données
        annee_min = df_original['Annee'].min()
        annee_max = df_original['Annee'].max()
        
        if annee_min == annee_max:
            output_filename = f'donnees_prix_spot_processed_{annee_min}.csv'
        else:
            output_filename = f'donnees_prix_spot_processed_{annee_min}_{annee_max}.csv'
        
        # Sauvegarder les données traitées
        print(f"\n💾 Sauvegarde vers {output_filename}...")
        df_processed.to_csv(output_filename, index=False)
        
        print(f"✅ Données sauvegardées avec succès!")
        print(f"📁 Fichier créé: {output_filename}")
        print(f"📊 Structure des données:")
        print(f"   • Colonnes: {list(df_processed.columns)}")
        print(f"   • Lignes: {len(df_processed):,}")
        print(f"   • Période: {df_original['Timestamp'].min()} à {df_original['Timestamp'].max()}")
        
        # Afficher des statistiques rapides
        print(f"\n📈 Statistiques rapides:")
        print(f"   • Prix moyen: {df_processed['Prix'].mean():.2f} €/MWh")
        print(f"   • Prix min: {df_processed['Prix'].min():.2f} €/MWh")
        print(f"   • Prix max: {df_processed['Prix'].max():.2f} €/MWh")
        
        # Statistiques par année
        print(f"\n📊 Statistiques par année:")
        for annee in sorted(df_processed['Annee'].unique()):
            df_annee = df_processed[df_processed['Annee'] == annee]
            print(f"   • {annee}: {len(df_annee):,} points, prix moyen: {df_annee['Prix'].mean():.2f} €/MWh")
        
        print(f"\n🔍 Aperçu final des données:")
        print(df_processed.head(10))
        
        return df_processed, output_filename
        
    except Exception as e:
        print(f"❌ Erreur lors du traitement: {e}")
        return None, None

if __name__ == "__main__":
    df_result, filename = main() 