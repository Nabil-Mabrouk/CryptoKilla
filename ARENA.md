# ARENA.md — Consignes CryptoKilla pour les agents développeurs

> Ce fichier est un FICHIER NOUVEAU du projet : il survit à `copier update`
> par construction (voir AGENTS.md §"À vous"). Il complète AGENTS.md et
> MODULES.md sans jamais les contredire sur l'infrastructure. Lisez les trois
> avant de modifier quoi que ce soit.

## 1. Les trois sources de vérité et leur préséance

1. **AGENTS.md / MODULES.md (le template)** — font foi pour l'INFRASTRUCTURE :
   contrat flotte (`GET /health` et son champ `modules`), noms de conteneurs et
   labels Traefik, structure de `.env` (gérée par scripts), `MODULE_FLAGS`,
   zones châssis. Ne JAMAIS enfreindre leur section "Ne touchez jamais".
2. **Le Livre CryptoKilla** (`docs/livre/`, avec ses annexes) — fait foi pour
   TOUT LE FONCTIONNEL : règles R-xx, exigences [NORME], schémas d'événements
   (Annexe B), contrats d'outils des agents (Annexe C), prompts (Annexe D),
   registre des paramètres (Annexe E), formules de fill (Annexe F), journal et
   questions ouvertes (Annexe G, incluant les amendements AMEND-xx).
3. **En cas de conflit** entre 1 et 2 : ne tranchez pas dans le code. Signalez,
   proposez un amendement AMEND-xx (Annexe G). Un code qui diverge du livre
   sans amendement est un bug, même s'il "marche" (Livre, chapitre 0.1).

## 2. Où vit le code CryptoKilla (AMEND-04)

- Backend : UNIQUEMENT des fichiers nouveaux sous `app/domain/arena/`
  (`orchestrator/`, `engine/`, `agents/`, `capture/`, `economy/`, `memoryx/`,
  `events/`), branchés via `app/domain/models.py` et `app/domain/routers.py`.
- Frontend : pages de l'arène en fichiers nouveaux ; personnalisation prévue de
  `Landing.tsx`, `Navbar.tsx`, `Footer.tsx`, `landing.css` (charte : Livre,
  chapitre 27, exécutée et détaillée par
  [`CHARTE-GRAPHIQUE.md`](CHARTE-GRAPHIQUE.md) — OPPOSABLE : à lire et
  appliquer avant toute création ou modification de page, existante ou
  future ; en cas de conflit avec le Livre, le Livre gagne, §1). Textes
  publics bilingues FR/EN via les clés i18n du template, ajouts ADDITIFS
  uniquement (AMEND-08).
- Base : PostgreSQL du template (`cryptokilla_db`), schéma du Livre chapitre 15
  (AMEND-03) : event-store append-only + ledgers. INTERDIT : colonne de solde
  mutable, modification d'événements passés, secret en base.
- JAMAIS de code arène dans `app/modules/` ni dans les composants châssis de
  `frontend/src/`. Le cœur du jeu (runtimes traders, orchestrateur, moteur de
  risque, stops) n'utilise PAS `MODULE_AGENTIC` (AMEND-11) ; Killa/spectateurs/
  notation : décision Q-20 en couche C3 — ne pas anticiper.

## 3. Interdits fonctionnels absolus (rappels du Livre)

- Aucune valeur de jeu en dur : tout passe par le registre des paramètres
  (Annexe E ; table `season_params`). Les prompts utilisent des gabarits
  `{{param}}`.
- Aucun secret (clés LLM, Kraken) hors de la gestion `.env` du template ;
  jamais en base, jamais en sandbox, jamais dans un prompt.
- Aucun endpoint n'expose : testaments non publiés, coefficients du pool,
  grille de coûts en tokens, détail du calcul du pool.
- `GET /health` du template : intouchable et sans information arène ; la santé
  arène vit sur des endpoints domaine dédiés (AMEND-07).
- Module boutique/Stripe : désactivé v1 (AMEND-06) — aucun code arène ne le
  référence.
- Aucune fonctionnalité de copy-trading, notification de trades aux humains,
  ou conseil d'investissement (R-93 ; chapitres 24, 30).
- Exécution du code des agents : uniquement dans la sandbox spécifiée
  (chapitre 28) — jamais dans le processus backend web.

## 4. Qualité et tests

- Chaque exigence [NORME] implémentée a au moins un test automatisé ; les
  composants sont testables avec un stub LLM scripté (chapitre 35). Les tests
  de `app/domain/` sont à notre charge (AGENTS.md) : `pytest` obligatoire
  avant push, en plus de `npm run typecheck && npm run test && npm run build`.
- Respecter l'idempotence de la séquence horaire (chapitre 12) et la reprise
  après crash sans pénalité (R-17) : toute logique d'état se reconstruit
  depuis l'event-store.

## 5. Procédure post-`copier update`

1. Vérifier que la ligne de renvoi vers ARENA.md existe toujours dans
   CLAUDE.md ; sinon la re-poser (une ligne additive).
2. Vérifier que les ajouts additifs (clés i18n ; et, si Q-20 a choisi
   MODULE_AGENTIC : entrées YAML et TOOLS) ont survécu à la fusion.
3. Relancer la suite de tests complète avant tout nouveau développement.

## 6. Questions ouvertes qui vous bloquent

- Q-19 (infrastructure : services docker additionnels pour les workers
  long-running et la sandbox, WebSocket via Traefik, planification horaire,
  vérification d'email, comportement au redeploy) : BLOQUANTE pour la couche
  C1 — ne commencez pas les workers sans sa réponse.
- La liste complète et l'état des Q-xx : Livre, Annexe G. Ne tranchez jamais
  une Q-xx dans le code.

---
*Ligne à maintenir dans CLAUDE.md (additive) :*
`Ce projet implémente CryptoKilla : lisez impérativement [ARENA.md](ARENA.md) (préséance et consignes) avant toute modification.`
