import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import gymnasium as gym
from time import sleep

EPOCHS = 15000
NUMBER_OF_BINS = 40
ALPHA = 0.8
GAMMA = 0.9
MIN_EPSILON = 0.01
MAX_EPSILON = 1.0
DECAY_RATE = 0.001

BURN_IN = 100
EPSILON_END = 10000
EPSILON_REDUCE = 0.0001

def create_bins(num_bins_per_observation = NUMBER_OF_BINS):
    position_x_car = np.linspace(-1.2, 0.6, num_bins_per_observation)
    velocity_car = np.linspace(-0.07, 0.07, num_bins_per_observation)
    return (np.array([position_x_car, velocity_car]))

def discretize_observation(observations, bins):
    binned_observations = []
    for i in range(len(observations)):
        binned_observations.append(np.digitize(observations[i], bins[i]))
    # for i, observation in enumerate(observations):
    #     discretized_observation = np.digitize(observation, bins[i])
    #     binned_observations.append(discretized_observation)
    return tuple(binned_observations) # Important for later indexing

def epsilon_greedy_action_selection(epsilon, q_table, discrete_state, env):
    random_number = np.random.random()
    # exploration
    if (epsilon > random_number):
        action = env.action_space.sample()
    # exploitation
    else:
        action = np.argmax(q_table[discrete_state])
    return action

# def reduce_epsilon(epoch, epsilon):
#     if (BURN_IN <= epoch <= EPSILON_END):
#         epsilon -= EPSILON_REDUCE
#     return epsilon

def reduce_epsilon(epoch):
    return (MIN_EPSILON + (MAX_EPSILON - MIN_EPSILON) * np.exp(-DECAY_RATE * epoch))

def compute_next_q_value(old_q_value, reward, next_optimal_q_value):
    return (old_q_value + ALPHA * (reward + GAMMA * next_optimal_q_value - old_q_value))

def train_model(save_path):
    env = gym.make("MountainCar-v0")  # default goal_velocity=0
    bins = create_bins()
    q_table_shape = (NUMBER_OF_BINS, NUMBER_OF_BINS, env.action_space.n)
    q_table = np.zeros(q_table_shape)
    epsilon = 1.0

    log_interval = 1000
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.ion()
    fig.canvas.draw()
    epochs_log = []
    mean_position_log = []
    max_pos_log = []

    for epoch in range(EPOCHS):
        init_obs = env.reset()[0]
        discretized_obs = discretize_observation(init_obs, bins)
        done = False
        epochs_log.append(epoch)
        max_car_pos = -1.2

        while not (done):
            action = epsilon_greedy_action_selection(epsilon, q_table, discretized_obs, env)
            next_obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            next_obs_discretized = discretize_observation(next_obs, bins)

            old_q_value = q_table[discretized_obs + (action, )]
            next_optimal_q_value = np.max(q_table[next_obs_discretized])

            next_q = compute_next_q_value(old_q_value, reward, next_optimal_q_value)
            q_table[discretized_obs + (action, )] = next_q
            discretized_obs = next_obs_discretized
            if (next_obs[0] > max_car_pos):
                max_car_pos = next_obs[0]

        epsilon = reduce_epsilon(epoch)
        max_pos_log.append(max_car_pos)
        max_pos_mean = round(np.mean(max_pos_log[-30:]), 2)
        mean_position_log.append(max_pos_mean)
        if (epoch % log_interval == 0):
            ax.clear()
            ax.plot(epochs_log, max_pos_log, label='Epoch vs Max pos')
            ax.plot(epochs_log, mean_position_log, label=f'Running Mean: {max_pos_mean}', color='red')
            plt.legend()
            fig.canvas.draw()
            plt.pause(0.01)


    np.save(save_path, q_table)
    env.close()
    print('Training successfully end')
    plt.show()
    input('press enter to quit...')

def play_model(model_to_load):
    try:
        model = np.load(model_to_load)
    except FileNotFoundError as e:
        print(f'Error: {e}')
        return

    env = gym.make("MountainCar-v0", goal_velocity=0.1, render_mode='human')
    bins = create_bins(NUMBER_OF_BINS)
    observation = env.reset()[0]
    done = False

    while (True):
        discretize_state = discretize_observation(observation, bins)
        action = np.argmax(model[discretize_state])
        observation, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        if (done):
            break
        # sleep(0.1)

    env.close()

def main():
    # train_model('models/mountain_car.npy')
    play_model('models/mountain_car.npy')
    return 0

if __name__ == '__main__':
    main()