from stable_baselines3.dqn.dqn import DQN

from sumo_rl import SumoEnvironment

env = SumoEnvironment(
    net_file="net/intersection.net.xml",
    single_agent=True,
    route_file="net/routes.rou.xml",
    out_csv_name="outputs/dqn/dqn",
    use_gui=False,
    num_seconds=5400,
    yellow_time=4,
    min_green=5,
    max_green=60
)

model = DQN(
    env=env,
    policy="MlpPolicy",
    learning_rate=1e-3,
    learning_starts=0,
    buffer_size=50000,
    train_freq=1,
    target_update_interval=500,
    exploration_fraction=0.05,
    exploration_final_eps=0.01,
    verbose=1
)
model.learn(total_timesteps=100000)
model.save("dqn_model_delay")
