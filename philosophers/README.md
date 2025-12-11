# philosophers

Projet 42 : Simulation du problème des **philosophes** avec **threads**, **mutex** (et **sémaphores** en bonus).

## Objectif

Créer un programme `philo` simulant des philosophes assis autour d’une table partageant des fourchettes. Ils doivent penser, manger et dormir sans mourir… ni provoquer de race conditions.

## Partie obligatoire

- Langage : C (norme 42)
- Pas de variables globales
- Chaque philosophe est un **thread**
- Utilisation de **mutex** pour protéger les fourchettes
- Affichage structuré : `timestamp_in_ms X is eating`, `... died`, etc.
- Arg. : `./philo nb_philo time_to_die time_to_eat time_to_sleep [must_eat]`

## Compilation & Exécution

make

gcc -Wall -Wextra -Werror ./philo 5 800 200 200
gcc -Wall -Wextra -Werror ./philo 5 800 200 200 5
