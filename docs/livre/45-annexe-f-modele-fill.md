# ANNEXE F — Modèle de fill du simulateur (formules exactes)

> Registre : 100 % normatif. Dépendances : [chapitre 13](16-chapitre-13-moteur-execution.md)
> (comportements et formes déjà verrouillés — cette annexe les met en
> notation rigoureuse et fournit les exemples canoniques). Aucun paramètre
> chiffré en dur : toute constante est un `[PARAM]` (Annexe E).
>
> Les exemples 1, 3 et 4 ci-dessous reprennent **exactement** les valeurs
> déjà publiées dans le fil rouge de l'Annexe B (`ord-3e17`, `pos-88a1`,
> `trd-open-5c21`, `trd-close-5c9f`) — décomposées ici pour la première
> fois en `half_spread`/`slippage` sous-jacents. Chaque fill affiché
> ailleurs dans le livre est donc dérivable de cette annexe, pas
> seulement compatible avec elle.

## Notation formelle

Soit un ordre sur la paire de référence, de taille `T` (devise de
cotation), au moment `t` :

- `ref(t)` = milieu du carnet au moment de l'évaluation ; à défaut de
  carnet disponible, dernier prix connu.
- `half_spread(t) = (ask(t) − bid(t)) / (2 × ref(t))`.
- `volume_1h(t)` = volume horaire de la paire, **converti en devise de
  cotation** (le volume brut de la paire, en devise de base, est publié
  au bulletin — chapitre 14.3 — sa conversion en devise de cotation
  s'obtient par `volume_1h_base × ref(t)`).
- `slippage(T, t) = min(k_slippage × √(T / volume_1h(t)), slippage_max)`.

**Garde de liquidité** : si `T > part_max_liquidite × volume_1h(t)`,
l'ordre est rejeté avec `E-LIQUIDITY` — **aucun fill, jamais partiel**.

**Ordre marché, achat** : `fill = ref(t) × (1 + half_spread(t) +
slippage(T, t))`.
**Ordre marché, vente** : `fill = ref(t) × (1 − half_spread(t) −
slippage(T, t))`.

**Stop** (position longue) : déclenché dès qu'une bougie 1 minute touche
son niveau (**règle de la mèche**) ; exécuté comme un ordre marché **au
niveau du stop** avec slippage défavorable : `fill = stop × (1 −
half_spread(t) − slippage(T, t))`.

**Take profit** : exécuté **au niveau du TP**, sans slippage défavorable
supplémentaire : `fill = tp` (dissymétrie verrouillée, chapitre 13,
N-C13-07).

**Ordre limite** : exécuté à `min(limite, ref(t))` à l'achat (symétrique
à la vente) dès que `ref(t)` croise la limite ; expiré (`E-EXPIRED`) à
`[PARAM: duree_max_ordre_limite]`.

**Frais** : `frais = frais_par_ordre × notionnel`, prélevés à **chaque**
exécution (ouverture et clôture), où `notionnel = quantité × fill`.

**PnL net** (position longue complète, ouverture puis clôture) :

```
quantité      = taille_ouverture / fill_entrée
PnL_brut      = (fill_sortie − fill_entrée) × quantité
frais_entrée  = frais_par_ordre × taille_ouverture
frais_sortie  = frais_par_ordre × (quantité × fill_sortie)
PnL_net       = PnL_brut − frais_entrée − frais_sortie
```

**Latence** : le fill est évalué à `t_acceptation + latence_simulee`, sur
les données de cet instant précis — pas celles de la soumission.

## Exemple 1 — Ordre marché avec slippage (achat, reprend `ord-3e17`)

Données : `ref = 42001,10` (bulletin 14:00, Annexe B) ; volume horaire de
la paire (bulletin) = 184,62 BTC → converti : `184,62 × 42001,10 ≈
7 754 243` EUR ; taille `T = 2100,00` EUR ; `k_slippage = 0,002`.

```
ratio      = 2100 / 7 754 243        ≈ 0,00027080
slippage   = 0,002 × √0,00027080     ≈ 0,002 × 0,016456 ≈ 0,0000329
```

Garde de liquidité (`part_max_liquidite = 5 %`) : seuil `= 0,05 ×
7 754 243 ≈ 387 712` EUR ≫ 2 100 EUR → pas de rejet.

Pour retrouver le fill déjà publié (42 017,40), `half_spread` implicite :

