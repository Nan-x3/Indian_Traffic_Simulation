# traffic_lights.py

import pygame
import math
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
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
        self.road_directions = self._get_road_directions_from_config()
        self.light_states = {}
        self._initialize_light_states()
        
        self.green_duration = 15.0
        self.cycle_start_time = time.time()
        
        self.colors = {
            LightState.RED: (255, 50, 50),
            LightState.GREEN: (50, 255, 50)     
        }
        
    def _get_road_directions_from_config(self):
        directions = {}
        if self.road_config['junction_type'] == 'cross':
            directions['top'] = RoadDirection(self.road_config['top_angle'], 'top')
            directions['right'] = RoadDirection(self.road_config['right_angle'], 'right') 
            directions['bottom'] = RoadDirection(self.road_config['bottom_angle'], 'bottom')
            directions['left'] = RoadDirection((self.road_config['right_angle'] + 180) % 360, 'left')
        elif self.road_config['junction_type'] == 't':
            # Simplified for now
            pass
        return directions
    
    def _initialize_light_states(self):
        for direction_name in self.road_directions.keys():
            self.light_states[direction_name] = LightState.RED
        
        # Start with top/bottom green
        if 'top' in self.light_states: self.light_states['top'] = LightState.GREEN
        if 'bottom' in self.light_states: self.light_states['bottom'] = LightState.GREEN
    
    def update_timing(self):
        if time.time() - self.cycle_start_time >= self.green_duration:
            self._switch_light_phases()
            self.cycle_start_time = time.time()
    
    def _switch_light_phases(self):
        if self.road_config['junction_type'] == 'cross':
            # If top is green, switch to left/right green, and vice-versa
            if self.light_states.get('top') == LightState.GREEN:
                self.light_states.update({'top': LightState.RED, 'bottom': LightState.RED, 'left': LightState.GREEN, 'right': LightState.GREEN})
            else:
                self.light_states.update({'top': LightState.GREEN, 'bottom': LightState.GREEN, 'left': LightState.RED, 'right': LightState.RED})

    # --- FIX #1: Simplified, direct methods to check light state ---
    def get_light_state_for_road(self, road_name: str) -> Optional[LightState]:
        """Gets the light state directly by the road's name ('top', 'left', etc.)."""
        return self.light_states.get(road_name)

    def is_red_light(self, road_name: str) -> bool:
        """Checks if the light for a specific road is RED."""
        return self.get_light_state_for_road(road_name) == LightState.RED

    def is_green_light(self, road_name: str) -> bool:
        """Checks if the light for a specific road is GREEN."""
        return self.get_light_state_for_road(road_name) == LightState.GREEN
    
    def update_road_config(self, new_road_config):
        self.road_config = new_road_config
        self.road_directions = self._get_road_directions_from_config()
        self._initialize_light_states()
        
    def draw(self, screen):
        pygame.draw.circle(screen, (80, 80, 80), (int(self.center_x), int(self.center_y)), self.light_radius)
        for direction_name, direction_info in self.road_directions.items():
            if direction_name in self.light_states:
                light_color = self.colors[self.light_states[direction_name]]
                angle_rad = math.radians(direction_info.angle)
                segment_distance = self.light_radius - 5
                segment_x = self.center_x + segment_distance * math.cos(angle_rad)
                segment_y = self.center_y + segment_distance * math.sin(angle_rad)
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
