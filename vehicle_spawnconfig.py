# vehicle_spawnconfig.py

import pygame
import math
import random
from abc import ABC, abstractmethod
from enum import Enum
from traffic_lights import TrafficLightManager, LightState

class VehicleType(Enum):
    BIKE = "bike"
    CAR = "car"
    AUTO = "auto"
    BUS = "bus"
    TRUCK = "truck"

class Direction(Enum):
    STRAIGHT = "straight"
    LEFT = "left"
    RIGHT = "right"
    U_TURN = "u_turn"

class Lane:
    def __init__(self, center_x, center_y, width, direction_angle, lane_number, road_side):
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.direction_angle = direction_angle
        self.lane_number = lane_number
        self.road_side = road_side

class VehicleBase(ABC):
    def __init__(self, x, y, angle, lane, destination):
        self.x = x
        self.y = y
        self.angle = angle
        self.original_angle = angle
        self.lane = lane
        self.destination = destination
        self.road_side = lane.road_side if lane else None

        self.speed = 0.0
        self.target_speed = random.uniform(0.8, 1.1) * self.get_max_speed()
        self.max_speed = self.get_max_speed()
        self.acceleration = self.get_acceleration()
        self.deceleration = self.get_deceleration()
        
        self.width = self.get_width()
        self.length = self.get_length()
        self.color = self.get_color()
        
        self.at_intersection = False

    @abstractmethod
    def get_max_speed(self): pass
    @abstractmethod
    def get_acceleration(self): pass
    @abstractmethod
    def get_deceleration(self): pass
    @abstractmethod
    def get_width(self): pass
    @abstractmethod
    def get_length(self): pass
    @abstractmethod
    def get_color(self): pass

    def is_in_intersection(self, intersection_bounds):
        return (intersection_bounds['left'] <= self.x <= intersection_bounds['right'] and
                intersection_bounds['top'] <= self.y <= intersection_bounds['bottom'])

    def update_position(self, dt):
        angle_rad = math.radians(self.angle)
        self.x += self.speed * math.cos(angle_rad) * dt * 60
        self.y += self.speed * math.sin(angle_rad) * dt * 60

    def check_traffic_light_compliance(self, traffic_light_manager):
        if self.at_intersection or not self.road_side:
            return "proceed"

        nearest_light = traffic_light_manager.get_nearest_traffic_light(self.x, self.y)
        if not nearest_light:
            return "proceed"

        stop_dist = 120 
        dist_to_light = math.hypot(self.x - nearest_light.center_x, self.y - nearest_light.center_y)

        if dist_to_light < stop_dist:
            if nearest_light.is_red_light(self.road_side):
                return "stop"
        
        return "proceed"

    def get_vehicle_ahead(self, all_vehicles, max_distance=120):
        closest_vehicle = None
        min_distance = max_distance
        
        angle_rad = math.radians(self.angle)
        our_dx, our_dy = math.cos(angle_rad), math.sin(angle_rad)
        front_x = self.x + (self.length / 2) * our_dx
        front_y = self.y + (self.length / 2) * our_dy
        
        for vehicle in all_vehicles:
            if vehicle == self: continue
            
            dx = vehicle.x - front_x
            dy = vehicle.y - front_y
            distance = math.hypot(dx, dy)
            
            if distance < min_distance:
                dot_product = dx * our_dx + dy * our_dy
                if dot_product > 0:
                    min_distance = distance
                    closest_vehicle = vehicle
        
        return closest_vehicle, min_distance

    def update_behavior(self, vehicles, intersection_bounds, dt, traffic_light_manager=None):
        self.at_intersection = self.is_in_intersection(intersection_bounds)

        if traffic_light_manager:
            action = self.check_traffic_light_compliance(traffic_light_manager)
            if action == "stop":
                self.speed = max(0, self.speed - self.deceleration * dt * 2)
                self.update_position(dt)
                return

        vehicle_ahead, distance = self.get_vehicle_ahead(vehicles)
        safe_dist = self.length / 2 + (vehicle_ahead.length / 2 if vehicle_ahead else 0) + 15
        
        if vehicle_ahead and distance < safe_dist:
             self.speed = max(0, self.speed - self.deceleration * dt)
        else:
             if self.speed < self.target_speed:
                 self.speed = min(self.target_speed, self.speed + self.acceleration * dt)

        self.update_position(dt)

    def draw(self, screen):
        angle_rad = math.radians(self.angle)
        half_len, half_wid = self.length / 2, self.width / 2
        corners = [(-half_len, -half_wid), (half_len, -half_wid), (half_len, half_wid), (-half_len, half_wid)]
        rotated_corners = []
        for x, y in corners:
            rx = x * math.cos(angle_rad) - y * math.sin(angle_rad) + self.x
            ry = x * math.sin(angle_rad) + y * math.cos(angle_rad) + self.y
            rotated_corners.append((rx, ry))
        pygame.draw.polygon(screen, self.color, rotated_corners)
        pygame.draw.polygon(screen, (0,0,0), rotated_corners, 1)


