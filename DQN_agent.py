import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque
from tqdm import trange  # Progress bar
import pygame
import matplotlib.pyplot as plt
from RLenv import RLenv

class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, output_dim)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class DQNAgent:
    def __init__(self, state_dim, action_dim, lr=1e-3, gamma=0.99, 
                 epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01, 
                 batch_size=32, memory_size=10000):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        
        self.memory = deque(maxlen=memory_size)
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.policy_net = DQN(state_dim, action_dim).to(self.device)
        self.target_net = DQN(state_dim, action_dim).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.lr)
        self.loss_fn = nn.MSELoss()
    
    def select_action(self, state):
        if random.random() < self.epsilon:
            return random.randrange(self.action_dim)
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            q_values = self.policy_net(state_tensor)
        return int(torch.argmax(q_values).item())
    
    def store_transition(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def sample_memory(self):
        return random.sample(self.memory, self.batch_size)
    
    def train_step(self):
        if len(self.memory) < self.batch_size:
            return
        
        batch = self.sample_memory()
        states, actions, rewards, next_states, dones = zip(*batch)
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).unsqueeze(1).to(self.device)
        
        current_q = self.policy_net(states).gather(1, actions)
        next_q = self.target_net(next_states).max(1)[0].unsqueeze(1)
        target_q = rewards + (1 - dones) * self.gamma * next_q
        
        loss = self.loss_fn(current_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
    
    def update_epsilon(self):
        self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)
    
    def update_target_network(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())

if __name__ == "__main__":
    # Create log folder if it doesn't exist.
    log_dir = "log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    # Create models folder if it doesn't exist.
    models_dir = "models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    
    # Open CSV log file and write header.
    log_file_path = os.path.join(log_dir, "training_metrics.csv")
    log_file = open(log_file_path, "w")
    log_file.write("Episode,Total Reward,Epsilon\n")
    
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("Asteroid Game")
    
    # Our state vector has 8 dimensions.
    state_dim = 8
    action_dim = 6

    env = RLenv(800,600, debug=True)
    agent = DQNAgent(state_dim, action_dim)

    num_episodes = 200
    target_update_freq = 10

    all_rewards = []
    best_reward = -float("inf")

    progress_bar = trange(num_episodes, desc="Training Episodes")
    for episode in progress_bar:
        state_dict = env.reset()
        state = [state_dict["spaceship_x"],
                 state_dict["spaceship_y"],
                 state_dict["asteroid_x"],
                 state_dict["asteroid_y"],
                 state_dict["asteroid_vel"],
                 state_dict["missile_ready"],
                 state_dict["normalized_distance"],
                 state_dict["collision_risk"]]
        total_reward = 0
        done = False

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            
            action = agent.select_action(state)
            next_state_dict, reward, done = env.step(action)
            next_state = [next_state_dict["spaceship_x"],
                          next_state_dict["spaceship_y"],
                          next_state_dict["asteroid_x"],
                          next_state_dict["asteroid_y"],
                          next_state_dict["asteroid_vel"],
                          next_state_dict["missile_ready"],
                          next_state_dict["normalized_distance"],
                          next_state_dict["collision_risk"]]
            agent.store_transition(state, action, reward, next_state, done)
            agent.train_step()
            state = next_state
            total_reward += reward

            if episode % 10 == 0:
                env.render(screen)
                pygame.time.delay(50)
        
        agent.update_epsilon()
        if episode % target_update_freq == 0:
            agent.update_target_network()
        
        all_rewards.append(total_reward)
        progress_bar.set_postfix({"Total Reward": total_reward, "Epsilon": agent.epsilon})
        log_file.write(f"{episode+1},{total_reward},{agent.epsilon}\n")
        
        if total_reward > best_reward:
            best_reward = total_reward
            torch.save(agent.policy_net.state_dict(), os.path.join(models_dir, "best_dqn_policy.pth"))
    
    log_file.close()
    
    torch.save(agent.policy_net.state_dict(), os.path.join(models_dir, "dqn_policy.pth"))
    print("Model checkpoint saved as dqn_policy.pth in the models folder")
    
    pygame.quit()
    
    plt.figure(figsize=(10,5))
    plt.plot(all_rewards, label="Total Reward per Episode")
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.title("Training Performance Metrics")
    plt.grid(True)
    plt.legend()
    plt.savefig(os.path.join(log_dir, "training_performance.png"))
    plt.show()