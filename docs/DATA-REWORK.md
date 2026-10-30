# Reprise des données DAKAFARM

## Objectif et cadre

La donnée précède l'habillage. Base de travail : fork livré 7a623237f5e395c9e7b3ed8f1c1ef6fda41d8e79.
Travail isolé dans la branche codex/campaign-data-foundation. Aucun commit, push ou changement
sur la base de qualification n'est effectué par cette reprise locale.

Plan d'exécution :
1. Ajouter activités et campagnes à dates libres, sans convertir ni attribuer l'historique.
2. Rattacher les opérations existantes par références traçables et commandes idempotentes.
3. Conserver l'historique des rattachements/corrections, détecter les sources modifiées.
4. Séparer ventes/charges/consommations et flux de trésorerie ; ne pas déduire la marge des achats.
5. Corriger l'atomicité alimentation/stock et introduire une valorisation explicite contrôlée.
6. Ajouter une vue sobre de validation des données et graphiques issus des mêmes agrégats serveur.
7. Tester migrations, concurrence, rejouabilité, protection des historiques et rapprochements.

Fichiers impactés : nouveau domaine backend/app/api/v1/campaigns, migration Alembic additive,
import des modèles/routeur, services de stock/achats/alimentation, page React Campagnes et
navigation existante. Frameworks conservés : FastAPI, SQLAlchemy, PostgreSQL, React et Recharts.

Validation : builds Docker existants, unittest d'intégration sur PostgreSQL 15 isolé,
compileall Python, npm ci/build frontend, contrôles navigateur de la page reliée à l'API de test.
Aucune recette ne doit créer de donnée métier dans le cluster partagé.

## Contrat de données de cette première reprise

- Une **activité** porte une devise XOF. Une **campagne** appartient à une activité,
  avec un début et une fin facultative ; elle peut traverser plusieurs années.
- Les sources métier restent les tables existantes : ventes, achats, dépenses,
  transactions de caisse, mouvements de stock, production et alimentation.
  Aucune copie de ces opérations n'est comptabilisée comme une seconde écriture.
- Une source entière a au plus une affectation active. Son rattachement demande
  la confirmation explicite de sa devise, de son empreinte et d'un motif.
  Une source hors période, sans date ou contenant un montant FCFA fractionnaire
  ou négatif est refusée. Il n'y a **aucune conversion TZS → XOF**.
- Les événements ASSIGN/RELEASE conservent auteur, motif, date, instantané,
  empreinte et événement précédent. Les triggers PostgreSQL refusent leur
  modification/suppression et les branches incohérentes. Une commande UUID
  identique est rejouable ; un autre contenu avec le même UUID donne HTTP 409.
- Les modifications/suppressions d'alimentation, production ou dépenses passent
  par un contrôle d'affectation ; l'alimentation vérifie aussi ses mouvements
  de stock liés. Une modification directe des champs projetés ou une suppression
  par un autre chemin est détectée au prochain rapport. Ce mécanisme ne rend pas
  immuables toutes les tables historiques de l'application.

### Mesures et rapprochements

| Mesure | Source autorisée |
| --- | --- |
| Ventes documentées | Total des ventes rattachées, payé ou non |
| Dépenses documentées | Montant des dépenses rattachées, payé ou non |
| Consommation de stock | Coût figé d'une sortie identifiée et valorisée |
| Flux de caisse | Transactions rattachées IN / OUT, sans ouverture |
| Production | Bons œufs des relevés rattachés |
| Résultat provisoire | Ventes − dépenses − consommation valorisée |

Les achats augmentent le stock ; leur total n'est pas soustrait une seconde fois
comme charge. L'alimentation est une mesure physique : son champ total_cost ne
s'ajoute pas au coût de sa sortie de stock. Les paiements ne s'ajoutent pas aux
ventes/dépenses. Une vente et une alimentation demandent le rattachement de tous
leurs mouvements de stock à la même campagne ; inversement, leur sortie demande
son document d'origine. Les transactions SALE/PURCHASE/EXPENSE doivent se
rapprocher de leur paiement et du document rattaché à la même campagne.

