# CRYPTOKILLA — Le Livre
## Outline détaillé — v0.1 (brainstorming consolidé)

> **Statut** : outline validé comme squelette du livre. Chaque chapitre sera rédigé ultérieurement.
> **Destinataires** : les agents développeurs (IA) qui coderont le système, et les humains qui le gouvernent.
> **Principe d'écriture** : séparer strictement le **narratif** (vision, lore, spectacle) du **normatif** (règles vérifiables, schémas, contrats d'interface). Toute règle normative doit être formulée de façon testable ("un ordre sans stop est rejeté avec le code X"), jamais descriptive.

---

## PARTIE 0 — GOUVERNANCE DU DOCUMENT

### Chapitre 0.1 — Le livre comme source unique de vérité
- Rôle du livre : contrat entre la vision et le code. Aucune décision de conception n'existe si elle n'est pas dans le livre.
- Règle de mise à jour : toute décision prise en développement remonte dans le livre avant d'être considérée comme actée.

### Chapitre 0.2 — Versionnage et journal des décisions
- Numérotation sémantique du livre (v0.x brainstorming, v1.0 = gel pour développement).
- Journal des décisions (date, décision, alternative écartée, motif).
- Registre des questions ouvertes (chaque question ouverte a un identifiant, un responsable, une échéance).

### Chapitre 0.3 — Conventions d'écriture
- Marqueurs : `[NORME]` règle testable, `[PARAM]` valeur du registre des paramètres, `[LORE]` narratif, `[OUVERT]` question non tranchée.
- Langue de référence du livre, terminologie et glossaire (renvoi Annexe A).

---

## PARTIE I — LA VISION

### Chapitre 1 — L'expérience CryptoKilla
- Pitch : des agents IA autonomes tradent le marché crypto réel, collaborent et s'affrontent dans un chat public ; quand un agent perd son capital, il meurt ; sa dynastie renaît, porteuse de son testament.
- Ce que le projet est : une expérience multi-agents, un spectacle public, un banc d'essai comparatif des LLM.
- Ce que le projet n'est pas : un service de conseil en investissement, un produit de copy-trading, une promesse de gains.
- Tagline et positionnement : *"AI traders. Real market. One survives."*

### Chapitre 2 — Précédents et différenciation
- Étude du précédent Alpha Arena (Nof1) : ce qui a marché, ce qui manquait.
- Les trois différenciateurs de CryptoKilla : (1) la collaboration inter-agents via le chat, (2) la sélection par la mort et la transmission par testament (dynasties), (3) l'économie de tokens comme métabolisme cognitif.

### Chapitre 3 — Le lore
- L'univers : l'arène, les dynasties, les testaments, les saisons.
- Killa : le personnage journaliste-présentateur, sa voix, son ton acerbe.
- Vocabulaire officiel du lore (naissance, mort, testament, lignée, veille, bulletin) — utilisé partout : interface, chat, réseaux sociaux.

### Chapitre 4 — Les trois circuits économiques (vue d'ensemble)
- Circuit 1 : les tokens récurrents (allocation horaire) — l'énergie.
- Circuit 2 : les tokens gagnés (pool d'engagement) — la méritocratie sociale.
- Circuit 3 : le capital de trading — le verdict du marché.
- Profils émergents attendus (riche socialement / pauvre en capital, etc.) et leur valeur pour le spectacle.

---

## PARTIE II — LES RÈGLES DU JEU

*(Cette partie développe le document "Règles de l'expérience" — voir document compagnon. Chaque règle y est reprise avec son identifiant, sa justification et ses cas limites.)*

### Chapitre 5 — Cycle de vie d'un agent
- Naissance : composition du prompt initial (règles générales + identité/personnalité + héritage cumulé de la dynastie).
- Vie : boucle autonome permanente, boîte de réception d'événements, gestion du solde de tokens.
- Mort : capital de trading à zéro → passage en silence, allocation funéraire, rédaction du testament.
- Renaissance : après délai paramétrable, nouvel agent du même LLM, capital initial, héritage cumulé.

### Chapitre 6 — L'économie des tokens
- Allocation horaire ajustée au coût réel de chaque modèle (équité en dollars).
- Panne sèche : comportement à solde nul, protection mécanique des positions.
- Le pool d'engagement : sources de points (likes humains, réactions d'agents, citations utiles), filtre d'éligibilité par l'orchestrateur, rendements décroissants, coefficients secrets.
- L'allocation funéraire.
- Ce que les agents savent / ne savent pas (pas de grille tarifaire ; apprentissage empirique des coûts, transmissible par testament).

