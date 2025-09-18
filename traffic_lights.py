# traffic_lights.py

import pygame
import math
import time
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class LightState(Enum):
    RED = "red"
    GREEN = "green"

@dataclass
class RoadDirection:
    angle: float
    name: str

class TrafficLight:
    def __init__(self, intersection_center_x, intersection_center_y, road_config, intersection_size=100):
        self.center_x = intersection_center_x
        self.center_y = intersection_center_y
        self.intersection_size = intersection_size
        self.road_config = road_config
        self.light_radius = 25
        self.segment_width = 8
        self.road_directions = {}
        self.light_states = {}
        
        self.green_duration = 15.0 # The 15-second rule
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

    # traffic_lights.py
    def _get_road_directions_from_config(self):
        directions = {}
        if self.road_config['junction_type'] == 'cross':
            # It reads the exact angles you set in the GUI!
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
        """--- NEW: Implements the '1 by 1' cycling logic ---"""
        if not self.cycle_order: return

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
    
    def get_light_state_for_direction(self, direction_angle: float) -> LightState:
        """Get traffic light state for a vehicle traveling at a specific angle"""
        direction_angle = direction_angle % 360
        
        # Find the closest road direction to the vehicle's travel angle
        closest_direction = None
        min_angle_diff = float('inf')
        
        for direction_name, road_direction in self.road_directions.items():
            angle_diff = abs(direction_angle - road_direction.angle)
            # Handle wrap-around (e.g., 350° vs 10°)
            angle_diff = min(angle_diff, 360 - angle_diff)
            
            if angle_diff < min_angle_diff:
                min_angle_diff = angle_diff
                closest_direction = direction_name
        
        return self.light_states.get(closest_direction, LightState.RED)
    
    def is_red_light_for_angle(self, direction_angle: float) -> bool:
        """Check if the light is red for a vehicle traveling at a specific angle"""
        return self.get_light_state_for_direction(direction_angle) == LightState.RED
    
    def is_green_light_for_angle(self, direction_angle: float) -> bool:
        """Check if the light is green for a vehicle traveling at a specific angle"""
        return self.get_light_state_for_direction(direction_angle) == LightState.GREEN

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