Les flux PAYROLL, OTHER_INCOME, ASSET_PURCHASE, ADJUSTMENT et les types inconnus
restent visibles en caisse mais bloquent le résultat économique : leur traitement
métier n'est pas encore validé. OWNER_INVESTMENT n'est pas assimilé à un revenu.
Les ajustements de stock restent également à qualifier. Un coût inconnu, une
source changée/manquante ou un rapprochement incomplet suspend le résultat et sa
courbe. Une source CASH changée/manquante suspend aussi le flux net et son graphique.
Les totaux détaillés conservent les instantanés du rattachement pour investiguer.

Les rapports lisent un même instantané PostgreSQL REPEATABLE READ, dédupliquent les
campagnes sélectionnées et exposent les mêmes agrégats aux cartes, tableaux et
graphiques. Les montants FCFA sont des entiers transmis en chaînes décimales ; les
coûts unitaires restent décimaux. L'interface utilise BigInt pour les montants et
refuse les graphiques hors plage numérique exacte JavaScript.

La situation « au » filtre les **dates métier** des sources actuellement affectées.
Ce n'est pas une reconstitution des affectations telles qu'elles existaient à
une date passée ; leur chronologie se consulte dans l'historique.
La lecture annuelle et le cumul des flux évitent d'additionner des soldes de bilan.
Le rapport refuse plus de 10 000 sources sélectionnées au lieu de les tronquer.

### Valorisation et transactions de stock

La migration conserve les quantités/prix historiques et les marque UNVERIFIED.
Un administrateur peut déclarer un coût d'ouverture justifié pour une quantité
inchangée : audit append-only, contrôle de concurrence et commande rejouable.
Cette déclaration ne réécrit jamais les anciennes sorties non valorisées.

Les achats calculent un coût moyen pondéré sur un stock vérifié, avec remise
répartie au prorata des lignes. Si le stock antérieur n'est pas vérifié, le
nouveau coût reste UNVERIFIED ; un stock initial vide peut recevoir le coût du
premier achat. Prix calculé à six décimales, arrondi HALF_UP ; chaque coût total
sortant est arrondi en FCFA entier HALF_UP et figé au moment du mouvement.
Un changement manuel de prix/quantité ou une entrée hors achat valorisé invalide
la base de coût. Une simple référence client « Purchase » ne certifie pas une entrée.

Les produits sont verrouillés avant modification du stock (ordre stable pour
plusieurs produits). Créer/modifier/supprimer une alimentation et ses mouvements
se fait dans une transaction unique, avec rollback sur échec intermédiaire.
La date de sortie d'une nouvelle alimentation suit sa date métier.

## Parcours de validation

1. Ouvrir **Campagnes et données** avec un administrateur ou finance_manager.
2. Créer une activité puis sa campagne (administrateur).
3. Contrôler les sources, leurs dates et leur devise avant rattachement motivé.
4. Contrôler les coûts d'ouverture des stocks concernés (administrateur).
5. Résoudre les alertes, puis lire les flux mensuels, le résultat cumulé provisoire,
   les années et la comparaison entre campagnes.
6. Corriger par libération motivée, puis modification de la pièce et nouveau
   rattachement ; conserver l'export JSON des sources/contrôles pour la recette.

Les rôles ferme ne reçoivent pas automatiquement l'accès aux données financières.
Les anciennes pages restent disponibles avec un avertissement sur leurs règles
et devises non validées. Elles ne deviennent pas des états fiables par le seul
ajout de cette page.

## Limites à valider avant une utilisation comptable réelle

- Le périmètre est **partiel**, limité aux sources explicitement rattachées.
  Les sources non rattachées sont comptées globalement ; aucun indicateur ne
  certifie la complétude des pièces, l'existence de justificatifs ou leur unicité
  métier en dehors des références existantes.
