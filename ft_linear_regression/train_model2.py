import pandas as pd
from math import sqrt
# import matplotlib.pyplot as plt

LEARNING_RATE = 0.03
EPOCHS = 1000

def train_model():
    try:
        df = pd.read_csv("data.csv")
    except Exception as e:
        print(f"[Error]: {e}")

    theta0 = 0
    theta1 = 0

    x = df["km"].values
    y = df["price"].values

    # normalization x
    variance_x = ((x - x.mean())**2).mean()
    x_std = sqrt(variance_x)
    x_norm = (x - x.mean()) / x_std
    if x_std == 0:
        raise ValueError("x std is 0 (all km identical)")

    # normalization y
    # variance_y = ((y - y.mean())**2).mean()
    # y_std = sqrt(variance_y)
    # y_norm = (y - y.mean()) / y_std
    # if y_std == 0:
    #     raise ValueError("y std is 0 (all km identical)")

    alpha = LEARNING_RATE

    epochs = 0
    for epoch in range(EPOCHS):
        # prediction
        ye = theta0 + (theta1 * x_norm)
        # error
        e = ye - y

        # gradient descent 1
        grad0 = e.mean()
        # gradient descent 2
        grad1 = (e*x_norm).mean()

        theta0 = theta0 - (alpha * grad0)
        theta1 = theta1 - (alpha * grad1)



def main():
    train_model()
    return 0
    
if __name__ == "__main__":
    main()