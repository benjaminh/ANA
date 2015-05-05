# ANA

Implémentation Python du système ANA : Apprentissage Naturel Automatique

Le système ANA effectue automatiquement l'extraction de la terminologie d'un domaine et structure cet ensemble de concepts en un réseau sémantique. Cette acquisition de connaissances est fondée sur l'étude de textes libres. Le système n'utilise ni grammaire ni dictionnaire mais s'appuie sur des procédures statistiques, ce qui le rend indépendant de la langue utilisée dans les textes.

ANA est un outil développé en 1992 dans la thèse de C. Enguehard.

# Description du système

ANA effectue la découverte de nouveaux candidats `CAND` au sein d'un texte en utilisant différents fichiers nécessaires à l'induction de concepts:
- une liste de `mots fonctionnels`
- une liste de `mots liés`
- une liste de `mots de schéma`
- un `bootstrap`: une liste de concepts d'initialisation du processus de découverte de nouveaux mots clés

Le texte est découpé et étiqueté à partir des mots du `bootstrap`. Puis ANA génère une liste de fenêtres autour des `CAND` existants dont la taille est fixée (par exemple 2 mots autour du mot courant). Cette liste de fenêtres est ensuite utilisée pour l'induction de nouveaux concepts par l'analyse de critères de validité. L'induction de nouveaux concepts fonctionne en suivant 3 modes parallèles:
- `Expressions`
- `Expansions`
- `Simples` (notés Candidats dans le manuscrit original et dont le nom a été changé pour gagner en compréhension)

Puis le système effectue une destruction pour mettre à jour le bootstrap en supprimant les candidats dont la fréquence n'est plus suffisante. Enfin, le système réalise ces étapes de manière itérative jusqu'à atteindre un nombre d'étapes fixé par l'opérateur.

## Classes

4 classes principales d'objets composent le système ANA.

### Candidat

La classe Candidat comprend l'ensemble des termes identifiés dans le texte par ANA comme concepts représentatifs. Chaque candidat se voit associer sa liste de fenêtres dans le texte, sa fréquence d'apparition ainsi que les formes lexicales similaires. Les Candidats sont sélectionnés à partir de 3 mécanismes effectués de manière parallèle.

### Expression

La recherche d'`Expressions` (p.122) consiste à identifier des termes de la forme : `CAND + mot_schema + terme_quelconque` où `terme_quelconque` est un terme n'étant pas un mot fonctionnel ni un mot de schéma mais pouvant être un CAND. Cette recherche se déroule en trois étapes:
- sélection des fenêtres valides
    * la taille de la fenêtre est fixée à 3 (la taille d'une fenêtre étant donnée par la somme des valeurs des termes inclus dans la fenêtre: un terme fonctionnel valant 0 et les autres valant 1).
    * une fenêtre est valide si elle comprend au moins deux concepts distincts dont l'un est en première position
- troncature des fenêtres sélectionnées:
    * les fenêtres valides sont tronquées autour des concepts (`CAND` ou `terme_quelconque`). S'il y a plusieurs concepts dans la fenêtre, la fonction produit plusieurs fenêtres tronquées, une pour chaque couple
    * une liste de fenêtres valides et tronquées est alors créée pour chaque couple `CAND + terme_quelconque` dans le texte
- identification de la morphologie la plus fréquente: toutes les formes (couples) dont la fréquence d'apparition est supérieur à un seuil `Sexp` (fixé à 3 par l'expérimentation') deviennent des candidats CAND

### Expansion

La recherche d'`Expansions` consiste à identifier des formes du type : `CAND + terme_quelconque`. La fenêtre a une taille fixée à 3. Les fenêtres étudiées sont donc du type `terme_quelconque + CAND + terme_quelconque`. Le processus se déroule en 2 étapes:
- sélection des fenêtres valides : une fenêtre est valide si elle comprend un unique `CAND`, que celui-ci est en une position définie (en l'occurrence au milieu) et qu'il n'y a pas de mot de schéma. Une liste de fenêtres valides dans le texte est alors créée pour chaque combinaison `CAND + terme_quelconque` ou `terme_quelconque + CAND`.
- identification de la morphologie du nouveau CAND : si la fréquence d'apparition de la combinaison est supérieure à un seuil (fixé à 3), elle devient `CAND`

### Simple

La recherche de `Simples` (p.134) consiste à identifier des `terme_quelconque` dans des formes du type : `CAND + mot_schema + terme_quelconque`. La fenêtre étudiée doit être de taille 3 au minimum. Le processus se déroule en trois étapes:
- - sélection des fenêtres valides
    * la taille de la fenêtre est fixée à 3 et produit des formes du type : `terme_quelconque + mot_stop + CAND + mot_schema + terme_quelconque` ou autres combinaisons (`mot_stop` n'étant pas compté dans la taille 3 de la fenêtre)
    * une fenêtre est valide si le `CAND` est en position 3, le `mot_schema` est en position 2 et si le symétrique de la fenêtre répond aussi à ces conditions.
- troncature des fenêtres sélectionnées: les fenêtres valides sont tronquées autour des portions de fenêtre comprenant `CAND`, `mot_schema` et `terme_quelconque`. Une liste de fenêtres valides et tronquées est alors créée pour `terme_quelconque`.
- identification de la morphologie la plus fréquente: le `Simple` peut se trouver dans différentes fenêtres possibles. En fonction des cas, différents seuils de validation existent:
    * si la fenêtre contient le même CAND avec le même mot_schema, alors le seuil de fréquence est de 3
    * si la fenêtre contient le même CAND avec des mot_schema différents, alors le seuil de fréquence est de 5
    * si la fenêtre contient des CAND différents avec le même mot_schema, alors le seuil de fréquence est de 5
    * si la fenêtre contient des CAND différents des mot_schema différents, alors le seuil de fréquence est de 10
