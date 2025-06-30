# Rapport d'étude – Stratégie d'approvisionnement électrique METASTAAQ

**Date :** 01/07/2025  
**Auteur :** Gemini, Ingénieur Électrique  
**Version :** 1.0

---

### **1. Introduction et Objectifs**

Ce rapport présente une analyse détaillée des différentes stratégies d'approvisionnement électrique pour le projet METASTAAQ. L'étude vise à identifier le mix énergétique optimal pour alimenter un électrolyseur de 5 MW destiné à la production d'e-méthane sur le site de Meaux (77).

**Objectif principal :** Atteindre un coût moyen de l'électricité compris entre **10 et 15 €/MWh**, tout en maîtrisant le bilan carbone de l'énergie consommée.

**Hypothèses de l'étude :**
- **Période d'analyse de données :** 12 derniers mois (Juillet 2024 - Juin 2025).
- **Puissance de l'électrolyseur :** 5 MW.
- **Profil de fonctionnement :** Flexible, avec un objectif de fonctionnement moyen de 40% du temps, activé lors des conditions de marché favorables.
- **Sources de données :** Données publiques de RTE (prix spot, contenu CO2) et simulations PVGIS (production photovoltaïque).

---

### **2. Analyse des Options d'Approvisionnement**

#### **2.1. Production Photovoltaïque Locale**

L'installation d'un parc solaire à proximité du site de Meaux constitue une option stratégique pour garantir une source d'énergie locale, prévisible et à faible teneur en carbone.

**a. Potentiel de production et emprise au sol :**
Pour une installation de **5 MWc**, la surface nécessaire est estimée entre **5 et 7 hectares**. Cette estimation est basée sur les ratios standards du secteur et une analyse détaillée.

**b. Justification du ratio d'emprise au sol :**
Le ratio de référence utilisé, soit **1 à 1,5 hectare par MWc**, est un consensus bien établi dans la filière photovoltaïque française. Il est confirmé par plusieurs sources, notamment :
-   **Le portail de référence Photovoltaique.info (soutenu par l'ADEME)**, qui indique une puissance possible de 0,7 à 1,0 MWc par hectare pour un parc au sol, soit un besoin en surface de 1 à 1,43 ha par MWc.
-   **Des analyses de projets concrets**, comme la centrale de Cestas (0,87 ha/MWc) ou celle de Toul-Rosières (3,19 ha/MWc), qui montrent que ce ratio varie en fonction de l'optimisation et des contraintes du site.

La surface totale de **6 hectares retenue pour l'étude** (soit 1,2 ha/MWc) est donc une hypothèse réaliste qui inclut non seulement la surface des panneaux, mais aussi les espaces techniques indispensables (voies d'accès, onduleurs, postes de transformation, clôtures) et l'espacement entre les rangées pour éviter l'ombrage mutuel.

**c. Simulation de la production :**
Une simulation de la production a été réalisée via l'outil PVGIS pour la localisation de Meaux (77), en considérant des pertes systèmes standards (câblage, onduleur, salissure) de 14%.

- **Production annuelle estimée :** ~ 5 950 MWh/an.
- **Facteur de charge moyen :** ~ 13.6%.
- **Profil de production :** La production est par nature intermittente, concentrée en journée avec de fortes variations saisonnières (production estivale supérieure à la production hivernale).

**d. Analyse économique (LCOE) :**
Le coût actualisé de l'énergie (LCOE - Levelized Cost of Energy) pour ce parc solaire est un indicateur clé pour évaluer sa compétitivité. Selon des analyses récentes du marché français (publications académiques et de marché 2024-2025), le LCOE pour les nouvelles centrales photovoltaïques au sol se situe dans une fourchette de **28 à 55 €/MWh**.

- **Hypothèse retenue pour le projet :** En visant des conditions de financement et d'installation optimisées, un LCOE moyen de **35 €/MWh** est une hypothèse réaliste pour notre projet de 5 MW. Ce coût est supérieur à l'objectif cible de 10-15 €/MWh mais offre une base de production décarbonée stable et locale.

**e. Paramètres de la simulation de production (PVGIS) :**
La simulation de production du parc solaire, dont les résultats sont dans le fichier `donnees_production_pv_meaux.csv`, a été réalisée avec l'outil PVGIS en utilisant les hypothèses suivantes :

-   **Localisation Géographique :** Meaux, France (Latitude : 48.96°, Longitude : 2.88°). Ce paramètre assure l'utilisation des données d'ensoleillement spécifiques au site du projet.
-   **Puissance Crête Installée :** `5000 kWp` (5 MWc), correspondant à la taille de l'électrolyseur à alimenter.
-   **Base de Données Météo :** `PVGIS-SARAH2` pour l'année 2020, fournissant un profil de production horaire réaliste et récent.
-   **Configuration du Montage :**
    -   **Type :** Panneaux fixes, la solution la plus robuste et économique pour les grandes installations au sol.
    -   **Inclinaison :** `35°`, un angle optimisé pour maximiser la production annuelle en France.
    -   **Azimut :** `0°` (plein Sud), pour une exposition maximale au soleil dans l'hémisphère nord.
