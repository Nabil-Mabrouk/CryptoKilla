# CHAPITRE 32 — Le registre des paramètres

> Registre : normatif. Dépendances : R-100, [chapitre 15](18-chapitre-15-base-donnees.md)
> (table `season_params`), [chapitre 11.2](14-chapitre-11-vue-ensemble.md)
> (rechargement par signal). Ce chapitre norme le **fonctionnement** du
> registre ; l'inventaire exhaustif des valeurs vit en **Annexe E**.

## Principe

**[NORME N-C32-01]** Tout est configuration (R-100) : chaque valeur de
règle marquée `[PARAM]` dans ce livre vit dans le registre, table
`season_params` (chapitre 15). Aucun composant ne lit une valeur de jeu
codée en dur — chacun lit le registre au démarrage et sur signal de
rechargement (chapitre 11.2, N-C11-05).

## Structure d'une entrée

**[NORME N-C32-02]** Chaque entrée du registre porte exactement :

| Champ | Description |
|---|---|
| `nom` | Identifiant technique (`snake_case`), ex. `risque_max_trade`. |
| `description` | Une phrase expliquant ce que la valeur contrôle. |
| `type` | Type de donnée (nombre, pourcentage, durée, liste, texte...). |
| `unite` | Unité explicite si applicable (%, secondes, EUR, tokens...). |
| `valeur_defaut_saison1` | Valeur proposée pour la saison 1 (Annexe E). |
| `visibilite` | `public` ou `secret`. |
| `modifiable_en_saison` | `oui`, `non`, ou `urgence_journalisee`. |
| `chapitre_proprietaire` | Le chapitre du livre qui définit ce paramètre. |

## Annexe E : projection, pas source

**[NORME N-C32-03]** La base de données (`season_params`) **fait foi**.
L'Annexe E est une **projection documentaire** — un miroir généré pour la
lecture humaine, jamais édité à la main indépendamment de la base. Toute
divergence entre l'Annexe E et la base est un bug documentaire, pas une
ambiguïté de règle.

## Cycle de vie d'un paramètre

1. **Création** — en état `configuration` (chapitre 10.1), avec sa
   valeur par défaut saison 1.
2. **Gel** — au démarrage de la saison (`active`), les paramètres publics
   structurants sont gelés (chapitre 10.5, N-C10-14) ; les secrets restent
   modifiables selon leur classe.
3. **Modification selon la classe** — `oui` : modifiable librement en
   saison ; `non` : modifiable uniquement en `configuration` ; `urgence_journalisee` :
   modifiable en saison active uniquement via la procédure de
   comportement dégénéré (chapitre 29, N-C29-02), toujours journalisée.
4. **Historisation** — chaque modification est elle-même un événement
   (Annexe B) ; l'historique complet d'un paramètre est donc
   reconstructible, comme tout le reste (event-sourcing).

## Trois exemples d'entrées complètes

| Champ | Exemple 1 | Exemple 2 | Exemple 3 |
|---|---|---|---|
| `nom` | `risque_max_trade` | `n_messages_plein_rendement` | `duree_max_funeraire` |
| `description` | Perte potentielle max au stop, en fraction du capital courant | Seuil de messages/heure au-delà duquel les rendements décroissent | Durée max de la phase funéraire |
| `type` | Pourcentage | Entier | Durée |
| `unite` | % du capital | messages/heure | minutes |
| `visibilite` | `public` | `secret` | `public` |
| `modifiable_en_saison` | `non` (structurant) | `urgence_journalisee` | `non` |
| `chapitre_proprietaire` | Chapitre 7 | Chapitre 6 | Chapitre 5 / 21 |

## Checklist de conformité

- [x] Structure d'entrée exhaustive (8 champs, N-C32-02).
- [x] « L'Annexe E est une projection, la base fait foi » présent (N-C32-03).
- [x] Cycle de vie d'un paramètre en 4 étapes.
- [x] 3 exemples d'entrées complètes.
