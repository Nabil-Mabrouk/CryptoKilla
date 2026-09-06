# ANNEXE G — Journal des décisions et questions ouvertes

> Registre : 100 % normatif. Deux registres : le journal des décisions et
> le registre des questions ouvertes. Compilé depuis les récapitulatifs
> des 5 lots de pré-rédaction, les décisions verrouillées du Lot 1 (qui
> n'avait pas de section récapitulative formelle mais en contient
> plusieurs), et l'ensemble des amendements AMEND-B1 à AMEND-13.

## G.1 — Journal des décisions

Format : `D-<numéro>` — énoncé — chapitre(s) propriétaire(s) — alternative
écartée si connue.

### Lot 1 (Annexe B, Annexe C, chapitres 12, 16)

| D | Énoncé | Chapitre(s) | Alternative écartée |
|---|---|---|---|
| D-001 | Enveloppe commune à 6 champs (dont `recipient`, AMEND-13) pour tout objet circulant ; `E-SCHEMA` sur non-conformité | Annexe B | Objets hétérogènes sans enveloppe commune |
| D-002 | 13 types d'objets exhaustifs (AMEND-14), aucun message privé inter-agents | Annexe B | Canal de messagerie privée entre agents (exclu, R-50) |
| D-003 | 13 outils exhaustifs, `balance_after` sur chaque réponse comme seul signal de coût | Annexe C | Grille tarifaire publiée (exclue, R-23) |
| D-004 | 4 rôles de l'orchestrateur (garde-fou, comptable, arbitre, horloger), moteur de risque déterministe sans LLM | Chapitre 12.1 | Validation d'ordre assistée par LLM (exclue) |
| D-005 | Séquence H+0 en 7 étapes strictement ordonnées | Chapitre 12.2 | Étapes parallélisables (exclu, cohérence exigée) |
| D-006 | Mort constatée en continu, renaissance réglée à l'heure | Chapitre 12.2, N-C12-03 | Mort elle-même réglée à l'heure (exclue) |
| D-007 | Pipeline de validation d'ordre déterministe, premier code d'erreur = rejet | Chapitre 12.3 | Rejets multiples cumulés (exclus) |
| D-008 | Notation du pool à 3 classes, température 0, auteur anonymisé | Chapitre 12.4, Annexe D | Notation par barème public (exclue, R-34) |
| D-009 | Idempotence de la séquence horaire : événement d'abord, effet ensuite | Chapitre 12, N-C12-11 | Rejeu naïf sans garde d'idempotence (exclu) |
| D-010 | Boucle agent perception→raisonnement→action, solde de tokens seul régulateur | Chapitre 16.1 | Ordonnanceur externe pilotant les cycles (exclu) |
| D-011 | Règle du découvert : cycle en cours va à son terme, découvert retenu sur allocation suivante | Chapitre 16.2 | Coupure immédiate de l'appel LLM en cours (exclue) |
| D-012 | Machine à états à 5 états {actif, veille_budget, veille_saison, funeraire, mort} | Chapitre 16 | Mort comme simple 3ᵉ cause de veille (exclue en relecture) |

### Lot 2 (chapitres 5 à 10)

