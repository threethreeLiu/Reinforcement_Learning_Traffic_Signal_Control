import os
import sys
import sumolib
import traci
import signal
import numpy as np
import pandas as pd

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")


class SumoSimulation:
    def __init__(self, net_file, route_file, max_depart_delay, waiting_time_memory, time_to_teleport):
        self.net_file = net_file
        self.current_step = 0
        self.route_file = route_file
        self.max_depart_delay = max_depart_delay
        self.waiting_time_memory = waiting_time_memory
        self.time_to_teleport = time_to_teleport
        self.sumo_cmd = [
            sumolib.checkBinary("sumo-gui" if LIBSUMO else "sumo"),
            "-n", net_file,
            "-r", route_file,
            "--max-depart-delay", str(max_depart_delay),
            "--waiting-time-memory", str(waiting_time_memory),
            "--time-to-teleport", str(time_to_teleport),
        ]
        self.vehicles = []
        self.speeds = []
        self.waiting_times = []

    def handle_interrupt(self, signum, frame):
        print("Simulation interrupted. Closing SUMO.")
        traci.close()
        sys.exit(0)

    def run_simulation(self):
        if LIBSUMO:
            # Start only to retrieve traffic light information
            traci.start(self.sumo_cmd)
            conn = traci
        else:
            traci.start(self.sumo_cmd, label="init_connection")
            conn = traci.getConnection("init_connection")
        signal.signal(signal.SIGINT, self.handle_interrupt)
        try:
            # Initial simulation step to retrieve traffic light information
            conn.simulationStep()
            metrics_list = []
            while conn.simulation.getMinExpectedNumber() > 0:
                conn.simulationStep()
                # Additional logic to retrieve information about vehicles
                self.vehicles = conn.vehicle.getIDList()
                self.speeds = [conn.vehicle.getSpeed(vehicle) for vehicle in self.vehicles]
                self.waiting_times = [conn.vehicle.getWaitingTime(vehicle) for vehicle in self.vehicles]

                # Real-time metrics retrieval
                metrics = self.get_simulation_metrics()
                metrics["step"] = self.current_step  # Add the current simulation step to the metrics
                metrics_list.append(metrics)
                self.current_step += 1

            traci.close()
            metrics_df = pd.DataFrame(metrics_list)
            metrics_df.to_csv("outputs/real/simulation_metrics.csv", index=False)
            print("Simulation metrics saved to simulation_real.xlsx")

        except traci.TraCIException as e:
            print(f"Error running SUMO simulation: {e}")

    def get_simulation_metrics(self):
        return {
            "step": self.current_step,
            "system_total_stopped": sum(int(speed < 0.1) for speed in self.speeds),
            "system_total_waiting_time": sum(self.waiting_times),
            "system_mean_waiting_time": 0.0 if not self.vehicles else np.mean(self.waiting_times),
            "system_mean_speed": 0.0 if not self.vehicles else np.mean(self.speeds),
        }


# Example usage
net_file_path = "/Users/lts/Documents/assignment/cp2/cp2/net/intersection.net.xml"
route_file_path = "/Users/lts/Documents/assignment/cp2/cp2/net/routes.rou.xml"
max_depart_delay_value = 60
waiting_time_memory_value = 300
time_to_teleport_value = 1000
LIBSUMO = True

sumo_simulation = SumoSimulation(
    net_file_path,
    route_file_path,
    max_depart_delay_value,
    waiting_time_memory_value,
    time_to_teleport_value
)

sumo_simulation.run_simulation()