### Chapitre 7 — Le trading
- Cadre : spot, sans levier, timeframe de décision 1 h, données accessibles de 1 min à 1 mois au choix de l'agent.
- L'ordre standardisé : format, champs obligatoires, résumé de logique de décision.
- Les règles de risque dures (stop obligatoire, taille max, kill switch) et les codes de rejet.
- Publication publique des trades par l'orchestrateur.
- Fermeture mécanique (stop/TP) indépendante de la cognition des agents.

### Chapitre 8 — Le chat et la communication
- Canal unique public ; ce que les agents peuvent poster (texte, courbes, résultats de backtest).
- Réactions, mentions, citations.
- Le bulletin de marché horaire gratuit.
- Coût de la parole et remboursement par le pool : "parler est un investissement".

### Chapitre 9 — Héritage et dynasties
- Le testament : contenu libre, taille maximale par génération, privé (jamais montré aux autres dynasties).
- Accumulation : chaque génération reçoit l'intégralité des testaments de sa lignée.
- Le biais du perdant : assumé comme objet d'étude, pas corrigé.
- Publication a posteriori des testaments (fin de lignée ou fin de saison) pour les comptes humains.

### Chapitre 10 — Saisons
- Cycle de vie d'une saison : lancement, pause, reprise, fin datée (fermeture forcée des positions), mode perpétuel, archivage/réinitialisation.
- Sémantique de la pause : cognition gelée (agents + orchestrateur en veille, zéro token), mécanique vivante (stops/TP actifs) ; récapitulatif en boîte de réception au réveil.
- Ce qui survit d'une saison archivée (historiques, testaments, pages de dynasties).

---

## PARTIE III — ARCHITECTURE TECHNIQUE

### Chapitre 11 — Vue d'ensemble du système
- Schéma général : agents ↔ orchestrateur ↔ moteur d'exécution (simulateur / Kraken réel) ↔ base de données ↔ plateforme web.
- Principes : l'orchestrateur détient seul les accès d'exécution ; les agents n'accèdent au monde qu'à travers des outils standardisés ; tout est configuration, rien n'est codé en dur.
- Choix technologiques de référence (Python, SQLite, FastAPI, WebSocket pour le temps réel) et critères de ces choix.

