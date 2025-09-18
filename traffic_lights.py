# traffic_lights.py# traffic_lights.py



import pygameimport pygame

import mathimport math

import timeimport time

from dataclasses import dataclassfrom dataclasses import dataclass

from typing import List, Optionalfrom typing import List, Optional

from enum import Enumfrom enum import Enum



class LightState(Enum):class LightState(Enum):

    RED = "red"    RED = "red"

    GREEN = "green"    GREEN = "green"



@dataclass@dataclass

class RoadDirection:class RoadDirection:

    angle: float    angle: float

    name: str    name: str



class TrafficLight:class TrafficLight:

    def __init__(self, intersection_center_x, intersection_center_y, road_config, intersection_size=100):    def __init__(self, intersection_center_x, intersection_center_y, road_config, intersection_size=100):

        self.center_x = intersection_center_x        self.center_x = intersection_center_x

        self.center_y = intersection_center_y        self.center_y = intersection_center_y

        self.intersection_size = intersection_size        self.intersection_size = intersection_size

        self.road_config = road_config        self.road_config = road_config

        self.light_radius = 25        self.light_radius = 25

        self.segment_width = 8        self.segment_width = 8

        self.road_directions = {}        self.road_directions = {}

        self.light_states = {}        self.light_states = {}

                

        self.green_duration = 10.0  # 10-second cycles (our enhancement)<<<<<<< HEAD

        self.cycle_start_time = time.time()        self.green_duration = 10.0  # Changed from 15.0 to 10.0 seconds

        =======

        # NEW: Logic for 1-by-1 cycling (from remote)        # traffic_lights.py

        self.cycle_order = []

        self.current_green_index = 0import pygame

        import math

        self.colors = { LightState.RED: (255, 50, 50), LightState.GREEN: (50, 255, 50) }import time

        from dataclasses import dataclass

        self.update_road_config(road_config) # Initialize everythingfrom typing import List, Optional

