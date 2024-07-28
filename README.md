# Étude longitudinale de l'évolution d'une tumeur (Esteban Dulaurans et Kerian Allaire)

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
côté) et des recalages (les 2 images en cote à côte).

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
