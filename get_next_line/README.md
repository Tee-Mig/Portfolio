# get_next_line

Projet 42 : Implémentation de `get_next_line(int fd)` pour lire un fichier ligne par ligne.

## Objectif

Créer une fonction `get_next_line()` qui lit depuis un `file descriptor` et retourne **une ligne à chaque appel**, y compris le `\n`.

## Contraintes

- Langage : C (norme 42)
- Fonctions autorisées : `read`, `malloc`, `free`
- Aucun leak mémoire, pas de variables globales
- Compilation avec : `-Wall -Wextra -Werror -D BUFFER_SIZE=n`
- Libft interdite

## Bonus (optionnel)

- Une seule variable statique
- Gestion de plusieurs `fd` en parallèle  
  (Fichiers `_bonus.c/.h` requis)

## Fichiers à rendre

- `get_next_line.c`, `get_next_line_utils.c`, `get_next_line.h`
- Bonus : `get_next_line_bonus.c`, `.h`, `utils_bonus.c`
