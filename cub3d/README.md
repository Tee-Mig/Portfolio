# cub3D

Projet 42 : Reproduction d’un mini **raycaster 3D** à la Wolfenstein3D en utilisant **MiniLibX**.

## Objectif

Créer un jeu de type FPS en 3D simplifiée avec une vue subjective, basé sur le **ray-casting**, dans un labyrinthe défini par un fichier `.cub`.

## Partie obligatoire

- Langage : C (norme 42)
- Utilisation de la MiniLibX et de la lib math (`-lm`)
- Déplacement : touches **W, A, S, D**
- Rotation caméra : **flèches gauche/droite**
- Affichage dynamique de textures (NO, SO, WE, EA)
- Gestion des couleurs sol/plafond (F, C)
- Fermeture propre de la fenêtre (ESC ou croix)
- Parsing et validation de cartes `.cub` **fermées**

## Bonus (si partie obligatoire parfaite)

- Minicarte
- Collisions
- Portes ouvertes/fermées
- Sprites animés
- Rotation caméra à la souris

## Exécution

gcc -Wall -Wextra -Werror ./cub3D maps/level.cub
