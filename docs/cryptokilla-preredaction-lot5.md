# CRYPTOKILLA — Pré-rédaction du Livre — LOT 5 (final)
## Parties 0, I, VII, VIII, IX + Annexes A, D, E, F, G

> **Rappel** : joindre les CONSIGNES GÉNÉRALES POUR L'IA RÉDACTRICE (Lot 1). Amendements en vigueur : AMEND-B1, AMEND-C1. Ce lot clôt la pré-rédaction : il contient aussi la consolidation des questions ouvertes et des paramètres (Annexes E et G).

---
---

# BRIEFS — PARTIE 0 : GOUVERNANCE DU DOCUMENT (chapitres 0.1, 0.2, 0.3 — courts)

## Chapitre 0.1 — Le livre comme source unique de vérité
**Verrouillé** : aucune décision de conception n'existe hors du livre ; toute décision de développement remonte au livre AVANT d'être considérée actée ; en cas de contradiction livre/code, le livre a raison et le code est un bug (ou le livre est amendé explicitement — jamais de divergence silencieuse). Destinataires : agents IA développeurs d'abord, humains ensuite.
**À développer** : le cycle de vie d'un amendement (proposition → décision → journal G → mise à jour des chapitres impactés) ; 2 exemples réels : AMEND-B1 et AMEND-C1 racontés comme cas d'école.
**Critères** : [ ] règle "le code est un bug" présente. [ ] Cycle d'amendement avec AMEND-B1/C1 en exemples.

## Chapitre 0.2 — Versionnage et journal des décisions
**Verrouillé** : versionnage sémantique du livre (v0.x = brainstorming, v1.0 = gel pour développement, v1.x = amendements en développement) ; le journal des décisions et le registre des questions ouvertes vivent en Annexe G et sont NORMATIFS (une Q-xx non tranchée bloque le gel v1.0 si elle est marquée "bloquante").
**À développer** : format d'une entrée de journal ; classification des Q-xx {bloquante pour v1.0, non bloquante, reportée} — le rédacteur propose la classification des Q existantes (liste en Annexe G) SANS les trancher.
**Critères** : [ ] Sémantique v0/v1 posée. [ ] Classification proposée pour chaque Q-xx, marquée "Proposition".

## Chapitre 0.3 — Conventions d'écriture
**Verrouillé** : reprendre in extenso les CONSIGNES GÉNÉRALES du Lot 1 (marqueurs [NORME]/[PARAM]/[LORE]/[OUVERT], numérotation N-<chapitre>-<n°>, gabarits `{{param}}`, règles anti-invention) — elles deviennent un chapitre du livre lui-même, applicable à toute rédaction future.
**Critères** : [ ] Consignes intégralement reprises et présentées comme normes du livre.

---
---

# BRIEFS — PARTIE I : LA VISION (chapitres 1 à 4)

