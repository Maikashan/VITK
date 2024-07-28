# Étude longitudinale de l'évolution d'une tumeur (Esteban Dulaurans et Kerian Allaire)

## Lien vers le [repo](https://github.com/Maikashan/VITK)

## Division du travail

- Recalage : Kerian
- Segmentation : Kerian & Esteban
- Visualisation : Esteban

## Recalage

Afin de recaler notre image, nous avons décidé d'étudier plusieurs approches. Pour
ce faire, on est passé par un jupyter un premier temps. Cela nous a notamment
permis de tester différentes transformations, telles qu'une transformation eulérienne,
une transformation de translation, une transformation Rigid3D de Versor avec une
initialiseur centré, que cela soit géométriquement ou à l'aide des moments,
ou encore une transformation affine. Afin d'essayer d'obtenir les meilleures
transformations possibles, on a benchmark divers hyper paramètres.

De même, on a essayé divers optimiseurs, tels que le `LBFGSB` avec une
`MeanSquareError` comme élément de mesure, un 1 + 1 évolution avec le
`MattesMutualInformation` comme métrique, ou encore un
`RegularStepGradientDescent`. Après l'utilisation d'une approche de grid search
ainsi que des vérifications des valeurs des autres métriques tel que la
corrélation, ainsi que d'une classe observer afin de stopper plus tôt si nécessaire.

Le `RegularStepGradient` avec une `TranslationTransform` a été retenu, donnant
les résultats qualitatifs et quantitatifs les plus satisfaisants.
Afin d'améliorer nos résultats, il serait probablement nécessaire d'amener une
transformation de rotation, car cela manque ici, et c'est possiblement le goulot
d'étranglement de notre recalage actuel. Tout le code est présent dans différents
fichiers tels que `registration.py` et `observer.py`.

## Segmentation

On a commencé par simplement reprendre la méthode vue dans un le TP d'ITK, en
utilisant la classe `ConnectedThresholdImageFilter` après avoir passé un flou
avec la classe `GradientAnisotropicDiffusionImageFilter`. Le plus de
temps passé dans cette section était la recherche empirique des points de Seed
de la méthode, ainsi que les différentes valeurs de thresholds. Nous avons
notamment utilisé diverses techniques de visualisations afin de déterminer ces
valeurs.

Nous avons également essayé la méthode `IsolatedConnectedImageFilter`, qui n'a
pas produit de résultats considérables, comparés à la segmentation que nous
avions alors, et ceci malgré des modifications des différents paramètres à notre
disposition.

Il serait intéressant de faire évaluer notre segmentation à un spécialiste, car
nous ne sommes pas sûrs d'avoir pris en compte toute la région d'intérêt. De
plus, il pourrait être intéressant de comparer nos résultats avec un algorithme
de type watershed.

Vous pouvez trouver l'implémentation dans `segmentation.py`.

## Visualisation

Notre première approche, pour la visualisation, était de passer par des slices
de l'IRM, qui était changeables interactivement avec la souris, en redéfinissant
des callbacks sur le `vtkInteractorStyleImage`. Elle servit en particulier au
début, pour pouvoir debug plus facilement les 2 autres parties. Cette
implémentation peut se trouver dans le fichier `render.py`.

Elle consistait à utiliser la classe vtkImageReslice avec différentes matrices
pour récupérer les différents axes de coupes. On a entendu le processus à
plusieurs viewports par la suite, grâce à des Renderer dédiés et la fonction
`SetViewport` ce qui nous permis de visualiser plus facilement les résultats
des segmentations (en affichant l'image d'origine avec la région segmentée à
côté) et des recalages (les 2 images en côte à côte).

Dans un deuxième temps, on s'est demandé s'il n'y avait pas une manière plus
claire de voir le positionnement des 2 nodules. Les slices permettaient
d'évaluer visuellement les différentes étapes que l'on traitait sur le moment,
mais ne rendaient pas vraiment compte de la taille ou de la différence des
nodules.

C'est pourquoi nous avons opté pour une visualisation en 3 dimensions, pour
profiter au mieux des capacités de la bibliothèque VTK. On a d'abord affiché les
nodules seuls, puis avec un volume de la tête autour, pour avoir une meilleure
visualisation de la taille des tumeurs. Enfin, l'ajout de la différence a semblé
être la dernière touche pour pouvoir réellement analyser l'évolution de la tumeur
dans le temps. Cette implémentation se trouve dans le fichier `threeDView.py`.
