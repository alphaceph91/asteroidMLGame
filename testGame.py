import pygame
import torch
from RLenv import RLenv
from DQN_agent import DQNAgent

def load_trained_agent(checkpoint_path="/models/best_dqn_policy.pth", state_dim=8, action_dim=6):
    agent = DQNAgent(state_dim, action_dim)
    agent.policy_net.load_state_dict(torch.load(checkpoint_path))
    agent.policy_net.eval()
    agent.epsilon = 0.0  #using greedy policy for evaluation
    return agent

def run_evaluation(episodes=5):
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("Autonomous Spaceship Evaluation")
    
    env = RLenv(800,600, debug=True)
    agent = load_trained_agent("/models/best_dqn_policy.pth")
    
    all_episode_rewards = []
    all_shooting_accuracies = []
    
    for ep in range(episodes):
        state_dict = env.reset()
        env.spaceship.missiles_fired = 0  
        state = [
            state_dict["spaceship_x"],
            state_dict["spaceship_y"],
            state_dict["asteroid_x"],
            state_dict["asteroid_y"],
            state_dict["asteroid_vel"],
            state_dict["missile_ready"],
            state_dict["normalized_distance"],
            state_dict["collision_risk"]
        ]
        ep_reward = 0
        running_episode = True
        clock = pygame.time.Clock()
        while running_episode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            
            action = agent.select_action(state)
            next_state_dict, reward, done = env.step(action)
            state = [
                next_state_dict["spaceship_x"],
                next_state_dict["spaceship_y"],
                next_state_dict["asteroid_x"],
                next_state_dict["asteroid_y"],
                next_state_dict["asteroid_vel"],
                next_state_dict["missile_ready"],
                next_state_dict["normalized_distance"],
                next_state_dict["collision_risk"]
            ]
            ep_reward += reward
            env.render(screen)
            clock.tick(30)
            
            if done:
                running_episode = False
        
        #computing shooting accuracy: asteroids_shot / missiles_fired
        if env.spaceship.missiles_fired > 0:
            shooting_accuracy = env.asteroids_shot / env.spaceship.missiles_fired
        else:
            shooting_accuracy = 0

        print(f"Episode {ep+1}: Total Reward = {ep_reward}, Missiles Fired = {env.spaceship.missiles_fired}, "
              f"Asteroids Shot = {env.asteroids_shot}, Shooting Accuracy = {shooting_accuracy:.2f}")
        all_episode_rewards.append(ep_reward)
        all_shooting_accuracies.append(shooting_accuracy)
    
    pygame.quit()
    
    avg_reward = sum(all_episode_rewards) / len(all_episode_rewards)
    avg_accuracy = sum(all_shooting_accuracies) / len(all_shooting_accuracies)
    print(f"Average Reward over {episodes} episodes: {avg_reward:.2f}")
    print(f"Average Shooting Accuracy over {episodes} episodes: {avg_accuracy:.2f}")

if __name__ == "__main__":
    run_evaluation(episodes=5)