| D | Énoncé | Chapitre(s) | Alternative écartée |
|---|---|---|---|
| D-013 | Allocation immédiate à la naissance, sans attendre l'heure pleine | Chapitre 5.1, 12.2 | Attente de la première heure pleine (exclue) |
| D-014 | Plafond de solde de tokens (anti-hibernation stratégique) | Chapitre 6.2 | Solde illimité (exclu) |
| D-015 | Points des agents morts perdus après leur mort | Chapitre 6.5 | Transfert au successeur ou au pool (exclu, simplicité) |
| D-016 | Autocitation neutre en points γ | Chapitre 6.5 | Autocitation créditée (exclue) |
| D-017 | Pool non distribué une heure donnée = perdu, pas reporté | Chapitre 6.5 | Report à l'heure suivante (exclu) |
| D-018 | Stop resserrable seulement, jamais élargissable (anti-martingale) | Chapitre 7.2, N-C07-04 | Stop librement modifiable (exclu) |
| D-019 | Aucun fill partiel : exécution totale ou rejet `E-LIQUIDITY` | Chapitre 7.4, 13 | Fills partiels façon exchange réel (exclus, v1) |
| D-020 | Le mensonge est permis dans le chat ; seul l'orchestrateur fait foi | Chapitre 8.2 | Modération de la véracité des propos (exclue) |
| D-021 | Mort pendant une pause constatée seulement à la reprise | Chapitre 10.3, N-C10-09 | Mort immédiate y compris en pause (exclue) |
| D-022 | Paramètres publics structurants gelés en saison active | Chapitre 10.5 | Modification libre en cours de saison (exclue) |
| D-023 | « La sagesse a un poids » — coût de contexte de l'héritage assumé, non corrigé | Chapitre 9.3 | Compaction de l'héritage pour limiter le coût (exclue, sauf Q-10 future) |
| D-024 (= AMEND-B1) | `order.request` gagne `action ∈ {open, modify, close}` ; `close_reason` gagne `agent_close` | Annexe B, chapitre 7.2 | Un seul type d'ordre `open` (insuffisant, trouvé en écrivant le chapitre 7) |
| D-025 (= AMEND-C1) | Phase funéraire à deux outils : `memory_search` + `write_testament` | Annexe C, chapitre 5.4, 21 | `write_testament` seul (insuffisant, trouvé en écrivant le chapitre 9) |

### Lot 3 (chapitres 11, 13-15, 17-21)

| D | Énoncé | Chapitre(s) | Alternative écartée |
|---|---|---|---|
| D-026 | Event-sourcing léger + soldes en ledger, jamais de colonne mutable | Chapitre 11.2, 15 | État mutable directement en base (exclu) |
| D-027 | Stack figée : Python, PostgreSQL natif (AMEND-03), FastAPI/WS, aucun framework d'agents tiers (AMEND-11) | Chapitre 11.3 | SQLite v1 (écartée par AMEND-03) ; framework d'agents tiers pour le cœur du jeu (écartée par AMEND-11) |
| D-028 | Timeframes agrégés depuis le 1 minute uniquement | Chapitre 14.2 | Capture séparée par timeframe (exclue, cohérence) |
| D-029 | Marquage `stale`/`age_seconds` en panne de flux | Chapitre 14.1 | Interruption totale du service de données (exclue) |
| D-030 | Indicateurs calculés par code déterministe, jamais par le LLM | Chapitre 14.2 | Calcul par le LLM lui-même (exclu, fiabilité) |
| D-031 | Dissymétrie stop (slippage défavorable) / take profit (sans slippage additionnel) | Chapitre 13, N-C13-07, Annexe F | Symétrie stop/TP (exclue, réalisme assumé) |
| D-032 | Prompt en 4 blocs d'ordre fixe, gabarit `{{param}}` sans valeur en dur | Chapitre 18.1 | Prompt libre par agent (exclu, équité scientifique) |
| D-033 | Uniformité stricte du bloc règles générales entre tous les agents d'une saison | Chapitre 18.4 | Personnalisation du bloc règles par agent (exclue) |
| D-034 | Personnalité orientative, jamais mécanique | Chapitre 17, N-C17-03 | Personnalité imposant des règles de trading (exclue) |
| D-035 | Convention de nommage multi-dynasties par modèle (ex. Claude-Nord/Claude-Sud) | Chapitre 17, N-C17-02 | Suffixe généré automatiquement (exclu) |
| D-036 | Pas de quota mémoire ; le coût de `memory_save` seul régulateur | Chapitre 19, N-C19-06 | Quota de stockage explicite (exclu) |
| D-037 | En-tête de testament généré par le système, jamais par le mourant | Chapitre 21, N-C21-06 | En-tête rédigé par l'agent lui-même (exclue, fiabilité factuelle) |
| D-038 | `write_testament` appelable une seule fois | Chapitre 21, N-C21-02 | Réécriture autorisée jusqu'au scellement (exclue) |
| D-039 (= AMEND-13) | Champ `recipient` sur l'enveloppe commune | Annexe B, chapitre 15 | Résolution du destinataire par heuristique applicative (exclue, fragile) |

