import pandas as pd
import matplotlib.pyplot as plt

def train_model():
    try:
        df = pd.read_csv("data.csv")
    except Exception as e:
        print(f"[Error]: {e}")

    x = df["km"].values
    y = df["price"].values

    x_mean = df["km"].mean()
    x_std = df["km"].std()

    x = (x - x_mean) / x_std

    # poids a sauvegarder
    theta0 = 0
    theta1 = 0

    alpha = 0.01
    epochs = 1000
    m = len(x)
    prev_cost = None   # not defined yet

    # keep track of gradientsa descend
    grad0_history = []
    grad1_history = []
    cost_history = []

    for epoch in range(epochs):
        estimated_price = theta0 + (theta1 * x)
        error = estimated_price - y

        # Gradients
        grad0 = (1/m) * error.sum()
        grad1 = (1/m) * (error * x).sum()

        # Update params
        theta0 -= alpha * grad0
        theta1 -= alpha * grad1

        # Compute cost
        current_cost = ((error ** 2).sum()) / (2*m)

        grad0_history.append(grad0)
        grad1_history.append(grad1)
        cost_history.append(current_cost)

        # Early stopping (skip first iteration)
        if prev_cost is not None:
            print(f'prev cost = {abs(prev_cost - current_cost) / prev_cost}')
            if prev_cost != 0 and abs(prev_cost - current_cost) / prev_cost < 1e-6:
                print(f"Stopped early at epoch {epoch}, cost={current_cost:.6f}")
                break

        prev_cost = current_cost  # update for next loop

    print("Trained model:")
    print(f"theta0 (intercept) = {theta0:.2f}")
    print(f"theta1 (slope) = {theta1:.2f}")
    print(f"cost = {prev_cost}")

    with open("thetas.txt", "w") as f:
        f.write(f"{theta0},{theta1}")

    plt.scatter(df["km"], y, color="blue", label="Data")
    x_norm = (df["km"] - x_mean) / x_std
    plt.plot(df["km"], theta0 + (theta1 * x_norm), color="red", label="Model")
    plt.xlabel("Mileage")
    plt.ylabel("Price")
    plt.legend()
    plt.show()

    plt.figure()
    plt.plot(grad0_history, label="grad0 (dJ/dθ0)")
    plt.plot(grad1_history, label="grad1 (dJ/dθ1)")
    plt.xlabel("Epoch")
    plt.ylabel("Gradient value")
    plt.legend()
    plt.title("Gradient evolution")
    plt.show()

    plt.figure()
    plt.plot(cost_history)
    plt.xlabel("Epoch")
    plt.ylabel("Cost J")
    plt.title("Cost evolution")
    plt.show()

def main():
    train_model()
    return 0
    
if __name__ == "__main__":
    main()