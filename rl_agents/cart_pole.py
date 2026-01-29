import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import gymnasium as gym
from time import sleep

NUM_BINS = 10
EPOCHS = 20000
ALPHA = 0.8 # learning rate
GAMMA = 0.9 # discount rate, multiplier by futur rewards -> to be less sure further the reward is
MAX_EPSILON = 1.0
MIN_EPSILON = 0.01
DECAY_RATE = 0.001

BURN_IN = 1
EPSILON_END = 14000
EPSILON_REDUCE = 0.0001

def create_bins(num_bins_per_obs = 10):
    bins_cart_position = np.linspace(-4.8, 4.8, num_bins_per_obs)
    bins_cart_velocity = np.linspace(-5, 5, num_bins_per_obs)
    bins_pole_angle = np.linspace(-0.418, 0.418, num_bins_per_obs)
    bins_pole_angular = np.linspace(-5, 5, num_bins_per_obs)

    bins = np.array([bins_cart_position, bins_cart_velocity, bins_pole_angle, bins_pole_angular])

    return (bins)

def discretize_observation(observations, bins):
    binned_observations = []
    for i, observation in enumerate(observations):
        discretized_observation = np.digitize(observation, bins[i])
        binned_observations.append(discretized_observation)
    # for i in range(len(observations)):
    #     binned_observations.append(np.digitize(observations[i], bins[i]))
    return (tuple(binned_observations))

def epsilon_greedy_action_selection(q_table, discrete_state, env, epsilon):
    random_number = np.random.random()
    # explotation
    if (random_number > epsilon):
        state_row = q_table[discrete_state]
        action = np.argmax(state_row)

    # exploration
    else:
        action = env.action_space.sample()

    return action

# def reduce_epsilon(epoch):
#     return (MIN_EPSILON + (MAX_EPSILON - MIN_EPSILON) * np.exp(-DECAY_RATE * epoch))

def reduce_epsilon(epoch, epsilon):
    if (BURN_IN <= epoch <= EPSILON_END):
        epsilon -= EPSILON_REDUCE
    return epsilon

def compute_next_q_value(old_q_value, reward, next_optimal_q_value):
    return (old_q_value + ALPHA * (reward + GAMMA * next_optimal_q_value - old_q_value))

def fail(done, points, reward):
    if (done and points < 200):
        reward = -200
    return reward

def train_model(save_path):
    env = gym.make("CartPole-v1")

    bins = create_bins(NUM_BINS)
    epsilon = 1.0
    q_table_shape = (NUM_BINS, NUM_BINS, NUM_BINS, NUM_BINS, env.action_space.n)
    q_table = np.zeros(q_table_shape)

    log_interval = 500
    render_interval = 30000

    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.ion()
    fig.canvas.draw()

    points_log = []
    mean_points_log = []
    epochs = []

    for epoch in range(EPOCHS):

        init_state = env.reset()[0]
        discretized_state = discretize_observation(init_state, bins)

        done = False
        points = 0

        epochs.append(epoch)

        while not (done):
            action = epsilon_greedy_action_selection(q_table, discretized_state, env, epsilon)
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            reward = fail(done, points, reward)

            next_state_discretized = discretize_observation(next_state, bins)

            old_q_value = q_table[discretized_state + (action,)]
            next_optimal_q_value = np.max(q_table[next_state_discretized])

            next_q = compute_next_q_value(old_q_value, reward, next_optimal_q_value)
            q_table[discretized_state + (action,)] = next_q

            discretized_state = next_state_discretized
            points += 1

        epsilon = reduce_epsilon(epoch, epsilon)
        points_log.append(points)
        running_mean = round(np.mean(points_log[-30:]), 2)
        mean_points_log.append(running_mean)
        if (epoch % log_interval == 0):
            ax.clear()
            ax.plot(epochs, points_log, label='Epoch vs Points log')
            ax.plot(epochs, mean_points_log, label=f'Running Mean: {running_mean}', color='red')
            plt.legend()
            fig.canvas.draw()
            plt.pause(0.01)

    env.close()
    np.save(save_path, q_table)
    print('Training successfully end')
    plt.show()
    input('press enter to quit...')

def play_model(model_to_load):
    try:
        model = np.load(model_to_load)
    except FileNotFoundError as e:
        print(f'Error: {e}')
        return

    env = gym.make("CartPole-v1", render_mode='human')
    bins = create_bins(NUM_BINS)
    observation = env.reset()[0]
    # done = False
    rewards = 0

    while (True):
        discretize_state = discretize_observation(observation, bins)
        action = np.argmax(model[discretize_state])
        observation, reward, terminated, truncated, info = env.step(action)
        # done = terminated or truncated
        if not (-0.418 <= observation[2] <= 0.418): # check if the pole fall
            break
        rewards += 1
        # sleep(0.1)

    print(f'rewards = {rewards}')
    env.close()


def main():
    # train_model('models/cart_pole.npy')
    play_model('models/cart_pole.npy')
    return 0

if __name__ == '__main__':
    main()