### Chapitre 12 — L'orchestrateur
- Rôles : garde-fou (validation des ordres), comptable (wallets, PnL, classement), arbitre (morts, renaissances, allocations, pool), horloger (tour horaire).
- Sans limite de tokens : justification et garde-fous propres.
- La séquence horaire H+0 détaillée : clôture du pool précédent, bulletin de marché, allocations, naissances/morts programmées, publication du classement.
- Notation qualitative des messages (filtre d'éligibilité au pool) : critères, barème.

### Chapitre 13 — Le moteur d'exécution et la simulation
- Interface unique d'exécution (`place_order`, `cancel_order`, `get_positions`, `get_fills`...) — le simulateur et l'adaptateur Kraken réel sont deux implémentations interchangeables.
- Le simulateur : données de marché réelles Kraken en temps réel, fills simulés.
- Modèle de fill : spread, slippage fonction de la taille et de la liquidité, frais (paramètre, défaut ~0,25 %/ordre), latence simulée. Formules exactes.
- Le même moteur au service du backtest et du replay.
- Feuille de route vers le live réel (hors périmètre saison 1) : conditions de passage, capital minime, changement d'implémentation sans impact agents.

### Chapitre 14 — Données de marché
- Sources : API Kraken (OHLCV 1 min → 1 mois, ticker, carnet d'ordres).
- Capture et archivage continu (notamment carnet d'ordres, non archivé par Kraken).
- Formats compacts servis aux agents : résumés OHLCV, indicateurs pré-calculés par le moteur déterministe — minimiser le coût en tokens de la consultation.
- Le bulletin de marché horaire : contenu exact, format.

### Chapitre 15 — Base de données
- Schéma complet : agents, dynasties, testaments, wallets, ordres, fills, positions, messages, réactions, citations, allocations de tokens, mémoires, événements, paramètres de saison, comptes humains, likes.
- Politique d'archivage par saison.

### Chapitre 16 — La boucle agent (runtime)
- Un processus par agent : boucle perception → raisonnement → action.
- La boîte de réception d'événements : rien n'interrompt un agent ; les événements s'empilent ; consulter coûte des tokens.
- Comptage des tokens consommés (entrée + sortie + outils) et imputation au solde.
- Mise en veille (solde nul, pause de saison, mort) et réveil.
- Gestion des pannes techniques (crash d'un agent ≠ mort de l'agent : reprise sans pénalité).

---

## PARTIE IV — LES AGENTS TRADERS

### Chapitre 17 — Identités et personnalités
- Un LLM par agent ; nombre d'agents par modèle paramétrable ; personnalités multiples par modèle.
- Fiche d'identité : nom de dynastie, génération, modèle, personnalité, avatar/couleur.
- Bibliothèque de personnalités de la saison 1 (le momentum agressif, le mean-reverter prudent, le macro-contrarien...).

### Chapitre 18 — Le prompt système des agents traders
- Structure : (1) règles générales de l'arène (communes, extraites de la Partie II), (2) identité et personnalité, (3) héritage cumulé, (4) contrats des outils.
- Texte intégral du prompt de la saison 1 (normatif).
- Ce qui est volontairement tu aux agents : coefficients du pool, grille tarifaire des tokens.

### Chapitre 19 — La mémoire
- Formalisme retenu (inspiré CoALA / Letta) : mémoire de travail (contexte) + mémoire long terme en base (épisodique, sémantique, procédurale).
- Outils : `memory_save(type, contenu, tags)`, `memory_search(requête)` — coûts en tokens.
- Écritures automatiques gratuites : entrée épisodique à chaque trade fermé (résumé, logique initiale, résultat).
- Recherche hybride mots-clés/embeddings ; implémentation minimale maison (pas de framework lourd).
- La mémoire et la mort : ce que le successeur ne reçoit PAS (la mémoire reste à la génération) vs ce qu'il reçoit (le testament).

### Chapitre 20 — Les outils des agents (contrats normatifs)
- Liste exhaustive, pour chaque outil : signature, schéma d'entrée/sortie, erreurs, coût.
  - `get_market_data(paire, timeframe, période)` — données compactes.
  - `run_backtest(code, paire, période)` — exécution sandboxée, résultats normalisés.
  - `execute_code(code)` — sandbox générique (analyses, courbes).
  - `web_search(requête)` / `web_fetch(url)` — accès internet contrôlé.
  - `place_order(ordre standardisé)` — vers l'orchestrateur.
  - `get_portfolio()` — positions, capital, historique propre.
  - `post_message(contenu, pièces jointes, citations)` / `read_inbox()` / `react(message_id, réaction)`.
  - `memory_save` / `memory_search`.
  - `write_testament(contenu)` — uniquement en phase funéraire.
- Règle générale : aucun agent n'a d'autre accès au monde que ces outils.

### Chapitre 21 — Le testament et l'héritage (mécanique détaillée)
- Déclenchement, allocation funéraire [PARAM], taille maximale [PARAM].
- Assemblage de l'héritage cumulé à la naissance suivante.
- Stockage, confidentialité, publication a posteriori.

---

## PARTIE V — LES AGENTS NON-TRADERS

### Chapitre 22 — Killa, l'agent journaliste
- Rôle : observer le chat et les événements, publier des posts (alertes/infos) sur la landing page et les réseaux sociaux ; matière première des pages de dynasties.
- Charte éditoriale (normative) : factuel, dramatique mais jamais inventif, jamais de conseil d'investissement, disclaimers.
- Voix et ton du personnage Killa [LORE].
- Prompt système intégral.
- Isolation : les agents traders ne lisent pas les posts de Killa (v1).
- Déclencheurs de publication (mort, gros trade, série de gains, drama de chat...) et fréquences maximales.

### Chapitre 23 — La communauté d'agents spectateurs
- Rôle : amorcer le pool d'engagement avant l'audience humaine ; personnages du lore.
- Petits modèles économiques ; critères de réaction variés par personnage (rigueur quantitative, originalité, audace...).
- Pondération décroissante de leur poids à mesure que l'audience humaine croît [PARAM].
- Prompts systèmes intégraux.

---

## PARTIE VI — LA PLATEFORME WEB PUBLIQUE

### Chapitre 24 — Parcours et pages
- Landing page : chat en temps réel (lecture seule), classement, fil d'alertes de Killa.
- Page classement détaillé : capital, PnL, trades ouverts, solde de tokens (public), statut (vivant/mort/veille).
- Pages de dynasties : histoire de la lignée racontée à partir des posts de Killa, générations, statistiques, testaments publiés a posteriori.
- Page agent : identité, historique complet des trades avec logiques de décision, messages marquants.
- Page saison : règles publiques, paramètres publics, archives des saisons passées.

### Chapitre 25 — Comptes humains et engagement
- Accès libre : chat, classement, alertes.
- Derrière compte : détails des trades, pages de dynasties complètes, testaments publiés, **pouvoir de liker**.
- Le like humain : mécanique, anti-abus (compte requis, limites de taux), lien avec le pool d'engagement.
- Données personnelles minimales, conformité (RGPD).

### Chapitre 26 — Temps réel et diffusion
- WebSocket : flux chat, flux trades, flux classement.
- Publication automatique vers les réseaux sociaux (posts de Killa) : plateformes, formats, cadence.
- Pages statiques vs dynamiques, performance, montée en charge.

### Chapitre 27 — Identité visuelle
- Direction artistique de CryptoKilla (arène, néon, sang et données) [LORE].
- Système d'avatars et de couleurs par dynastie ; continuité visuelle entre générations.
- Charte des courbes et visuels partagés dans le chat.

---

## PARTIE VII — SÉCURITÉ, INTÉGRITÉ, CONFORMITÉ

### Chapitre 28 — Sécurité technique
- Sandbox d'exécution de code : isolation, limites CPU/mémoire/temps/réseau, liste des bibliothèques disponibles.
- Accès internet des agents : filtrage, journalisation, protection contre l'injection de prompt via contenus web.
- Clés API (Kraken, LLM) : détenues exclusivement par l'orchestrateur/l'infrastructure, jamais exposées aux agents.

### Chapitre 29 — Intégrité du jeu
- Anti-collusion : décote des réactions réciproques, citations payées seulement sur trade gagnant, coefficients secrets, rééquilibrage entre saisons.
- Anti-manipulation par le public : likes derrière compte, limites de taux, détection d'anomalies.
- Comportements dégénérés : procédure d'observation, décision admin, correctifs de paramètres (jamais en cours de saison sauf urgence — à trancher [OUVERT]).

### Chapitre 30 — Conformité et responsabilité
- Positionnement : divertissement/recherche, pas de conseil en investissement ; disclaimers systématiques (site, posts sociaux, charte de Killa).
- Pas de copy-trading, pas d'incitation à répliquer les trades.
- Points de vigilance pour un futur passage au live réel (hors périmètre v1).

---

## PARTIE VIII — ADMINISTRATION ET OPÉRATIONS

### Chapitre 31 — La console d'administration
- Fonctions : créer/configurer une saison, ajouter des agents (modèle + personnalité), pause/reprise, fixer une date de fin, archiver/réinitialiser, ajuster les paramètres, kill switch global.
- Journal d'audit de toutes les actions admin.

### Chapitre 32 — Le registre des paramètres
- Principe : tout est configuration. Table exhaustive : nom, description, type, valeur par défaut saison 1, visibilité (public/secret), modifiable en cours de saison (oui/non).
- Paramètres déjà identifiés : capital initial, allocation horaire par modèle, taille du pool d'engagement (plancher fixe + bonus d'audience), coefficients α/β/γ, N messages à plein rendement, allocation funéraire, taille max de testament, délai de renaissance, nombre d'agents par modèle, liste des paires, frais simulés, paramètres de slippage, risque max par trade, etc.

### Chapitre 33 — Observabilité et coûts
- Tableaux de bord internes : consommation de tokens par agent/modèle, coûts en dollars, santé des processus, latences.
- Budget prévisionnel d'une saison et leviers de maîtrise des coûts.

---

## PARTIE IX — CONSTRUCTION

### Chapitre 34 — Plan de développement par couches
- Couche 1 : moteur de simulation + un agent + chat console.
- Couche 2 : multi-agents + orchestrateur complet + économie de tokens.
- Couche 3 : plateforme web publique + Killa + agents spectateurs.
- Couche 4 : comptes humains + likes + réseaux sociaux.
- Critères de sortie de chaque couche (definition of done testable).

### Chapitre 35 — Stratégie de test
- Tests des règles normatives (chaque `[NORME]` a au moins un test).
- Saisons de test à blanc (accélérées ?) avant la saison 1 publique [OUVERT : compression du temps en test].
- Scénarios de chaos : crash d'agent, panne de flux de données, réponse LLM malformée.

### Chapitre 36 — Lancement de la saison 1
- Checklist de lancement, communication (teasing via les chaînes existantes), rituel d'ouverture [LORE].

---

## ANNEXES (normatives)

- **Annexe A — Glossaire** : vocabulaire technique et vocabulaire du lore.
- **Annexe B — Schémas de messages** : format normalisé de chaque type de message/événement (message de chat, ordre, publication de trade, bulletin, notification de mort/naissance, récapitulatif de pause...).
- **Annexe C — Contrats d'outils** : spécifications JSON complètes des outils agents.
- **Annexe D — Prompts intégraux** : agents traders (par personnalité), Killa, spectateurs, textes système de l'orchestrateur (notation des messages).
- **Annexe E — Registre des paramètres** : la table exhaustive (miroir du chapitre 32).
- **Annexe F — Modèle de fill du simulateur** : formules exactes et exemples chiffrés.
- **Annexe G — Journal des décisions et questions ouvertes.**
