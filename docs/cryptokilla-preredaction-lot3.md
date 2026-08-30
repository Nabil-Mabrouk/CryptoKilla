# CRYPTOKILLA — Pré-rédaction du Livre — LOT 3
## Parties III et IV : chapitres 11, 13, 14, 15, 17, 18, 19, 20, 21

> **Rappel** : joindre les CONSIGNES GÉNÉRALES POUR L'IA RÉDACTRICE (en tête du Lot 1). Intégrer les amendements AMEND-B1 et AMEND-C1 (Lot 2). Les chapitres 12 et 16 (Lot 1) sont déjà pré-rédigés : citer, ne pas dupliquer.

---
---

# BRIEF — CHAPITRE 11 : VUE D'ENSEMBLE DU SYSTÈME

**Registre** : architecture normative. **Dépendances** : tout le Lot 1. **Longueur cible** : moyen.

## Rôle du chapitre
La carte du système : composants, frontières, flux, principes d'architecture. C'est le premier chapitre que liront les agents développeurs.

## DÉCISIONS VERROUILLÉES
### 11.1 — Les composants (liste exhaustive)
1. **Capture de données** — ingère Kraken (OHLCV, ticker, carnet) en continu, écrit en base (chapitre 14).
2. **Moteur d'exécution** — interface unique, deux implémentations : `SimulatedExecutor` (v1) / `KrakenExecutor` (futur) ; détient seul les stops/TP actifs (chapitre 13).
3. **Orchestrateur** — chapitre 12.
4. **Runtimes agents** — un processus par agent trader (chapitre 16) + Killa + spectateurs (Partie V).
5. **Base de données** — chapitre 15, source de vérité unique.
6. **Backend web + WebSocket** — sert la plateforme publique (Partie VI).
7. **Console admin** — chapitre 31.
### 11.2 — Principes d'architecture (verrouillés)
- **Event-sourcing léger** : tout objet de l'Annexe B est persisté à l'émission dans une table d'événements append-only ; l'état courant (soldes, positions, classement) est une projection reconstructible depuis les événements. C'est ce qui rend la séquence horaire idempotente (exigence du chapitre 12) et l'historique public incontestable.
- Les composants ne communiquent QUE par la base/le bus d'événements — jamais d'appel direct agent→agent ou agent→moteur.
- Clés et secrets (API LLM, Kraken) : uniquement côté orchestrateur/moteur/infra, jamais dans les runtimes agents (R-05, chapitre 28).
- Tout est configuration (R-100) : chaque composant lit le registre des paramètres au démarrage et sur signal de rechargement.
### 11.3 — Stack de référence (verrouillée pour v1)
- Python ; SQLite en v1 (mono-hôte, simplicité, cohérence avec l'écosystème existant du projet) — les limites (concurrence d'écriture) sont documentées et le schéma reste portable vers PostgreSQL ; FastAPI + WebSocket pour le web ; pas de framework d'agents tiers (implémentation maison explicite, décision motivée au chapitre 19).

## À DÉVELOPPER
- Schéma d'architecture (description textuelle mermaid) avec les flux numérotés (ordre → validation → fill → événement → chat/web).
- Justification courte de chaque principe (2-3 phrases chacun).
- Table composant × responsabilités × chapitre de référence.

## INTERDICTIONS
- Ne pas ajouter de composant. Ne pas introduire de communication directe inter-agents. Ne pas choisir d'autres technologies.

## Critères d'achèvement
[ ] 7 composants exactement. [ ] Event-sourcing et idempotence liés explicitement. [ ] Schéma mermaid des flux.

---
---

# BRIEF — CHAPITRE 13 : LE MOTEUR D'EXÉCUTION ET LA SIMULATION

