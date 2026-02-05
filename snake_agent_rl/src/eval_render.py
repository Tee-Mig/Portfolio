import argparse
import time
from pathlib import Path

import numpy as np
import torch

from snake_env import SnakeEnv, SnakeConfig
from dqn_agent import DQNCNN


def resolve_model_path(arg: str) -> str:
    arg_l = arg.lower()
    if arg_l in ("best", "last"):
        fname = "best.pt" if arg_l == "best" else "last.pt"

        p0 = Path("runs") / "models" / fname
        if p0.exists():
            return p0.as_posix()

        root = Path("runs")
        if root.exists():
            candidates = sorted(
                root.glob(f"**/models/{fname}"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if candidates:
                return candidates[0].as_posix()

        return (Path("runs") / fname).as_posix()

    return arg


def infer_in_channels_from_state_dict(sd: dict) -> int:
    w = sd.get("conv.0.weight", None)
    if w is None:
        raise KeyError("conv.0.weight not found in checkpoint (unexpected model key names).")
    return int(w.shape[1])


@torch.no_grad()
def greedy_action(model: torch.nn.Module, state: np.ndarray, device: str, in_channels: int) -> int:
    if in_channels == 3:
        state = state[:3]
    elif in_channels == 4:
        pass
    else:
        raise ValueError(f"Unsupported in_channels={in_channels} (expected 3 or 4).")

    state_t = torch.as_tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
    q = model(state_t)
    return int(torch.argmax(q, dim=1).item())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="best", help="best | last | custom path (.pt)")
    parser.add_argument("--grid-size", type=int, default=10, help="playable grid size (e.g. 10)")
    parser.add_argument("--obs-size", type=int, default=10, help="observation size used by CNN (must match training)")
    parser.add_argument("--seed", type=int, default=None, help="random seed (default random)")
    parser.add_argument("--device", type=str, default=None, help="cpu | cuda (default auto)")
    parser.add_argument("--sleep", type=float, default=0.05, help="delay between frames")
    parser.add_argument(
        "--no-shaping",
        action="store_true",
        help="disable env shaping/safety shaping during eval (recommended to see true skill)",
    )
    args = parser.parse_args()

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    seed = args.seed if args.seed is not None else int(np.random.randint(0, 10_000))

    # Env
    cfg = SnakeConfig(
        grid_size=int(args.grid_size),
        obs_size=int(args.obs_size),
        safety_shaping=not args.no_shaping,
        shaping=not args.no_shaping,
    )
    env = SnakeEnv(cfg, seed=seed)

    model_path = resolve_model_path(args.model)
    if not Path(model_path).exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    state_dict = torch.load(model_path, map_location=device)
    in_channels = infer_in_channels_from_state_dict(state_dict)

    model = DQNCNN(
        input_channels=in_channels,
        grid_size=int(args.obs_size),
        action_dim=env.action_space.n,
    ).to(device)
    model.load_state_dict(state_dict)
    model.eval()

    print(f"Loaded: {model_path}")
    print(f"Device: {device}")
    print(f"Seed: {seed}")
    print(f"Playable grid: {args.grid_size}x{args.grid_size} | Obs size: {args.obs_size} | Model in_channels: {in_channels}")
    if args.no_shaping:
        print("Eval mode: NO shaping (greedy skill only)")
    else:
        print("Eval mode: shaping ENABLED (closer to training reward)")

    state, _ = env.reset(seed=seed)
    total_reward = 0.0
    steps = 0

    while True:
        action = greedy_action(model, state, device, in_channels)
        state, reward, terminated, truncated, info = env.step(action)

        total_reward += float(reward)
        steps += 1

        print("\x1b[2J\x1b[H", end="")
        print(env.render_ascii())
        print(f"\nsteps={steps} | length={info['snake_length']} | reward={total_reward:.1f}")

        time.sleep(args.sleep)

        if terminated or truncated:
            break

    print("\nDone.")
    print("Final length:", info["snake_length"])
    print("Total reward:", total_reward)


if __name__ == "__main__":
    main()
