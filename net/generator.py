import numpy as np
import pandas as pd


class TrafficGenerator:
    def __init__(self, max_steps, n_vehicles_generated, car_ratio, real_speeds_dataset_path):
        self._n_vehicles_generated = n_vehicles_generated
        self._max_steps = max_steps
        self._car_ratio = car_ratio
        self._real_speeds_dataset_path = real_speeds_dataset_path

    def _write_routes_header(self, routes):
        print("""<routes>
            <vType accel="1.0" decel="4.5" id="standard_car" length="5.0" minGap="2.5" maxSpeed="100" sigma="0.5" />
            <vType id="bus" accel="1.0" decel="4.5" length="12.0" minGap="3.0" maxSpeed="100" sigma="0.5" />
            <route id="W_N" edges="W2TL TL2N"/>
            <route id="W_E" edges="W2TL TL2E"/>
            <route id="W_S" edges="W2TL TL2S"/>
            <route id="N_W" edges="N2TL TL2W"/>
            <route id="N_E" edges="N2TL TL2E"/>
            <route id="N_S" edges="N2TL TL2S"/>
            <route id="E_W" edges="E2TL TL2W"/>
            <route id="E_N" edges="E2TL TL2N"/>
            <route id="E_S" edges="E2TL TL2S"/>
            <route id="S_W" edges="S2TL TL2W"/>
            <route id="S_N" edges="S2TL TL2N"/>
            <route id="S_E" edges="S2TL TL2E"/>
            """, file=routes)

    def generate_route_file(self, seed):
        np.random.seed(seed)
        # Load real speed data from the dataset
        real_speeds_data = pd.read_csv(self._real_speeds_dataset_path, encoding='ISO-8859-1')
        real_speeds_data.drop(
            ['pk_id', 'target_type', 'object_type', 'object_status', 'junction_id', 'object_uuid', 'object_sub_brand',
             'object_brand', 'object_body_color', 'object_id', 'protocol_version', 'object_plate_color', ], axis=1,
            inplace=True)
        real_speeds_data.dropna(axis=1, how='all', inplace=True)
        real_speeds_data.dropna(axis=0, inplace=True)
        real_speeds_data = real_speeds_data.sample(frac=1).reset_index(drop=True)
        real_speeds_data = real_speeds_data[real_speeds_data['object_speed'] != 0]

        # Modify: Assign vehicle_type based on object_vehicle_class
        real_speeds_data['vehicle_type'] = np.where(real_speeds_data['object_vehicle_class'] == 99, 'standard_car',
                                                    'bus')

        # Sort the real speed data by timestamps
        real_speeds_data['time_stamp'] = pd.to_datetime(real_speeds_data['time_stamp'])
        real_speeds_data.sort_values(by='time_stamp', inplace=True)

        timings = np.sort(np.random.weibull(2, self._n_vehicles_generated))
        vehicle_gen_steps = np.rint(np.interp(timings, (timings.min(), timings.max()), (0, self._max_steps)))

        with open("routes.rou.xml", "w") as routes:
            self._write_routes_header(routes)

            for vehicle_counter, step in enumerate(vehicle_gen_steps):
                straight_or_turn = np.random.uniform()
                route_type, route_name = self._choose_route(straight_or_turn)

                # Get the corresponding speed from the real dataset
                real_speed = real_speeds_data.iloc[vehicle_counter]['object_speed']

                # Modify: Get vehicle_type from the 'vehicle_type' column
                vehicle_type = real_speeds_data.iloc[vehicle_counter]['vehicle_type']

                self._write_vehicle_entry(routes, vehicle_counter, vehicle_type, route_name, step, real_speed)

            self._write_routes_footer(routes)

    def _choose_route(self, straight_or_turn):
        if straight_or_turn < 0.57:
            route_type = "straight"
            route_name = np.random.choice(["W_E", "E_W", "N_S", "S_N"])
        else:
            route_type = "turn"
            route_name = np.random.choice(["W_N", "W_S", "N_W", "N_E", "E_N", "E_S", "S_W", "S_E"])
        return route_type, route_name

    def _write_vehicle_entry(self, routes, vehicle_counter, vehicle_type, route_name, step, random_speed):
        print(
            f'    <vehicle id="{vehicle_counter}" type="{vehicle_type}" route="{route_name}" depart="{step}" departLane="random" departSpeed="{random_speed}" />',
            file=routes,
        )

    def _write_routes_footer(self, routes):
        print("</routes>", file=routes)


# Example usage:
real_speeds_dataset_path = "/Users/lts/Documents/assignment/cp2/cp2/data/flw_fusion_junctions_data_311241-100812-100900.csv"
TrafficGenerator(6000, 4000, real_speeds_dataset_path=real_speeds_dataset_path, car_ratio=0.86).generate_route_file(0)
