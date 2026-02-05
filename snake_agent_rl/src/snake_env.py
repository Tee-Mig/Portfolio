from __future__ import annotations

from dataclasses import dataclass
from collections import deque
from typing import Deque, Tuple, Dict, Any, Optional

import numpy as np
import gymnasium as gym
from gymnasium import spaces


UP = (-1, 0)
RIGHT = (0, 1)
DOWN = (1, 0)
LEFT = (0, -1)

DIRS = [UP, RIGHT, DOWN, LEFT]
DIR_TO_IDX = {UP: 0, RIGHT: 1, DOWN: 2, LEFT: 3}


@dataclass
class SnakeConfig:
    grid_size: int = 10
    init_length: int = 3
    max_steps_without_food: int = 200

    step_penalty: float = -0.01
    food_reward: float = 10.0
    death_penalty: float = -10.0

    shaping: bool = True
    shaping_reward: float = 0.1

    safety_shaping: bool = True
    safety_weight: float = 0.2
    trap_penalty: float = 2.0
    require_tail_path: bool = True
    tail_path_bonus: float = 0.2

    obs_size: int = 10


class SnakeEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, config: SnakeConfig = SnakeConfig(), seed: Optional[int] = None):
        super().__init__()
        self.cfg = config
        self.grid_size = int(self.cfg.grid_size)
        self._seed = seed

        n = int(self.cfg.obs_size)
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(4, n, n), dtype=np.float32)
        self.action_space = spaces.Discrete(3)

        self.np_random = None

        # State
        self.snake: Deque[Tuple[int, int]] = deque()
        self.snake_set: set[Tuple[int, int]] = set()
        self.occ = np.zeros((self.grid_size, self.grid_size), dtype=np.bool_)

        self.direction = RIGHT
        self.food: Tuple[int, int] = (0, 0)

        self.steps = 0
        self.steps_since_food = 0
        self._prev_food_dist = None

        self.reset(seed=seed)

    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        if seed is not None:
            self._seed = seed

        if self.np_random is None:
            self.np_random = np.random.default_rng(self._seed)

        self.steps = 0
        self.steps_since_food = 0

        center_r = self.grid_size // 2
        center_c = self.grid_size // 2

        self.snake.clear()
        self.snake_set.clear()
        self.occ.fill(False)

        self.direction = RIGHT

        for i in range(self.cfg.init_length):
            pos = (center_r, center_c - i)
            self.snake.append(pos)
            self.snake_set.add(pos)
            self.occ[pos[0], pos[1]] = True

        self._spawn_food()
        self._prev_food_dist = self._food_distance()

        return self._get_obs(), self._get_info()

    def step(self, action: int):
        assert self.action_space.contains(action), f"Invalid action: {action}"

        self.steps += 1
        self.steps_since_food += 1

        dir_idx = DIR_TO_IDX[self.direction]
        if action == 0:
            dir_idx = (dir_idx - 1) % 4
        elif action == 2:
            dir_idx = (dir_idx + 1) % 4
        self.direction = DIRS[dir_idx]

        head_r, head_c = self.snake[0]
        dr, dc = self.direction
        new_head = (head_r + dr, head_c + dc)

        terminated = False
        truncated = False
        reward = self.cfg.step_penalty

        if not (0 <= new_head[0] < self.grid_size and 0 <= new_head[1] < self.grid_size):
            terminated = True
            reward = self.cfg.death_penalty
            return self._get_obs(), reward, terminated, truncated, self._get_info(terminated, truncated)

        tail = self.snake[-1]
        will_eat = (new_head == self.food)

        if new_head in self.snake_set and not (new_head == tail and not will_eat):
            terminated = True
            reward = self.cfg.death_penalty
            return self._get_obs(), reward, terminated, truncated, self._get_info(terminated, truncated)

        self.snake.appendleft(new_head)
        self.snake_set.add(new_head)
        self.occ[new_head[0], new_head[1]] = True

        if will_eat:
            reward = self.cfg.food_reward
            reward += 1.0
            self.steps_since_food = 0
            self._spawn_food()
        else:
            old_tail = self.snake.pop()
            if old_tail != new_head:
                self.snake_set.remove(old_tail)
                self.occ[old_tail[0], old_tail[1]] = False

        if self.cfg.safety_shaping and not terminated:
            head = self.snake[0]
            tail = self.snake[-1]
            tail_free = (not will_eat)

            reachable = self._bfs_reachable_occ(head, tail, tail_free)
            reachable_norm = reachable / float(self.grid_size * self.grid_size)
            reward += self.cfg.safety_weight * reachable_norm

            if reachable < len(self.snake):
                scale = len(self.snake) / float(self.grid_size * self.grid_size)
                reward -= self.cfg.trap_penalty * (0.5 + 1.5 * scale)

            if self.cfg.require_tail_path:
                if self._bfs_path_exists_occ(head, tail, tail, tail_free):
                    reward += self.cfg.tail_path_bonus
                else:
                    reward -= self.cfg.tail_path_bonus

        if self.cfg.shaping and not terminated:
            new_dist = self._food_distance()
            prev_dist = self._prev_food_dist if self._prev_food_dist is not None else new_dist
            if new_dist < prev_dist:
                reward += self.cfg.shaping_reward
            elif new_dist > prev_dist:
                reward -= self.cfg.shaping_reward
            self._prev_food_dist = new_dist

        if self.steps_since_food >= self.cfg.max_steps_without_food:
            truncated = True

        return self._get_obs(), reward, terminated, truncated, self._get_info(terminated, truncated)

    def render_ascii(self) -> str:
        grid = [["." for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        fr, fc = self.food
        grid[fr][fc] = "F"
        for i, (r, c) in enumerate(self.snake):
            grid[r][c] = "H" if i == 0 else "o"
        return "\n".join(" ".join(row) for row in grid)

    def _bfs_reachable_occ(self, start: Tuple[int, int], tail: Tuple[int, int], tail_free: bool) -> int:
        n = self.grid_size
        q = deque([start])
        visited = np.zeros((n, n), dtype=np.bool_)
        visited[start[0], start[1]] = True
        count = 1

        while q:
            r, c = q.popleft()
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n and not visited[nr, nc]:
                    if self.occ[nr, nc]:
                        if not (tail_free and (nr, nc) == tail):
                            continue
                    visited[nr, nc] = True
                    count += 1
                    q.append((nr, nc))
        return count

    def _bfs_path_exists_occ(self, start: Tuple[int, int], goal: Tuple[int, int], tail: Tuple[int, int], tail_free: bool) -> bool:
        n = self.grid_size
        q = deque([start])
        visited = np.zeros((n, n), dtype=np.bool_)
        visited[start[0], start[1]] = True

        while q:
            r, c = q.popleft()
            if (r, c) == goal:
                return True
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n and not visited[nr, nc]:
                    if self.occ[nr, nc]:
                        if not (tail_free and (nr, nc) == tail):
                            continue
                    visited[nr, nc] = True
                    q.append((nr, nc))
        return False

    def _spawn_food(self):
        empties = self.grid_size * self.grid_size - len(self.snake_set)
        if empties <= 0:
            self.food = self.snake[0]
            return

        while True:
            r = int(self.np_random.integers(0, self.grid_size))
            c = int(self.np_random.integers(0, self.grid_size))
            if (r, c) not in self.snake_set:
                self.food = (r, c)
                return

    def _food_distance(self) -> float:
        hr, hc = self.snake[0]
        fr, fc = self.food
        return float(abs(hr - fr) + abs(hc - fc))

    def _get_obs(self) -> np.ndarray:
        n = int(self.cfg.obs_size)
        obs = np.zeros((4, n, n), dtype=np.float32)

        gs = self.grid_size
        if gs < n:
            obs[3, gs:, :] = 1.0
            obs[3, :, gs:] = 1.0

        fr, fc = self.food
        obs[2, fr, fc] = 1.0

        for i, (r, c) in enumerate(self.snake):
            if i == 0:
                obs[0, r, c] = 1.0
            else:
                obs[1, r, c] = 1.0

        return obs

    def _get_info(self, terminated: bool = False, truncated: bool = False) -> Dict[str, Any]:
        return {
            "grid_size": self.grid_size,
            "steps": self.steps,
            "snake_length": len(self.snake),
            "steps_since_food": self.steps_since_food,
            "food": self.food,
            "head": self.snake[0],
            "direction": DIR_TO_IDX[self.direction],
            "terminated": terminated,
            "truncated": truncated,
        }
