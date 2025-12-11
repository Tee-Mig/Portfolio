# ft_printf

Projet 42 : Recréation de la fonction `printf()` en C avec gestion des arguments variables.

## Objectif

Implémenter `ft_printf(const char *format, ...)`, capable de gérer les conversions :

- `%c`, `%s`, `%p`, `%d`, `%i`, `%u`, `%x`, `%X`, `%%`

## Contraintes

- Langage C, norme 42
- Aucune gestion de buffer
- Libft autorisée
- Compilation : `-Wall -Wextra -Werror`
- Création d'une bibliothèque `libftprintf.a`

## Utilisation

make
gcc -Wall -Wextra -Werror main.c
