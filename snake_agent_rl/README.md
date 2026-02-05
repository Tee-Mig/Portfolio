# Snake Agent – Reinforcement Learning

## Objectif du projet

Langage Le projet **snake_agent_rl** consiste à utilisé un **agent d’intelligence artificielle capable d’apprendre à jouer au jeu Snake** grâce à des techniques d’**apprentissage par renforcement (Reinforcement Learning)**.

L’agent apprend de manière autonome par essais et erreurs, en recevant des récompenses positives ou négatives selon ses actions, avec pour objectif de :

- survivre le plus longtemps possible,
- manger un maximum de nourriture,
- éviter les collisions avec les murs et son propre corps.

Ce projet a été réalisé dans un but pédagogique et démonstratif, notamment pour illustrer ma compréhension des mécanismes fondamentaux du Reinforcement Learning.

---

## Concepts clés abordés

- **Agent** : entité intelligente prenant des décisions à chaque étape
- **Environnement** : simulation du jeu Snake
- **État (State)** : représentation de la situation actuelle du jeu
- **Actions** : déplacements possibles du serpent
- **Récompenses** :
  - récompense positive lorsqu’une nourriture est mangée
  - pénalité en cas de collision ou de mauvaise action
- **Politique d’apprentissage** : amélioration progressive de la stratégie de jeu

---

## Installation

Prérequis : **Python 3.10**

```bash
git clone https://github.com/Tee-Mig/Portfolio.git
cd Portfolio/snake_agent_rl

python -m venv venv
source venv/bin/activate
venv\Scripts\activate

pip install -r requirements.txt

```
