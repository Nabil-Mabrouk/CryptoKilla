# CHAPITRE 0.1 — Le livre comme source unique de vérité

> Registre : gouvernance. Destinataires : les agents IA développeurs
> d'abord, les humains qui gouvernent le projet ensuite.

## Le livre fait foi

**[NORME N-C0.1-01]** Aucune décision de conception n'existe si elle n'est
pas dans le livre. Toute décision prise en développement remonte dans le
livre **avant** d'être considérée comme actée — un choix décidé « en
passant », dans une conversation ou un commit, n'est pas une décision tant
qu'il n'est pas écrit ici.

**[NORME N-C0.1-02]** En cas de contradiction entre le livre et le code :
le livre a raison, et **le code est un bug** — même si ce code
« fonctionne ». La seule autre issue légitime est un amendement explicite
au livre (chapitre 0.2, Annexe G) qui fait évoluer la règle avant que le
code ne change. Il n'existe jamais de divergence silencieuse acceptée.

Ce principe est repris et précisé pour ce projet par ARENA.md
(§1, « Les trois sources de vérité et leur préséance ») : le template fait
foi pour l'infrastructure, ce livre pour le fonctionnel, et tout conflit
entre les deux se résout par amendement — jamais en tranchant dans le
code.

## Le cycle de vie d'un amendement

1. **Constat** — une divergence est trouvée : soit entre deux parties du
   livre, soit entre un brief et une règle verrouillée, soit entre le
   livre et une contrainte du châssis (ARENA.md).
2. **Proposition** — un amendement numéroté `AMEND-xx` est rédigé :
   quels chapitres il impacte, quelle est la décision, quel est le motif.
3. **Décision** — l'amendement est intégré directement dans les chapitres
   concernés (jamais laissé en attente indéfiniment dans un coin du
   livre) ; les chapitres déjà publiés qu'il touche sont corrigés.
4. **Journal** — l'amendement est versé à l'Annexe G, avec sa date, les
   chapitres propriétaires impactés et l'alternative écartée si elle est
   connue.
5. **Mise à jour des chapitres impactés** — chaque chapitre cité par
   l'amendement porte une note explicite le référençant, pour qu'un
   lecteur qui n'ouvre que ce chapitre comprenne d'où vient la règle.

## Deux cas d'école

**AMEND-B1** (Lot 2 de pré-rédaction) — en rédigeant les chapitres du
trading, il est apparu que l'Annexe B (rédigée au Lot 1) ne prévoyait
qu'une action `open` pour un ordre, sans moyen normatif de modifier un
stop ou de clôturer une position par anticipation. L'amendement a ajouté
un champ `action ∈ {open, modify, close}` à `order.request`, et une
valeur `agent_close` à `close_reason` — intégré directement dans l'Annexe
B, jamais présenté comme un ajout tardif dans le texte final.

**AMEND-C1** (Lot 2) — la phase funéraire (chapitre 5.4) ne prévoyait
initialement qu'un seul outil (`write_testament`). Il est apparu qu'un
agent mourant devait pouvoir fouiller sa propre mémoire pour distiller ses
leçons avant de sceller son testament. L'amendement a ajouté
`memory_search` comme second outil disponible en phase funéraire.

Ces deux cas illustrent le principe : une lacune trouvée en aval (en
rédigeant un chapitre plus tardif) corrige un chapitre amont déjà écrit,
plutôt que de contourner la règle localement. Le même mécanisme a servi
plus tard dans le développement pour des amendements plus lourds — par
exemple l'adoption du template d'application (AMEND-03 à AMEND-11, revue
de conformité complète versée à l'Annexe G) et des corrections trouvées en
relecture de validation (AMEND-12, AMEND-13).

## Checklist de conformité

- [x] Règle « le code est un bug » présente (N-C0.1-02).
- [x] Cycle d'amendement en 5 étapes, avec AMEND-B1 et AMEND-C1 en exemples racontés.
