# Simulation de coexistence DAKREX

Jeu : `dakrex-coexistence-v1`. Devise : XOF. Date d'arrêt des pièces : 30 octobre 2026.
Aucune opération bancaire ou Mobile Money réelle n'est exécutée.

| Activité | Scénario financier |
| --- | --- |
| Élevage | Vente de lots de volailles, marge positive et frais propres |
| Boutique | Vente régulière de denrées avec marge et apport initial |
| Bar | Marge insuffisante pour couvrir les frais : déficit visible |
| GSM | Coupons/recharges avec faible marge ; aucun float Mobile Money simulé |
| Téléphonie | Rentabilité positive mais financement initial insuffisant et encaissements différés |
| Cultures | Lots commercialisés et encaissements différés de trois mois |
| Huile de palme | Lots commercialisés, marge positive et encaissements différés |
| Palmiste | Marge faible, frais trop élevés et financement partiel |

Chaque activité dispose de sa caisse fictive initialement à zéro et de quatre
campagnes démarrées respectivement en janvier 2024, juillet 2024, juillet 2025 et
janvier 2026. Les ventes sont prévues sur 24 mois ; la période de campagne inclut
le délai d'encaissement. Les campagnes se chevauchent volontairement. Aucune pièce
future au-delà du 30 octobre 2026 n'est insérée. Les dates de fin prévues restent
visibles dans la chronologie. Le statut technique OPEN ne constitue pas une clôture.

Les volumes, prix et frais varient entre campagnes/mois de façon déterministe.
Un lot est acheté et payé en début de campagne, puis consommé par les ventes.
Les coûts des sorties sont figés. Les paiements clients tardifs ne sont insérés
que lorsqu'ils sont survenus à la date d'arrêt ; les autres ventes restent impayées.
Les apports initiaux sont des financements et ne deviennent jamais des recettes.
Chaque document, paiement et mouvement est rattaché à la même campagne. Les stocks
restants sont égaux aux entrées moins les sorties ; ils ne sont pas artificiellement
vendus en fin de période.

Ces scénarios évaluent la coexistence **financière**. Ils utilisent des lots
achetés/revendus, y compris pour cultures, palme et palmiste. Ils ne prétendent pas
modéliser la naissance/croissance des animaux, les rendements agricoles, les
transformations matière, les amortissements, les charges communes, la fiscalité
ni des écritures de clôture. Aucun transfert automatique ne permet à une activité
d'excédent de masquer le déficit d'une autre.

## Import explicite

L'image API doit déjà être migrée et un administrateur actif doit exister.
Exécuter dans le contexte privé de qualification :

```sh
DAKAFARM_DEMO_ALLOWED=qualification-only python -m app.demo_seed --confirm-qualification
```

Ce drapeau est fourni au seul processus d'import ; il n'est pas nécessaire au
serveur API. Le script utilise la connexion PostgreSQL déjà configurée, signe les
affectations avec l'administrateur actif et n'affiche aucun identifiant.
Tout échec intermédiaire annule la transaction. Une relance vérifie le manifeste
et les agrégats puis renvoie `replayed: true`, sans créer de nouvelles pièces.
Si le jeu a été corrigé ou dégradé entre-temps, l'import ne le répare pas silencieusement.

La provenance est conservée dans `demo_datasets`, `activities.demo_dataset` et
`demo_sources`. Les sources fictives ne peuvent pas être déplacées vers une
activité réelle. Il est possible de travailler sur les activités réelles dans
le sélecteur de périmètre, sans inclure la démonstration dans leurs rapports.

Le menu **Campagnes et données → Activités côte à côte** sélectionne les 32
campagnes du jeu à l'ouverture. Choisir une activité isole ses quatre campagnes ;
les cases permettent une sélection plus fine. Les tableaux et graphiques utilisent
les agrégats du serveur, pas des valeurs de démonstration écrites dans le frontend.

Le hook ArgoCD de qualification utilise aussi `--if-absent` : les déploiements
suivants n’écrasent et ne réinitialisent jamais les essais faits sur le jeu déjà
importé. La commande sans ce drapeau reste disponible pour vérifier le manifeste.
