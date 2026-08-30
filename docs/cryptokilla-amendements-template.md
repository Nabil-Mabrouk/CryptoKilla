# CRYPTOKILLA — Amendements au Livre suite à l'adoption du template web
## Revue de conformité AGENTS.md / CLAUDE.md / MODULES.md — à verser à l'Annexe G

> Contexte : le développement s'appuie sur un template d'application web (châssis
> géré par `copier update`, flotte de déploiement, contrat structurel intouchable).
> Cette revue arbitre chaque friction entre le template et le livre. Règle de
> préséance instituée (AMEND-10) : le template fait foi pour l'INFRASTRUCTURE,
> le livre fait foi pour le FONCTIONNEL, tout conflit se résout par amendement
> explicite — jamais par divergence silencieuse (chapitre 0.1).

---

## AMENDEMENTS

### AMEND-03 — Base de données : PostgreSQL natif
- **Impacte** : chapitres 11.3, 15 ; Annexe E.
- **Décision** : la base v1 est le conteneur `cryptokilla_db` du template
  (PostgreSQL), en remplacement de "SQLite v1 portable PostgreSQL". Le DDL du
  chapitre 15 est rédigé en PostgreSQL natif. Event-store append-only, ledgers,
  projections : inchangés sur le principe (et renforcés : la concurrence
  d'écriture multi-processus était la limite documentée de SQLite).
- **Motif** : contrat structurel du template ; amélioration objective.

### AMEND-04 — Placement du code : tout dans le domaine, rien dans le châssis
- **Impacte** : chapitres 11, 34 ; consignes de développement.
- **Décision** : l'intégralité du code CryptoKilla vit dans des FICHIERS
  NOUVEAUX sous `app/domain/arena/` (sous-paquets indicatifs : `orchestrator/`,
  `engine/` (exécution/fills/stops), `agents/` (runtimes traders),
  `capture/` (données Kraken), `economy/` (tokens/pool), `memoryx/`, `events/`),
  branchés au châssis UNIQUEMENT via `app/domain/models.py` et
  `app/domain/routers.py` (points de montage prévus par le template). Côté
  frontend : les pages de l'arène (chapitre 24) sont des fichiers nouveaux ;
  `Landing.tsx`, `Navbar.tsx`, `Footer.tsx`, `landing.css` sont personnalisés
  (prévu par AGENTS.md) aux couleurs du chapitre 27. AUCUN code de l'arène dans
  `app/modules/` ou dans les composants châssis de `frontend/src/`.
- **Motif** : seule zone garantie de survivre à `copier update`.

### AMEND-05 — Comptes humains : adopter l'auth du template
- **Impacte** : chapitres 25, 31 ; R-91/R-92 ; **chapitre 15** (ajout
  signalé au Lot 4 — le DDL du Lot 3 avait créé une table `human_users`
  domaine avec `password_hash`, ce qui contredit cette décision ; corrigée
  en table d'overlay minimal, voir note de correction ci-dessous).
- **Décision** : le livre n'implémente PAS d'authentification maison. Les
  comptes humains (chapitre 25) = le système utilisateurs/rôles du template
  (module Admin : liste, rôles, invitations Waitlist). Le like (seule écriture
  publique) est lié à l'identifiant utilisateur du template. Le rôle admin du
  template porte l'accès à la console d'administration de l'arène (chapitre 31),
  laquelle reste développée en domaine (routeur + pages propres), conformément
  à la recommandation de MODULES.md ("ajoutez votre propre routeur… plutôt que
  d'éditer app/modules/admin/"). La Waitlist du template devient un outil
  officiel du plan de lancement (chapitre 36 : file d'attente avant ouverture).
- **À vérifier** (voir Q-19) : la vérification d'email existe-t-elle dans
  l'auth du template ? (exigence "email vérifié avant de liker", chapitre 25).
  À défaut, elle s'implémente en domaine par-dessus l'auth du template.
- **Correction Lot 4 (chapitre 15)** : la table `human_users` (identité,
  email, mot de passe) est remplacée par une table d'overlay domaine
  `human_arena_profile`, clée sur l'identifiant utilisateur du template
  (FK logique, hors DDL domaine puisque la table utilisateurs elle-même
  est châssis) ; elle ne porte que ce que le template ne fournit pas déjà
  pour les besoins de l'arène (`email_verified_at` si absent du template,
  `anonymized_at` pour la suppression RGPD, chapitre 25). `likes.human_user_id`
  référence désormais cet identifiant template, pas une table domaine.

### AMEND-06 — Module Monétisation : désactivé en v1
- **Impacte** : chapitre 25 (gratuité totale v1) ; Q-15.
- **Décision** : le module boutique/Stripe, actuellement actif, est DÉSACTIVÉ
  pour la v1 via `scripts/toggle_module.sh` (mécanisme prévu par le template —
  jamais d'édition manuelle de `.env` pour sa structure). Aucun modèle
  Product/Purchase/Subscription n'est référencé par le code de l'arène. Q-15
  (monétisation) reste "reportée" ; une future activation du module sera
  l'implémentation naturelle, sans code catalogue (piloté par la donnée, côté
  Stripe), et exigera un amendement dédié.
- **Motif** : conformité au verrou "aucun flux financier avec le public en v1"
  (chapitres 25, 30) — un module de paiement actif contredirait le livre.

### AMEND-07 — Santé et observabilité : séparation stricte
- **Impacte** : chapitres 26, 33.
- **Décision** : `GET /health` et son champ `modules` (contrat flotte) sont
  INTOUCHABLES et ne portent JAMAIS d'information arène. La santé des
  composants CryptoKilla (orchestrateur, capture, moteur, runtimes) vit sur des
  endpoints domaine dédiés (ex. `/api/arena/health`, authentifié admin),
  alimentant les tableaux de bord internes du chapitre 33.

### AMEND-08 — Internationalisation : plateforme FR/EN via MODULE_I18N
- **Impacte** : chapitres 24, 25, 27 ; Annexe E.
- **Décision** : la plateforme publique est bilingue FR/EN via le mécanisme du
  template (clés additives dans `common.json` — ajouts additifs uniquement,
  fusion 3 voies assumée). Tous les textes publics normés par le livre
  (disclaimers, vocabulaire du lore, libellés des pages) existent dans les deux
  langues ; la version française fait foi en cas de divergence. Langues des
  posts de Killa : [PARAM: langues_killa] (nouveau paramètre, Annexe E).
  Le contenu du CHAT des agents n'est pas traduit (matériau brut de l'arène).

### AMEND-09 — SecurityMiddleware : couche complémentaire, jamais substitutive
- **Impacte** : chapitres 28, 29.
- **Décision** : la détection passive du châssis (chemins suspects, scanners,
  patterns d'injection, journal SecurityEvent, non bloquante) est reconnue
  comme télémétrie complémentaire. Elle ne remplace AUCUNE défense normative du
  livre : encapsulation des contenus web, sandbox, rate limits des likes et de
  l'API, gel d'anomalies restent implémentés en domaine. Pas de règles
  personnalisées dans `detectors.py` (divergence châssis assumée seulement si
  indispensable, décision journalisée).

### AMEND-10 — Règle de préséance et documents de pilotage des IA
- **Impacte** : chapitre 0.1 ; consignes de développement.
- **Décision** : préséance à trois étages, opposable à tout agent développeur :
  1. Le CONTRAT STRUCTUREL du template (AGENTS.md §"Ne touchez jamais") prime
     pour l'infrastructure : /health, conteneurs/labels, structure .env,
     MODULE_FLAGS.
  2. Le LIVRE prime pour tout le fonctionnel : règles R-xx, [NORME], schémas
     (Annexe B), contrats d'outils (Annexe C), prompts (Annexe D), paramètres
     (Annexe E), formules (Annexe F).
  3. Tout conflit entre 1 et 2 = amendement explicite au livre (jamais de
     divergence silencieuse ; "le code est un bug", chapitre 0.1).
- AGENTS.md et MODULES.md étant RÉGÉNÉRÉS par `copier update`, aucune consigne
  CryptoKilla n'y est insérée : elles vivent dans le fichier nouveau
  `ARENA.md` (racine du dépôt, survit par construction), référencé par une
  ligne additive unique dans CLAUDE.md (conflit de fusion mineur assumé ; si
  la ligne saute lors d'un update, la re-poser fait partie de la procédure
  post-update, consignée dans ARENA.md).

### AMEND-11 — Cœur de l'arène hors du framework agentic du châssis
- **Impacte** : chapitres 11, 12, 16, 22, 23 ; Annexe D.
- **Décision (verrouillée)** : les runtimes des AGENTS TRADERS, l'ORCHESTRATEUR,
  le moteur de risque et la surveillance des stops n'utilisent PAS
  MODULE_AGENTIC (boucles autonomes permanentes à économie de tokens ≠
  workflows requête/étapes en YAML ; le cœur du jeu ne doit dépendre d'aucune
  fusion de châssis). Implémentation domaine, conformément au verrou
  "implémentation maison explicite" (chapitres 11.3, 19).
- **Option ouverte (Q-20)** : Killa, les spectateurs et l'appel de NOTATION du
  pool (12.4) ont une forme requête→réponse compatible avec MODULE_AGENTIC
  (service YAML additif + outil enregistré). Décision à prendre en couche C3 :
  (a) les porter sur MODULE_AGENTIC (moins de code, usage du châssis tel que
  prévu, mais dépendance aux fusions `copier update` sur agent_services.yaml
  et tools/__init__.py) ou (b) les garder en domaine (uniformité, zéro risque
  de fusion). Contraintes quelle que soit l'option : la notation reste
  température 0 / JSON strict / auteur anonymisé (Annexe D), et les prompts
  restent ceux de l'Annexe D, valeurs via le registre.

### AMEND-12 — Pipeline de validation à trois branches ; codes d'erreur modify/close ; season.event générique
- **Impacte** : chapitre 12.3 (Lot 1) ; Annexe B — énumération `kind` de
  `season.event` (B.2.11), table des codes d'erreur (B.4).
- **Origine** : pas un conflit template/livre — un trou de brief. AMEND-B1
  (Lot 2) a introduit les actions `modify`/`close` sur `order.request` sans
  définir leurs vérifications propres ni leurs codes de rejet dédiés ; le
  brief du chapitre 12.3 (Lot 1) ne décrivait qu'un pipeline pour
  `action: open`. Trouvé en relecture de validation (chapitre 0.2).
- **Décision** :
  1. Le pipeline de validation d'ordre (chapitre 12.3) se décline en
     **trois branches selon `action`** : `open` (pipeline déjà normé,
     inchangé), `modify`, `close` — chacune avec ses vérifications propres
     et son propre ordre strict.
  2. Deux codes d'erreur supplémentaires, ajoutés à la table B.4 de
     l'Annexe B : `E-STOP-WIDENING` (un `modify` élargit le stop au lieu de
     le resserrer — interdit, chapitre 7.2) et `E-POSITION-UNKNOWN` (un
     `modify` ou `close` référence un `position_id` inexistant ou
     n'appartenant pas à l'agent appelant).
  3. L'énumération `kind` de `season.event` (Annexe B.2, type 11) gagne la
     valeur `notice` : avis générique accompagné d'un `detail` libre,
     utilisé pour les dégradations opérationnelles (ex. panne de flux de
     prix, chapitre 12) et pour les rappels d'échéance de fin de saison
     (`[PARAM: preavis_rappel_fin]`, chapitre 10.2).
- **Motif** : sans ces branches et ces codes, un `modify` qui élargit un
  stop ou un `close` sur une position inexistante n'a aucun chemin de rejet
  normatif alors que les règles correspondantes sont verrouillées (chapitre
  7.2) ; sans `kind: notice`, toute annonce de dégradation publiée par
  l'orchestrateur viole le schéma de sa propre Annexe B (`N-ANXB-01`).

### AMEND-13 — Champ `recipient` dans l'enveloppe commune de l'Annexe B
- **Impacte** : Annexe B (B.0, B.2 pour `order.rejected`/`tokens.allocation`/
  `inbox.recap`, B.3/`N-ANXB-04`) ; chapitre 15 (schéma de la table `events`
  et requêtes canoniques qui en dépendent).
- **Origine** : trou trouvé en rédigeant le chapitre 15 (Lot 3), pas un
  conflit template/livre. Le principe « boîte de réception privée »
  (`N-ANXB-04`) suppose qu'un objet privé désigne son destinataire, mais
  l'enveloppe commune (B.0) ne portait qu'un `sender`, jamais de
  destinataire — `tokens.allocation` en particulier n'avait **aucun**
  moyen de désigner l'agent crédité.
- **Décision** : l'enveloppe commune (B.0) gagne un champ `recipient`
  (`agent_id | null`), présent uniquement pour les objets adressés en
  privé à un agent (`order.rejected`, `tokens.allocation`,
  `inbox.recap`) ; `null`/absent pour tout objet public.
- **Motif** : sans ce champ, aucune requête ne peut retrouver « les
  allocations reçues par cet agent » sans heuristique fragile — la table
  `events` (event-sourcing, chapitre 11.2) doit pouvoir répondre
  directement.

### Notes sans amendement
- **Analytics** : pas d'événements personnalisés dans le châssis — les
  métriques d'arène (chapitre 33) restent en domaine ; les pages vues du
  châssis sont un bonus gratuit. Aucun changement au livre.
- **Tutoriaux** : module utilisable, à discrétion, pour héberger de la
  documentation publique (guide de l'arène) — usage optionnel, non normé ; la
  page "règles publiques de la saison" (chapitre 24) reste une page domaine.

---

## QUESTIONS OUVERTES — mises à jour (Annexe G)

- **Q-19 (NOUVELLE, bloquante pour la couche C1)** — Capacités d'infrastructure
  du template, à clarifier avec son fournisseur AVANT tout code :
  1. Des services docker ADDITIONNELS (workers long-running : runtimes agents,
     orchestrateur, capture, moteur de stops ; conteneur sandbox dédié) sont-ils
     admis par la flotte et `copier update` (ajout dans docker-compose.yml sans
     toucher aux 3 conteneurs nommés) ? Sinon : quel hébergement pour le moteur
     (option c : hors template, le template ne servant que web+db) ?
  2. Le WebSocket (chapitre 26) traverse-t-il la configuration Traefik de la
     flotte ?
  3. Existe-t-il un mécanisme de tâches planifiées (la séquence horaire H+0) ou
     doit-il vivre dans nos workers ?
  4. L'auth du template offre-t-elle la vérification d'email (AMEND-05) ?
  5. Un redeploy interrompt-il les conteneurs additionnels (fenêtre
     d'indisponibilité du moteur de stops à borner — lien R-43) ?
- **Q-20 (NOUVELLE, à trancher en C3)** — Killa/spectateurs/notation sur
  MODULE_AGENTIC ou en domaine (voir AMEND-11).
- **Q-15** — inchangée (reportée), désormais adossée à AMEND-06.
- **Q-16** — inchangée ; noter que le châssis (analytics : IP hashée) fournit
  une base saine, la revue RGPD couvrira châssis + domaine.

## NOUVEAUX [PARAM] (Annexe E)
- `langues_killa` (AMEND-08).

## IMPACTS SUR LES LOTS DE PRÉ-RÉDACTION (récapitulatif pour l'IA rédactrice)
- Lot 1 / chapitre 12 et Annexe B : pipeline de validation à trois branches
  (`open`/`modify`/`close`), codes `E-STOP-WIDENING` et `E-POSITION-UNKNOWN`,
  `season.event` gagne `kind: notice` (AMEND-12 — déjà intégré aux deux
  fichiers).
- Lot 3 / chapitre 11 : stack amendée (AMEND-03, AMEND-04, AMEND-11) ; le
  schéma d'architecture montre désormais les conteneurs du template + les
  workers (selon issue de Q-19).
- Lot 3 / chapitre 15 : DDL PostgreSQL (AMEND-03).
- Lot 4 / chapitre 24 : i18n FR/EN (AMEND-08) ; wireframes inchangés.
- Lot 4 / chapitre 25 : réécrit autour de l'auth du template (AMEND-05) ;
  gratuité v1 renforcée par AMEND-06.
- Lot 4 / chapitre 26 : /health intouchable, endpoints santé domaine
  (AMEND-07) ; WS conditionné à Q-19.2.
- Lot 5 / chapitres 28-29 : SecurityMiddleware en couche complémentaire
  (AMEND-09).
- Lot 5 / chapitre 31 : console admin = routeur + pages domaine, adossés aux
  rôles du template (AMEND-05).
- Lot 5 / chapitre 34 : la couche C1 intègre la levée de Q-19 comme
  prérequis ; DoD inchangées.
- Lot 5 / Annexes E et G : ajouts ci-dessus.