from enum import Enum

    def update_road_config(self, new_road_config):

        # Only update if the config has actually changed (our enhancement)class LightState(Enum):

        if hasattr(self, 'road_config') and self.road_config == new_road_config:    RED = "red"

            return    GREEN = "green"

            

        self.road_config = new_road_config@dataclass

        self.road_directions = self._get_road_directions_from_config()class RoadDirection:

        # NEW: Define the order for cycling (from remote)    angle: float

        self.cycle_order = ['top', 'right', 'bottom', 'left']    name: str

        # Filter out roads that don't exist in the current junction type

        self.cycle_order = [road for road in self.cycle_order if road in self.road_directions]class TrafficLight:

        self._initialize_light_states()    def __init__(self, intersection_center_x, intersection_center_y, road_config, intersection_size=100):

        self.cycle_start_time = time.time()  # Reset timing when config changes (our enhancement)        self.center_x = intersection_center_x

        self.center_y = intersection_center_y

    def _get_road_directions_from_config(self):        self.intersection_size = intersection_size

        directions = {}        self.road_config = road_config

        if self.road_config['junction_type'] == 'cross':        self.light_radius = 25

            directions['top'] = RoadDirection(self.road_config['top_angle'], 'top')        self.segment_width = 8

            directions['right'] = RoadDirection(self.road_config['right_angle'], 'right')         self.road_directions = {}

            directions['bottom'] = RoadDirection(self.road_config['bottom_angle'], 'bottom')        self.light_states = {}

            directions['left'] = RoadDirection((self.road_config['right_angle'] + 180) % 360, 'left')        

        elif self.road_config['junction_type'] == 't':        self.green_duration = 10.0  # 10-second cycles (our enhancement)

            # Simplified for now        self.cycle_start_time = time.time()

            pass        

        return directions        # NEW: Logic for 1-by-1 cycling (from remote)

            self.cycle_order = []

    def _initialize_light_states(self):        self.current_green_index = 0

        for direction_name in self.road_directions.keys():        

            self.light_states[direction_name] = LightState.RED        self.colors = { LightState.RED: (255, 50, 50), LightState.GREEN: (50, 255, 50) }

                

        # NEW: Start with the first road in cycle order as green (from remote)        self.update_road_config(road_config) # Initialize everything

        if self.cycle_order:

            self.current_green_index = 0    def update_road_config(self, new_road_config):

            current_green_road = self.cycle_order[self.current_green_index]        # Only update if the config has actually changed (our enhancement)

            if current_green_road in self.light_states:        if hasattr(self, 'road_config') and self.road_config == new_road_config:

                self.light_states[current_green_road] = LightState.GREEN            return

                

    def update_timing(self):        self.road_config = new_road_config

        if time.time() - self.cycle_start_time >= self.green_duration:        self.road_directions = self._get_road_directions_from_config()

            self._switch_light_phases()        # NEW: Define the order for cycling (from remote)

            self.cycle_start_time = time.time()        self.cycle_order = ['top', 'right', 'bottom', 'left']

            # Filter out roads that don't exist in the current junction type

    def _switch_light_phases(self):        self.cycle_order = [road for road in self.cycle_order if road in self.road_directions]

        # NEW: 1-by-1 cycling logic (from remote) with our debug output        self._initialize_light_states()

        if self.cycle_order:        self.cycle_start_time = time.time()  # Reset timing when config changes (our enhancement)

            # Set current green road to red

            current_green_road = self.cycle_order[self.current_green_index]    def _get_road_directions_from_config(self):

            self.light_states[current_green_road] = LightState.RED        directions = {}

                    if self.road_config['junction_type'] == 'cross':

            # Move to next road            directions['top'] = RoadDirection(self.road_config['top_angle'], 'top')

            self.current_green_index = (self.current_green_index + 1) % len(self.cycle_order)            directions['right'] = RoadDirection(self.road_config['right_angle'], 'right') 

            next_green_road = self.cycle_order[self.current_green_index]            directions['bottom'] = RoadDirection(self.road_config['bottom_angle'], 'bottom')

            self.light_states[next_green_road] = LightState.GREEN            directions['left'] = RoadDirection((self.road_config['right_angle'] + 180) % 360, 'left')

                    elif self.road_config['junction_type'] == 't':

            print(f"Traffic Light: Switched to {next_green_road.upper()} GREEN")  # Our debug output            # Simplified for now

            pass

    # Simplified, direct methods to check light state (our enhancement)        return directions

    def get_light_state_for_road(self, road_name: str) -> Optional[LightState]:    

        """Gets the light state directly by the road's name ('top', 'left', etc.)."""    def _initialize_light_states(self):

        return self.light_states.get(road_name)        for direction_name in self.road_directions.keys():

            self.light_states[direction_name] = LightState.RED

    def is_red_light(self, road_name: str) -> bool:        

        """Checks if the light for a specific road is RED."""        # NEW: Start with the first road in cycle order as green (from remote)

        return self.get_light_state_for_road(road_name) == LightState.RED        if self.cycle_order:

            self.current_green_index = 0

    def is_green_light(self, road_name: str) -> bool:            current_green_road = self.cycle_order[self.current_green_index]

        """Checks if the light for a specific road is GREEN."""            if current_green_road in self.light_states:

        return self.get_light_state_for_road(road_name) == LightState.GREEN                self.light_states[current_green_road] = LightState.GREEN

        

    def get_remaining_time(self):    def update_timing(self):

        """Get the remaining time in seconds for the current light phase (our enhancement)"""        if time.time() - self.cycle_start_time >= self.green_duration:

        elapsed_time = time.time() - self.cycle_start_time            self._switch_light_phases()

        remaining = self.green_duration - elapsed_time            self.cycle_start_time = time.time()

        return max(0, remaining)    

        def _switch_light_phases(self):

    def get_current_phase_info(self):        # NEW: 1-by-1 cycling logic (from remote) with our debug output

        """Get info about current phase for display (our enhancement)"""        if self.cycle_order:

        remaining = self.get_remaining_time()            # Set current green road to red

        if self.cycle_order and self.current_green_index < len(self.cycle_order):            current_green_road = self.cycle_order[self.current_green_index]

            current_road = self.cycle_order[self.current_green_index]            self.light_states[current_green_road] = LightState.RED

            current_phase = f"{current_road.upper()} GREEN"            

        else:            # Move to next road

            current_phase = "Unknown"            self.current_green_index = (self.current_green_index + 1) % len(self.cycle_order)

        return current_phase, remaining            next_green_road = self.cycle_order[self.current_green_index]

                    self.light_states[next_green_road] = LightState.GREEN

    def draw(self, screen):            

        pygame.draw.circle(screen, (80, 80, 80), (int(self.center_x), int(self.center_y)), self.light_radius)            print(f"Traffic Light: Switched to {next_green_road.upper()} GREEN")  # Our debug output

        for direction_name, direction_info in self.road_directions.items():

            if direction_name in self.light_states:    # Simplified, direct methods to check light state (our enhancement)

                light_color = self.colors[self.light_states[direction_name]]    def get_light_state_for_road(self, road_name: str) -> Optional[LightState]:

                angle_rad = math.radians(direction_info.angle)        """Gets the light state directly by the road's name ('top', 'left', etc.)."""

                segment_distance = self.light_radius - 5        return self.light_states.get(road_name)

                segment_x = self.center_x + segment_distance * math.cos(angle_rad)

                segment_y = self.center_y + segment_distance * math.sin(angle_rad)    def is_red_light(self, road_name: str) -> bool:

                pygame.draw.circle(screen, light_color, (int(segment_x), int(segment_y)), self.segment_width)        """Checks if the light for a specific road is RED."""

        return self.get_light_state_for_road(road_name) == LightState.RED

