# Asteroid Machine Learning Game
AsteroidMLGame is a python based game consisting of a spaceship and asteroids. The spaceship is controlled by a Deep Q-Network (DQN) agent. The spaceship must navigate through an asteroid field. The agent learns to dodge asteroids and fire heat-seeking missiles to destroy them based on the astroids trajectory and close proximity to the spaceship. The project is built using [PyGame](https://github.com/pygame/pygame), [PyTorch](https://pytorch.org/) and standard Python libraries. The game is trained and tested for Linux.


## Features

### Custom Reinforcement Learning Environment
- The spaceship is controlled by a DQN agent that learns from the environment.
- The environment features a detection circle around the spaceship. When an asteroid enters this circle and is approaching, the spaceship fires a heat-seeking missile.
- Asteroids have varied sizes, speeds, and horizontal movements. Asteroids even interact with each other via simple collision physics.
- The environment maintains various metrics, including score, number of asteroids shot, missiles fired, and shooting accuracy.

### Deep Q-Network (DQN) Agent:
- The agent learns a policy using experience replay and periodically updates a target network.
- Training metrics (total reward, epsilon) are logged in a CSV file, and performance plots are generated.
- Model checkpoints are saved in the models folder, including both the final model and the best-performing model.

### Deep Q-Network (DQN) Agent:
- A separate evaluation script (load_checkpoint.py) loads the trained model checkpoint and runs test episodes with a greedy policy (epsilon set to 0).
- During evaluation, performance metrics such as shooting accuracy (asteroids shot / missiles fired) are computed and printed.
