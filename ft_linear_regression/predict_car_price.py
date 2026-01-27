import pandas as pd

def predict_csv(file_to_predict):
    try:
        df = pd.read_csv(file_to_predict)
    except Exception as e:
        print(f"[Error]: {e}")

    with open("thetas.txt", "r") as f:
        thetas = f.read()
    theta0 = thetas.split(",")[0]
    theta1 = thetas.split(",")[1]

    with (
        open("data_to_predict.csv", "r") as f_in,
        open("predictions.csv", "w") as f_out
        ):
        for line in f_in:
            if ("km" in line):
                f_out.write(line)
                continue
            km = float(line.strip())
            f_out.write(line.strip() + "," + str(float(theta0) + float(theta1) * km) + "\n")


def main():
    predict_csv("data_to_predict.csv")
    return 0
    
if __name__ == "__main__":
    main()