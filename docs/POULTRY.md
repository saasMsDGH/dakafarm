# Scénario fictif de poules pondeuses

Objectif : suivre quatre campagnes de ponte dans la même activité, avec achats,
nourriture, vaccins, mortalité, œufs, vente de fin de cycle, paies et apports.
Le socle existant FastAPI/PostgreSQL/React/Recharts est conservé. Les modifications
portent sur les liens avicoles, la ventilation salariale, les projections des
sources, une migration additive et l'écran de campagne. La recette utilise une
base Docker jetable avant mise à jour de la qualification via ArgoCD.

## Hypothèses de démonstration

- Quatre bandes de 1 000, 1 200, 1 400 et 1 600 poulettes achetées à 3 000 FCFA.
- Œuf vendu à 120 FCFA ; poule de fin de cycle vendue à 1 500 FCFA.
- Aliment à 350 FCFA/kg. Consommation fictive de 0,110 kg par poule-jour.
- Vaccins fictifs à 35 FCFA/dose fictive. Les entrées de soins sont des exemples
  de coûts, **pas un protocole sanitaire ni une recommandation de vaccination**.
- Dix employés au total, chacun payé 100 000 FCFA/mois : 1 000 000 FCFA/mois
  pour l'ensemble des bandes, hors cotisations patronales non paramétrées.
- Dix clients fictifs se partagent les ventes.
- Arrêt des opérations au 30 octobre 2026 ; deux cycles terminés et deux en cours.

Ces montants et rendements ne sont pas des prix de marché ni des références
techniques agricoles. Les taux de ponte et de perte sont des paramètres fictifs.

## Preuves et calculs

L'ancien négoce de volailles V1 est conservé en historique. Ses affectations
originales sont libérées par contre-événements et enregistrées dans
`retired_demo_sources`. Ses produits/comptes sont désactivés. Les mêmes quatre
campagnes reçoivent les cycles de ponte ; les sept autres activités sont conservées.
L'extension refuse de remplacer une source ou affectation initiale modifiée par
l'utilisateur. Aucun enregistrement financier historique n'est effacé.

Chaque bande possède des produits distincts : poulettes, œufs, aliment et vaccins.
Les achats ont leurs lignes, paiements et entrées de stock. Les consommations
alimentaires, vaccins et mortalités possèdent leurs relevés et sorties valorisées.
Les œufs entrent en stock lors de la production, puis sortent à la vente.
Les coûts de ponte sont reconnus via aliments/soins/paies : ils ne sont pas déduits
une seconde fois dans la sortie des œufs. Les oiseaux perdus ou vendus sortent à
leur coût d'achat ; les oiseaux vivants demeurent en stock.

Les productions sont regroupées par demi-mois. `record_date` est la fin de la
période, `period_start_date` son début et `bird_days` le dénominateur réel simulé
du taux de ponte. Une lecture antérieure n'inclut jamais un relevé qui se termine
plus tard. Les enregistrements journaliers existants restent compatibles.

Il existe une seule paie RH par employé et mois. `payroll_allocations` la répartit
entre les bandes actives, au prorata de leur effectif initial. Les plus forts
restes attribuent les FCFA indivisibles sans perte ni duplication. Chaque part
a son règlement et son flux de caisse. La somme des parts doit égaler la paie ;
les flux PAYROLL ne sont jamais ajoutés une deuxième fois aux charges.
La paie et son identité sont rapprochées à chaque rapport. Une anomalie suspend
le résultat et le ROI. Les allocations et liens avicoles sont protégés contre
modification/suppression en base ; les relevés rattachés demandent une libération
motivée avant correction.

Le ROI affiché est **réalisé en trésorerie**, pas annualisé :
`100 × (encaissements − décaissements hors apports/retraits) / apports`.
Les achats de stocks pour les mois futurs restent donc visibles comme sorties
de trésorerie. Le résultat de gestion distingue ces achats des coûts consommés.
La date de récupération est le premier retour du flux cumulé hors apports à zéro
après son creux initial ; aucun versement à l'investisseur n'est présumé.
Les cycles en cours ne contiennent aucune vente future de poules de réforme.

## Exécution et contrôles

La commande privée de qualification `python -m app.demo_seed --confirm-qualification
--if-absent`, avec `DAKAFARM_DEMO_ALLOWED=qualification-only`, importe le socle puis
l'extension `dakrex-poultry-v2`. Chaque étape est transactionnelle. Un marqueur
complet empêche la duplication et conserve les essais aux déploiements suivants.
L'import n'est pas exécuté au démarrage du serveur API.

La recette teste les paies à 100 000 FCFA, le total salarial non multiplié, les
ventes d'œufs/poules, stocks, mortalités, regroupements de production, rejeu et
absence de données futures. Des tests navigateur vérifient aussi les listes
natives clients/employés/paies/ferme et les graphiques sur ordinateur et mobile.
Les anciens libellés TZS/TSh sont remplacés par FCFA ; aucun taux de change ni
conversion des montants n'est appliqué.

L'écran avicole présente une fiche par bande (coûts, ventes, salaires et ROI), puis
les graphiques de ventes, fonctionnement, ponte/pertes et récupération de trésorerie.
Le lien direct est `/#/campaigns?view=poultry`.
