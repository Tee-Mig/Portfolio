# ft_containers

Projet 42 : Re-implémentation de plusieurs **containers standards C++98** pour mieux comprendre leur fonctionnement interne.

## Objectif

Reproduire les containers C++ `vector`, `map`, `stack` ainsi que des utilitaires associés (`pair`, `iterators`, `enable_if`, etc.), le tout en respectant le standard **C++98**.

## Partie obligatoire

- Containers à implémenter :

  - `ft::vector`
  - `ft::map`
  - `ft::stack` (utilise `vector` par défaut)

- Utilitaires à coder :

  - `iterator_traits`, `reverse_iterator`, `enable_if`, `is_integral`,  
    `equal`, `lexicographical_compare`, `pair`, `make_pair`

- Contraintes :
  - Namespace `ft`
  - Utilisation de `std::allocator`
  - Interdiction d’utiliser la STL dans vos implémentations

## Tests

- Fournir un `main.cpp` de tests comparant `ft::containers` vs `std::containers`
- Deux binaires : un avec vos containers, un avec ceux de la STL
- Tolérance de performances : vos containers peuvent être jusqu’à **20× plus lents**

## Bonus (si partie obligatoire parfaite)

- Implémenter `ft::set` avec un **arbre rouge/noir**

## Compilation

c++ -Wall -Wextra -Werror -std=c++98 main.cpp
