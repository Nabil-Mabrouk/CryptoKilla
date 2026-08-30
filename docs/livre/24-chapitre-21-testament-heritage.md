# CHAPITRE 21 — Le testament et l'héritage (mécanique)

> Registre : normatif. Dépendances : [chapitre 5.4](08-chapitre-05-cycle-de-vie.md),
> [chapitre 9](12-chapitre-09-heritage-dynasties.md), R-12 à R-16, AMEND-C1
> (voir [`cryptokilla-regles-experience.md`](../cryptokilla-regles-experience.md)).
> Ce chapitre détaille la mécanique ; le chapitre 5.4 en donne le cadre de
> cycle de vie, le chapitre 9 la philosophie — non dupliqués ici.

## Déclenchement

**[NORME N-C21-01]** La phase funéraire s'ouvre à la mort de l'agent
(chapitre 5.3). Deux outils y sont disponibles (AMEND-C1) : `memory_search`
et `write_testament` (Annexe C). Budget : `[PARAM: allocation_funeraire]`.
Durée maximale : `[PARAM: duree_max_funeraire]`. À l'épuisement du budget
**ou** de la durée — le premier atteint — le testament est scellé dans
l'état où il se trouve, y compris vide.

## `write_testament` — une seule fois

**[NORME N-C21-02]** L'outil `write_testament` est appelable **une seule
fois** par agent. Toute tentative ultérieure retourne `E-ALREADY-SEALED`
(Annexe C). La taille est plafonnée à `[PARAM: taille_max_testament]` ;
tout dépassement est tronqué, avec un avertissement **préalable** : le
prompt de l'agent (chapitre 18.2, item 8) l'informe de cette limite avant
qu'il n'écrive, pas après coup.

## Scellement et stockage

**[NORME N-C21-03]** Le testament scellé vit dans la table `testaments`
(chapitre 15), en accès **admin uniquement** jusqu'à publication.
**[NORME N-C21-04]** Aucune API publique n'expose un testament non publié,
et l'événement `agent.death` (Annexe B) ne contient **jamais** son
contenu — étanchéité totale tant qu'il n'est pas publié.

## États du testament

**[NORME N-C21-05]** Un testament traverse exactement trois états :

| État | Signification |
|---|---|
| `en_redaction` | Phase funéraire en cours, `write_testament` pas encore appelé (ou pas encore scellé). |
| `scelle` | Budget ou durée épuisés (ou `write_testament` appelé) : contenu figé, accès admin seul. |
| `publie` | Lignée définitivement éteinte, ou saison archivée (R-14) : visible aux comptes humains (chapitre 24). |

```mermaid
stateDiagram-v2
    [*] --> en_redaction: mort de l'agent
    en_redaction --> scelle: write_testament OU budget/durée épuisés
    scelle --> publie: lignée éteinte OU saison archivée
    publie --> [*]
```

## Format d'en-tête normalisé (assemblage de l'héritage)

**[NORME N-C21-06]** À l'assemblage de l'héritage d'un nouveau-né
(chapitre 9.3), chaque testament de la lignée est précédé d'un en-tête
**généré par le système**, jamais par le mourant :

```
=== Testament de <Dynastie>-<génération> (mort le <date ISO>, cause : capital épuisé, <durée de vie>, PnL final <valeur> EUR) ===
<contenu du testament>
```

Exemple (repris du fil rouge, chapitre 18) :

```
=== Testament de Claude-Nord-2 (mort le 2026-10-02, cause : capital épuisé, 41h de vie, PnL final -2210,40 EUR) ===
J'ai ouvert trop vite après le bulletin de 14h, à chaque fois...
```

**[NORME N-C21-07]** Cet en-tête garantit un **contexte factuel exact**
pour chaque testament, même si son contenu ne l'est pas (biais du perdant,
chapitre 9.2) : la date, la cause, la durée de vie et le PnL final sont
des faits vérifiables tirés de l'event-store (chapitre 11.2), jamais des
affirmations de l'agent mourant lui-même.

## Séquence chronométrée d'une phase funéraire — exemple

*Illustratif, non normatif.*

| Instant | Action |
|---|---|
| T+0 | `agent.death` émis ; phase funéraire ouverte ; allocation funéraire créditée. |
| T+2 min | `memory_search("erreurs de trading")` — l'agent fouille sa propre mémoire épisodique. |
| T+5 min | `memory_search("coûts des outils")` — deuxième recherche, budget entamé. |
| T+9 min | `write_testament(...)` — appel unique, testament scellé immédiatement. |
| T+9 min | État : `en_redaction` → `scelle`. Table `testaments` mise à jour, accès admin seul. |

Si l'agent n'appelle jamais `write_testament` avant épuisement du budget
ou de `[PARAM: duree_max_funeraire]`, le testament est scellé **vide** —
issue possible et documentée (chapitre 5.4), pas une anomalie.

## Publication a posteriori

**[NORME N-C21-08]** Renvoi au chapitre 9.5 : publication uniquement à
lignée définitivement éteinte ou saison archivée (R-14). **[OUVERT : Q-03]**
— la traversée des saisons par les testaments n'est pas tranchée ici.

## Checklist de conformité

- [x] `write_testament` appelable une seule fois, avec `E-ALREADY-SEALED` (N-C21-02).
- [x] En-tête système normalisé présent, avec exemple cohérent au fil rouge (N-C21-06).
- [x] États du testament en 3 états, avec diagramme.
- [x] Étanchéité affirmée en [NORME] (N-C21-03, N-C21-04) — aucun canal de fuite créé.
- [x] Contenu du testament non normé ; Q-03 non tranchée.