class Bike(VehicleBase):
    def get_max_speed(self): return random.uniform(4.0, 5.0)
    def get_acceleration(self): return 0.20
    def get_deceleration(self): return 0.50
    def get_width(self): return 8
    def get_length(self): return 16
    def get_color(self): return (200, 200, 200)

class Car(VehicleBase):
    def get_max_speed(self): return random.uniform(3.0, 4.0)
    def get_acceleration(self): return 0.15
    def get_deceleration(self): return 0.40
    def get_width(self): return 18
    def get_length(self): return 35
    def get_color(self): return (100, 100, 255)

class Auto(VehicleBase):
    def get_max_speed(self): return random.uniform(2.0, 3.0)
    def get_acceleration(self): return 0.12
    def get_deceleration(self): return 0.35
    def get_width(self): return 12
    def get_length(self): return 22
    def get_color(self): return (255, 255, 0)

class Bus(VehicleBase):
    def get_max_speed(self): return random.uniform(1.5, 2.5)
    def get_acceleration(self): return 0.08
    def get_deceleration(self): return 0.25
    def get_width(self): return 25
    def get_length(self): return 65
    def get_color(self): return (255, 165, 0)

class Truck(VehicleBase):
    def get_max_speed(self): return random.uniform(1.8, 2.8)
    def get_acceleration(self): return 0.10
    def get_deceleration(self): return 0.30
    def get_width(self): return 22
    def get_length(self): return 55
    def get_color(self): return (150, 150, 150)


class LaneManager:
    def __init__(self):
        self.lanes = []
        self.intersection_bounds = {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}

    def setup_lanes(self, road_config, center_x=960, center_y=540):
        self.lanes = []
        lane_width = 40
        total_lanes = road_config['lane_count']
        road_width = total_lanes * lane_width
        
        intersection_half = road_width // 2
        self.intersection_bounds = {
            'left': center_x - intersection_half, 'right': center_x + intersection_half,
            'top': center_y - intersection_half, 'bottom': center_y + intersection_half
        }
        
        if road_config['junction_type'] == 'cross':
            self._setup_cross_lanes(road_config, center_x, center_y, lane_width, total_lanes)

    def _setup_cross_lanes(self, road_config, center_x, center_y, lane_width, total_lanes):
        road_half_width = (total_lanes * lane_width) // 2
        lanes_per_dir = total_lanes // 2 if '2way' in road_config['road_type'] else total_lanes

        # LEFT ROAD (vehicles moving RIGHT, angle 0)
        for i in range(lanes_per_dir):
            lane_center_y = center_y - road_half_width + (i + 0.5) * lane_width
            self.lanes.append(Lane(center_x - 500, lane_center_y, lane_width, 0, i, 'left'))
        
        # RIGHT ROAD (vehicles moving LEFT, angle 180)
        for i in range(lanes_per_dir):
            lane_center_y = center_y + road_half_width - (i + 0.5) * lane_width
            self.lanes.append(Lane(center_x + 500, lane_center_y, lane_width, 180, i, 'right'))

        # TOP ROAD (vehicles moving DOWN, angle 90)
        for i in range(lanes_per_dir):
            lane_center_x = center_x + road_half_width - (i + 0.5) * lane_width
            self.lanes.append(Lane(lane_center_x, center_y - 500, lane_width, 90, i, 'top'))
        
        # BOTTOM ROAD (vehicles moving UP, angle 270)
        for i in range(lanes_per_dir):
            lane_center_x = center_x - road_half_width + (i + 0.5) * lane_width
            self.lanes.append(Lane(lane_center_x, center_y + 500, lane_width, 270, i, 'bottom'))

    def get_spawn_lanes(self):
        return self.lanes
    
    def get_random_destination(self, current_lane):
        return random.choice(list(Direction))