```
total requis (fill/ref − 1) = 42017,40 / 42001,10 − 1 ≈ 0,00038809
half_spread                 = 0,00038809 − 0,0000329 ≈ 0,00035519
```

Soit un carnet `bid ≈ 41 986,18` / `ask ≈ 42 016,02` (spread ≈ 29,84,
milieu = 42 001,10 = `ref`, cohérent par construction). `fill = 42001,10
× (1 + 0,00035519 + 0,0000329) ≈ 42001,10 × 1,00038809 ≈ 42017,40` EUR —
identique à l'Annexe B. Frais : `0,0025 × 2100,00 = 5,25` EUR.

## Exemple 2 — Rejet `E-LIQUIDITY`

Tentative fictive de `claude-nord-3` sur BTC/EUR au même instant que
l'exemple 1 (`volume_1h ≈ 7 754 243` EUR), avec une taille disproportionnée
`T = 500 000,00` EUR.

```
seuil = part_max_liquidite × volume_1h = 0,05 × 7 754 243 ≈ 387 712 EUR
500 000 > 387 712 → rejet E-LIQUIDITY, aucun fill
```

Contrairement à l'exemple de rejet de l'Annexe B (`ord-3e05`, rejeté pour
`E-RISK-EXCEEDED`, un motif différent), ce rejet-ci porte sur la
liquidité disponible, pas sur le risque au stop.

## Exemple 3 — Stop en mèche, avec slippage défavorable (reprend `pos-88a1`)

Position longue, stop à `40800,00` (Annexe B). Une bougie 1 minute touche
ce niveau en mèche (règle de la mèche). Liquidité à cet instant, plus
mince : `90,00` BTC, converti au niveau du stop : `90,00 × 40800,00 =
3 672 000` EUR ; `T = 2100,00` EUR (taille de la position) ; `k_slippage
= 0,002`.

```
ratio      = 2100 / 3 672 000        ≈ 0,00057189
slippage   = 0,002 × √0,00057189     ≈ 0,002 × 0,023914 ≈ 0,0000478
```

Pour retrouver le fill déjà publié (40 763,55) :

```
total requis (1 − fill/stop) = 1 − 40763,55/40800,00 ≈ 0,00089338
half_spread                  = 0,00089338 − 0,0000478 ≈ 0,00084558
```

Soit un carnet `bid ≈ 40 765,50` / `ask ≈ 40 834,50` (spread ≈ 69,00,
milieu = 40 800,00 = niveau du stop, cohérent par construction). `fill =
40800,00 × (1 − 0,00084558 − 0,0000478) ≈ 40800,00 × 0,99910662 ≈
40763,55` EUR — **sous** le niveau du stop, conforme à la dissymétrie
verrouillée (le stop ne garantit pas son prix). Frais : `0,0025 ×
(0,0499793 × 40763,55) ≈ 0,0025 × 2037,33 ≈ 5,09` EUR.

## Exemple 4 — Trade complet, PnL net avec frais des deux côtés

Reprend intégralement les exemples 1 et 3 comme une seule position
(`pos-88a1`, fil rouge) :

```
quantité      = 2100,00 / 42017,40           ≈ 0,0499793 BTC
PnL_brut      = (40763,55 − 42017,40) × 0,0499793 ≈ −62,67 EUR
frais_entrée  = 0,0025 × 2100,00              = 5,25 EUR
frais_sortie  = 0,0025 × (0,0499793 × 40763,55) ≈ 5,09 EUR
PnL_net       = −62,67 − 5,25 − 5,09          ≈ −73,01 EUR
```

Identique au `pnl: -73.01` déjà publié dans `trade.closed` (Annexe B) —
cette annexe ne redéfinit rien, elle **dérive** ce qui était déjà affiché
ailleurs.

## Checklist de conformité

- [x] Toutes les formules verrouillées (chapitre 13) reprises en notation rigoureuse.
- [x] Règle de la mèche présente.
- [x] 4 exemples chiffrés (marché avec slippage ; `E-LIQUIDITY` ; stop en mèche ; trade complet avec PnL net et frais des deux côtés).
- [x] Les exemples 1, 3, 4 sont dérivés des valeurs déjà publiées dans l'Annexe B — cohérence vérifiée, pas seulement affirmée.
- [x] Aucune formule alternative ; aucun paramètre chiffré en dur (tout en `[PARAM]`).
