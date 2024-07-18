import os
import sys
from datetime import datetime

from sumo_rl import SumoEnvironment
from sumo_rl.agents import QLAgent
from sumo_rl.exploration import EpsilonGreedy

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")

if __name__ == "__main__":

    experiment_time = str(datetime.now()).split(".")[0]
    out_csv = f"outputs/ql/ql-"

    env = SumoEnvironment(
        net_file="net/intersection.net.xml",
        route_file='net/routes.rou.xml',
        out_csv_name=out_csv,
        use_gui=True,
        num_seconds=5400,
        yellow_time=4,
        min_green=5,
        max_green=60,
    )

    for run in range(1, 10):
        initial_states = env.reset()
        ql_agents = {
            ts: QLAgent(
                starting_state=env.encode(initial_states[ts], ts),
                state_space=env.observation_space,
                action_space=env.action_space,
                alpha=0.001,
                gamma=500,
                exploration_strategy=EpsilonGreedy(
                    initial_epsilon=0.05, min_epsilon=0.01, decay=1.0
                ),
            )
            for ts in env.ts_ids
        }
        done = {"__all__": False}
        infos = []
        while not done["__all__"]:
            actions = {ts: ql_agents[ts].act() for ts in ql_agents.keys()}
            s, r, done, _ = env.step(action=actions)
            for agent_id in ql_agents.keys():
                ql_agents[agent_id].learn(next_state=env.encode(s[agent_id], agent_id), reward=r[agent_id])
    env.save_csv(out_csv, run)
    env.close()