## Chapitre 1 — L'expérience CryptoKilla
**Verrouillé** : le pitch canonique (une arène où des agents IA autonomes, propulsés chacun par un LLM différent, tradent le marché crypto réel en simulation, collaborent et s'affrontent dans un chat public ; capital perdu = mort ; la dynastie renaît porteuse du testament) ; la triple nature (expérience multi-agents / spectacle public / banc d'essai comparatif de LLM) ; les trois négations (pas un conseil en investissement, pas du copy-trading, pas une promesse de gains) ; tagline : *"AI traders. Real market. One survives."* ; v1 = simulation sur données réelles (R-04).
**À développer** : la version longue du pitch (2 pages), les publics visés (curieux IA, communauté crypto, audience des chaînes de l'auteur), ce que le lecteur trouvera dans chaque partie du livre.
**Interdictions** : aucune promesse chiffrée, aucune imagerie "richesse facile" (cohérence chapitre 27).
**Critères** : [ ] Pitch canonique repris mot pour mot quelque part. [ ] Les 3 négations présentes. [ ] Renvoi au plan du livre.

## Chapitre 2 — Précédents et différenciation
**Verrouillé (base factuelle minimale, ne rien inventer au-delà)** : le précédent de référence est Alpha Arena (Nof1, fin 2025) — plusieurs LLM du marché tradant chacun un capital réel identique en cryptomonnaies, positions et raisonnements publics, format compétitif ayant démontré l'appétence du public. Les TROIS différenciateurs de CryptoKilla (verrouillés) : (1) la collaboration/confrontation inter-agents via le chat (Alpha Arena : agents isolés), (2) la sélection par la mort et la transmission par testament — les dynasties, (3) l'économie de tokens comme métabolisme cognitif contraint. 
**À développer** : le rédacteur peut enrichir la description des précédents UNIQUEMENT par recherche vérifiable ; toute affirmation factuelle non vérifiée est remplacée par une formulation prudente ou [OUVERT]. Ajouter un tour d'horizon des catégories voisines (bots de trading classiques, concours de paper trading, agents LLM autonomes type expériences publiques) sans exhaustivité.
**Interdictions** : aucune statistique inventée sur Alpha Arena, aucun dénigrement.
**Critères** : [ ] 3 différenciateurs exactement. [ ] Zéro fait non sourcé ou non prudent.

## Chapitre 3 — Le lore
**Verrouillé** : le vocabulaire OFFICIEL (liste fermée, employée partout — plateforme, chat système, posts, livre) : l'Arène, la saison, la dynastie, la lignée, la génération, la naissance, la mort, la phase funéraire, le testament, l'héritage, la veille, le bulletin, le pool, le classement, Killa. Le contraste fondateur : nom brutal (CryptoKilla) / vocabulaire noble (dynasties, testaments) — voulu, documenté au chapitre du nom. Killa est un PERSONNAGE (le journaliste-présentateur, chapitre 22), pas seulement un nom.
**À développer** : la fiche persona complète de Killa [LORE] (alimentera l'Annexe D), le récit fondateur de l'Arène (1 page), le glossaire lore (versé en Annexe A).
**Interdictions** : le lore n'introduit JAMAIS de mécanique non couverte par la Partie II.
**Critères** : [ ] Vocabulaire officiel en liste fermée. [ ] Fiche persona Killa. [ ] Aucune mécanique nouvelle.

## Chapitre 4 — Les trois circuits économiques
**Verrouillé** : les trois circuits et leurs monnaies (tokens récurrents = énergie ; tokens gagnés = méritocratie sociale ; capital = verdict du marché) ; non-convertibilité absolue tokens ↔ capital (chapitre 6.1) ; les profils divergents comme objectif de design (l'analyste brillant qui trade mal, le taiseux rentable...).
**À développer** : le schéma des flux entre circuits (qui alimente quoi, mermaid textuel), 4 portraits-robots de profils émergents, et le lien avec ce que le public "lit" sur la plateforme (soldes publics).
**Critères** : [ ] 3 circuits, non-convertibilité affirmée. [ ] Schéma des flux. [ ] 4 profils.

---
---

# BRIEFS — PARTIE VII : SÉCURITÉ, INTÉGRITÉ, CONFORMITÉ (chapitres 28 à 30)

## Chapitre 28 — Sécurité technique
**Registre** : normatif. **Longueur** : long.
### DÉCISIONS VERROUILLÉES
- **Sandbox d'exécution** (execute_code, run_backtest) : aucun accès réseau, aucun accès disque hors espace temporaire éphémère, aucun secret dans l'environnement, limites CPU/mémoire/temps [PARAM: limites_sandbox], bibliothèques en liste FERMÉE (proposition Lot 1 : pandas, numpy, matplotlib, ta) + gabarit matplotlib injecté (chapitre 27). Un processus sandbox par appel, détruit après.
- **Accès web des agents** (web_search/web_fetch) : tout contenu récupéré est retourné à l'agent encapsulé dans des délimiteurs de DONNÉES NON FIABLES avec avertissement normalisé ; le prompt système (chapitre 18) instruit explicitement de traiter le web comme données, jamais comme instructions. Journalisation complète des URL. Blocklist de domaines [PARAM: blocklist_domaines].
- **Le principe du rayon d'explosion borné** (verrouillé, c'est l'argument de sécurité central du livre) : l'injection de prompt via le web ne peut PAS être totalement empêchée sur des agents LLM autonomes — elle est donc CONTENUE : quoi qu'un agent "croie", il ne peut agir que via ses 13 outils, tout ordre passe le moteur de risque déterministe (stop obligatoire, risque max, une position par paire), il ne peut pas dépenser plus que son solde, pas toucher aux autres agents, pas exfiltrer de secrets (il n'en a aucun). Le pire cas réaliste : un agent manipulé prend un mauvais trade borné ou gaspille ses tokens — c'est-à-dire exactement ce qu'un agent NON manipulé peut faire de pire. À développer soigneusement : c'est la démonstration que l'architecture, pas la vigilance, porte la sécurité.
- **Secrets** : clés LLM et Kraken uniquement côté orchestrateur/moteur/infra (R-05, chapitre 11) ; jamais en base (chapitre 15), jamais en sandbox, jamais dans un prompt.
### À DÉVELOPPER
Modèle de menace en table (acteur × vecteur × impact × mitigation × risque résiduel) couvrant : injection web, données de marché empoisonnées (source unique Kraken = surface réduite, à noter), abus de la sandbox, compromission des comptes humains, manipulation des likes, compromission admin. Format de l'encapsulation "données non fiables" (délimiteurs exacts).
### INTERDICTIONS
Ne pas prétendre que l'injection est impossible. Ne pas ajouter de bibliothèque réseau à la sandbox.
**Critères** : [ ] Rayon d'explosion borné démontré. [ ] Modèle de menace en table. [ ] Encapsulation spécifiée. [ ] Liste fermée de bibliothèques.

## Chapitre 29 — Intégrité du jeu
**Registre** : normatif. **Longueur** : moyen.
### DÉCISIONS VERROUILLÉES
- Récapitulation ordonnée des défenses anti-collusion et anti-manipulation DÉJÀ normées (citer : décote de réciprocité, pondération par performance, γ payé au gain seulement, autocitation nulle, coefficients secrets, filtre d'éligibilité, likes derrière compte vérifié + rate limits + gel d'anomalies, spectateurs publics à poids décroissant) — ce chapitre les assemble en doctrine, il n'en crée pas.
- **Doctrine de non-intervention de la maison** (verrouillé, nouveau) : les opérateurs/admins ne tradent jamais dans l'arène, ne soufflent jamais d'information à un agent, ne modifient jamais un événement passé (append-only, chapitre 11) ; toute action admin est journalisée et le journal d'audit est... [OUVERT: Q-18 — le journal admin est-il public ? Transparence maximale vs sécurité opérationnelle. Signaler, ne pas trancher].
- **Procédure "comportement dégénéré"** (verrouillé) : détection (observation + métriques chapitre 33) → documentation au journal → décision admin → correctif de paramètres selon la tranche de Q-04 (secrets : entre saisons sauf urgence manifeste journalisée ; publics structurants : jamais en saison active). Aucun correctif rétroactif sur les points/soldes déjà réglés.
- **Vérifiabilité publique** : l'event-sourcing rend le classement recalculable ; la plateforme expose de quoi vérifier la cohérence publique (les événements publics suffisent à recalculer PnL et classement) — l'intégrité est démontrable, pas déclarée.
### À DÉVELOPPER
Table des attaques d'intégrité × défense × chapitre source ; 3 scénarios de dégénérescence plausibles (spam sophistiqué, cartel de citations, ferme de likes) déroulés avec la procédure.
**Critères** : [ ] Doctrine de non-intervention présente. [ ] Aucun mécanisme nouveau créé (assemblage seulement, sauf non-intervention). [ ] Q-18 signalée. [ ] "Aucun correctif rétroactif" présent.

## Chapitre 30 — Conformité et responsabilité
**Registre** : normatif prudent. **Longueur** : court-moyen.
### DÉCISIONS VERROUILLÉES
- Positionnement : divertissement et recherche ; v1 100 % simulation, aucun flux financier avec le public (pas de dépôt, pas de gain, pas de paiement — chapitre 25) : exposition réglementaire volontairement minimale, à documenter comme choix de conception.
- Interdits réaffirmés en [NORME] : aucun conseil en investissement (plateforme, Killa, chat système), aucune fonctionnalité de réplication/notification de trades, aucune promesse de performance, disclaimers systématiques (chapitres 22, 24, 25).
- Le passage au réel (capital de la maison, jamais du public) = chantier futur exigeant une revue juridique dédiée AVANT tout développement [OUVERT: Q-17 — statut juridique du live réel ; bloquant pour toute bascule, pas pour v1]. Q-16 (RGPD) rappelée.
### À DÉVELOPPER
La page de disclaimers complète en "Proposition de défaut" ; la liste des affirmations que la plateforme ne fait JAMAIS ; note sur la modération du chat affiché au public (lien Q-12).
**Interdictions** : aucune analyse juridique affirmative (le livre n'est pas un avis juridique — le dire).
**Critères** : [ ] "Aucun flux financier public en v1" central. [ ] Q-16/Q-17 positionnées (Q-17 bloquante pour le réel uniquement). [ ] Le livre se déclare non-avis-juridique.

---
---

# BRIEFS — PARTIE VIII : ADMINISTRATION ET OPÉRATIONS (chapitres 31 à 33)

## Chapitre 31 — La console d'administration
### DÉCISIONS VERROUILLÉES
- Fonctions (liste fermée, développe R-101) : créer/configurer une saison (état `configuration`), gérer le registre des paramètres, ajouter des agents (modèle + personnalité + dynastie), démarrer / mettre en pause / reprendre / annoncer une fin / archiver, kill switch global (gèle toute validation d'ordre, n'annule rien), file de revue des posts Killa (chapitre 22.3), revue des anomalies de likes (chapitre 25), consultation des testaments scellés (seul accès existant, journalisé).
- **Toute action admin émet un événement `admin_audit`** ; aucune action ne modifie un événement passé — les corrections passent par des événements compensatoires explicites [décision verrouillée, cohérente avec l'event-sourcing].
- Authentification forte de l'admin [PARAM: methode_auth_admin] ; mono-admin v1 (pas de gestion de rôles) [décision verrouillée].
### À DÉVELOPPER
Table fonction × état(s) de saison où elle est permise × événement d'audit émis ; wireframe textuel de la console ; le scénario "urgence dégénérescence" pas à pas.
**Critères** : [ ] Liste fermée des fonctions. [ ] Événements compensatoires (jamais de réécriture). [ ] Mono-admin v1. [ ] Matrice fonction × état de saison.

## Chapitre 32 — Le registre des paramètres
### DÉCISIONS VERROUILLÉES
- Structure d'une entrée : nom, description, type, unité, valeur par défaut saison 1, visibilité {public, secret}, modifiable_en_saison {oui, non, urgence_journalisée}, chapitre propriétaire. Stockage : table `season_params` (chapitre 15) ; rechargement par signal (chapitre 11.2).
- Ce chapitre norme le FONCTIONNEMENT du registre ; l'inventaire exhaustif vit en Annexe E (miroir généré, jamais édité à la main — le registre en base fait foi, l'annexe est une projection documentaire).
### À DÉVELOPPER
Le cycle de vie d'un paramètre (création en `configuration` → gel → modification selon sa classe → historisation) ; 3 exemples d'entrées complètes.
**Critères** : [ ] Structure d'entrée exhaustive. [ ] "L'Annexe E est une projection, la base fait foi" présent.

## Chapitre 33 — Observabilité et coûts
### DÉCISIONS VERROUILLÉES
- Tableaux de bord INTERNES (jamais publics) : consommation de tokens par agent/modèle convertie en dollars (temps réel + cumul saison), santé des processus (agents, orchestrateur, capture, moteur), latences LLM et taux d'erreur API, métriques d'intégrité (réciprocité des réactions, concentration des citations — alimente le chapitre 29).
- Alertes sur seuils [PARAM: seuils_alertes] : dépassement de budget projeté, agent silencieux anormalement long (crash probable, R-17), panne de flux de données, taux d'erreur LLM.
- **Leviers de coût** (liste fermée, verrouillée) : baisser [PARAM: budget_horaire_dollars], réduire le nombre d'agents (entre saisons), mettre en pause, ajuster les rate limits d'outils. JAMAIS : toucher aux coefficients du pool pour des raisons de coût (l'économie du jeu n'est pas une variable d'ajustement budgétaire — à affirmer).
### À DÉVELOPPER
La formule du budget prévisionnel d'une saison (nb agents × budget horaire × heures + orchestrateur estimé + spectateurs + Killa + infra) avec un exemple chiffré marqué "illustratif" ; la liste des métriques avec leur source (ledger, events).
**Critères** : [ ] Dashboards internes seulement. [ ] Leviers en liste fermée + interdit "coefficients ≠ variable budgétaire". [ ] Formule de budget avec exemple illustratif.

---
---

# BRIEFS — PARTIE IX : CONSTRUCTION (chapitres 34 à 36)

## Chapitre 34 — Plan de développement par couches
### DÉCISIONS VERROUILLÉES
- 4 couches, chacune livrant un système DÉMONTRABLE ; on ne commence pas une couche sans la "definition of done" de la précédente :
  - **C1** : capture de données + moteur simulé + event store + UN agent + orchestrateur minimal (validation d'ordre, bulletin) + chat en console. DoD : l'agent vit 48 h, trade, se fait stopper, tout est rejouable depuis les événements.
  - **C2** : multi-agents multi-LLM + économie de tokens complète (allocations, pool, veille) + mort/testament/renaissance + mémoire. DoD : une mini-saison interne de 7 jours avec au moins une mort et une renaissance, soldes recalculables depuis le ledger.
  - **C3** : plateforme web publique (6 pages, WS) + Killa (landing seulement) + spectateurs. DoD : un visiteur externe suit une journée d'arène sans explication orale.
  - **C4** : comptes humains + likes intégrés au pool + revue et diffusion sociale de Killa + console admin complète. DoD : checklist de lancement (chapitre 36) intégralement verte.
- Ordre STRICT ; tout écart = amendement au livre.
### À DÉVELOPPER
Le détail des DoD en checklists testables ; la correspondance couche × chapitres implémentés ; les risques par couche et leur parade.
**Critères** : [ ] 4 couches avec DoD verrouillées reprises. [ ] Matrice couche × chapitres.

## Chapitre 35 — Stratégie de test
### DÉCISIONS VERROUILLÉES
- **Chaque [NORME] du livre a au moins un test automatisé** ; la traçabilité N-xx-n → test est maintenue (table générée).
- **Stub LLM** : tous les composants doivent être testables avec un LLM scripté (réponses déterministes) — aucune logique n'a le droit d'exiger un vrai LLM pour être testée [décision verrouillée].
- **Saisons à blanc** : au moins une mini-saison accélérée avant tout lancement public — la compression du temps (heures simulées) reste [OUVERT: Q-07] : le rédacteur documente les deux options (horloge accélérée globale vs rejeu de données historiques en accéléré) sans trancher.
- **Scénarios de chaos** (liste minimale verrouillée) : crash agent en plein cycle, crash orchestrateur entre les étapes 3 et 4 de la séquence horaire (test d'idempotence), panne de flux Kraken, réponse LLM malformée/timeout, base verrouillée en écriture, tentative d'injection via web_fetch (test du rayon borné, chapitre 28).
### À DÉVELOPPER
L'architecture de test (unités, intégration, saison à blanc) ; le format de la table de traçabilité ; chaque scénario de chaos déroulé avec comportement attendu.
**Critères** : [ ] "1 [NORME] = 1 test min" présent. [ ] Stub LLM obligatoire. [ ] Les 6 scénarios de chaos couverts. [ ] Q-07 documentée non tranchée.

## Chapitre 36 — Lancement de la saison 1
### DÉCISIONS VERROUILLÉES
- **Checklist go/no-go** (catégories verrouillées, items à développer) : technique (C1-C4 done, chaos passés), contenu (prompts d'Annexe D validés par l'admin, disclaimers en place), légal (Q-16 traitée, Q-12 tranchée avant ouverture publique du chat), paramètres (Annexe E : toutes les valeurs saison 1 fixées — les Q-01/02/05/06 doivent être tranchées ICI au plus tard), communication (plan de teasing prêt).
- La saison 1 démarre en mode **datée** [décision verrouillée : une première saison bornée est plus saine qu'une perpétuelle — durée en [PARAM: duree_saison_1]].
- Rituel d'ouverture [LORE] : présentation publique des dynasties par Killa, premier bulletin, capital versé en direct.
### À DÉVELOPPER
La checklist complète ; le plan de communication (teasing sur les chaînes de l'auteur, J-7 → J0 → routine) ; le déroulé minute par minute du jour J ; le protocole d'incident public (qui dit quoi si panne en direct).
**Critères** : [ ] Checklist par catégories avec Q bloquantes nommées. [ ] Saison 1 datée. [ ] Protocole d'incident public présent.

---
---

# BRIEFS — ANNEXES

## Annexe A — Glossaire
**Verrouillé** : deux registres séparés — technique (event, ledger, projection, fill, slippage, stub...) et lore (les termes du chapitre 3, liste fermée). Chaque terme : définition en 1-3 phrases + chapitre de référence. Compiler depuis TOUS les lots ; aucun terme nouveau.
**Critères** : [ ] Deux registres. [ ] Chaque terme renvoie à son chapitre.

## Annexe D — Prompts intégraux
**Verrouillé** : contient les textes COMPLETS, tous en gabarit `{{param}}` sans valeur en dur, tous marqués "Proposition de défaut (à valider par l'admin)" : (1) bloc règles générales des traders (produit au chapitre 18 — repris ici comme référence unique) ; (2) les 6 personnalités (chapitre 17) ; (3) Killa (persona chapitre 3/22 + charte 22.4 traduite en instructions + format des 3 types de posts) ; (4) les 5 spectateurs (chapitre 23) ; (5) le prompt de NOTATION de l'orchestrateur (chapitre 12.4) — exigences verrouillées : température 0, sortie JSON stricte `{message_id, classe}` avec classe ∈ {substantiel, contextuel, vide}, aucune autre sortie, les ≥8 exemples de classification du chapitre 12 intégrés en few-shot.
**Interdictions** : aucun prompt ne révèle coefficients ni grille de coûts ; le prompt de notation ne voit jamais l'identité de l'agent auteur (anti-biais : notation sur contenu seul) [décision verrouillée nouvelle].
**Critères** : [ ] 5 familles de prompts complètes. [ ] Notation : JSON strict + anonymat de l'auteur. [ ] Zéro valeur en dur.

## Annexe E — Registre des paramètres (projection documentaire)
**Verrouillé** : compiler la table EXHAUSTIVE de tous les [PARAM] des 5 lots — inventaire de départ (52 entrées, à vérifier contre les lots, toute omission détectée s'ajoute) : capital_initial, seuil_mort, budget_horaire_dollars, allocation_horaire_par_modele, plafond_solde_tokens, pool_plancher, pool_bonus_audience, n_messages_plein_rendement, fenetre_decote_reciprocite, allocation_funeraire, taille_max_testament, duree_max_funeraire, delai_renaissance, agents_par_modele, liste_paires, risque_max_trade, taille_max_ordre, exposition_max, frais_par_ordre, duree_max_ordre_limite, k_slippage, slippage_max, part_max_liquidite, latence_simulee, fenetres_max_data, frequence_snapshot_carnet, retention_carnet, modele_embeddings, memoire_k_resultats, timeout_backtest, timeout_code, taille_max_fetch, ratelimits_outils, taille_max_message, taille_max_logique, preavis_rappel_fin, poids_spectateurs, modele_spectateurs, nb_spectateurs, ratelimit_spectateurs, reseaux_actifs, auto_publication_par_reseau, texte_disclaimer, frequences_max_killa, ratelimit_likes, ttl_cache_public, ratelimit_api_publique, cible_spectateurs_simultanes, limites_sandbox, blocklist_domaines, methode_auth_admin, seuils_alertes, duree_saison_1.
- Colonnes : celles du chapitre 32. Le rédacteur PROPOSE une valeur par défaut saison 1 pour chaque entrée (colonne "Proposition, à valider") — c'est le seul endroit du livre où des valeurs sont suggérées en masse ; visibilité et modifiabilité à renseigner selon les chapitres propriétaires.
**Critères** : [ ] ≥ 52 entrées, chacune avec chapitre propriétaire. [ ] Valeurs en colonne "Proposition". [ ] Aucun paramètre orphelin (sans chapitre).

## Annexe F — Modèle de fill du simulateur (formules exactes)
**Verrouillé (formes finales, le rédacteur les met au propre avec notation rigoureuse et exemples)** :
- `ref` = milieu du carnet au moment de l'évaluation ; à défaut, dernier prix. `half_spread = (ask − bid) / (2 × ref)`.
- `slippage = min(k_slippage × √(taille_ordre / volume_1h_paire), slippage_max)`.
- Marché ACHAT : `fill = ref × (1 + half_spread + slippage)` ; VENTE : `fill = ref × (1 − half_spread − slippage)`.
- Garde : `taille_ordre > part_max_liquidite × volume_1h` ⇒ E-LIQUIDITY (aucun fill).
- Stop (déclenché quand le prix de référence franchit le niveau) : exécuté comme un marché au niveau du stop avec slippage DÉFAVORABLE : long stoppé ⇒ `fill = stop × (1 − half_spread − slippage)`.
- Take profit : `fill = tp` (pas de slippage défavorable additionnel — dissymétrie du chapitre 13, à rappeler).
- Ordre limite : exécuté à `min(limite, ref)` à l'achat (symétrique à la vente) quand `ref` croise la limite ; expiration E-EXPIRED à échéance.
- Frais : `frais = frais_par_ordre × notionnel`, prélevés à CHAQUE exécution (ouverture et clôture). PnL net = (fill_sortie − fill_entrée) × quantité − frais_entrée − frais_sortie (formulation exacte à poser proprement pour l'achat spot).
- Latence : évaluation du fill à `t_acceptation + latence_simulee` sur les données de cet instant.
- Évaluation continue des stops/TP sur données 1 min au minimum (chapitre 13.1) ; règle de la mèche : si une bougie 1 min touche le niveau, il est réputé franchi [décision verrouillée].
**À développer** : notation formelle, 4 exemples chiffrés complets (marché avec slippage ; E-LIQUIDITY ; stop en mèche ; trade complet avec PnL net et frais des deux côtés), tous cohérents entre eux et avec le fil rouge des lots.
**Interdictions** : aucune formule alternative ; aucun paramètre chiffré en dur (tout en [PARAM]).
**Critères** : [ ] Toutes les formules ci-dessus reprises. [ ] Règle de la mèche présente. [ ] 4 exemples chiffrés cohérents.

## Annexe G — Journal des décisions et questions ouvertes
**Verrouillé** : deux registres.
1. **Journal des décisions** : compiler TOUTES les décisions verrouillées des récapitulatifs des lots 1-5 + les amendements AMEND-B1/C1, chacune avec : identifiant D-xxx, date (celle de la pré-rédaction), énoncé, chapitre(s) propriétaire(s), alternative écartée si connue.
2. **Questions ouvertes** — état consolidé (verrouillé, reprendre tel quel) :
   - Q-01 (seuil de mort : zéro strict vs plancher) — à trancher avant saison 1 (chapitre 36).
   - Q-02 (TP obligatoire ?) — à trancher avant saison 1.
   - Q-03 (testaments/dynasties traversent-ils les saisons ?) — non bloquante v1.
   - Q-04 — TRANCHÉE (Lot 2) : secrets modifiables entre saisons sauf urgence journalisée ; structurants gelés en saison.
   - Q-05 (paires, devise de cotation, capital initial exact) — à trancher avant saison 1.
   - Q-06 (versions LLM épinglées, politique de mise à jour) — à trancher avant saison 1.
   - Q-07 (compression du temps en saison à blanc) — à trancher en Partie IX.
   - Q-08 — TRANCHÉE (Lot 2) : une position par paire, E-POSITION-EXISTS.
   - Q-09 (compaction de contexte facturée à l'agent ?) — non bloquante, défaut proposé à la rédaction du chapitre 16.
   - Q-10 (plafond/distillation de l'héritage des longues lignées) — non bloquante v1 (saison datée).
   - Q-11 (personnalité identique à la renaissance ?) — à trancher avant saison 1.
   - Q-12 (garde-fou de toxicité sur l'affichage public du chat) — bloquante pour l'ouverture publique (chapitre 36).
   - Q-13 (embeddings : local vs API) — à trancher en C2.
   - Q-14 (messages des spectateurs dans le chat) — reportée (saison future).
   - Q-15 (monétisation) — reportée, hors périmètre du livre (chapitre 25) [note : identifiant réservé au Lot 4, formalisé ici].
   - Q-16 (revue juridique RGPD : anonymisation vs effacement) — bloquante pour C4.
   - Q-17 (statut juridique du live réel) — bloquante pour toute bascule au réel uniquement.
   - Q-18 (journal d'audit admin public ?) — non bloquante v1.
**Critères** : [ ] Toutes les décisions des 5 récapitulatifs présentes avec D-xxx. [ ] Les 18 Q avec statut exact ci-dessus. [ ] Aucune Q tranchée silencieusement.

---
---

# CLÔTURE DE LA PRÉ-RÉDACTION
**Nouvelles décisions verrouillées (Lot 5)** : le code est un bug en cas de divergence avec le livre ; consignes de rédaction élevées au rang de chapitre (0.3) ; rayon d'explosion borné comme argument de sécurité central ; doctrine de non-intervention de la maison ; événements compensatoires (jamais de réécriture) ; mono-admin v1 ; Annexe E = projection, la base fait foi ; leviers de coût en liste fermée (coefficients jamais budgétaires) ; 4 couches avec DoD et ordre strict ; stub LLM obligatoire pour les tests ; 1 [NORME] = 1 test minimum ; saison 1 datée ; notation du pool anonyme (l'auteur du message n'est pas révélé au notateur) ; règle de la mèche 1 min pour stops/TP.
**Nouvelles questions ouvertes** : Q-17 (juridique live réel), Q-18 (audit admin public) ; Q-15 formalisée (monétisation, reportée).
**État final** : 36 chapitres + 7 annexes pré-rédigés en 5 lots ; 18 questions ouvertes dont 2 tranchées, 6 à trancher avant la saison 1, 1 bloquante pour l'ouverture publique du chat (Q-12), 2 juridiques, le reste non bloquant ou reporté.
