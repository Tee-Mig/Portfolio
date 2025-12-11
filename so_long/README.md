# so_long

Projet 42 : Création d’un petit **jeu 2D** en C utilisant la **MiniLibX**.

## Objectif

Programmer un jeu où le joueur doit **collecter tous les items** puis **rejoindre la sortie**, à l’aide des touches **W, A, S, D** sur une carte au format `.ber`.

## Contraintes

- Langage : C (norme 42)
- Libft et MiniLibX autorisées
- Carte `.ber` rectangulaire, entourée de murs, contenant `P`, `C`, `E`
- Gestion d’événements clavier et fermeture de fenêtre
- Affichage du nombre de mouvements dans le shell
- Aucun **leak** mémoire

## Bonus (si partie obligatoire parfaite)

- Ennemi (perte possible du joueur)
- Animations
- Affichage du score dans la fenêtre

## Exemple

gcc -Wall -Wextra -Werror ./so_long maps/map.ber
