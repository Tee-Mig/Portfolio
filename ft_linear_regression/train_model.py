import pandas as pd
import matplotlib.pyplot as plt
import os

def train_model(file: str):
    if not os.path.exists(file):
        raise FileNotFoundError("File not found")

    df = pd.read_csv(file)

    x = df["km"].values
    y = df["price"].values

    x_mean = df["km"].mean()
    x_std = df["km"].std()

    y_mean = df["price"].mean()
    y_std = df["price"].std()

    if x_std == 0 or y_std == 0:
        raise ValueError("Std is 0, impossible to normalize.")
    x_norm = (x - x_mean) / x_std # normalisation x
    y_norm = (y - y_mean) / y_std # normalisation y

    # poids a sauvegarder
    theta0_norm = 0
    theta1_norm = 0

    alpha = 0.01 # learning rate
    epochs = 1000
    m = len(x)
    prev_cost = None

    # keep track of gradientsa descend
    grad0_history = []
    grad1_history = []
    cost_history = []

    for epoch in range(epochs):
        estimated_price_norm = theta0_norm + (theta1_norm * x_norm)
        error = estimated_price_norm - y_norm

        # Gradients
        grad0 = (1/m) * error.sum()
        grad1 = (1/m) * (error * x_norm).sum()

        # Update params
        theta0_norm -= alpha * grad0
        theta1_norm -= alpha * grad1

        # Compute cost
        current_cost = ((error ** 2).sum()) / (2 * m)

        grad0_history.append(grad0)
        grad1_history.append(grad1)
        cost_history.append(current_cost)

        # Early stopping (skip first iteration)
        if prev_cost is not None:
            if prev_cost != 0 and abs(prev_cost - current_cost) / prev_cost < 1e-6:
                print(f"Stopped early at epoch {epoch}, cost={current_cost:.6f}")
                break

        prev_cost = current_cost  # update for next loop

    theta0 = y_mean + (y_std * theta0_norm) - ((y_std * theta1_norm * x_mean) / x_std)
    theta1 = (y_std / x_std) * theta1_norm

    print("Trained model:")
    print(f"theta0 (intercept) = {theta0:.2f}")
    print(f"theta1 (slope) = {theta1:.2f}")
    print(f"cost = {prev_cost}")

    with open("thetas.txt", "w") as f:
        f.write(f"{theta0},{theta1}")

    _, axes = plt.subplots(3, 1, figsize=(8, 10))

    y_pred = theta0 + (theta1 * x)

    # --- Plot 1 : data + model ---
    axes[0].scatter(x, df["price"], color="blue", label="Data")

    axes[0].plot(x, y_pred, color="red", label="Model")

    axes[0].set_xlabel("Mileage")
    axes[0].set_ylabel("Price")
    axes[0].legend()
    axes[0].set_title("Linear regression")

    # --- Plot 2 : gradients ---
    axes[1].plot(grad0_history, label="grad0 (intercept)")
    axes[1].plot(grad1_history, label="grad1 (pente)")

    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Gradient value")
    axes[1].legend()
    axes[1].set_title("Gradient evolution")

    # --- Plot 3 : cost ---
    axes[2].plot(cost_history)

    axes[2].set_xlabel("Epoch")
    axes[2].set_ylabel("Cost J")
    axes[2].set_title("Cost evolution")

    plt.tight_layout()
    plt.show()

def main():
    try:
        train_model("data.csv")
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
    return 0
    
if __name__ == "__main__":
    main()