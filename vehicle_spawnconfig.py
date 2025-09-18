"""
Vehicle Spawn Configuration Module for Indian Traffic Simulation

This module handles vehicle spawning and traffic flow configuration for Indian roads.
It includes different vehicle types and realistic spawning patterns.
"""

import pygame
import random
import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
from road_config import LaneDirection, RoadConfig

class VehicleType(Enum):
    """Types of vehicles commonly found on Indian roads"""
    CAR = "car"
    BUS = "bus"
    TRUCK = "truck"
    MOTORCYCLE = "motorcycle"
    AUTO_RICKSHAW = "auto_rickshaw"
    BICYCLE = "bicycle"
    TEMPO = "tempo"

@dataclass
class VehicleProperties:
    """Properties for different vehicle types"""
    length: int
    width: int
    max_speed: int  # km/h
    acceleration: float
    deceleration: float
    color: Tuple[int, int, int]
    spawn_probability: float  # 0.0 to 1.0

@dataclass
class Vehicle:
    """Individual vehicle instance"""
    vehicle_type: VehicleType
    x: float
    y: float
    speed: float
    direction: LaneDirection
    lane_position: int
    properties: VehicleProperties
    target_speed: float
    following_distance: float = 50.0

class TrafficDensity(Enum):
    """Traffic density levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PEAK_HOUR = "peak_hour"

class VehicleSpawnConfig:
    """Main vehicle spawning configuration class"""
    
    def __init__(self, road_config: RoadConfig):
        self.road_config = road_config
        self.vehicles: List[Vehicle] = []
        self.spawn_timer = 0
        self.current_density = TrafficDensity.MEDIUM
        
        # Vehicle type properties (Indian road specific)
        self.vehicle_properties = {
            VehicleType.CAR: VehicleProperties(
                length=40, width=20, max_speed=80, acceleration=2.0, deceleration=3.5,
                color=(255, 100, 100), spawn_probability=0.35
            ),
            VehicleType.BUS: VehicleProperties(
                length=80, width=25, max_speed=60, acceleration=1.0, deceleration=2.5,
                color=(100, 255, 100), spawn_probability=0.15
            ),
            VehicleType.TRUCK: VehicleProperties(
                length=60, width=22, max_speed=70, acceleration=1.2, deceleration=2.8,
                color=(100, 100, 255), spawn_probability=0.20
            ),
            VehicleType.MOTORCYCLE: VehicleProperties(
                length=25, width=12, max_speed=90, acceleration=3.0, deceleration=4.0,
                color=(255, 255, 100), spawn_probability=0.15
            ),
            VehicleType.AUTO_RICKSHAW: VehicleProperties(
                length=30, width=15, max_speed=50, acceleration=1.8, deceleration=3.0,
                color=(255, 150, 0), spawn_probability=0.10
            ),
            VehicleType.BICYCLE: VehicleProperties(
                length=20, width=8, max_speed=25, acceleration=1.0, deceleration=2.0,
                color=(150, 75, 0), spawn_probability=0.03
            ),
            VehicleType.TEMPO: VehicleProperties(
                length=45, width=18, max_speed=55, acceleration=1.5, deceleration=3.0,
                color=(200, 100, 200), spawn_probability=0.02
            )
        }
        
        # Spawn rate configurations based on traffic density
        self.density_configs = {
            TrafficDensity.LOW: {
                'spawn_rate': 180,  # frames between spawns
                'speed_variation': 0.8,  # vehicles go 80% of max speed on average
                'lane_change_probability': 0.02
            },
            TrafficDensity.MEDIUM: {
                'spawn_rate': 120,
                'speed_variation': 0.7,
                'lane_change_probability': 0.05
            },
            TrafficDensity.HIGH: {
                'spawn_rate': 80,
                'speed_variation': 0.6,
                'lane_change_probability': 0.08
            },
            TrafficDensity.PEAK_HOUR: {
                'spawn_rate': 40,
                'speed_variation': 0.4,
                'lane_change_probability': 0.12
            }
        }
    
    def set_traffic_density(self, density: TrafficDensity):
        """Set the current traffic density level"""
        self.current_density = density
    
    def get_vehicle_type_to_spawn(self) -> VehicleType:
        """Randomly select a vehicle type based on spawn probabilities"""
        rand_value = random.random()
        cumulative_prob = 0.0
        
        for vehicle_type, properties in self.vehicle_properties.items():
            cumulative_prob += properties.spawn_probability
            if rand_value <= cumulative_prob:
                return vehicle_type
        
        return VehicleType.CAR  # fallback
    
    def create_vehicle(self, vehicle_type: VehicleType, spawn_point: Tuple[int, int, LaneDirection]) -> Vehicle:
        """Create a new vehicle at the specified spawn point"""
        properties = self.vehicle_properties[vehicle_type]
        
        # Calculate target speed based on current density
        density_config = self.density_configs[self.current_density]
        base_speed = properties.max_speed * density_config['speed_variation']
        # Add some random variation
        target_speed = base_speed * (0.8 + random.random() * 0.4)
        
        vehicle = Vehicle(
            vehicle_type=vehicle_type,
            x=float(spawn_point[0]),
            y=float(spawn_point[1]),
            speed=0.0,  # Start from rest
            direction=spawn_point[2],
            lane_position=0,
            properties=properties,
            target_speed=target_speed
        )
        
        return vehicle
    
    def should_spawn_vehicle(self) -> bool:
        """Determine if a new vehicle should be spawned"""
        self.spawn_timer += 1
        spawn_rate = self.density_configs[self.current_density]['spawn_rate']
        
        # Add some randomness to spawn timing
        random_factor = random.uniform(0.7, 1.3)
        adjusted_spawn_rate = int(spawn_rate * random_factor)
        
        if self.spawn_timer >= adjusted_spawn_rate:
            self.spawn_timer = 0
            return True
        return False
    
    def spawn_vehicle(self):
        """Spawn a new vehicle if conditions are met"""
        if not self.should_spawn_vehicle():
            return
        
        spawn_points = self.road_config.get_spawn_points()
        if not spawn_points:
            return
        
        # Choose a random spawn point
        spawn_point = random.choice(spawn_points)
        
        # Check if spawn point is clear
        if not self._is_spawn_point_clear(spawn_point):
            return
        
        # Select vehicle type and create vehicle
        vehicle_type = self.get_vehicle_type_to_spawn()
        new_vehicle = self.create_vehicle(vehicle_type, spawn_point)
        
        self.vehicles.append(new_vehicle)
    
    def _is_spawn_point_clear(self, spawn_point: Tuple[int, int, LaneDirection]) -> bool:
        """Check if the spawn point is clear of other vehicles"""
        spawn_x, spawn_y, spawn_direction = spawn_point
        min_distance = 100  # Minimum distance from other vehicles
        
        for vehicle in self.vehicles:
            if vehicle.direction == spawn_direction:
                distance = math.sqrt((vehicle.x - spawn_x)**2 + (vehicle.y - spawn_y)**2)
                if distance < min_distance:
                    return False
        return True
    
    def update_vehicles(self, dt: float):
        """Update all vehicles' positions and behavior"""
        vehicles_to_remove = []
        
        for vehicle in self.vehicles:
            # Update vehicle position
            self._update_vehicle_position(vehicle, dt)
            
            # Apply traffic behavior
            self._apply_traffic_behavior(vehicle)
            
            # Remove vehicles that have left the screen
            if self._should_remove_vehicle(vehicle):
                vehicles_to_remove.append(vehicle)
        
        # Remove vehicles that have left the screen
        for vehicle in vehicles_to_remove:
            self.vehicles.remove(vehicle)
    
    def _update_vehicle_position(self, vehicle: Vehicle, dt: float):
        """Update a single vehicle's position"""
        # Convert km/h to pixels per frame (assuming 60 FPS)
        speed_multiplier = 1.0 / 3.6 / 60.0 * 100  # Adjusted for simulation
        
        # Accelerate towards target speed
        speed_diff = vehicle.target_speed - vehicle.speed
        if abs(speed_diff) > 0.1:
            acceleration = vehicle.properties.acceleration if speed_diff > 0 else -vehicle.properties.deceleration
            vehicle.speed += acceleration * dt
            vehicle.speed = max(0, min(vehicle.speed, vehicle.target_speed))
        
        # Update position based on direction
        movement = vehicle.speed * speed_multiplier * dt
        
        if vehicle.direction == LaneDirection.EAST:
            vehicle.x += movement
        elif vehicle.direction == LaneDirection.WEST:
            vehicle.x -= movement
        elif vehicle.direction == LaneDirection.SOUTH:
            vehicle.y += movement
        elif vehicle.direction == LaneDirection.NORTH:
            vehicle.y -= movement
    
    def _apply_traffic_behavior(self, vehicle: Vehicle):
        """Apply realistic traffic behavior including following and lane changing"""
        # Find vehicle in front
        front_vehicle = self._find_vehicle_in_front(vehicle)
        
        if front_vehicle:
            distance = self._calculate_distance(vehicle, front_vehicle)
            
            # Adjust speed based on following distance
            if distance < vehicle.following_distance:
                # Slow down if too close
                vehicle.target_speed = min(vehicle.target_speed, front_vehicle.speed * 0.8)
            elif distance > vehicle.following_distance * 2:
                # Speed up if far enough
                vehicle.target_speed = min(
                    vehicle.properties.max_speed * self.density_configs[self.current_density]['speed_variation'],
                    vehicle.properties.max_speed
                )
        
        # Lane changing behavior (simplified)
        lane_change_prob = self.density_configs[self.current_density]['lane_change_probability']
        if random.random() < lane_change_prob * 0.01:  # Very low probability per frame
            self._attempt_lane_change(vehicle)
    
    def _find_vehicle_in_front(self, vehicle: Vehicle) -> Optional[Vehicle]:
        """Find the closest vehicle in front in the same lane"""
        closest_vehicle = None
        min_distance = float('inf')
        
        for other_vehicle in self.vehicles:
            if (other_vehicle != vehicle and 
                other_vehicle.direction == vehicle.direction and
                abs(other_vehicle.y - vehicle.y) < 30):  # Same lane approximation
                
                # Check if vehicle is in front
                is_in_front = False
                if vehicle.direction == LaneDirection.EAST and other_vehicle.x > vehicle.x:
                    is_in_front = True
                elif vehicle.direction == LaneDirection.WEST and other_vehicle.x < vehicle.x:
                    is_in_front = True
                elif vehicle.direction == LaneDirection.SOUTH and other_vehicle.y > vehicle.y:
                    is_in_front = True
                elif vehicle.direction == LaneDirection.NORTH and other_vehicle.y < vehicle.y:
                    is_in_front = True
                
                if is_in_front:
                    distance = self._calculate_distance(vehicle, other_vehicle)
                    if distance < min_distance:
                        min_distance = distance
                        closest_vehicle = other_vehicle
        
        return closest_vehicle
    
    def _calculate_distance(self, vehicle1: Vehicle, vehicle2: Vehicle) -> float:
        """Calculate distance between two vehicles"""
        return math.sqrt((vehicle1.x - vehicle2.x)**2 + (vehicle1.y - vehicle2.y)**2)
    
    def _attempt_lane_change(self, vehicle: Vehicle):
        """Attempt to change lanes (simplified implementation)"""
        # This is a simplified lane change - in a full implementation,
        # you would check for safe gaps and valid lane transitions
        pass
    
    def _should_remove_vehicle(self, vehicle: Vehicle) -> bool:
        """Check if vehicle should be removed from simulation"""
        margin = 100
        screen_width = self.road_config.screen_width
        screen_height = self.road_config.screen_height
        
        return (vehicle.x < -margin or vehicle.x > screen_width + margin or
                vehicle.y < -margin or vehicle.y > screen_height + margin)
    
    def draw_vehicles(self, screen: pygame.Surface):
        """Draw all vehicles on the screen"""
        for vehicle in self.vehicles:
            self._draw_vehicle(screen, vehicle)
    
    def _draw_vehicle(self, screen: pygame.Surface, vehicle: Vehicle):
        """Draw a single vehicle"""
        # Create vehicle rectangle
        rect = pygame.Rect(
            vehicle.x - vehicle.properties.length // 2,
            vehicle.y - vehicle.properties.width // 2,
            vehicle.properties.length,
            vehicle.properties.width
        )
        
        # Draw vehicle body
        pygame.draw.rect(screen, vehicle.properties.color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)  # Black border
        
        # Draw vehicle direction indicator (simple arrow)
        self._draw_direction_indicator(screen, vehicle)
    
    def _draw_direction_indicator(self, screen: pygame.Surface, vehicle: Vehicle):
        """Draw direction indicator on vehicle"""
        center_x, center_y = int(vehicle.x), int(vehicle.y)
        arrow_size = 8
        
        if vehicle.direction == LaneDirection.EAST:
            points = [(center_x + arrow_size, center_y), 
                     (center_x - arrow_size, center_y - arrow_size//2),
                     (center_x - arrow_size, center_y + arrow_size//2)]
        elif vehicle.direction == LaneDirection.WEST:
            points = [(center_x - arrow_size, center_y), 
                     (center_x + arrow_size, center_y - arrow_size//2),
                     (center_x + arrow_size, center_y + arrow_size//2)]
        elif vehicle.direction == LaneDirection.SOUTH:
            points = [(center_x, center_y + arrow_size), 
                     (center_x - arrow_size//2, center_y - arrow_size),
                     (center_x + arrow_size//2, center_y - arrow_size)]
        elif vehicle.direction == LaneDirection.NORTH:
            points = [(center_x, center_y - arrow_size), 
                     (center_x - arrow_size//2, center_y + arrow_size),
                     (center_x + arrow_size//2, center_y + arrow_size)]
        
        pygame.draw.polygon(screen, (255, 255, 255), points)
    
    def get_traffic_stats(self) -> Dict[str, Any]:
        """Get current traffic statistics"""
        stats = {
            'total_vehicles': len(self.vehicles),
            'vehicle_types': {},
            'average_speed': 0.0,
            'traffic_density': self.current_density.value
        }
        
        if self.vehicles:
            total_speed = 0
            for vehicle in self.vehicles:
                vehicle_type = vehicle.vehicle_type.value
                stats['vehicle_types'][vehicle_type] = stats['vehicle_types'].get(vehicle_type, 0) + 1
                total_speed += vehicle.speed
            
            stats['average_speed'] = total_speed / len(self.vehicles)
        
        return stats
    
    def clear_all_vehicles(self):
        """Remove all vehicles from the simulation"""
        self.vehicles.clear()
    
    def set_custom_spawn_probabilities(self, probabilities: Dict[VehicleType, float]):
        """Set custom spawn probabilities for vehicle types"""
        total_prob = sum(probabilities.values())
        if abs(total_prob - 1.0) > 0.01:
            # Normalize probabilities
            for vehicle_type in probabilities:
                probabilities[vehicle_type] /= total_prob
        
        for vehicle_type, probability in probabilities.items():
            if vehicle_type in self.vehicle_properties:
                self.vehicle_properties[vehicle_type].spawn_probability = probability