- Pas encore de ventilation des charges communes entre campagnes, de lettrage
  complet, de valorisation des œufs produits, de reprise automatique des coûts
  anciens, d'amortissements ni de traitement complet des salaires et actifs.
- Pas encore de clôture/réouverture métier, de périodes verrouillées, de reprise
  comptable complète ni d'états SYSCOHADA/Bénin validés. Le statut CLOSED existe
  dans le modèle et bloque les affectations, sans interface de clôture à ce stade.
- Pas de nouveaux parcours hors ligne, de rapprochement bancaire/Mobile Money,
  de synchronisation Dolibarr ou de fusion de leurs bases. Les forks inspirent
  cette reprise ; aucune intégration comptable n'est présumée.
- Les contrôles portent sur les champs projetés des documents et leurs liens
  décrits ici. Un audit complet de toutes les tables et de tous les services
  historiques reste distinct de cette première reprise.

## Vérification reproductible

Depuis la racine du fork (Docker et Node disponibles) :

```sh
python3 -m compileall -q backend/app backend/migrations backend/tests
docker build -f Dockerfile.api -t dakafarm-api:data .
python3 deploy/check-data.py
cd frontend
npm ci --ignore-scripts --no-audit --no-fund
node --test src/pages/campaigns/numbers.test.mjs
npm run build -- --outDir /tmp/dakafarm-data-dist
```

Recette navigateur facultative, avec Playwright/Chrome déjà installés :

```sh
docker build -f Dockerfile.web -t dakafarm-web:data .
python3 deploy/check-data.py --browser
```

`PLAYWRIGHT_MODULE` et `CHROME_BIN` peuvent remplacer les chemins de la machine de
recette. Le script crée des identifiants aléatoires en fichiers privés, une base
jetable PostgreSQL 15 et des conteneurs séparés du cluster. Sans navigateur, le
réseau Docker est interne. Avec navigateur, seul le Web est publié sur un port
aléatoire de 127.0.0.1. Les ressources et identifiants temporaires sont supprimés
à la fin. Les captures sous docs/screenshots contiennent uniquement des données
synthétiques. Ne jamais utiliser ce script avec des identifiants de qualification.

Le rollback Alembic refuse de supprimer les nouveaux axes/événements dès qu'ils
contiennent des données. La migration n'est pas lancée sur la base déployée par
cette reprise locale ; un déploiement devra conserver une sauvegarde et exécuter
la migration avant de démarrer la nouvelle API.

Le workflow GitHub vérifie désormais le contrat de données et les formats FCFA
avant de publier les images. Les pull requests exécutent ces contrôles sans droit
packages:write et sans publication ; la publication reste réservée au dépôt du
fork hors événement pull_request. Cette configuration CI est préparée localement,
sans exécution distante déclenchée par cette reprise.

## Extension autorisée : coexistence des activités et simulation de qualification

La reprise est maintenant destinée à publication et à déploiement, à la demande
explicite de l'utilisateur. Le jeu `dakrex-coexistence-v1` ajoute huit activités
et quatre campagnes par activité. Le [scénario de simulation](SIMULATION.md)
décrit les hypothèses et la procédure d'import.

La provenance des activités et des sources est persistée séparément. L'API refuse
le rattachement d'une source réelle à une campagne fictive et inversement, ainsi
que leur consolidation dans un rapport commun. L'import est une transaction
unique, rejouable sans duplication, et ne supprime aucune donnée existante.
Il n'est jamais exécuté automatiquement au démarrage de l'application.

La vue **Activités côte à côte** présente les résultats, apports, flux après
apports, besoin maximal avant apports et chevauchements des campagnes. Le besoin
est le minimum du cumul **journalier** des flux rattachés, sans ouverture présumée,
hors apports/retraits. Les soldes d'activités ne sont pas compensés dans leurs
lignes individuelles ; aucun transfert d'argent entre activités n'est déclenché.
Les états « Déficitaire », « Trésorerie à soutenir » et « Excédentaire » sont des
lectures provisoires des seuls flux sélectionnés, sans projection future.