class TrafficLightManager:

    def __init__(self):    def is_green_light(self, road_name: str) -> bool:

        self.traffic_lights: List[TrafficLight] = []        """Checks if the light for a specific road is GREEN."""

                return self.get_light_state_for_road(road_name) == LightState.GREEN

    def add_traffic_light(self, intersection_x, intersection_y, road_config, intersection_size=100):    

        light = TrafficLight(intersection_x, intersection_y, road_config, intersection_size)    def get_remaining_time(self):

        self.traffic_lights.append(light)        """Get the remaining time in seconds for the current light phase (our enhancement)"""

        return light        elapsed_time = time.time() - self.cycle_start_time

                remaining = self.green_duration - elapsed_time

    def update_all(self):        return max(0, remaining)

        for light in self.traffic_lights:    

            light.update_timing()    def get_current_phase_info(self):

                    """Get info about current phase for display (our enhancement)"""

    def draw_all(self, screen):        remaining = self.get_remaining_time()

        for light in self.traffic_lights:        if self.cycle_order and self.current_green_index < len(self.cycle_order):

            light.draw(screen)            current_road = self.cycle_order[self.current_green_index]

                        current_phase = f"{current_road.upper()} GREEN"

    def get_nearest_traffic_light(self, x, y, max_distance=200) -> Optional[TrafficLight]:        else:

        nearest_light = None            current_phase = "Unknown"

        min_distance = float('inf')        return current_phase, remaining

        for light in self.traffic_lights:        

            distance = math.hypot(light.center_x - x, light.center_y - y)    def draw(self, screen):

            if distance < min_distance:        pygame.draw.circle(screen, (80, 80, 80), (int(self.center_x), int(self.center_y)), self.light_radius)

                min_distance = distance        for direction_name, direction_info in self.road_directions.items():

                nearest_light = light            if direction_name in self.light_states:

        return nearest_light if min_distance <= max_distance else None                light_color = self.colors[self.light_states[direction_name]]

                    angle_rad = math.radians(direction_info.angle)

    def update_road_config(self, new_road_config):                segment_distance = self.light_radius - 5

        for light in self.traffic_lights:                segment_x = self.center_x + segment_distance * math.cos(angle_rad)

            light.update_road_config(new_road_config)                segment_y = self.center_y + segment_distance * math.sin(angle_rad)
                pygame.draw.circle(screen, light_color, (int(segment_x), int(segment_y)), self.segment_width)

