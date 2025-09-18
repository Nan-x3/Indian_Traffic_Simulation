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
        self.passed_lights = set()  # Track which traffic lights this vehicle has passed

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

    def check_for_overlap(self, other_vehicle):
        """Check if this vehicle is overlapping with another vehicle"""
        dx = abs(self.x - other_vehicle.x)
        dy = abs(self.y - other_vehicle.y)
        
        # Calculate minimum safe distances based on vehicle dimensions (tighter)
        min_x_distance = (self.length + other_vehicle.length) / 2 + 1  # Very small buffer
        min_y_distance = (self.width + other_vehicle.width) / 2 + 1   # Very small buffer
        
        # Check if vehicles are overlapping
        return dx < min_x_distance and dy < min_y_distance

    def update_position(self, dt):
        angle_rad = math.radians(self.angle)
        self.x += self.speed * math.cos(angle_rad) * dt * 60
        self.y += self.speed * math.sin(angle_rad) * dt * 60

    def check_traffic_light_compliance(self, traffic_light_manager):
        if not self.road_side:
            return "proceed"

        nearest_light = traffic_light_manager.get_nearest_traffic_light(self.x, self.y)
        if not nearest_light:
            return "proceed"

        # Create a unique identifier for this traffic light
        light_id = (nearest_light.center_x, nearest_light.center_y)
        
        dist_to_light = math.hypot(self.x - nearest_light.center_x, self.y - nearest_light.center_y)
        
        # If vehicle is very close to or past the intersection center, mark as passed
        if dist_to_light <= 60:  # Close to intersection center
            if light_id not in self.passed_lights:
                # Vehicle is crossing the intersection - check if it was green when approaching
                if nearest_light.is_green_light(self.road_side):
                    self.passed_lights.add(light_id)  # Mark as legally passed
                    return "proceed"
                # If it's red and we haven't marked it as passed, we should stop
                elif nearest_light.is_red_light(self.road_side):
                    return "stop"
            else:
                # Already passed this light when it was green, continue regardless of current state
                return "proceed"
        
        # Vehicle is approaching the intersection
        elif dist_to_light <= 120:  # Within stopping distance
            if light_id in self.passed_lights:
                # This shouldn't happen (vehicle moving backwards), but handle it
                return "proceed"
            
            if nearest_light.is_red_light(self.road_side):
                return "stop"
        
        # Vehicle is far from intersection or has passed through
        return "proceed"

    def cleanup_passed_lights(self, traffic_light_manager):
        """Remove traffic light IDs that are far away to prevent memory buildup"""
        if not self.passed_lights:
            return
            
        lights_to_remove = []
        for light_id in self.passed_lights:
            light_x, light_y = light_id
            dist = math.hypot(self.x - light_x, self.y - light_y)
            # If vehicle is more than 300 pixels away from a passed light, remove it
            if dist > 300:
                lights_to_remove.append(light_id)
        
        for light_id in lights_to_remove:
            self.passed_lights.remove(light_id)

    def get_vehicle_ahead(self, all_vehicles, max_distance=200):
        closest_vehicle = None
        min_distance = max_distance
        
        angle_rad = math.radians(self.angle)
        our_dx, our_dy = math.cos(angle_rad), math.sin(angle_rad)
        
        # Calculate our front position
        front_x = self.x + (self.length / 2) * our_dx
        front_y = self.y + (self.length / 2) * our_dy
        
        for vehicle in all_vehicles:
            if vehicle == self: continue
            
            # Vector from our front to the other vehicle's center
            dx = vehicle.x - front_x
            dy = vehicle.y - front_y
            distance = math.hypot(dx, dy)
            
            if distance < max_distance:
                # Check if the vehicle is in front of us (dot product > 0)
                dot_product = dx * our_dx + dy * our_dy
                
                # More strict lane checking - vehicles must be very close to our path
                # Cross product gives perpendicular distance
                cross_product = abs(dx * our_dy - dy * our_dx)
                lane_tolerance = (max(self.width, vehicle.width) / 2) + 8  # Tighter lane tolerance
                
                # Also check for potential overlap by considering vehicle sizes
                vehicle_front_x = vehicle.x - (vehicle.length / 2) * math.cos(math.radians(vehicle.angle))
                vehicle_front_y = vehicle.y - (vehicle.length / 2) * math.sin(math.radians(vehicle.angle))
                vehicle_back_x = vehicle.x + (vehicle.length / 2) * math.cos(math.radians(vehicle.angle))
                vehicle_back_y = vehicle.y + (vehicle.length / 2) * math.sin(math.radians(vehicle.angle))
                
                # Check distance to both front and back of the other vehicle
                dist_to_front = math.hypot(vehicle_front_x - front_x, vehicle_front_y - front_y)
                dist_to_back = math.hypot(vehicle_back_x - front_x, vehicle_back_y - front_y)
                actual_distance = min(distance, dist_to_front, dist_to_back)
                
                if dot_product > -20 and cross_product < lane_tolerance and actual_distance < min_distance:
                    min_distance = actual_distance
                    closest_vehicle = vehicle
        
        return closest_vehicle, min_distance

    def calculate_stopping_distance(self, current_speed):
        """Calculate the distance needed to stop completely given current speed"""
        if current_speed <= 0:
            return 0
        # Using basic physics: d = v²/(2*a) where v is speed, a is deceleration
        return (current_speed * current_speed) / (2 * self.deceleration * 60)  # 60 for frame rate conversion

    def calculate_optimal_following_distance(self, vehicle_ahead):
        """Calculate the optimal distance to maintain behind another vehicle"""
        if not vehicle_ahead:
            return 0
        
        # Base distance: half of both vehicle lengths plus a minimal buffer
        base_distance = (self.length + vehicle_ahead.length) / 2 + 5  # Reduced buffer for tighter following
        
        # Add stopping distance based on current speed (more precise)
        stopping_distance = self.calculate_stopping_distance(self.speed)
        
        # Add a smaller buffer based on speed difference
        speed_buffer = max(0, self.speed - vehicle_ahead.speed) * 8  # Reduced multiplier
        
        return base_distance + stopping_distance + speed_buffer

    def update_behavior(self, vehicles, intersection_bounds, dt, traffic_light_manager=None):
        self.at_intersection = self.is_in_intersection(intersection_bounds)

        # Clean up old passed traffic light records
        if traffic_light_manager:
            self.cleanup_passed_lights(traffic_light_manager)

        # EMERGENCY CHECK: Stop immediately if overlapping with any vehicle
        for vehicle in vehicles:
            if vehicle != self and self.check_for_overlap(vehicle):
                self.speed = 0  # Full stop if overlapping
                self.update_position(dt)
                return

        # Check traffic lights first
        if traffic_light_manager:
            action = self.check_traffic_light_compliance(traffic_light_manager)
            if action == "stop":
                self.speed = max(0, self.speed - self.deceleration * dt * 3)
                self.update_position(dt)
                return

        # Enhanced collision detection and avoidance with precise distance control
        vehicle_ahead, distance = self.get_vehicle_ahead(vehicles)
        
        if vehicle_ahead:
            # Calculate optimal following distance
            optimal_distance = self.calculate_optimal_following_distance(vehicle_ahead)
            
            # Calculate how much we're over/under the optimal distance
            distance_error = distance - optimal_distance
            
            # More precise zones for tighter control
            # Emergency zone - too close, immediate hard brake
            if distance_error < -10:  # Tighter emergency zone
                self.speed = max(0, self.speed - self.deceleration * dt * 10)  # Even stronger braking
            # Critical zone - brake to maintain safe distance
            elif distance_error < -3:  # Tighter critical zone
                # More precise braking calculation
                if self.speed > 0.1:
                    # Proportional braking based on how close we are
                    brake_intensity = min(8, abs(distance_error) * 2)
                    self.speed = max(0, self.speed - self.deceleration * dt * brake_intensity)
            # Fine adjustment zone - very precise speed matching
            elif distance_error < 2:  # Very tight following zone
                # Precise speed matching with very small adjustments
                speed_difference = self.speed - vehicle_ahead.speed
                if speed_difference > 0.1:  # We're going even slightly faster
                    self.speed = max(vehicle_ahead.speed * 0.98, self.speed - self.deceleration * dt * 3)
                elif speed_difference < -0.1:  # We're going slightly slower
                    # Only accelerate very gently if we have room
                    if distance_error > 0:
                        self.speed = min(vehicle_ahead.speed * 0.99, self.speed + self.acceleration * dt * 0.3)
            # Comfortable zone - gradual acceleration
            elif distance_error < 15:  # Reduced comfortable zone
                if self.speed < self.target_speed * 0.85:  # Slightly higher target when following
                    self.speed = min(self.target_speed * 0.85, self.speed + self.acceleration * dt * 0.5)
            # Free zone - normal acceleration
            else:
                if self.speed < self.target_speed:
                    self.speed = min(self.target_speed, self.speed + self.acceleration * dt)
        else:
            # No vehicle ahead - normal acceleration
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

    def draw_collision_zones(self, screen, vehicle_ahead=None):
        """Draw collision detection zones for debugging"""
        angle_rad = math.radians(self.angle)
        dx, dy = math.cos(angle_rad), math.sin(angle_rad)
        
        # Calculate zones based on optimal following distance if vehicle ahead exists
        if vehicle_ahead:
            optimal_distance = self.calculate_optimal_following_distance(vehicle_ahead)
            emergency_distance = optimal_distance - 15
            warning_distance = optimal_distance - 5
            comfortable_distance = optimal_distance + 5
        else:
            # Default zones when no vehicle ahead
            base_safe_dist = self.length / 2 + 10
            speed_factor = self.speed * 15
            emergency_distance = base_safe_dist + 5
            warning_distance = base_safe_dist + speed_factor
            comfortable_distance = warning_distance * 1.5
        
        # Draw detection zones
        front_x = self.x + (self.length / 2) * dx
        front_y = self.y + (self.length / 2) * dy
        
        # Emergency zone (red)
        end_x = front_x + emergency_distance * dx
        end_y = front_y + emergency_distance * dy
        pygame.draw.line(screen, (255, 0, 0), (front_x, front_y), (end_x, end_y), 3)
        
        # Warning zone (yellow)
        end_x = front_x + warning_distance * dx
        end_y = front_y + warning_distance * dy
        pygame.draw.line(screen, (255, 255, 0), (front_x, front_y), (end_x, end_y), 2)
        
        # Comfortable zone (green)
        end_x = front_x + comfortable_distance * dx
        end_y = front_y + comfortable_distance * dy
        pygame.draw.line(screen, (0, 255, 0), (front_x, front_y), (end_x, end_y), 1)
        
        # Draw optimal stopping point (cyan) when vehicle ahead exists
        if vehicle_ahead:
            optimal_distance = self.calculate_optimal_following_distance(vehicle_ahead)
            end_x = front_x + optimal_distance * dx
            end_y = front_y + optimal_distance * dy
            pygame.draw.circle(screen, (0, 255, 255), (int(end_x), int(end_y)), 4)