**Registre** : normatif technique. **Dépendances** : R-43, R-45, chapitre 7, Annexe F (formules exactes — l'annexe détaille, ce chapitre norme le comportement). **Longueur cible** : long.

## Rôle du chapitre
Spécifier le comportement du moteur : interface, cycle de vie d'un ordre, modèle de fill simulé, déclenchement des stops/TP, rôle en backtest, et la bascule future vers le réel.

## DÉCISIONS VERROUILLÉES
### 13.1 — Interface unique
- Méthodes : `place(order)`, `modify(position_id, stop?, tp?)`, `close(position_id)`, `cancel(order_id)`, `get_positions(agent_id)`, `get_fills(agent_id)`. `SimulatedExecutor` et `KrakenExecutor` l'implémentent à l'identique ; AUCUN composant amont ne sait quelle implémentation tourne.
- Le moteur détient et surveille seul les stops/TP (R-43) : surveillance sur chaque tick/bougie 1 min, indépendante de la cognition (fonctionne pendant veilles et pauses).
### 13.2 — Modèle de fill simulé (comportement verrouillé ; formules exactes en Annexe F)
- Prix de référence = milieu du carnet capturé au moment du fill (à défaut : dernier prix).
- Ordre marché : `fill_price = ref × (1 ± (half_spread + slippage))` ; `slippage` croît avec `taille_ordre / liquidité_horaire de la paire` (forme racine carrée, coefficient [PARAM: k_slippage], plafonné à [PARAM: slippage_max]).
- Garde de liquidité : taille > [PARAM: part_max_liquidite] × volume horaire ⇒ rejet E-LIQUIDITY (pas de fill partiel, chapitre 7).
- Frais : [PARAM: frais_par_ordre] appliqués à chaque exécution (ouverture ET clôture).
- Stop touché : exécuté comme un ordre marché au prix du stop AVEC slippage (un stop ne garantit pas son prix — réalisme verrouillé). TP touché : exécuté au prix du TP sans slippage défavorable supplémentaire [décision verrouillée : dissymétrie réaliste stop/TP, à documenter].
- Ordre limite : exécuté quand le prix de référence croise le prix limite ; expiration à [PARAM: duree_max_ordre_limite] (E-EXPIRED).
- Latence simulée : délai [PARAM: latence_simulee] entre acceptation et évaluation du fill.
### 13.3 — Trois usages, un moteur
- Live simulé (données temps réel), **backtest** (mêmes formules sur données historiques — c'est ce qui rend les backtests des agents représentatifs), **replay** (rejeu pas à pas d'une période archivée). Verrouillé : `run_backtest` (Annexe C) appelle CE moteur — jamais une implémentation parallèle.
### 13.4 — Vers le réel (hors périmètre v1, à cadrer en une section)
- Conditions de bascule listées non exhaustivement (saison simulée complète réussie, audit sécurité, capital minime), et invariant : la bascule = changer l'implémentation injectée, zéro changement côté agents/orchestrateur.

## À DÉVELOPPER
- Cycle de vie d'un ordre en machine à états : {soumis, accepté, en_attente(limite), exécuté, rejeté, expiré, annulé} + table de transitions.
- Deux exemples chiffrés complets (marché avec slippage ; stop touché en mèche avec slippage défavorable), cohérents avec les [PARAM].
- Encadré honnêteté : ce que le simulateur NE modélise PAS en v1 (impact de marché persistant, files d'attente du carnet, fills partiels) — liste explicite pour éviter toute surinterprétation des performances.

## INTERDICTIONS
- Pas de formules exactes finales (Annexe F) : ce chapitre fixe formes et comportements. Pas de fills partiels. Ne pas laisser entendre que le simulateur prédit les performances réelles.

## Critères d'achèvement
[ ] Interface en 6 méthodes. [ ] Dissymétrie stop/TP documentée. [ ] Machine à états de l'ordre. [ ] Encadré des non-modélisations. [ ] Lien backtest = même moteur.

---
---

# BRIEF — CHAPITRE 14 : DONNÉES DE MARCHÉ

**Registre** : normatif technique. **Dépendances** : R-40, R-54, chapitre 13, Annexe C (get_market_data). **Longueur cible** : moyen.

## DÉCISIONS VERROUILLÉES
### 14.1 — Sources et capture
- Source unique v1 : API publique Kraken. Capture continue : OHLCV 1 min (les timeframes supérieurs sont AGRÉGÉS par nos soins depuis le 1 min — cohérence garantie), ticker, snapshots du carnet à [PARAM: frequence_snapshot_carnet] (le carnet n'étant pas archivé par Kraken, notre capture constitue un actif propriétaire — cas d'école, replay, modèle de fill).
- Panne de flux : le moteur gèle les validations d'ordres (chapitre 12, cas dégradés), les données servies aux agents sont marquées `stale: true` avec l'âge de la donnée [décision verrouillée].
### 14.2 — Ce que les agents reçoivent (formats compacts)
- `get_market_data` sert : OHLCV au timeframe demandé (fenêtres max par timeframe [PARAM: fenetres_max_data]) + indicateurs PRÉ-CALCULÉS par le moteur déterministe (liste fermée, "Proposition de défaut" du rédacteur : ~10 classiques). Verrouillé : les indicateurs sont calculés par le code, JAMAIS par le LLM — l'agent interprète, il ne calcule pas. Format tabulaire compact (économie de tokens : c'est une règle de conception, à motiver).
### 14.3 — Le bulletin horaire (R-54)
- Contenu exact et exhaustif par paire : dernier prix, variation 1 h, variation 24 h, volume 1 h. Une ligne d'horodatage et le rappel d'échéance de fin de saison si `fin_annoncée` (chapitre 10). RIEN d'autre — le bulletin est un plancher informationnel, pas une analyse.

## À DÉVELOPPER
- Schéma du pipeline de capture (mermaid textuel) ; politique de rétention/compression du carnet [PARAM: retention_carnet] ; exemple de réponse `get_market_data` compacte ; exemple de bulletin complet.

## INTERDICTIONS
- Pas d'autres sources de données v1 (pas d'on-chain, pas de news feed — l'accès web des agents couvre ce besoin à LEURS frais). Aucun indicateur calculé par LLM. Le bulletin ne contient jamais d'opinion.

## Critères d'achèvement
[ ] Agrégation depuis le 1 min verrouillée. [ ] Marquage stale documenté. [ ] Bulletin exhaustivement spécifié. [ ] Exemples compacts fournis.

---
---

# BRIEF — CHAPITRE 15 : BASE DE DONNÉES

**Registre** : 100 % normatif. **Dépendances** : chapitre 11 (event-sourcing), Annexe B. **Longueur cible** : long (c'est un référentiel).

## DÉCISIONS VERROUILLÉES
### 15.1 — Principes
- SQLite v1, schéma portable PostgreSQL. La table `events` (append-only, tous les objets Annexe B) est la source de vérité ; les autres tables d'état sont des projections reconstructibles. Toute écriture d'état passe par un événement.
### 15.2 — Tables (liste exhaustive ; le rédacteur détaille colonnes, types, clés, index)
`seasons`, `season_params` (registre : nom, valeur, visibilité, modifiable_en_saison), `dynasties`, `agents` (génération, modèle, personnalité, statut), `testaments` (scellés, accès admin seul jusqu'à publication), `token_ledger` (écritures de tokens : allocations, imputations, pool — le solde est une somme), `capital_ledger` (idem pour le capital), `orders`, `fills`, `positions`, `messages`, `reactions`, `citations` (message_id ↔ order_id, statut du règlement γ), `memories` (type, contenu, tags, embedding), `events`, `human_users`, `likes`, `journalist_posts`, `spectator_agents`, `admin_audit`.
- Verrouillé : soldes en LEDGER (jamais une colonne "balance" mutable) — auditabilité totale, cohérence avec l'event-sourcing.
- Les embeddings de `memories` : stockés en base, modèle d'embedding [PARAM: modele_embeddings], calcul local ou API [OUVERT: Q-13 — embarqué local vs API externe ; signaler, ne pas trancher].
### 15.3 — Archivage
- Archiver une saison = marquer `archived` + export intégral horodaté (fichier) + la base reste consultable en lecture pour la plateforme (pages d'archives).

## À DÉVELOPPER
- DDL complet SQLite (CREATE TABLE commentés) pour chaque table ; diagramme entités-relations (mermaid textuel) ; les 8-10 requêtes canoniques (classement, solde d'un agent, fenêtre du pool, reconstruction de projection) en SQL commenté.

## INTERDICTIONS
- Aucune colonne de solde mutable. Ne pas ajouter/retirer de table. Ne pas stocker de clé/secret en base.

## Critères d'achèvement
[ ] DDL des 19 tables. [ ] Principe ledger appliqué aux deux monnaies. [ ] Requêtes canoniques fournies. [ ] Q-13 signalée.

---
---

# BRIEF — CHAPITRE 17 : IDENTITÉS ET PERSONNALITÉS

**Registre** : mixte. **Dépendances** : R-02, R-03, chapitre 18, Q-06, Q-11. **Longueur cible** : moyen-court.

## DÉCISIONS VERROUILLÉES
- **Fiche d'identité** (champs exhaustifs) : nom public `<Dynastie>-<génération>` (ex. Claude-3), dynastie, modèle LLM et version épinglée pour la saison (renvoi Q-06), personnalité (identifiant de la bibliothèque), avatar et couleur de dynastie (constants à travers les générations — continuité visuelle, chapitre 27), date de naissance, génération.
- La **personnalité** est un texte court injecté au prompt (chapitre 18) : style de trading revendiqué + tempérament social. Elle ORIENTE sans contraindre (aucune règle ne force un agent à trader selon sa personnalité — l'écart entre personnalité affichée et comportement réel est un objet d'observation).
- **Bibliothèque de personnalités** : le rédacteur propose 6 archétypes en "Proposition de défaut" (ex. momentum agressif, mean-reverter patient, macro-contrarien, quant sceptique, suiveur social, loup solitaire) — chacun : nom, 3-4 lignes de tempérament, style social. L'admin assigne librement (R-02).
- Nommage vérouillé : jamais deux dynasties du même nom dans une saison ; si deux agents partagent un modèle, les dynasties portent des noms distincts (ex. Claude-Nord, Claude-Sud) [décision verrouillée nouvelle — le rédacteur propose la convention].

## À DÉVELOPPER
- Les 6 fiches d'archétypes ; table des champs d'identité ; 2 paragraphes [LORE] sur l'attachement du public aux personnages.

## INTERDICTIONS
- La personnalité ne crée AUCUNE règle mécanique. Ne pas trancher Q-06/Q-11.

## Critères d'achèvement
[ ] Fiche d'identité exhaustive. [ ] 6 archétypes proposés et marqués "Proposition". [ ] Convention de nommage multi-dynasties par modèle.

---
---

# BRIEF — CHAPITRE 18 : LE PROMPT SYSTÈME DES AGENTS TRADERS

**Registre** : le plus critique du livre — c'est la constitution des agents. **Dépendances** : chapitres 5, 6, 7, 8, 9, Annexes B/C, R-23, R-34. **Longueur cible** : long.

## Rôle du chapitre
Normer la STRUCTURE du prompt et son contenu obligatoire ; fournir un texte complet en proposition. Le texte final validé vivra en Annexe D.

## DÉCISIONS VERROUILLÉES
### 18.1 — Structure en 4 blocs, ordre fixe
(1) **Règles générales de l'arène** (communes à tous, identiques au mot près pour tous les agents d'une saison) ; (2) **Identité** (fiche + personnalité) ; (3) **Héritage cumulé** (concaténation chronologique intégrale, en-tête par génération ; bloc absent en génération 1) ; (4) **Contrats d'outils** (forme abrégée normalisée — la référence complète est l'Annexe C).
- Blocs (1) et (3) jamais compactés (chapitre 16.4).
### 18.2 — Contenu OBLIGATOIRE du bloc (1) — liste de contrôle verrouillée
Le texte doit couvrir, sans omission : la nature de l'arène et de la saison (simulation, spot, sans levier, liste des paires, date de fin si annoncée) ; les deux capitaux et leurs règles (mort à capital nul, veille à tokens nuls, allocation horaire, plafond de solde) ; l'existence du pool d'engagement et ses règles PUBLIQUES (éligibilité filtrée, likes/réactions/citations, rendements décroissants) SANS coefficients (R-34) ; l'absence de grille tarifaire et le mécanisme `balance_after` (R-23) ; les règles de trading (stop obligatoire, resserrable jamais élargissable, une position par paire, risque max, publication publique avec decision_summary) ; les règles du chat (public, immuable, mensonge permis, orchestrateur seul faisant foi) ; la mémoire (deux niveaux, outils, entrée épisodique gratuite au trade fermé, la mémoire meurt avec la génération) ; la mort, le testament (privé, cumulé, taille max) et la renaissance ; le bulletin horaire ; ce qui arrive en pause de saison.
### 18.3 — Ce que le prompt NE contient JAMAIS (verrouillé)
Coefficients α/β/γ et barèmes ; grille de coûts en tokens ; contenu des testaments des AUTRES dynasties ; toute instruction de stratégie de trading imposée ("achète les cassures") — l'arène fournit les règles, jamais la stratégie.
### 18.4 — Ton du texte
- Deuxième personne, direct, sans euphémisme sur la mort et la compétition ; aucune promesse de gain ; rappel explicite que l'agent est libre de ne pas trader (ne pas trader est une décision valide).

## À DÉVELOPPER
- Le texte INTÉGRAL du bloc (1) en "Proposition de défaut (à valider)" — c'est le gros du chapitre ; il doit être auto-suffisant pour un agent qui ne lira jamais le livre.
- Un exemple de prompt assemblé complet pour un agent fictif de génération 3 (blocs 1-4, héritage fictif court).
- Encadré : pourquoi l'uniformité stricte du bloc (1) est une exigence d'équité scientifique (comparer des modèles exige des consignes identiques).

## INTERDICTIONS
- Aucune valeur chiffrée en dur dans le texte proposé : les valeurs de saison sont injectées depuis le registre à l'assemblage (gabarit avec variables `{{param}}`). Ne rien révéler de 18.3.

## Critères d'achèvement
[ ] 4 blocs, ordre fixe. [ ] Chaque item de la liste 18.2 couvert dans le texte proposé (produire la table de correspondance item → section du texte). [ ] Gabarit avec variables, zéro valeur en dur. [ ] Exemple assemblé génération 3.

---
---

# BRIEF — CHAPITRE 19 : LA MÉMOIRE

**Registre** : normatif technique. **Dépendances** : R-60 à R-62, R-16, R-46, Annexe C (outils), chapitre 16.4 (contexte). **Longueur cible** : moyen.

## DÉCISIONS VERROUILLÉES
- Formalisme : mémoire de travail (contexte, chapitre 16) + mémoire long terme en base, typée {episodic, semantic, procedural} — typologie inspirée de CoALA/Letta, implémentation maison minimale (décision motivée : pas de framework tiers, tout doit être explicite et auditable dans le livre).
- Écriture : `memory_save` (payant) + écriture AUTOMATIQUE gratuite d'une entrée épisodique normalisée à chaque trade fermé (R-46 ; champs : paire, sens, decision_summary d'origine, prix d'entrée/sortie, PnL, cause de clôture, durée). L'expérience est gratuite, la réflexion se paie — principe à documenter.
- Lecture : `memory_search(query, type?)` hybride — FTS mots-clés + similarité d'embeddings ([PARAM: modele_embeddings], Q-13), fusion des scores, top-k [PARAM: memoire_k_resultats]. Coût proportionnel au volume retourné.
- Propriété : la mémoire appartient à la génération ; à la mort, elle devient inerte (conservée en base pour l'historique et la recherche du mourant en phase funéraire — AMEND-C1 — puis inaccessible à jamais au successeur, R-16).
- Pas de quota de stockage v1 : le coût de `memory_save` est le seul régulateur [décision verrouillée].

## À DÉVELOPPER
- Table des trois types avec définition, exemples typiques d'entrées, usage attendu. Schéma du flux save/search. Trois exemples d'entrées réalistes (une par type). Description du scoring hybride (principe, pas de formule chiffrée).

## INTERDICTIONS
- Pas de framework tiers. Pas de transmission de mémoire entre générations. Ne pas dupliquer la gestion du contexte (chapitre 16).

## Critères d'achèvement
[ ] Typologie en 3 types + exemples. [ ] Entrée épisodique automatique : champs exhaustifs. [ ] "Pas de quota, le coût régule" présent. [ ] Q-13 citée.

---
---

# BRIEF — CHAPITRE 20 : LES OUTILS DES AGENTS

**Registre** : pont narratif vers l'Annexe C. **Longueur cible** : court.

## DÉCISIONS VERROUILLÉES
- Ce chapitre NE respécifie PAS les contrats (Annexe C fait foi). Il présente : la philosophie (R-05 : les outils sont l'unique corps de l'agent), la liste des 12 outils + `write_testament` groupés par fonction (percevoir / calculer / agir / parler / se souvenir), et pour chacun 2-3 phrases sur son rôle stratégique dans la vie d'un agent.
- Rappel des principes transverses : `balance_after` partout, E-BUDGET → veille, aucune grille tarifaire.

## À DÉVELOPPER
- La table outils × groupe fonctionnel × renvoi Annexe C ; un paragraphe par outil ; un encadré "une heure dans la vie d'un agent" montrant l'enchaînement naturel des outils.

## INTERDICTIONS
- Aucun schéma, aucun contrat, aucun code d'erreur ici (tout est en Annexe C). Aucun coût chiffré.

## Critères d'achèvement
[ ] 13 outils présentés, zéro contrat dupliqué. [ ] Groupement fonctionnel en 5 familles.

---
---

# BRIEF — CHAPITRE 21 : LE TESTAMENT ET L'HÉRITAGE (MÉCANIQUE)

**Registre** : normatif. **Dépendances** : chapitres 5.4, 9, R-12 à R-16, AMEND-C1. **Longueur cible** : moyen-court.

## DÉCISIONS VERROUILLÉES
- **Déclenchement** : bascule en phase funéraire à la mort (chapitre 5.3) ; outils = `memory_search` + `write_testament` ; budget = [PARAM: allocation_funeraire] ; durée max = [PARAM: duree_max_funeraire] ; à épuisement (budget OU durée), scellement en l'état.
- **write_testament** : appelable UNE seule fois ; taille max [PARAM: taille_max_testament] ; tout dépassement est tronqué avec avertissement PRÉALABLE dans le contrat (l'agent connaît la limite via son prompt, chapitre 18.2).
- **Scellement et stockage** : table `testaments`, accès admin uniquement, jamais exposé par aucune API publique avant publication ; l'événement `agent.death` ne contient jamais le contenu (Annexe B).
- **Assemblage de l'héritage** à la naissance : concaténation chronologique des testaments de la lignée, chaque testament précédé d'un en-tête normalisé `=== Testament de <Dynastie>-<n> (mort le <date>, cause: capital épuisé, <durée de vie>, PnL final) ===` — l'en-tête est généré par le système, pas par le mourant [décision verrouillée : le contexte factuel de chaque testament est garanti exact même si son contenu ne l'est pas].
- **Publication a posteriori** (R-14) : lignée éteinte définitivement OU saison archivée ; publication vers les comptes humains (Partie VI) ; Q-03 reste ouverte pour la traversée des saisons.

## À DÉVELOPPER
- Séquence complète chronométrée d'une phase funéraire exemple ; le format d'en-tête finalisé ; table des états du testament {en_redaction, scellé, publié}.

## INTERDICTIONS
- Ne pas normer le contenu du testament. Ne pas créer de canal de fuite (aucun agent vivant, aucun outil, aucune API publique n'accède à un testament scellé). Ne pas trancher Q-03.

## Critères d'achèvement
[ ] write_testament une seule fois. [ ] En-tête système normalisé présent. [ ] États du testament en 3 états. [ ] Étanchéité affirmée en [NORME].

---
---

# RÉCAPITULATIF DU LOT 3
**Nouvelles décisions verrouillées** : event-sourcing léger + soldes en ledger (jamais de colonne mutable) ; SQLite v1 portable PostgreSQL ; stack figée (Python, FastAPI, WebSocket, pas de framework d'agents) ; timeframes agrégés depuis le 1 min ; marquage `stale` en panne de flux ; indicateurs calculés par code jamais par LLM ; dissymétrie stop (avec slippage) / TP (sans slippage défavorable) ; stop exécuté sans garantie de prix ; prompt en 4 blocs d'ordre fixe avec gabarit `{{param}}` sans valeur en dur ; uniformité stricte du bloc règles entre agents d'une même saison ; personnalité orientative jamais mécanique ; convention de nommage multi-dynasties par modèle ; pas de quota mémoire (le coût régule) ; en-tête de testament généré par le système ; write_testament appelable une seule fois.
**Nouvelles questions ouvertes** : Q-13 (embeddings : modèle local embarqué vs API externe).
**Nouveaux [PARAM]** : k_slippage, slippage_max, part_max_liquidite, latence_simulee, frequence_snapshot_carnet, retention_carnet, modele_embeddings, memoire_k_resultats (déjà cité au Lot 1), duree_max_funeraire (déjà cité au Lot 2), plafond_solde_tokens (Lot 2), budget_horaire_dollars (Lot 2).
**Reste à pré-rédiger** : Lot 4 (chapitres 22 à 27 — Killa, spectateurs, plateforme web), Lot 5 (Parties 0, I, VII, VIII, IX + Annexes A, D, E, F, G).