class TrafficLightManager:
    def __init__(self):
        self.traffic_lights: List[TrafficLight] = []
        
    def add_traffic_light(self, intersection_x, intersection_y, road_config, intersection_size=100):
        light = TrafficLight(intersection_x, intersection_y, road_config, intersection_size)
        self.traffic_lights.append(light)
        return light
        
    def update_all(self):
        for light in self.traffic_lights:
            light.update_timing()
            
    def draw_all(self, screen):
        for light in self.traffic_lights:
            light.draw(screen)
            
    def get_nearest_traffic_light(self, x, y, max_distance=200) -> Optional[TrafficLight]:
        nearest_light = None
        min_distance = float('inf')
        for light in self.traffic_lights:
            distance = math.hypot(light.center_x - x, light.center_y - y)
            if distance < min_distance:
                min_distance = distance
                nearest_light = light
        return nearest_light if min_distance <= max_distance else None
    
    def update_road_config(self, new_road_config):
        for light in self.traffic_lights:
            light.update_road_config(new_road_config)
>>>>>>> b7ff80acdf3d16908caa584e8d4b791f7fc34d49
        self.cycle_start_time = time.time()
        
        # --- NEW: Logic for 1-by-1 cycling ---
        self.cycle_order = []
        self.current_green_index = 0
        
        self.colors = { LightState.RED: (255, 50, 50), LightState.GREEN: (50, 255, 50) }
        
        self.update_road_config(road_config) # Initialize everything

    def update_road_config(self, new_road_config):
        self.road_config = new_road_config
        self.road_directions = self._get_road_directions_from_config()
        # --- NEW: Define the order for cycling ---
        self.cycle_order = ['top', 'right', 'bottom', 'left']
        # Filter out roads that don't exist in the current junction type
        self.cycle_order = [name for name in self.cycle_order if name in self.road_directions]
        self._initialize_light_states()

    def _get_road_directions_from_config(self):
        directions = {}
        if self.road_config['junction_type'] == 'cross':
            directions['top'] = RoadDirection(self.road_config['top_angle'], 'top')
            directions['right'] = RoadDirection(self.road_config['right_angle'], 'right') 
            directions['bottom'] = RoadDirection(self.road_config['bottom_angle'], 'bottom')
            directions['left'] = RoadDirection((self.road_config['right_angle'] + 180) % 360, 'left')
        return directions # T-junction logic can be added later
    
    def _initialize_light_states(self):
        for direction_name in self.road_directions.keys():
            self.light_states[direction_name] = LightState.RED
        
        if self.cycle_order:
            # Set the first road in the cycle to green
            first_green = self.cycle_order[0]
            self.light_states[first_green] = LightState.GREEN
        self.current_green_index = 0
        self.cycle_start_time = time.time()
    
    def update_timing(self):
        # --- NEW: Check the mode from the config ---
        mode = self.road_config.get('traffic_light_mode', 'timer')

        if mode == 'timer':
            if time.time() - self.cycle_start_time >= self.green_duration:
                self._switch_light_phases()
                self.cycle_start_time = time.time()
        elif mode == 'smart':
            # This is where you will add your smart logic later
            pass
    
    def _switch_light_phases(self):
