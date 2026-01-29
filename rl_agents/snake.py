import pyautogui as pg
import cv2
import tensorflow as tf
import keras
from collections import deque
import random
import numpy as np
import pyscreeze
from time import sleep
import matplotlib.pyplot as plt
import dxcam
import pytesseract
import csv
import keyboard
import json

pyscreeze.USE_IMAGE_NOT_FOUND_EXCEPTION = False

def create_dqn_model(input_shape, num_actions):
    model = keras.Sequential()

    # input -> grayscale image of 84x84 with 1 color channel (84, 84, 1)
    model.add(keras.layers.InputLayer(input_shape))

    # extract image features
    model.add(keras.layers.Conv2D(32, (8, 8), strides=(4, 4), activation='relu'))
    model.add(keras.layers.Conv2D(64, (4, 4), strides=(2, 2), activation='relu'))
    model.add(keras.layers.Conv2D(64, (3, 3), activation='relu'))

    # make 1 dimensionnal array for model to process it
    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dense(512, activation='relu'))

    # output layer
    model.add(keras.layers.Dense(num_actions, activation='linear'))

    model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.00025),
                  loss='mean_squared_error',
                  metrics=['mae'])
    return (model)

def preprocess_frame(frame):
    # convert to grayscale
    if (len(frame.shape) == 3 and frame.shape[2] != 1):
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # resize to 84x84
    frame = cv2.resize(frame, (84, 84))

    # normalize pixels values
    frame = frame / 255.0

    if (len(frame.shape) == 2):
        frame = np.expand_dims(frame, axis=-1)
    # if (len(frame.shape) == 3):
    #     frame = np.expand_dims(frame, axis=0)
    return frame

class ReplayBuffer:
    def __init__(self, buffer_size, batch_size):
        self.buffer_size = buffer_size
        self.batch_size = batch_size
        self.buffer = deque(maxlen=buffer_size)
    
    def add(self, observation, action, reward, next_observation, done):
        experience = (observation, action, reward, next_observation, done)
        self.buffer.append(experience)
    
    def sample(self):
        return (random.sample(self.buffer, self.batch_size))

    def size(self):
        return (len(self.buffer))

def update_epsilon(epsilon, epsilon_min, epsilon_decay):
        if (epsilon > epsilon_min):
            epsilon *= epsilon_decay # exponential decay
        else:
            epsilon = epsilon_min

def epsilon_greedy_policy(model, observation, epsilon, num_actions):
    if (random.random() < epsilon):
        action = random.randint(0, num_actions - 1)
    else:
        q_value = model.predict(np.expand_dims(observation, axis=0), verbose=0)
        action = np.argmax(q_value)
    return (action)

def click_image(image_path, image_to_wait = None):

    while (True):
        image_pos = pg.locateOnScreen(image_path, confidence=0.9)
        if (image_pos):
            x_pos = random.randint(image_pos.left, image_pos.left + image_pos.width)
            y_pos = random.randint(image_pos.top, image_pos.top + image_pos.height)
            pg.click(x_pos, y_pos)
        if (image_to_wait == None):
            break
        else:
            if (pg.locateOnScreen(image_to_wait, confidence=0.9)):
                break
        sleep(random.uniform(1, 1.2))

def reset_snake(cam):
    if (pg.locateOnScreen('img/snake_init_frame.png', confidence=0.9) == None):
        click_image('img/jouer_snake.png', 'img/snake_init_frame.png')
    else:
        click_image('img/snake_init_frame.png')
    while (True):
        observation = cam.grab()
        if (observation is not None):
            break
    return (observation)

def do_step(action, cam, score):

    while (True):
        observation = cam.grab()
        if (observation is not None):
            break
    observation = cv2.cvtColor(observation, cv2.COLOR_RGB2GRAY)
    reward = -0.01
    done = False

    if (action == 0):
        keyboard.press_and_release('down')
    elif (action == 1):
        keyboard.press_and_release('right')
    elif (action == 2):
        keyboard.press_and_release('up')
    elif (action == 3):
        keyboard.press_and_release('left')

    result = cv2.matchTemplate(observation,
                            cv2.cvtColor(cv2.imread('img.jouer_snake.png'), cv2.COLOR_RGB2GRAY),
                            cv2.TM_CCOEFF_NORMED)
    max_val = cv2.minMaxLoc(result)[1]
    if (max_val >= 0.9):
        done = True
        reward = -10

    elif (int(convert_image_into_string((845, 331, 45, 68))) != score):
        reward = 10
        score += 1
    
    return (observation, reward, done, score)

def print_snake():
    click_image('img/chrome_icon.png', 'img/chrome_snake_icon.png')
    click_image('img/chrome_snake_icon.png', 'img/jouer_snake.png')

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\migue\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def convert_image_into_string(region):
    img_to_convert = pg.screenshot(region=region)

    # Convert the PIL Image to a NumPy array
    img_to_convert = np.array(img_to_convert)

    # Convert RGB (PIL format) to BGR (OpenCV format)
    img_to_convert = cv2.cvtColor(img_to_convert, cv2.COLOR_RGB2BGR)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img_to_convert, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to the grayscale image
    thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Resize the thresholded image
    thresh = cv2.resize(thresh, (0, 0), fx=1.25, fy=1.25)  # scale image 1.25X

    return (pytesseract.image_to_string(thresh, config = '--psm 6')[0])

pg.PAUSE = 0

