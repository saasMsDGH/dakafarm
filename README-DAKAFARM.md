# DAKAFARM — qualification

Fork MIT de https://github.com/tajirdev/AMAS-FARM-Management-System,
base amont `b399cb2cd92987e8eb409dc0793d54248bbca6e1`.

Instance : https://dakafarm.qual.dgsynthex.online ; namespace et Application ArgoCD
`dakafarm-qual`. GitOps : `saasMsDGH/admin-platform-gitops`, chemin `apps/dakafarm-qual`.
L'instance ne partage ni base ni données avec DAKREX ou DOLIDAKREX.

## Livraison

`Dockerfile.api` : Python 3.11, dépendances verrouillées dans `backend/requirements.lock`,
UID 10001, Uvicorn sans reload ni journalisation des requêtes. `Dockerfile.web` :
build Vite avec `npm ci`, fichiers statiques Nginx UID 101, proxy de même origine vers
l'API. Les bases d'images et images déployées sont épinglées par empreinte.
Le workflow `dakafarm.yml` publie deux images GHCR privées, avec provenance et SBOM.
Les références exactes de déploiement sont conservées dans le GitOps.

PostgreSQL 15 dispose d'un volume local dédié. L'utilisateur applicatif `dakafarm`
est propriétaire de sa base, sans privilèges superutilisateur ou création de rôles.
Les secrets de base, de JWT, de tirage GHCR et du premier compte sont conservés hors Git.
Le compte initial est créé uniquement par `python -m app.bootstrap` dans un initContainer,
après migration Alembic ; son mot de passe aléatoire n'est ni affiché ni réinitialisé
au redémarrage. Aucun endpoint public de bootstrap n'est ajouté.

## Français

Français par défaut et sélection FR/EN/SW. Le catalogue français couvre les 454 clés
du catalogue anglais existant. Les menus, formulaires et tableaux utilisant i18next
en bénéficient ; des libellés codés en dur, certaines erreurs dynamiques et impressions
peuvent rester en anglais. Il ne s'agit pas d'une validation linguistique de tous les écrans.
L'identité DAKAFARM est affichée, les mentions de licence et d'auteur amont sont conservées.

## Validation et limites

Frontend : `cd frontend && npm ci --ignore-scripts && npm run build`.
API : `docker build -f Dockerfile.api -t dakafarm-api:qualification .`.
L'initialisation, les droits de base et les endpoints authentifiés sont vérifiés dans
une base synthétique isolée avant recette HTTPS de l'instance.

Qualification avec stockage local non répliqué, sans sauvegarde externe ni restauration
testée, sans SMTP configuré. Ne pas utiliser pour des écritures engageantes sans recette
métier. SYSCOHADA et e-MECeF ne sont pas implémentés par cette livraison. Le risque de
transaction partielle entre consommation d'aliment et stock repéré dans le code amont
reste à corriger. Les montées de version exigent une sauvegarde et une migration contrôlée.
