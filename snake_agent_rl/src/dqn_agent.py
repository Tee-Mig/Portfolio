import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


class DQNCNN(nn.Module):
    def __init__(self, input_channels: int, grid_size: int, action_dim: int):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(input_channels, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(),
        )

        with torch.no_grad():
            dummy = torch.zeros(1, input_channels, grid_size, grid_size)
            conv_out = self.conv(dummy)
            flat_dim = conv_out.view(1, -1).shape[1]

        self.head = nn.Sequential(
            nn.Linear(flat_dim, 256),
            nn.ReLU(),
            nn.Linear(256, action_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.conv(x)
        z = z.view(z.size(0), -1)
        return self.head(z)


class DQNAgent:
    def __init__(
        self,
        grid_size: int,
        action_dim: int,
        lr: float = 1e-3,
        gamma: float = 0.99,
        epsilon_start: float = 1.0,
        epsilon_min: float = 0.02,
        epsilon_decay: float = 0.999,
        device: str = "cpu",
        use_amp: bool | None = None,
        input_channels: int = 4,
    ):
        self.device = device
        self.gamma = float(gamma)

        self.epsilon = float(epsilon_start)
        self.epsilon_min = float(epsilon_min)
        self.epsilon_decay = float(epsilon_decay)

        self.action_dim = int(action_dim)

        self.policy_net = DQNCNN(input_channels=input_channels, grid_size=grid_size, action_dim=action_dim).to(self.device)
        self.target_net = DQNCNN(input_channels=input_channels, grid_size=grid_size, action_dim=action_dim).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.loss_fn = nn.MSELoss()

        if use_amp is None:
            use_amp = self.device.startswith("cuda")
        self.use_amp = bool(use_amp)
        self.scaler = torch.cuda.amp.GradScaler(enabled=self.use_amp)

    @torch.no_grad()
    def select_actions_batch(self, states: np.ndarray) -> np.ndarray:
        """
        states: np.ndarray shape (B, 4, N, N)
        returns actions: np.ndarray shape (B,)
        """
        B = states.shape[0]
        rand_mask = (np.random.rand(B) < self.epsilon)

        actions = np.empty((B,), dtype=np.int64)

        if rand_mask.any():
            actions[rand_mask] = np.random.randint(self.action_dim, size=rand_mask.sum(), dtype=np.int64)

        if (~rand_mask).any():
            s = torch.as_tensor(states[~rand_mask], dtype=torch.float32, device=self.device)
            q = self.policy_net(s)
            actions[~rand_mask] = torch.argmax(q, dim=1).detach().cpu().numpy().astype(np.int64)

        return actions

    @torch.no_grad()
    def select_action(self, state: np.ndarray) -> int:
        if np.random.rand() < self.epsilon:
            return int(np.random.randint(self.action_dim))

        state_t = torch.as_tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)  # (1,4,N,N)
        q_values = self.policy_net(state_t)
        return int(torch.argmax(q_values, dim=1).item())

    def train_step(self, batch) -> float:
        states, actions, rewards, next_states, dones = batch

        states_t = torch.as_tensor(states, dtype=torch.float32, device=self.device)
        actions_t = torch.as_tensor(actions, dtype=torch.int64, device=self.device).unsqueeze(1)
        rewards_t = torch.as_tensor(rewards, dtype=torch.float32, device=self.device).unsqueeze(1)
        next_states_t = torch.as_tensor(next_states, dtype=torch.float32, device=self.device)
        dones_t = torch.as_tensor(dones, dtype=torch.float32, device=self.device).unsqueeze(1)

        self.optimizer.zero_grad(set_to_none=True)

        with torch.cuda.amp.autocast(enabled=self.use_amp):
            q_values = self.policy_net(states_t).gather(1, actions_t)
            with torch.no_grad():
                next_q_values = self.target_net(next_states_t).max(1, keepdim=True)[0]
            target = rewards_t + self.gamma * next_q_values * (1.0 - dones_t)
            loss = self.loss_fn(q_values, target)

        if self.use_amp:
            self.scaler.scale(loss).backward()
            self.scaler.step(self.optimizer)
            self.scaler.update()
        else:
            loss.backward()
            self.optimizer.step()

        return float(loss.item())

    def update_target(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
