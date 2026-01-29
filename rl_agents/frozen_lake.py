import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import gymnasium as gym
from time import sleep

EPOCHS = 20000 # how many times the agent finish the game
ALPHA = 0.8 # learning rate
GAMMA = 0.95 # discount rate, multiplier by futur rewards -> to be less sure further the reward is
MAX_EPSILON = 1.0
MIN_EPSILON = 0.01
DECAY_RATE = 0.001

def reduce_epsilon(epoch):
    return (MIN_EPSILON + (MAX_EPSILON - MIN_EPSILON) * np.exp(-DECAY_RATE * epoch))

def compute_next_q_value(old_q_value, reward, nex_optimal_q_value):
    return (old_q_value + ALPHA * (reward + GAMMA * nex_optimal_q_value - old_q_value))
 
def epsilon_greedy_action_selection(q_table, discrete_state, env, epsilon):
    random_number = np.random.random()
    # explotation
    if (random_number > epsilon):
        state_row = q_table[discrete_state, :]
        action = np.argmax(state_row)

    # exploration
    else:
        action = env.action_space.sample()

    return action

def play_model(model_to_load):
    try:
        model = np.load(model_to_load)
    except FileNotFoundError as e:
        print(f'Error: {e}')
        return
    env = gym.make('FrozenLake-v1', max_episode_steps=100, desc=None, map_name="4x4", is_slippery=False, render_mode='human')

    state = env.reset()[0]
    done  = False
    while not done:
        # env.render()
        action = np.argmax(model[state, :])
        state, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        sleep(0.2)
        if (done):
            break

    env.close()

def train_model(save_path):
    env = gym.make('FrozenLake-v1', max_episode_steps=100, desc=None, map_name="4x4", is_slippery=False)

    action_size = env.action_space.n
    state_size = env.observation_space.n
    q_table = np.zeros([state_size, action_size])

    rewards = []
    log_interval = 1000
    epsilon = 1.0 # for distribution betweeen exploration and explotation

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.ion()
    fig.canvas.draw()
    epoch_plot_tracker = []
    total_reward_plot_tracker = []

    for epoch in range(EPOCHS):
        state = env.reset()[0]
        done = False
        total_rewards = 0

        while not (done):
            action = epsilon_greedy_action_selection(q_table, state, env, epsilon)
            new_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            old_q_value = q_table[state, action]

            next_optimal_q_value = np.max(q_table[new_state, :])
            next_q_value = compute_next_q_value(old_q_value, reward, next_optimal_q_value)
            q_table[state, action] = next_q_value

            total_rewards += reward
            state = new_state
        
        epoch += 1
        epsilon = reduce_epsilon(epoch)

        rewards.append(total_rewards)
        total_reward_plot_tracker.append(np.sum(rewards))
        epoch_plot_tracker.append(epoch)
        if (epoch % log_interval == 0):
            ax.clear()
            ax.plot(epoch_plot_tracker, total_reward_plot_tracker)
            fig.canvas.draw()
            plt.pause(0.01)

    env.close()

    plt.show()
    input('press enter to quit...')

    np.save(save_path, q_table)

def main():

    # train_model('frozen_lake.npy')
    play_model('frozen_lake.npy')
    return 0

if __name__ == '__main__':
    main()