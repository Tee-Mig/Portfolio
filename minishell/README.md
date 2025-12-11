# minishell

Projet 42 : Recréer un shell UNIX basique en C, avec gestion de processus, redirections et commandes internes.

## Objectif

Créer un shell interactif capable d’exécuter des commandes avec redirections (`<`, `>`, `<<`, `>>`), pipes (`|`), variables d’environnement (`$`, `$?`) et commandes intégrées (`cd`, `echo`, `pwd`, `export`, `unset`, `env`, `exit`).

## Contraintes

- Langage : C (norme 42)
- Libft autorisée
- Gestion de `ctrl-C`, `ctrl-D`, `ctrl-\`
- Un **seul** `global variable` autorisé (signal uniquement)
- Utilisation de readline autorisée

## Lancement

make

gcc -Wall -Wextra -Werror ./minishell
