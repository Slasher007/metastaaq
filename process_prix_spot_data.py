import pandas as pd
import numpy as np
from datetime import datetime

def charger_donnees_prix():
    """Charge et prépare les données de prix spot"""
    print("📊 Chargement des données de prix spot...")
    
    # Charger les données sans utiliser la première colonne comme index
    df = pd.read_csv('donnees_prix_spot_fr_2024_2025.csv')
    
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
    
    print(f"✅ Données chargées: {len(df)} points de données")
    print(f"📅 Période: {df['Timestamp'].min()} à {df['Timestamp'].max()}")
    
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
    
    print(f"✅ Données traitées: {len(df_processed)} lignes")
    print(f"📝 Colonnes: {list(df_processed.columns)}")
    print(f"📊 Aperçu des premières lignes:")
    print(df_processed.head())
    
    return df_processed

def main():
    """Fonction principale pour traiter et sauvegarder les données"""
    print("🚀 TRAITEMENT DES DONNÉES PRIX SPOT")
    print("="*50)
    
    try:
        # Charger les données originales
        df_original = charger_donnees_prix()
        
        # Traiter les données selon le format demandé
        df_processed = processder_donnees_pour_export(df_original)
        
        # Nom du fichier de sortie
        output_filename = 'donnees_prix_spot_processed.csv'
        
        # Sauvegarder les données traitées
        print(f"\n💾 Sauvegarde vers {output_filename}...")
        df_processed.to_csv(output_filename)
        
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
        
        print(f"\n🔍 Aperçu final des données:")
        print(df_processed.head(10))
        
        return df_processed
        
    except Exception as e:
        print(f"❌ Erreur lors du traitement: {e}")
        return None

if __name__ == "__main__":
    df_result = main() 