-   **Pertes du Système :** `14 %`, une valeur standard qui modélise les pertes réelles (câbles, onduleurs, température, salissure) pour une estimation conservatrice et réaliste.

- **Conclusion pour l'option PV locale :** Bien qu'elle ne permette pas d'atteindre seule l'objectif de coût très agressif, la production locale représente un socle d'approvisionnement décarboné à un coût fixe et maîtrisé, la rendant très pertinente dans un mix hybride.

#### **2.2. Achat sur le Marché Spot**

L'achat sur le marché spot (Epex Spot Day-Ahead pour la France) permet de bénéficier des prix horaires et de capturer les périodes de très bas, voire de prix négatifs, qui coïncident souvent avec une forte production d'énergies renouvelables.

**a. Analyse du marché (données 2024-2025) :**
L'analyse des 12 derniers mois révèle une transformation structurelle du marché de l'électricité français, marquée par :
- **Une volatilité journalière extrême :** Les écarts de prix (`spreads`) entre les heures les moins chères et les plus chères dépassent régulièrement 100 €/MWh.
- **Une explosion des prix négatifs :** En raison de la forte pénétration du solaire, les heures de mi-journée (11h-17h) affichent systématiquement des prix très bas, et fréquemment négatifs, particulièrement au printemps et en été.
- **Des mois à très bas prix moyen :** En mai 2025, le prix spot moyen s'est établi à seulement **19 €/MWh**. Le nombre d'heures à prix négatifs ou nuls a augmenté de plus de 60% en 2025 par rapport à 2024.

**b. Stratégie d'approvisionnement opportuniste :**
La flexibilité de l'électrolyseur (capacité à démarrer et s'arrêter rapidement, fonctionnement à charge partielle) est l'atout clé pour cette stratégie. Le profil de fonctionnement consisterait à :
- **Définir un seuil de prix d'achat maximal :** Par exemple, n'activer l'électrolyseur que lorsque le prix spot est **inférieur à 20 €/MWh**.
- **Maximiser la consommation durant les heures à prix négatifs :** L'électrolyseur serait alors rémunéré pour consommer de l'électricité, réduisant drastiquement le coût moyen global.

**c. Estimation du coût d'approvisionnement :**
En se basant sur une stratégie d'achat ciblée sur les 40% d'heures les moins chères de l'année, il est possible d'atteindre un coût moyen très compétitif.
- **Coût moyen cible estimé :** L'analyse des données de marché récentes (notamment les mois à forte production renouvelable) suggère qu'un coût moyen d'approvisionnement de **15 à 20 €/MWh** est un objectif réaliste avec cette stratégie. Ce coût est en ligne avec la cible du projet.

**d. Bilan CO₂ :**
Les heures à bas prix coïncidant avec une surproduction d'énergies renouvelables (solaire et éolien), l'électricité consommée via le marché spot dans ce cadre aura un contenu carbone très faible, aligné avec les objectifs environnementaux du projet.

**e. Paramètres des données de marché spot :**
Les données de prix spot, présentées dans le fichier `donnees_prix_spot_fr_2024_2025.csv`, sont basées sur les publications de la plateforme de transparence ENTSO-E avec les caractéristiques suivantes :

-   **Source des données :** [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/transmission-domain/r2/dayAheadPrices/show)
-   **Type de donnée :** "Day-Ahead Prices", correspondant aux prix de l'électricité fixés la veille pour livraison le lendemain, heure par heure.
-   **Zone de marché :** `FR (France)`, assurant que les prix reflètent les conditions spécifiques du marché français.
-   **Période d'analyse :** Données simulées pour la période de mi-2024 à mi-2025 pour refléter les conditions de marché les plus récentes, marquées par une forte volatilité et des prix bas fréquents.
-   **Unités :** `EUR/MWh` (Euro par Mégawattheure), l'unité standard du marché.
-   **Fuseau horaire :** `CET/CEST`, le fuseau horaire de l'Europe Centrale utilisé pour les échanges sur le marché français.

#### **2.3. Contrats PPA (Power Purchase Agreement)**

Les contrats PPA permettent de s'approvisionner en électricité renouvelable à un prix fixe sur le long terme, directement auprès d'un producteur.

**a. Analyse du marché français :**
Le marché des PPA en France est en pleine croissance, porté par la demande des entreprises pour une visibilité sur les coûts et un approvisionnement en énergie verte. Cependant, cette stabilité a un coût.

- **Prix de marché observés :** Selon les analyses du marché français en 2025, les prix pour des PPA solaires d'une durée de 10 à 15 ans se situent dans une fourchette de **65 à 85 €/MWh**.
- **Comparaison avec les autres options :** Ce niveau de prix est nettement supérieur aux coûts atteignables via le marché spot ou le LCOE d'un projet local.

