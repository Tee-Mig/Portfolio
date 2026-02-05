import argparse
from pathlib import Path

import numpy as np
import torch
import pygame

from snake_env import SnakeEnv, SnakeConfig
from dqn_agent import DQNCNN


# -------------------------
# Model helpers
# -------------------------
def infer_in_channels_from_state_dict(sd: dict) -> int:
    w = sd.get("conv.0.weight", None)
    if w is None:
        raise KeyError("conv.0.weight not found in checkpoint")
    return int(w.shape[1])


@torch.no_grad()
def greedy_action(model, obs, device, in_channels: int) -> int:
    if in_channels == 3:
        obs = obs[:3]
    x = torch.as_tensor(obs, dtype=torch.float32, device=device).unsqueeze(0)
    q = model(x)
    return int(torch.argmax(q, dim=1).item())


# -------------------------
# Render helpers
# -------------------------
def draw_grid(screen, grid_size, cell, grid_col=(32, 32, 32)):
    for r in range(grid_size):
        y = r * cell
        pygame.draw.line(screen, grid_col, (0, y), (grid_size * cell, y), 1)
    for c in range(grid_size):
        x = c * cell
        pygame.draw.line(screen, grid_col, (x, 0), (x, grid_size * cell), 1)


def draw_food(screen, fr, fc, cell):
    x = fc * cell + cell // 2
    y = fr * cell + cell // 2
    pygame.draw.circle(screen, (235, 80, 80), (x, y), max(3, cell // 6))


def draw_snake_dark_square(screen, snake, cell):
    if not snake:
        return

    BODY_COL = (25, 110, 60)
    HEAD_COL = (20, 95, 50)
    NOTCH_COL = (15, 75, 40)

    # body blocks
    body_size = int(cell * 0.85)
    body_pad = (cell - body_size) // 2

    # head block
    head_size = int(cell * 0.95)
    head_pad = (cell - head_size) // 2

    # --- body ---
    for r, c in snake[1:]:
        rect = pygame.Rect(
            c * cell + body_pad,
            r * cell + body_pad,
            body_size,
            body_size,
        )
        pygame.draw.rect(screen, BODY_COL, rect)

    # --- head ---
    hr, hc = snake[0]
    head_rect = pygame.Rect(
        hc * cell + head_pad,
        hr * cell + head_pad,
        head_size,
        head_size,
    )
    pygame.draw.rect(screen, HEAD_COL, head_rect)

    # --- direction ---
    if len(snake) >= 2:
        nr, nc = snake[1]
        dr = hr - nr
        dc = hc - nc
    else:
        dr, dc = 0, 1

    notch_w = int(head_size * 0.35)
    notch_h = int(head_size * 0.20)

    cx, cy = head_rect.center

    if dr == -1:  # up
        notch = pygame.Rect(cx - notch_w // 2, head_rect.top, notch_w, notch_h)
    elif dr == 1:  # down
        notch = pygame.Rect(cx - notch_w // 2, head_rect.bottom - notch_h, notch_w, notch_h)
    elif dc == -1:  # left
        notch = pygame.Rect(head_rect.left, cy - notch_w // 2, notch_h, notch_w)
    else:  # right
        notch = pygame.Rect(head_rect.right - notch_h, cy - notch_w // 2, notch_h, notch_w)

    pygame.draw.rect(screen, NOTCH_COL, notch)


def render_text_fit(font_name: str, text: str, max_width: int, base_size: int, min_size: int, color):
    size = base_size
    while size >= min_size:
        f = pygame.font.SysFont(font_name, size)
        s = f.render(text, True, color)
        if s.get_width() <= max_width:
            return f, s
        size -= 1
    f = pygame.font.SysFont(font_name, min_size)
    s = f.render(text, True, color)
    return f, s


def draw_ui_minimal(screen, W, ui_y, ui_h, line1: str, line2: str):
    pygame.draw.rect(screen, (14, 14, 14), pygame.Rect(0, ui_y, W, ui_h))
    pad = 16
    max_w = W - 2 * pad

    _, surf1 = render_text_fit("consolas", line1, max_w, base_size=17, min_size=12, color=(235, 235, 235))
    _, surf2 = render_text_fit("consolas", line2, max_w, base_size=14, min_size=11, color=(180, 180, 180))

    x1 = (W - surf1.get_width()) // 2
    x2 = (W - surf2.get_width()) // 2

    total_h = surf1.get_height() + 5 + surf2.get_height()
    y_start = ui_y + (ui_h - total_h) // 2

    screen.blit(surf1, (x1, y_start))
    screen.blit(surf2, (x2, y_start + surf1.get_height() + 5))


# -------------------------
# Main
# -------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True, help="path to .pt")
    parser.add_argument("--grid-size", type=int, default=10)
    parser.add_argument("--obs-size", type=int, default=10)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--cell", type=int, default=56, help="pixel size of a cell")
    parser.add_argument("--fps", type=int, default=8, help="default slower speed")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    seed = args.seed if args.seed is not None else int(np.random.randint(0, 10_000))

    cfg = SnakeConfig(
        grid_size=args.grid_size,
        obs_size=args.obs_size,
        safety_shaping=False,
        shaping=False,
    )
    env = SnakeEnv(cfg, seed=seed)

    model_path = Path(args.model)
    if not model_path.exists():
        raise FileNotFoundError(model_path)

    sd = torch.load(model_path, map_location=device)
    in_channels = infer_in_channels_from_state_dict(sd)

    model = DQNCNN(input_channels=in_channels, grid_size=args.obs_size, action_dim=env.action_space.n).to(device)
    model.load_state_dict(sd)
    model.eval()

    pygame.init()
    cell = int(args.cell)
    W = int(args.grid_size) * cell
    ui_h = 72
    H = int(args.grid_size) * cell + ui_h
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Snake RL")
    clock = pygame.time.Clock()

    obs, _ = env.reset(seed=seed)
    total_reward = 0.0
    steps = 0

    fps = int(args.fps)
    paused = False
    running = True

    while running:
        clock.tick(max(1, fps))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    obs, _ = env.reset(seed=seed)
                    total_reward = 0.0
                    steps = 0
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    fps = max(1, fps - 1)
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    fps = min(120, fps + 1)

        if not paused:
            a = greedy_action(model, obs, device, in_channels)
            obs, r, terminated, truncated, info = env.step(a)
            total_reward += float(r)
            steps += 1

            if terminated or truncated:
                pygame.time.wait(250)
                obs, _ = env.reset(seed=seed)
                total_reward = 0.0
                steps = 0

        # draw
        screen.fill((18, 18, 18))
        draw_grid(screen, int(args.grid_size), cell)

        fr, fc = env.food
        draw_food(screen, fr, fc, cell)

        draw_snake_dark_square(screen, list(env.snake), cell)

        ui_y = int(args.grid_size) * cell
        line1 = f"len={len(env.snake)}   steps={steps}   reward={total_reward:.1f}   fps={fps}   seed={seed}"
        line2 = "SPACE: pause   |   +/-: speed   |   R: reset"
        draw_ui_minimal(screen, W, ui_y, ui_h, line1, line2)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
