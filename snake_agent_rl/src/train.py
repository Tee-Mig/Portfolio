import argparse
import time
import random
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import gymnasium as gym

from snake_env import SnakeEnv, SnakeConfig
from replay_buffer import ReplayBuffer
from dqn_agent import DQNAgent


# -------------------------
# Utils
# -------------------------
def get_info_value(infos, key: str, i: int):
    if isinstance(infos, dict):
        v = infos.get(key, None)
        if v is None:
            return None
        try:
            return v[i]
        except Exception:
            return v

    if isinstance(infos, (list, tuple)):
        try:
            return infos[i].get(key, None)
        except Exception:
            return None

    return None


def length_from_obs(obs_i: np.ndarray) -> int:
    return int((obs_i[0] > 0.5).sum() + (obs_i[1] > 0.5).sum())


def get_snake_length(infos, i: int, next_obs_i: np.ndarray) -> int:
    finfo = get_info_value(infos, "final_info", i)
    if finfo is not None and isinstance(finfo, dict) and "snake_length" in finfo:
        return int(finfo["snake_length"])
    finfo_u = get_info_value(infos, "_final_info", i)
    if finfo_u is not None and isinstance(finfo_u, dict) and "snake_length" in finfo_u:
        return int(finfo_u["snake_length"])

    fobs = get_info_value(infos, "final_observation", i)
    if fobs is not None:
        return length_from_obs(fobs)
    fobs_u = get_info_value(infos, "_final_observation", i)
    if fobs_u is not None:
        return length_from_obs(fobs_u)

    val = get_info_value(infos, "snake_length", i)
    if val is None:
        val = get_info_value(infos, "_snake_length", i)
    if val is not None:
        return int(val)

    return length_from_obs(next_obs_i)


def greedy_action_from_model(model: torch.nn.Module, obs: np.ndarray, device: str) -> int:
    x = torch.as_tensor(obs, dtype=torch.float32, device=device).unsqueeze(0)
    with torch.no_grad():
        q = model(x)
    return int(torch.argmax(q, dim=1).item())


def evaluate_greedy(
    model: torch.nn.Module,
    device: str,
    grid_size: int,
    init_length: int,
    n_episodes: int = 50,
    seed_base: int = 12345,
) -> dict:
    cfg = SnakeConfig(
        grid_size=grid_size,
        obs_size=10,
        safety_shaping=False,
        shaping=False,
    )

    lengths = []
    foods = []

    for k in range(n_episodes):
        env = SnakeEnv(cfg, seed=seed_base + k * 9973)
        obs, _ = env.reset(seed=seed_base + k * 7919)

        while True:
            a = greedy_action_from_model(model, obs, device)
            obs, r, terminated, truncated, info = env.step(a)
            if terminated or truncated:
                L = int(info["snake_length"])
                lengths.append(L)
                foods.append(L - init_length)
                break

    lengths = np.array(lengths, dtype=np.int32)
    foods = np.array(foods, dtype=np.int32)

    return {
        "n": int(n_episodes),
        "mean_len": float(lengths.mean()),
        "max_len": int(lengths.max()),
        "mean_foods": float(foods.mean()),
        "max_foods": int(foods.max()),
        "sr_len_ge_10": float((lengths >= 10).mean()),
        "sr_len_ge_20": float((lengths >= 20).mean()),
    }


def make_env(grid_size: int, obs_size: int, seed: int):
    def _thunk():
        cfg = SnakeConfig(
            grid_size=grid_size,
            obs_size=obs_size,

            safety_shaping=True,
            safety_weight=0.30,
            trap_penalty=4.0,
            require_tail_path=True,
            tail_path_bonus=0.30,

            shaping=False,
            shaping_reward=0.0,
        )
        return SnakeEnv(cfg, seed=seed)
    return _thunk


def safe_close_env(venv):
    try:
        venv.close()
    except Exception:
        pass


def make_run_dir() -> Path:
    Path("runs").mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    rnd = random.randint(100000, 999999)
    run_dir = Path("runs") / f"run_{ts}_{rnd}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def infer_run_dir_from_metrics(metrics_path: Path) -> Path:
    mp = metrics_path.resolve()
    if len(mp.parents) < 2:
        raise ValueError(f"Cannot infer run_dir from metrics path: {metrics_path}")
    return mp.parents[1]