<<<<<<< HEAD
        if self.road_config['junction_type'] == 'cross':
            # If top is green, switch to left/right green, and vice-versa
            if self.light_states.get('top') == LightState.GREEN:
                self.light_states.update({'top': LightState.RED, 'bottom': LightState.RED, 'left': LightState.GREEN, 'right': LightState.GREEN})
                print("Traffic Light: Switched to East-West GREEN")
            else:
                self.light_states.update({'top': LightState.GREEN, 'bottom': LightState.GREEN, 'left': LightState.RED, 'right': LightState.RED})
                print("Traffic Light: Switched to North-South GREEN")
=======
        """--- NEW: Implements the '1 by 1' cycling logic ---"""
        if not self.cycle_order: return
>>>>>>> b7ff80acdf3d16908caa584e8d4b791f7fc34d49

        # Turn the current green light RED
        current_green_road = self.cycle_order[self.current_green_index]
        self.light_states[current_green_road] = LightState.RED

        # Move to the next light in the cycle
        self.current_green_index = (self.current_green_index + 1) % len(self.cycle_order)
        
        # Turn the new light GREEN
        next_green_road = self.cycle_order[self.current_green_index]
        self.light_states[next_green_road] = LightState.GREEN

    def is_red_light(self, road_name: str) -> bool:
        return self.light_states.get(road_name) == LightState.RED

<<<<<<< HEAD
    def is_green_light(self, road_name: str) -> bool:
        """Checks if the light for a specific road is GREEN."""
        return self.get_light_state_for_road(road_name) == LightState.GREEN
    
    def get_remaining_time(self):
        """Get the remaining time in seconds for the current light phase"""
        elapsed_time = time.time() - self.cycle_start_time
        remaining = self.green_duration - elapsed_time
        return max(0, remaining)
    
    def get_current_phase_info(self):
        """Get info about current phase for display"""
        remaining = self.get_remaining_time()
        if self.light_states.get('top') == LightState.GREEN:
            current_phase = "North-South GREEN"
        else:
            current_phase = "East-West GREEN"
        return current_phase, remaining
    
    def update_road_config(self, new_road_config):
        # Only update if the config has actually changed
        if self.road_config != new_road_config:
            self.road_config = new_road_config
            self.road_directions = self._get_road_directions_from_config()
            self._initialize_light_states()
            self.cycle_start_time = time.time()  # Reset timing when config changes
        
=======
>>>>>>> b7ff80acdf3d16908caa584e8d4b791f7fc34d49
    def draw(self, screen):
        pygame.draw.circle(screen, (80, 80, 80), (self.center_x, self.center_y), self.light_radius)
        for name, direction in self.road_directions.items():
            if name in self.light_states:
                color = self.colors[self.light_states[name]]
                angle_rad = math.radians(direction.angle)
                x = self.center_x + (self.light_radius - 5) * math.cos(angle_rad)
                y = self.center_y + (self.light_radius - 5) * math.sin(angle_rad)
                pygame.draw.circle(screen, color, (int(x), int(y)), self.segment_width)

class TrafficLightManager:
    def __init__(self):
        self.traffic_lights: List[TrafficLight] = []
        
    def add_traffic_light(self, x, y, road_config, intersection_size=100):
        light = TrafficLight(x, y, road_config, intersection_size)
        self.traffic_lights.append(light)
        return light
        
    def update_all(self):
        for light in self.traffic_lights:
            light.update_timing()
            
    def draw_all(self, screen):
        for light in self.traffic_lights:
            light.draw(screen)
            
    def get_nearest_traffic_light(self, x, y, max_distance=200) -> Optional[TrafficLight]:
        # ... (This method is unchanged) ...
        nearest = None
        min_dist = float('inf')
        for light in self.traffic_lights:
            dist = math.hypot(light.center_x - x, light.center_y - y)
            if dist < min_dist:
                min_dist = dist
                nearest = light
        return nearest if min_dist <= max_distance else None
    
    def update_road_config(self, new_road_config):
        for light in self.traffic_lights:
            light.update_road_config(new_road_config)
