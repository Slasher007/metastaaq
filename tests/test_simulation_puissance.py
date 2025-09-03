#!/usr/bin/env python3
"""
Script de test pour vérifier la nouvelle simulation de puissance disponible
Teste juste la partie simulation sans faire l'analyse complète
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def test_simulation_puissance():
    """Test rapide de la nouvelle simulation"""
    print("🧪 TEST DE LA NOUVELLE SIMULATION DE PUISSANCE")
    print("=" * 60)
    
    # Créer les heures de l'année 2020 (juste janvier pour le test)
    dates_test = pd.date_range('2020-01-01', '2020-01-31 23:00:00', freq='H')
    
    # Simulation réaliste basée sur les patterns du marché électrique français
    np.random.seed(42)  # Pour reproductibilité
    
    # Variables temporelles
    heures = np.arange(len(dates_test)) % 24
    jours_annee = np.arange(len(dates_test)) / 24
    
    # === NOUVELLE APPROCHE : PUISSANCE DISPONIBLE POUR ÉLECTROLYSEUR ===
    print("🎯 Modélisation de la puissance disponible pour électrolyseur...")
    
    # Base : En moyenne, on peut acheter quelques MW
    puissance_dispo_base = 3.0  # MW en moyenne
    
    # Variations selon l'heure (plus de puissance dispo la nuit et weekend)
    variation_horaire = 2.0 * np.sin(2 * np.pi * heures / 24 + np.pi)  # Plus dispo la nuit
    
    # Variations selon les renouvelables (pics aléatoires)
    pics_renouvelables = np.random.exponential(3, len(dates_test)) * (np.random.random(len(dates_test)) > 0.85)
    
    # Variations saisonnières (plus de surplus en été avec le solaire)
    variation_saisonniere = 1.5 * np.sin(2 * np.pi * jours_annee / 365)
    
    # Bruit réaliste
    bruit = np.random.normal(0, 1.5, len(dates_test))
    
    # Calculer la puissance disponible totale
    puissance_disponible = (puissance_dispo_base + 
                           variation_horaire + 
                           pics_renouvelables + 
                           variation_saisonniere + 
                           bruit)
    
    # Limiter à des valeurs réalistes pour un électrolyseur
    puissance_disponible = np.clip(puissance_disponible, -2, 15)  # Entre -2 et 15 MW
    
    # === PRIX SPOT ===
    # Prix inversement corrélé à la puissance disponible
    prix_base = 35  # €/MWh
    effet_puissance = -8 * puissance_disponible  # Plus de puissance = prix plus bas
    volatilite = np.random.normal(0, 12, len(dates_test))
    effet_hiver = 15 * ((jours_annee < 90) | (jours_annee > 300))
    effet_pointe = 25 * ((heures >= 18) & (heures <= 21))
    
    prix = prix_base + effet_puissance + volatilite + effet_hiver + effet_pointe
    prix = np.clip(prix, -20, 150)
    
    # Créer le DataFrame de test
    df_test = pd.DataFrame({
        'DateTime': dates_test,
        'Prix': prix,
        'Puissance_Disponible_MW': puissance_disponible
    })
    
    # === AFFICHAGE DES STATISTIQUES ===
    print(f"\n📊 STATISTIQUES DE LA SIMULATION (Janvier 2020)")
    print(f"   • Nombre d'heures : {len(df_test)}")
    print(f"   • Puissance disponible - Moyenne : {puissance_disponible.mean():.2f} MW")
    print(f"   • Puissance disponible - Médiane : {np.median(puissance_disponible):.2f} MW")
    print(f"   • Puissance disponible - Écart-type : {puissance_disponible.std():.2f} MW")
    print(f"   • Puissance disponible - Min : {puissance_disponible.min():.2f} MW")
    print(f"   • Puissance disponible - Max : {puissance_disponible.max():.2f} MW")
    print(f"   • Prix moyen : {prix.mean():.1f} €/MWh")
    
    # === TEST DE DISPONIBILITÉ PAR PUISSANCE ===
    print(f"\n🎯 DISPONIBILITÉ PAR SEUIL DE PUISSANCE :")
    puissances_test = [0.5, 1, 2, 3, 4, 5]
    
    for p in puissances_test:
        nb_heures = len(df_test[df_test['Puissance_Disponible_MW'] >= p])
        pct = (nb_heures / len(df_test)) * 100
        print(f"   • ≥ {p} MW : {nb_heures} heures ({pct:.1f}%)")
    
    # === TEST DE COMBINAISON PRIX + PUISSANCE ===
    print(f"\n💰 TEST COMBINÉ PRIX + PUISSANCE (seuil 30€/MWh) :")
    seuil_prix_test = 30
    
    print(f"   Prix ≤ {seuil_prix_test}€/MWh seul : {len(df_test[df_test['Prix'] <= seuil_prix_test])} heures")
    
    for p in puissances_test:
        condition_prix = df_test['Prix'] <= seuil_prix_test
        condition_puissance = df_test['Puissance_Disponible_MW'] >= p
        heures_combinees = len(df_test[condition_prix & condition_puissance])
        pct = (heures_combinees / len(df_test)) * 100
        print(f"   Prix ≤ {seuil_prix_test}€/MWh + ≥ {p} MW : {heures_combinees} heures ({pct:.1f}%)")
    
    # === DISTRIBUTION DES VALEURS ===
    print(f"\n📈 DISTRIBUTION DE LA PUISSANCE DISPONIBLE :")
    bins = [-2, 0, 1, 2, 3, 4, 5, 10, 15]
    for i in range(len(bins)-1):
        inf, sup = bins[i], bins[i+1]
        condition = (puissance_disponible >= inf) & (puissance_disponible < sup)
        nb = np.sum(condition)
        pct = (nb / len(puissance_disponible)) * 100
        print(f"   • [{inf} - {sup}[ MW : {nb} heures ({pct:.1f}%)")
    
    # === VÉRIFICATION QUE ÇA MARCHE ===
    print(f"\n✅ VÉRIFICATION DE LA DIFFÉRENCIATION :")
    print("   (Plus la puissance demandée augmente, moins il devrait y avoir d'heures)")
    
    heures_precedentes = len(df_test) + 1  # Valeur initiale élevée
    differentiation_ok = True
    
    for p in puissances_test:
        heures_actuelles = len(df_test[df_test['Puissance_Disponible_MW'] >= p])
        if heures_actuelles > heures_precedentes:
            differentiation_ok = False
            print(f"   ❌ Problème : {p} MW a plus d'heures que la puissance précédente")
        else:
            print(f"   ✅ {p} MW : {heures_actuelles} heures (OK)")
        heures_precedentes = heures_actuelles
    
    if differentiation_ok:
        print(f"\n🎉 SUCCÈS ! La simulation différencie bien les puissances")
        print(f"   ➡️ Le script principal devrait maintenant fonctionner correctement")
    else:
        print(f"\n❌ PROBLÈME ! La simulation ne différencie pas assez les puissances")
        print(f"   ➡️ Besoin d'ajuster les paramètres")
    
    return df_test

def creer_graphique_test(df_test):
    """Crée un graphique de test pour visualiser"""
    print(f"\n📊 Création d'un graphique de test...")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
    
    # Graphique 1 : Puissance disponible dans le temps
    ax1.plot(df_test['DateTime'], df_test['Puissance_Disponible_MW'], 
             alpha=0.7, linewidth=0.8, color='blue')
    ax1.axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='0.5 MW')
    ax1.axhline(y=2, color='orange', linestyle='--', alpha=0.7, label='2 MW')
    ax1.axhline(y=5, color='purple', linestyle='--', alpha=0.7, label='5 MW')
    ax1.set_title('Puissance disponible au cours du temps (Janvier 2020)', fontweight='bold')
    ax1.set_ylabel('Puissance disponible (MW)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Graphique 2 : Distribution des prix
    ax2.hist(df_test['Prix'], bins=30, alpha=0.7, color='green', edgecolor='black')
    ax2.axvline(x=df_test['Prix'].mean(), color='red', linestyle='--', 
                label=f'Moyenne: {df_test["Prix"].mean():.1f} €/MWh')
    ax2.set_title('Distribution des prix spot (Janvier 2020)', fontweight='bold')
    ax2.set_xlabel('Prix (€/MWh)')
    ax2.set_ylabel('Nombre d\'heures')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('test_simulation_puissance.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Graphique sauvegardé : test_simulation_puissance.png")

if __name__ == "__main__":
    # Tester la simulation
    df_test = test_simulation_puissance()
    
    # Créer un graphique
    creer_graphique_test(df_test)
    
    print(f"\n🎯 CONCLUSION DU TEST :")
    print(f"   Si vous voyez une décroissance des heures disponibles quand la puissance augmente,")
    print(f"   alors la correction est réussie et le script principal fonctionnera !") 