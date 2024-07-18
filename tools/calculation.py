class RouteGenerator:
    @staticmethod
    def generate_route_xml(heading_angle):
        heading_degrees = heading_angle * 1e-4
        direction = (360 - heading_degrees) % 360
        route_id = None
        if 0 <= direction < 30 or 330 <= direction < 360:
            route_id = "N_S"
        elif 30 <= direction < 60:
            route_id = "N_W"
        elif 60 <= direction < 120:
            route_id = "E_W"
        elif 120 <= direction < 150:
            route_id = "E_N"
        elif 150 <= direction < 210:
            route_id = "S_N"
        elif 210 <= direction < 240:
            route_id = "S_E"
        elif 240 <= direction < 300:
            route_id = 'W_E'
        elif 300 <= direction < 330:
            route_id = "W_S"
        elif 30 <= direction < 120:
            route_id = "N_E"
        elif 120 <= direction < 210:
            route_id = "E_S"
        elif 210 <= direction < 300:
            route_id = "S_W"
        elif 300 <= direction < 30:
            route_id = 'W_N'
        return route_id


heading_angle = 4500
route_generator = RouteGenerator()
route_id = route_generator.generate_route_xml(heading_angle)
print(route_id)
