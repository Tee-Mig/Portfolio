import cv2
# from tensorflow.python.keras import layers, models
# from tensorflow.python.keras.optimizer_v2.adam import Adam
import numpy as np
import pyscreeze
import dxcam
import tensorflow as tf
import keras

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

    model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001),
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
        frame = np.expand_dims(frame, axis=0)
    return frame

def main():
    # parameters
    num_actions = 4
    state_shape = (84, 84, 1)

    # screen
    snake_game__region = (790, 461, 1741, 1304)
    cam = dxcam.create(device_idx=0, region=snake_game__region)

    # preparing model
    model = create_dqn_model(state_shape, num_actions)
    # target_model = create_dqn_model(state_shape, num_actions)
    # target_model.set_weights(model.get_weights())

    observation = cam.grab()
    observation = preprocess_frame(observation)

    print(model.predict(observation))

    return 0

if __name__ == '__main__':
    main()