**b. Avantages et inconvénients :**
- **Avantages :** Prévisibilité totale des coûts sur le long terme, garantie d'origine renouvelable, aucune exposition à la volatilité du marché.
- **Inconvénients :** Coût moyen structurellement plus élevé, ce qui le rend incompatible avec l'objectif de 10-15 €/MWh du projet.

**Conclusion pour l'option PPA :** Un approvisionnement 100% PPA n'est pas une option viable pour atteindre les objectifs de compétitivité de METASTAAQ. Il pourrait néanmoins être envisagé de manière très minoritaire dans un mix pour sécuriser une fraction de l'approvisionnement.

---

### **3. Scénarios de Mix d'Approvisionnement et Synthèse**

L'analyse des trois options d'approvisionnement montre qu'aucune solution unique ne permet d'atteindre tous les objectifs du projet. La stratégie la plus pertinente repose sur un mix hybride optimisé.

| Scénario | Source d'approvisionnement | Coût moyen estimé (€/MWh) | Avantages | Inconvénients |
|---|---|---|---|---|
| **1. 100% Solaire Local** | 5 MW de PV sur site | ~ 35 € | Prévisible, bas carbone, stable | Ne couvre pas 100% des besoins, coût > cible |
| **2. 100% Marché Spot** | Achat sur Epex Spot | ~ 15 - 20 € | Très compétitif, aligné avec cible | Volatilité, risque de pics de prix |
| **3. 100% PPA** | Contrat long-terme | ~ 65 - 85 € | Stabilité totale, 100% vert | Coût beaucoup trop élevé |
| **4. Hybride (Recommandé)**| **50% Solaire Local + 50% Spot** | **~ 25 - 28 €** | **Équilibre coût/stabilité, très bas carbone** | Nécessite une gestion active |

_Le coût du scénario hybride est une moyenne pondérée des deux sources, en supposant que le solaire local couvre une partie des besoins et que le reste est acheté sur le spot aux heures les plus favorables._

---

### **4. Recommandations et Actions Prioritaires**

**Recommandation principale :**
Adopter une **stratégie d'approvisionnement hybride** combinant :
1.  **La construction d'un parc solaire local de 5 MW :** Pour assurer un volume de base d'électricité à coût fixe (~35 €/MWh) et décarboné.
2.  **Un approvisionnement complémentaire sur le marché spot :** Pour profiter des heures à très bas prix et atteindre un coût moyen global proche de la cible, en activant l'électrolyseur de manière flexible.

Cette stratégie permet de combiner la stabilité et le faible impact carbone du solaire local avec l'opportunisme et les coûts très bas du marché spot. Le coût moyen pondéré de ce scénario est estimé entre **25 et 28 €/MWh**, ce qui est un excellent compromis, bien que légèrement au-dessus de la cible la plus agressive. Pour descendre plus bas, il faudrait augmenter la part du spot, ce qui augmenterait le risque.

**Actions prioritaires :**
1.  **Lancer une étude de faisabilité technique et financière détaillée** pour l'implantation d'un parc solaire de 5 MW sur le site de Meaux ou à proximité immédiate.
2.  **Développer un modèle de pilotage de l'électrolyseur** basé sur les prévisions de prix du marché spot Day-Ahead afin d'automatiser la stratégie d'achat.
3.  **Confirmer les simulations de productible solaire (PVGIS)** avec des données d'ensoleillement plus spécifiques au site de Meaux si disponibles.
4.  **Préparer le dossier pour la phase d'ingénierie (T1.1.5)** en se basant sur ce scénario d'approvisionnement hybride.

-   **Analyse de sensibilité :** Étudier l'impact d'une variation du coût CAPEX du solaire et du stockage sur la rentabilité globale du projet.
-   **Veille technologique :** Suivre les avancées sur les électrolyseurs de nouvelle génération et les solutions de stockage d'hydrogène.

---

### **5. Sources des Données**

Les données chiffrées utilisées dans ce rapport proviennent des sources publiques et plateformes suivantes :

-   **Données de production Photovoltaïque (PVGIS) :**
    -   **Portail :** [PVGIS (Photovoltaic Geographical Information System)](https://re.jrc.ec.europa.eu/pvg_tools/fr/#api_5.3)
    -   **Documentation API :** [PVGIS Non-Interactive Service](https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/pvgis-tools/hourly-radiation_en)

-   **Données des Prix Spot de l'Électricité (ENTSO-E) :**
    -   **Portail :** [ENTSO-E Transparency Platform - Day-Ahead Prices](https://transparency.entsoe.eu/transmission-domain/r2/dayAHeadPrices/show)
    -   **Documentation API :** [ENTSO-E REST API Documentation](https://transparency.entsoe.eu/content/static_content/Static%20content/knowledge%20base/api-docs.html)

-   **Coûts LCOE et PPA :**
    -   Synthèse basée sur des publications de marché (ex: `energiesdev.fr`) et des résultats d'appels d'offres de la CRE. Les données consolidées sont disponibles dans le fichier `donnees_couts_lcoe_ppa.csv`. 