def train(
    resume_metrics_path: str | None,
    num_envs: int,
    fresh: bool,
    total_steps: int,
):
    # -------------------------
    # Curriculum setup
    # -------------------------
    obs_size = 10
    if total_steps < 5_000_000:
        raise ValueError("For V3 curriculum, total_steps should be >= 5_000_000")

    phases = [
        {"grid_size": 6, "steps": 2_000_000},
        {"grid_size": 8, "steps": 3_000_000},
        {"grid_size": 10, "steps": total_steps - 5_000_000},
    ]

    torch.set_float32_matmul_precision("high")
    torch.backends.cudnn.benchmark = True

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("Device:", device)

    init_length = 3

    # -------------------------
    # Run directory setup
    # -------------------------
    if resume_metrics_path is not None:
        metrics_path = Path(resume_metrics_path)
        if not metrics_path.exists():
            raise FileNotFoundError(metrics_path)
        run_dir = infer_run_dir_from_metrics(metrics_path)
        print(f"Resuming run: {run_dir.as_posix()}")
    else:
        run_dir = make_run_dir()
        print(f"Starting NEW run → {run_dir.as_posix()}")

    models_dir = run_dir / "models"
    metrics_dir = run_dir / "metrics"
    ckpt_dir = run_dir / "checkpoints"
    models_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    if resume_metrics_path is None:
        metrics_path = metrics_dir / "metrics.parquet"

    # -------------------------
    # Agent (kept across phases)
    # -------------------------
    agent = DQNAgent(
        grid_size=obs_size,
        action_dim=3,
        device=device,
        lr=5e-4 if device == "cuda" else 1e-3,
        epsilon_min=0.02,
        epsilon_decay=0.999,
        input_channels=4,
    )

    # Replay buffer (kept across steps but CLEARED per phase)
    buffer = ReplayBuffer(capacity=1_200_000 if device == "cuda" else 300_000)

    # Hyperparams
    batch_size = 2048 if device == "cuda" else 256
    warmup_steps = 300_000
    target_update = 50_000
    train_every = 2
    gradient_steps = 8

    # Epsilon schedule (global across phases)
    eps_start = 1.0
    eps_end = agent.epsilon_min
    eps_decay_steps = 6_000_000

    # Saving / logging cadence (global_step-based)
    save_every_steps = 50_000
    flush_metrics_every_steps = 50_000
    print_every_steps = 25_000
    checkpoint_every_steps = 250_000
    greedy_eval_every_steps = 250_000
    greedy_eval_episodes = 50

    # Metrics
    logs: list[dict] = []
    global_step = 0
    total_updates = 0
    episode_counter = 0
    best_reward = float("-inf")
    best_length = init_length

    # -------------------------
    # Resume metrics (optional)
    # -------------------------
    if resume_metrics_path is not None:
        df_prev = pd.read_parquet(metrics_path)
        if len(df_prev) > 0:
            logs = df_prev.to_dict("records")
            episode_counter = int(df_prev["episode"].max()) + 1
            best_reward = float(pd.to_numeric(df_prev.get("reward", pd.Series([])), errors="coerce").max())
            if "length" in df_prev.columns:
                best_length = int(pd.to_numeric(df_prev["length"], errors="coerce").max())
        print(f"Resuming metrics from {metrics_path.as_posix()}")

    # -------------------------
    # Load weights (optional)
    # -------------------------
    last_path = models_dir / "last.pt"
    if (not fresh) and last_path.exists():
        agent.policy_net.load_state_dict(torch.load(last_path, map_location=device))
        agent.target_net.load_state_dict(agent.policy_net.state_dict())
        print("Loaded model weights:", last_path.as_posix())
    else:
        print("Starting from scratch (fresh model)")

    t0 = time.time()
    interrupted = False

    def set_epsilon(step: int):
        progress = min(1.0, step / float(eps_decay_steps))
        agent.epsilon = max(eps_end, eps_start - progress * (eps_start - eps_end))

    try:
        # -------------------------
        # Phase loop
        # -------------------------
        for phase_id, phase in enumerate(phases, start=1):
            phase_grid = phase["grid_size"]
            phase_steps = int(phase["steps"])
            phase_start_step = global_step
            phase_end_step = phase_start_step + phase_steps

            print(f"\n=== PHASE {phase_id}/3 | playable_grid={phase_grid}x{phase_grid} | steps={phase_steps:,} ===")

            # Create env for this phase
            base_seed = int(time.time()) + phase_id * 10_000
            env_fns = [make_env(phase_grid, obs_size, base_seed + i * 1000) for i in range(num_envs)]

            try:
                venv = gym.vector.AsyncVectorEnv(env_fns, autoreset_mode="disabled")
            except TypeError:
                venv = gym.vector.AsyncVectorEnv(env_fns)

            buffer.clear()
            print("Replay buffer cleared.")

            # Reset envs
            obs, _ = venv.reset()

            # Per-env trackers
            ep_rewards = np.zeros(num_envs, dtype=np.float32)
            ep_steps = np.zeros(num_envs, dtype=np.int32)
            ep_lengths = np.full(num_envs, init_length, dtype=np.int32)

            # Phase training loop
            while global_step < phase_end_step:
                set_epsilon(global_step)

                actions = agent.select_actions_batch(obs)
                next_obs, rewards, terms, truncs, infos = venv.step(actions)
                dones = np.logical_or(terms, truncs)

                for i in range(num_envs):
                    buffer.push(obs[i], int(actions[i]), float(rewards[i]), next_obs[i], bool(dones[i]))

                    ep_rewards[i] += float(rewards[i])
                    ep_steps[i] += 1

                    if dones[i]:
                        ep_lengths[i] = get_snake_length(infos, i, next_obs[i])

                        ep_r = float(ep_rewards[i])
                        ep_len = int(ep_lengths[i])
                        ep_s = int(ep_steps[i])

                        logs.append(
                            {
                                "episode": episode_counter,
                                "reward": ep_r,
                                "length": ep_len,
                                "steps": ep_s,
                                "epsilon": float(agent.epsilon),
                                "loss": None,
                                "phase": phase_id,
                                "playable_grid": phase_grid,
                                "global_step": global_step,
                            }
                        )

                        saved_best = False
                        best_path = models_dir / "best.pt"
                        if ep_len > best_length:
                            best_length = ep_len
                            torch.save(agent.policy_net.state_dict(), best_path)
                            saved_best = True

                        if ep_r > best_reward and not saved_best:
                            best_reward = ep_r
                            torch.save(agent.policy_net.state_dict(), best_path)

                        episode_counter += 1
                        ep_rewards[i] = 0.0
                        ep_steps[i] = 0
                        ep_lengths[i] = init_length

                obs = next_obs
                global_step += num_envs

                # Target update
                if global_step % target_update < num_envs:
                    agent.update_target()

                # Train
                if len(buffer) >= warmup_steps and (global_step % train_every < num_envs):
                    last_loss = None
                    for _ in range(gradient_steps):
                        last_loss = agent.train_step(buffer.sample(batch_size))
                        total_updates += 1
                    if logs:
                        logs[-1]["loss"] = last_loss

                # Save last.pt
                if global_step % save_every_steps < num_envs:
                    torch.save(agent.policy_net.state_dict(), models_dir / "last.pt")

                # Flush metrics
                if global_step % flush_metrics_every_steps < num_envs:
                    pd.DataFrame(logs).to_parquet(metrics_path, index=False)

                # Full checkpoint
                if global_step % checkpoint_every_steps < num_envs:
                    ckpt = {
                        "run_dir": run_dir.as_posix(),
                        "global_step": global_step,
                        "episode_counter": episode_counter,
                        "epsilon": agent.epsilon,
                        "policy_state": agent.policy_net.state_dict(),
                        "target_state": agent.target_net.state_dict(),
                        "optim_state": agent.optimizer.state_dict(),
                        "best_length": best_length,
                        "best_reward": best_reward,
                        "phase_id": phase_id,
                        "phase_grid": phase_grid,
                    }
                    ckpt_path = ckpt_dir / f"ckpt_steps_{global_step}.pt"
                    torch.save(ckpt, ckpt_path)

                # Greedy eval
                if global_step % greedy_eval_every_steps < num_envs and global_step >= warmup_steps:
                    agent.policy_net.eval()
                    stats = evaluate_greedy(
                        model=agent.policy_net,
                        device=device,
                        grid_size=10,  # evaluate on 10x10 always
                        init_length=init_length,
                        n_episodes=greedy_eval_episodes,
                        seed_base=12345 + global_step,
                    )
                    agent.policy_net.train()
                    print(
                        f"[GREEDY EVAL @steps={global_step:,}] "
                        f"mean_len={stats['mean_len']:.1f} max_len={stats['max_len']} "
                        f"mean_foods={stats['mean_foods']:.1f} max_foods={stats['max_foods']} "
                        f"sr_len>=10={stats['sr_len_ge_10']:.0%} sr_len>=20={stats['sr_len_ge_20']:.0%}"
                    )

                # Print stats
                if global_step % print_every_steps < num_envs:
                    dt = time.time() - t0
                    env_steps_per_sec = global_step / max(dt, 1e-9)
                    updates_per_sec = total_updates / max(dt, 1e-9)

                    tail = logs[-100:] if logs else []
                    if tail:
                        lens = [int(x["length"]) for x in tail]
                        foods = [L - init_length for L in lens]
                        avg_r = sum(float(x["reward"]) for x in tail) / len(tail)
                        avg_len = sum(lens) / len(lens)
                        max_len_100 = max(lens)
                        avg_foods = sum(foods) / len(foods)
                        max_foods_100 = max(foods)
                        sr_ge_4 = sum(1 for L in lens if L >= 4) / len(lens)
                        sr_ge_10 = sum(1 for L in lens if L >= 10) / len(lens)
                        sr_ge_20 = sum(1 for L in lens if L >= 20) / len(lens)
                        sr_ge_50 = sum(1 for L in lens if L >= 50) / len(lens)
                        sr_ge_75 = sum(1 for L in lens if L >= 75) / len(lens)
                    else:
                        avg_r = avg_len = avg_foods = float("nan")
                        max_len_100 = max_foods_100 = None
                        sr_ge_4 = sr_ge_10 = sr_ge_20 = sr_ge_50 = sr_ge_75 = float("nan")

                    coverage = best_length / float(phase_grid * phase_grid)
                    best_foods = best_length - init_length

                    print(
                        f"steps={global_step:,} | episodes={episode_counter:,} | eps={agent.epsilon:.3f} "
                        f"| env-steps/sec={env_steps_per_sec:.1f} | updates/sec={updates_per_sec:.1f} "
                        f"| buffer={len(buffer):,} | avg100 len={avg_len:.1f} (foods={avg_foods:.1f}) "
                        f"| max100 len={max_len_100} (foods={max_foods_100}) "
                        f"| SR len>=4:{sr_ge_4:.0%} len>=10:{sr_ge_10:.0%} len>=20:{sr_ge_20:.0%} "
                        f"len>=50:{sr_ge_50:.0%} len>=75:{sr_ge_75:.0%} "
                        f"| best_len={best_length} (foods={best_foods}, cov={coverage:.0%}) "
                        f"| avg100 reward={avg_r:.1f} best_reward={best_reward:.1f}"
                    )

            safe_close_env(venv)

    except KeyboardInterrupt:
        interrupted = True
        print("Interrupted. Saving...")

    # Final save
    torch.save(agent.policy_net.state_dict(), models_dir / "last.pt")
    pd.DataFrame(logs).to_parquet(metrics_path, index=False)
    print(f"Saved: {metrics_path.as_posix()} (interrupted={interrupted})")
    print(f"Run dir: {run_dir.as_posix()}")
    print(f"Models:  {(models_dir / 'best.pt').as_posix()} , {(models_dir / 'last.pt').as_posix()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", type=str, default=None, help="path to metrics parquet inside a run dir")
    parser.add_argument("--num-envs", type=int, default=64)
    parser.add_argument("--fresh", action="store_true", help="start from scratch (ignore last.pt)")
    parser.add_argument("--total-steps", type=int, default=20_000_000, help="total env steps to run (>=5M)")
    args = parser.parse_args()

    train(
        resume_metrics_path=args.resume,
        num_envs=args.num_envs,
        fresh=args.fresh,
        total_steps=args.total_steps,
    )