class VehicleFactory:
    VEHICLE_CLASSES = {
        VehicleType.BIKE: Bike, VehicleType.CAR: Car, VehicleType.AUTO: Auto,
        VehicleType.BUS: Bus, VehicleType.TRUCK: Truck,
    }
    
    @classmethod
    def create_vehicle(cls, vehicle_type, x, y, angle, lane, destination):
        return cls.VEHICLE_CLASSES[vehicle_type](x, y, angle, lane, destination)
    
    @classmethod
    def create_random_vehicle(cls, x, y, angle, lane, destination, distribution):
        vehicle_type = random.choices(list(distribution.keys()), list(distribution.values()))[0]
        return cls.create_vehicle(vehicle_type, x, y, angle, lane, destination)

class VehicleSpawner:
    def __init__(self):
        self.vehicles = []
        self.lane_manager = LaneManager()
        self.spawn_interval = 0.8
        self.last_spawn_time = 0
        self.max_vehicles = 100
        self.spawning_enabled = False
        self.vehicle_distribution = {
            VehicleType.BIKE: 0.747, VehicleType.CAR: 0.136, VehicleType.TRUCK: 0.093,
            VehicleType.AUTO: 0.018, VehicleType.BUS: 0.006,
        }
    
    def set_road_config(self, road_config):
        self.lane_manager.setup_lanes(road_config)
    
    def update_vehicles(self, dt, current_time, road_config, traffic_light_manager=None):
        self.vehicles = [v for v in self.vehicles if -150 <= v.x <= 2070 and -150 <= v.y <= 1230]
        
        for vehicle in self.vehicles:
            vehicle.update_behavior(self.vehicles, self.lane_manager.intersection_bounds, dt, traffic_light_manager)
        
        if self.spawning_enabled and (current_time - self.last_spawn_time > self.spawn_interval) and len(self.vehicles) < self.max_vehicles:
            self.spawn_vehicle(current_time)
            self.last_spawn_time = current_time

    def spawn_vehicle(self, current_time):
        spawn_lanes = self.lane_manager.get_spawn_lanes()
        if not spawn_lanes: return
        
        spawn_lane = random.choice(spawn_lanes)
        spawn_x, spawn_y = spawn_lane.center_x, spawn_lane.center_y
        
        for v in self.vehicles:
            if math.hypot(v.x - spawn_x, v.y - spawn_y) < 80: # Min spawn distance
                return

        destination = self.lane_manager.get_random_destination(spawn_lane)
        new_vehicle = VehicleFactory.create_random_vehicle(
            spawn_x, spawn_y, spawn_lane.direction_angle,
            spawn_lane, destination, self.vehicle_distribution
        )
        self.vehicles.append(new_vehicle)
    
    def draw_vehicles(self, screen):
        for vehicle in self.vehicles:
            vehicle.draw(screen)

    def draw_debug_info(self, screen):
        bounds = self.lane_manager.intersection_bounds
        pygame.draw.rect(screen, (255, 0, 0), (bounds['left'], bounds['top'], bounds['right'] - bounds['left'], bounds['bottom'] - bounds['top']), 2)
        for lane in self.lane_manager.lanes:
            pygame.draw.circle(screen, (255,0,0), (int(lane.center_x), int(lane.center_y)), 3)

    def clear_vehicles(self): self.vehicles = []
    def get_vehicle_count(self): return len(self.vehicles)
    def set_spawn_rate(self, interval): self.spawn_interval = interval
    def set_max_vehicles(self, max_count): self.max_vehicles = max_count
    def enable_spawning(self): self.spawning_enabled = True
    def disable_spawning(self): self.spawning_enabled = False
    def is_spawning_enabled(self): return self.spawning_enabled