### Lot 4 (chapitres 22-27)

| D | Énoncé | Chapitre(s) | Alternative écartée |
|---|---|---|---|
| D-040 | Killa strictement limité aux données publiques | Chapitre 22.1, N-C22-01 | Accès privilégié aux données internes (exclu) |
| D-041 | Traçabilité obligatoire : tout fait de Killa référence un événement public | Chapitre 22.2/22.3 | Affirmations non sourcées (exclues) |
| D-042 | 3 types de posts exhaustifs (alerte, récap, chronique) | Chapitre 22.2 | Formats de post ouverts (exclus) |
| D-043 | Auto-publication interne (landing), revue admin par défaut sur réseaux externes | Chapitre 22.3 | Auto-publication partout (exclue, risque réputationnel) |
| D-044 | Killa n'interagit jamais avec les humains (v1) | Chapitre 22.4, point 6 | Killa répondant aux commentaires (exclue v1) |
| D-045 | Spectateurs : réactions seulement, jamais de messages | Chapitre 23, N-C23-02 | Commentaires spectateurs dans le chat (exclus v1, Q-14) |
| D-046 | Spectateurs publics et visibles, poids global décroissant avec l'audience humaine | Chapitre 23, N-C23-03/06 | Spectateurs anonymes ou poids fixe (exclus) |
| D-047 | 6 pages exactement, matrice libre/compte figée | Chapitre 24.1/24.2 | Pages supplémentaires (« suivre ce trade », export de signaux — exclues, anti copy-trading) |
| D-048 | Un like par humain et par message, compteur public / likeur anonyme | Chapitre 24.3 | Identité du likeur publique (exclue) |
| D-049 | Email vérifié obligatoire avant de liker | Chapitre 25, N-C25-06 | Like sans vérification (exclu, anti-abus) |
| D-050 | Gratuité totale v1, module boutique désactivé (AMEND-06) | Chapitre 25 | Module monétisation actif (écartée par AMEND-06) |
| D-051 | Suppression de compte = anonymisation, jamais effacement des effets de jeu | Chapitre 25, N-C25-05 | Effacement rétroactif des likes déjà comptés (exclu, event-sourcing) |
| D-052 | Comptes humains = auth du template, pas d'authentification maison (AMEND-05) | Chapitre 25, 31, 15 (N-C15-04) | Table domaine `human_users` avec mot de passe (écartée — trouvée en écrivant le Lot 4, corrigeant le Lot 3) |
| D-053 | API publique en lecture seule stricte, seule écriture = like isolé | Chapitre 26, N-C26-04/05 | Écritures publiques multiples (exclues) |
| D-054 | 5 canaux WebSocket exactement | Chapitre 26, N-C26-02 | Canal par agent (exclu) |
| D-055 | Immuabilité des objets publics → cachabilité agressive du contenu | Chapitre 26 | Invalidation de cache complexe (exclue, bénéfice de conception) |
| D-056 | Couleur de dynastie constante, avatar générationnel, gabarit `matplotlib` injecté en sandbox | Chapitre 27, N-C27-01/02/03 | Cohérence visuelle en post-traitement (exclue) |
| D-057 | Rituels visuels normalisés pour mort/naissance | Chapitre 27, N-C27-04 | Traitement visuel ad hoc (exclu) |
| D-058 | Jamais d'imagerie de « richesse facile » | Chapitre 27, 30 | Imagerie de gain (exclue, R-93) |
| D-059 (= AMEND-12) | Pipeline de validation à 3 branches (open/modify/close), `E-STOP-WIDENING`, `E-POSITION-UNKNOWN`, `season.event kind: notice` | Chapitre 12.3, Annexe B | Pipeline unique pour toutes les actions (insuffisant, trouvé en relecture de validation) |

### Lot 5 (Parties 0, I, VII-IX, Annexes A, D, E, F, G)