def plot_result():
    with open(f'metrics/dqn_metrics_snake_800_epochs.csv', 'r') as f:
        metrics = json.load(f)

    # Access the individual plots (or data)
    epoch_plot = metrics['epoch_plot']
    epoch_rewards_plot = metrics['epoch_rewards_plot']
    max_score_plot = metrics['max_score_plot']

    # Create a figure and axis for plotting
    plt.figure(figsize=(12, 6))

    # Plot the epoch plot (assuming it's a list of epoch values)
    plt.subplot(131)  # 1 row, 3 columns, 1st plot
    plt.plot(epoch_plot)
    plt.title('Epoch Plot')
    plt.xlabel('Epoch')
    plt.ylabel('Value')

    # Plot the rewards plot (assuming it's a list of rewards per epoch)
    plt.subplot(132)  # 1 row, 3 columns, 2nd plot
    plt.plot(epoch_rewards_plot)
    plt.title('Epoch Rewards Plot')
    plt.xlabel('Epoch')
    plt.ylabel('Reward')

    # Plot the max score plot (assuming it's a list of max scores per epoch)
    plt.subplot(133)  # 1 row, 3 columns, 3rd plot
    plt.plot(max_score_plot)
    plt.title('Max Score Plot')
    plt.xlabel('Epoch')
    plt.ylabel('Max Score')

    # Display the plots
    plt.tight_layout()
    plt.show()

def main():

    # parameters
    num_actions = 4
    state_shape = (84, 84, 1)
    gamma = 0.99
    buffer_size = 100000
    batch_size = 64
    epochs = 100000 # default 100000
    current_epoch = 39400

    # periodic
    update_target_model_frequency_step = 5000
    save_model_frequency = 200

    # metrics
    epoch_rewards_plot = []
    epoch_plot = []
    max_score_plot = []
    epsilon_plot = []
    step_plot = []

    # epsilon
    epsilon_start = 1
    epsilon_min = 0.01
    epsilon_decay = ((epsilon_start - epsilon_min) / epochs)
    epsilon = epsilon_start

    # screen
    snake_game__region = (790, 461, 1741, 1304)
    cam = dxcam.create(device_idx=0, region=snake_game__region)

    # preparing model
    # model = create_dqn_model(state_shape, num_actions)
    model = keras.models.load_model(f'models/snake_model_{current_epoch}_steps.keras')
    # model = keras.models.load_model(f'models/snake_model_4000_steps.keras')
    target_model = create_dqn_model(state_shape, num_actions)
    target_model.set_weights(model.get_weights())
    replay_buffer = ReplayBuffer(buffer_size, batch_size)

    # print_snake() #* put back if on one screen
    max_score = int(convert_image_into_string((845, 331, 45, 68)))
    # max_score = 3
    step = 219882
    # for epoch in range(1):
    for epoch in range(current_epoch, epochs):
        observation = reset_snake(cam)
        observation = preprocess_frame(observation)
        done = False
        total_reward = 0
        score = 0

        while (pg.locateOnScreen('img/snake_init_frame.png', confidence=0.95)):
            keyboard.press_and_release('right')
        while not (done):
            action = epsilon_greedy_policy(model, observation, epsilon, num_actions)

            next_observation, reward, done, score = do_step(action, cam, score)
            next_observation = preprocess_frame(next_observation)

            replay_buffer.add(observation, action, reward, next_observation, done)
            if (replay_buffer.size() > batch_size):
                batch = replay_buffer.sample()
                observations, actions, rewards, next_observations, dones = zip(*batch)

                observations = np.array(observations)
                actions = np.array(actions)
                rewards = np.array(rewards)
                dones = np.array(dones)
                next_observations = np.array(next_observations)

                target_q_values = model.predict(observations, verbose=0)
                next_q_values = target_model.predict(next_observations, verbose=0)
                for i in range(batch_size):
                    target_q_values[i][actions[i]] = rewards[i] + gamma * np.max(next_q_values[i]) * (1 - dones[i])

                model.fit(observations, target_q_values, epochs=1, verbose=0)

            step += 1
            if ((step) % update_target_model_frequency_step == 0):
                target_model.set_weights(model.get_weights())
                print('update target model')

            observation = next_observation
            total_reward += reward

        if (score > max_score):
            max_score = score

        epsilon = max(epsilon_min, epsilon_start - epsilon_decay * epoch)
        print(f'epsilon = {epsilon}')
        print(f'step = {step}')

        epoch_plot.append((epoch))
        epoch_rewards_plot.append(total_reward)
        max_score_plot.append(max_score)
        epsilon_plot.append(epsilon)
        step_plot.append(step)

        if ((epoch) % save_model_frequency == 0):
            print(f'save current model state at {epoch} epochs')
            model.save_weights(f'./checkpoints/snake_checkpoint_{epoch}_steps.weights.h5')
            model.save(f'models/snake_model_{(epoch)}_steps.keras')
            metrics = {
                'epoch_plot': epoch_plot,
                'epoch_rewards_plot': epoch_rewards_plot,
                'max_score_plot': max_score_plot,
                'epsilon_plot': epsilon_plot,
                'step_plot': step_plot
            }

            with open(f'metrics/dqn_metrics_snake_{epoch}_epochs.csv', 'w') as f:
                json.dump(metrics, f)

        print(f'epoch number {(epoch)}')

    return 0

if __name__ == '__main__':
    main()