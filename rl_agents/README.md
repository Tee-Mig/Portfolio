# Reinforcement Learning Agents

Ce projet regroupe plusieurs agents de **reinforcement learning** appliqués à des environnements classiques (Gymnasium) ainsi qu’à un agent **DQN** jouant au jeu Snake via capture d’écran et contrôle clavier.

---

## Environnements & algorithmes

- **CartPole-v1**

  - Q-Learning avec **discrétisation de l’espace d’état**
  - Politique **epsilon-greedy** avec décroissance progressive
  - Pénalité en cas d’échec pour accélérer la convergence
  - Suivi des scores + moyenne glissante

- **FrozenLake-v1 (4x4, non glissant)**

  - **Q-Learning tabulaire**
  - Décroissance exponentielle d’epsilon
  - Visualisation du cumul des récompenses

- **MountainCar-v0**

  - Q-Learning avec **bins sur position et vitesse**
  - Epsilon-greedy + décroissance exponentielle
  - Suivi de la position maximale atteinte

- **Google Snake – DQN**
  - Réseau convolutionnel (CNN) inspiré de l’architecture DeepMind Atari
  - **Replay buffer**, réseau cible, epsilon-greedy
  - Capture d’écran en temps réel + OCR pour le score
  - Sauvegarde régulière des poids et des métriques

---

## Structure

├── cartpole/ # Q-Learning CartPole
├── frozen_lake/ # Q-Learning tabulaire
├── mountain_car/ # Q-Learning MountainCar
├── snake_dqn/ # DQN pour Google Snake
└── models/ # Modèles entraînés (.npy / .keras)

---

## Technologies

- **Python**, **NumPy**, **Pandas**
- **Matplotlib**, **Seaborn**
- **Gymnasium** (CartPole, FrozenLake, MountainCar)
- **TensorFlow / Keras** (DQN)
- **OpenCV**, **PyAutoGUI**, **dxcam**, **keyboard**
- **pytesseract** pour l’OCR du score dans Snake

---

## Utilisation

Chaque environnement propose deux fonctions :

### **Entraîner un agent**

```python
train_model('models/cart_pole.npy')
```
