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
        self.road_config = road_config
        self.light_radius = 25
        self.segment_width = 8
        self.road_directions = {}
        self.light_states = {}
        
        # --- REQUIREMENT FULFILLED: Green light lasts 15 seconds ---
        self.green_duration = 15.0
        self.cycle_start_time = time.time()
        
        self.cycle_order = []
        self.current_green_index = 0
        self.colors = { LightState.RED: (255, 50, 50), LightState.GREEN: (50, 255, 50) }
        
        self.update_road_config(road_config)

    def update_road_config(self, new_road_config):
        # Check if this is the first time or if we need to reinitialize
        if not hasattr(self, '_config_hash') or self._should_update_config(new_road_config):
            self.road_config = new_road_config
            self.road_directions = self._get_road_directions_from_config()
            self.cycle_order = ['top', 'right', 'bottom', 'left']
            self.cycle_order = [name for name in self.cycle_order if name in self.road_directions]
            self._initialize_light_states()
            self._config_hash = self._get_config_hash(new_road_config)
            print(f"Traffic light config updated - timer reset")
    
    def _should_update_config(self, new_config):
        """Check if the config has meaningfully changed"""
        if not hasattr(self, 'road_config') or not self.road_config:
            return True
        
        # Check key values that would affect traffic lights
        key_fields = ['junction_type', 'top_angle', 'right_angle', 'bottom_angle']
        for field in key_fields:
            if self.road_config.get(field) != new_config.get(field):
                return True
        return False
    
    def _get_config_hash(self, config):
        """Get a simple hash of the config for comparison"""
        key_fields = ['junction_type', 'top_angle', 'right_angle', 'bottom_angle']
        return hash(tuple(config.get(field) for field in key_fields))

    def _get_road_directions_from_config(self):
        directions = {}
        if self.road_config['junction_type'] == 'cross':
            directions['top'] = RoadDirection(self.road_config['top_angle'], 'top')
            directions['right'] = RoadDirection(self.road_config['right_angle'], 'right') 
            directions['bottom'] = RoadDirection(self.road_config['bottom_angle'], 'bottom')
            # The 'left' road is always 180 degrees from the 'right' road's origin point
            directions['left'] = RoadDirection(180, 'left')
        return directions
    
    def _initialize_light_states(self):
        for direction_name in self.road_directions.keys():
            self.light_states[direction_name] = LightState.RED
        
        if self.cycle_order:
            first_green = self.cycle_order[0]
            self.light_states[first_green] = LightState.GREEN
        self.current_green_index = 0
        self.cycle_start_time = time.time()
    
    def update_timing(self):
        mode = self.road_config.get('traffic_light_mode', 'timer')
        if mode == 'timer':
            if time.time() - self.cycle_start_time >= self.green_duration:
                self._switch_light_phases()
                self.cycle_start_time = time.time()
        elif mode == 'smart':
            pass
    
    def _switch_light_phases(self):
        if not self.cycle_order: return
        current_green_road = self.cycle_order[self.current_green_index]
        self.light_states[current_green_road] = LightState.RED
        self.current_green_index = (self.current_green_index + 1) % len(self.cycle_order)
        next_green_road = self.cycle_order[self.current_green_index]
        self.light_states[next_green_road] = LightState.GREEN

    # --- CLEANUP: Removed old angle-based functions for clarity ---
    def is_red_light(self, road_name: str) -> bool:
        """The one simple, reliable way to check the light status."""
        return self.light_states.get(road_name) == LightState.RED
    
    def get_current_green_direction(self):
        """Get the name of the currently green direction"""
        if self.cycle_order and 0 <= self.current_green_index < len(self.cycle_order):
            return self.cycle_order[self.current_green_index]
        return None
    
    def get_time_until_change(self):
        """Get remaining time in seconds until next light change"""
        elapsed = time.time() - self.cycle_start_time
        remaining = self.green_duration - elapsed
        return max(0, remaining)
    
    def get_timer_info(self):
        """Get comprehensive timer information for display"""
        current_green = self.get_current_green_direction()
        time_remaining = self.get_time_until_change()
        
        return {
            'current_green': current_green or 'None',
            'time_remaining': time_remaining,
            'cycle_duration': self.green_duration,
            'cycle_progress': 1.0 - (time_remaining / self.green_duration) if self.green_duration > 0 else 0
        }

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
            
    def get_nearest_traffic_light(self, x, y, max_distance=300) -> Optional[TrafficLight]:
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