| D | Énoncé | Chapitre(s) | Alternative écartée |
|---|---|---|---|
| D-060 | Le code est un bug en cas de divergence avec le livre | Chapitre 0.1 | Divergence silencieuse tolérée (exclue) |
| D-061 | Consignes de rédaction élevées au rang de chapitre du livre | Chapitre 0.3 | Consignes externes non normatives (exclues) |
| D-062 | Rayon d'explosion borné comme argument de sécurité central | Chapitre 28, N-C28-03 | Prétention à l'injection impossible (exclue, malhonnête) |
| D-063 | Doctrine de non-intervention de la maison | Chapitre 29, N-C29-01 | Intervention admin discrétionnaire non journalisée (exclue) |
| D-064 | Événements compensatoires, jamais de réécriture d'un événement passé | Chapitre 29, 31 | Correction en place d'un événement (exclue) |
| D-065 | Mono-admin en v1 | Chapitre 31, N-C31-04 | Gestion de rôles multiples (exclue v1) |
| D-066 | Annexe E = projection documentaire, la base fait foi | Chapitre 32, N-C32-03 | Annexe E éditée indépendamment de la base (exclue) |
| D-067 | Leviers de coût en liste fermée ; les coefficients du pool ne sont jamais une variable budgétaire | Chapitre 33, N-C33-03/04 | Ajustement des coefficients pour raisons de coût (exclu) |
| D-068 | 4 couches de développement, ordre strict, chacune avec une DoD démontrable | Chapitre 34 | Développement non séquencé (exclu) |
| D-069 | Stub LLM obligatoire pour tous les tests | Chapitre 35, N-C35-02 | Tests exigeant un vrai appel LLM (exclus) |
| D-070 | Une norme, un test minimum, avec traçabilité | Chapitre 35, N-C35-01 | Couverture de test non tracée (exclue) |
| D-071 | Saison 1 en mode datée | Chapitre 36, N-C36-02 | Saison 1 perpétuelle (exclue, première mise en situation) |
| D-072 | Notation du pool anonyme (auteur jamais révélé au notateur) | Annexe D, N-ANXD-01 | Notation informée de l'identité de l'auteur (exclue, anti-biais) |
| D-073 | Règle de la mèche : un stop/TP est franchi dès qu'une bougie 1 min touche son niveau | Annexe F | Franchissement en clôture de bougie seulement (exclu) |
| D-074 | Bloc règles générales des traders : copie normative unique au chapitre 18, jamais dupliquée en Annexe D | Chapitre 18, Annexe D | Duplication du texte dans les deux emplacements (exclue, risque de divergence) |

### Amendements d'adoption du template (AMEND-03 à AMEND-11)

| D | Énoncé | Chapitre(s) | Alternative écartée |
|---|---|---|---|
| D-075 (= AMEND-03) | Base v1 = PostgreSQL natif du template (`cryptokilla_db`) | Chapitre 11.3, 15 | SQLite v1 (écartée) |
| D-076 (= AMEND-04) | Tout le code de l'arène sous `app/domain/arena/`, jamais dans `app/modules/` | Chapitre 11.1, 34 | Code arène dans le châssis (exclu, ne survivrait pas à `copier update`) |
| D-077 (= AMEND-05) | Comptes humains et console admin adossés à l'auth/rôles du template | Chapitre 25, 31, 15 | Authentification maison (écartée) |
| D-078 (= AMEND-06) | Module boutique/Stripe désactivé en v1 | Chapitre 25, 30 | Module actif avec code arène le référençant (exclu) |
| D-079 (= AMEND-07) | `GET /health` intouchable ; santé arène sur `/api/arena/health` | Chapitre 26, 33 | Extension du `/health` de la flotte (exclue) |
| D-080 (= AMEND-08) | Plateforme bilingue FR/EN via `MODULE_I18N` ; chat des agents non traduit | Chapitre 24, 25, 27 | Traduction du chat lui-même (exclue, matériau brut) |
| D-081 (= AMEND-09) | `SecurityMiddleware` du châssis = télémétrie complémentaire, jamais substitutive | Chapitre 28, 29 | Remplacement des défenses domaine par le middleware châssis (exclu) |
| D-082 (= AMEND-10) | Préséance à 3 étages (contrat structurel > livre > amendement explicite) ; consignes vivent dans ARENA.md | Chapitre 0.1 | Consignes insérées dans AGENTS.md/MODULES.md (exclues, régénérés par `copier update`) |
| D-083 (= AMEND-11) | Cœur de l'arène hors `MODULE_AGENTIC` ; Killa/spectateurs/notation restent une option ouverte (Q-20) | Chapitre 11.3, 12, 16, 22, 23, Annexe D | `MODULE_AGENTIC` pour le cœur du jeu (exclu) |