class Bike(VehicleBase):
    def get_max_speed(self): return random.uniform(4.0, 5.0)
    def get_acceleration(self): return 0.20
    def get_deceleration(self): return 0.80  # Increased from 0.50
    def get_width(self): return 8
    def get_length(self): return 16
    def get_color(self): return (200, 200, 200)

class Car(VehicleBase):
    def get_max_speed(self): return random.uniform(3.0, 4.0)
    def get_acceleration(self): return 0.15
    def get_deceleration(self): return 0.70  # Increased from 0.40
    def get_width(self): return 18
    def get_length(self): return 35
    def get_color(self): return (100, 100, 255)

class Auto(VehicleBase):
    def get_max_speed(self): return random.uniform(2.0, 3.0)
    def get_acceleration(self): return 0.12
    def get_deceleration(self): return 0.60  # Increased from 0.35
    def get_width(self): return 12
    def get_length(self): return 22
    def get_color(self): return (255, 255, 0)

class Bus(VehicleBase):
    def get_max_speed(self): return random.uniform(1.5, 2.5)
    def get_acceleration(self): return 0.08
    def get_deceleration(self): return 0.50  # Increased from 0.25
    def get_width(self): return 25
    def get_length(self): return 65
    def get_color(self): return (255, 165, 0)

class Truck(VehicleBase):
    def get_max_speed(self): return random.uniform(1.8, 2.8)
    def get_acceleration(self): return 0.10
    def get_deceleration(self): return 0.55  # Increased from 0.30
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
        
        # Much stricter spawn checking to prevent overlaps
        min_spawn_distance = 120  # Increased minimum distance
        for v in self.vehicles:
            distance = math.hypot(v.x - spawn_x, v.y - spawn_y)
            if distance < min_spawn_distance:
                return  # Don't spawn if too close to existing vehicle
            
            # Also check if vehicle is approaching spawn point with larger buffer
            angle_rad = math.radians(v.angle)
            dx_to_spawn = spawn_x - v.x
            dy_to_spawn = spawn_y - v.y
            dot_product = dx_to_spawn * math.cos(angle_rad) + dy_to_spawn * math.sin(angle_rad)
            
            # If vehicle is moving towards spawn point and close, don't spawn
            if dot_product > 0 and distance < 200:  # Increased buffer distance
                return
            
            # Additional check for vehicles that might be very close in perpendicular direction
            cross_product = abs(dx_to_spawn * math.sin(angle_rad) - dy_to_spawn * math.cos(angle_rad))
            if cross_product < 50 and distance < 150:  # Don't spawn if vehicle is close in any lane
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

    def draw_debug_info(self, screen, show_collision_zones=False):
        # Draw intersection bounds
        bounds = self.lane_manager.intersection_bounds
        pygame.draw.rect(screen, (255, 0, 0), (bounds['left'], bounds['top'], bounds['right'] - bounds['left'], bounds['bottom'] - bounds['top']), 2)
        
        # Draw lane centers
        for lane in self.lane_manager.lanes:
            pygame.draw.circle(screen, (255,0,0), (int(lane.center_x), int(lane.center_y)), 3)
        
        # Draw collision detection zones if enabled
        if show_collision_zones:
            for vehicle in self.vehicles:
                # Get the vehicle ahead for this vehicle to show optimal stopping distance
                vehicle_ahead, _ = vehicle.get_vehicle_ahead(self.vehicles)
                vehicle.draw_collision_zones(screen, vehicle_ahead)

    def clear_vehicles(self): self.vehicles = []
    def get_vehicle_count(self): return len(self.vehicles)
    def set_spawn_rate(self, interval): self.spawn_interval = interval
    def set_max_vehicles(self, max_count): self.max_vehicles = max_count
    def enable_spawning(self): self.spawning_enabled = True
    def disable_spawning(self): self.spawning_enabled = False
    def is_spawning_enabled(self): return self.spawning_enabled