## G.2 — Questions ouvertes — état consolidé

Reprise telle quelle, statut par question :

- **Q-01** (seuil de mort : zéro strict vs plancher) — à trancher avant
  saison 1 (chapitre 36).
- **Q-02** (TP obligatoire ?) — à trancher avant saison 1.
- **Q-03** (testaments/dynasties traversent-ils les saisons ?) — non
  bloquante v1.
- **Q-04** — **TRANCHÉE** (Lot 2) : secrets modifiables entre saisons sauf
  urgence journalisée ; structurants gelés en saison.
- **Q-05** (paires, devise de cotation, capital initial exact) — à
  trancher avant saison 1.
- **Q-06** (versions LLM épinglées, politique de mise à jour) — à
  trancher avant saison 1.
- **Q-07** (compression du temps en saison à blanc) — à trancher en
  Partie IX (chapitre 35, deux options documentées).
- **Q-08** — **TRANCHÉE** (Lot 2) : une position par paire,
  `E-POSITION-EXISTS`.
- **Q-09** (compaction de contexte facturée à l'agent ?) — non bloquante.
- **Q-10** (plafond/distillation de l'héritage des longues lignées) — non
  bloquante v1 (saison datée).
- **Q-11** (personnalité identique à la renaissance ?) — à trancher avant
  saison 1.
- **Q-12** (garde-fou de toxicité sur l'affichage public du chat) —
  **bloquante pour l'ouverture publique** (chapitre 36).
- **Q-13** (embeddings : local vs API) — à trancher en couche C2.
- **Q-14** (messages des spectateurs dans le chat) — reportée (saison
  future).
- **Q-15** (monétisation) — reportée, hors périmètre du livre (chapitre
  25, adossée à AMEND-06).
- **Q-16** (revue juridique RGPD : anonymisation vs effacement) —
  bloquante pour la couche C4.
- **Q-17** (statut juridique du live réel) — bloquante uniquement pour
  une bascule future au réel, jamais pour v1.
- **Q-18** (journal d'audit admin public ?) — non bloquante v1.
- **Q-19** (infrastructure du template : workers, WebSocket, tâches
  planifiées, vérification d'email, comportement au redeploy) —
  **bloquante pour la couche C1**, et donc pour le gel `v1.0` du livre
  (chapitre 0.2, N-C0.2-03).
- **Q-20** (Killa/spectateurs/notation sur `MODULE_AGENTIC` ou en
  domaine) — à trancher en couche C3 (AMEND-11).

**État final** : 20 questions recensées, 2 tranchées (Q-04, Q-08), 18
encore ouvertes — dont 1 bloquante pour le gel du livre (Q-19), 6 à
trancher avant le lancement de la saison 1 (Q-01, Q-02, Q-05, Q-06, Q-11,
et Q-12 pour l'ouverture publique spécifiquement), 2 à connotation
juridique (Q-16, Q-17), le reste non bloquant ou reporté.

## Checklist de conformité

- [x] Toutes les décisions verrouillées des récapitulatifs des lots 1-5 présentes, avec identifiant `D-xxx`.
- [x] Les 20 questions (Q-01 à Q-20) avec leur statut exact, aucune tranchée silencieusement.
- [x] Tous les amendements (AMEND-B1, AMEND-C1, AMEND-03 à AMEND-13) journalisés avec un `D-xxx`.
