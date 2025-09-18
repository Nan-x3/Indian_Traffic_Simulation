import pygame
import math
import random
from abc import ABC, abstractmethod
from enum import Enum

class VehicleType(Enum):
    """Simple vehicle types - keep it basic!"""
    BIKE = "bike"           # Motorcycles/scooters
    CAR = "car"            # All passenger cars
    AUTO = "auto"          # Auto-rickshaw  
    BUS = "bus"            # All buses
    TRUCK = "truck"        # All trucks

class Direction(Enum):
    """Possible directions a vehicle can take"""
    STRAIGHT = "straight"
    LEFT = "left"
    RIGHT = "right"
    U_TURN = "u_turn"

class Lane:
    """Represents a traffic lane with position, direction, and legal boundaries"""
    def __init__(self, center_x, center_y, width, direction_angle, lane_number, road_side):
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.direction_angle = direction_angle  # Angle of traffic flow
        self.lane_number = lane_number  # 0 = leftmost, 1 = next, etc.
        self.road_side = road_side  # 'left', 'right', 'top', 'bottom'
        
        # Calculate lane boundaries for collision detection
        angle_rad = math.radians(direction_angle)
        perp_x = math.sin(angle_rad) * (width / 2)
        perp_y = -math.cos(angle_rad) * (width / 2)
        
        self.left_bound = (center_x - perp_x, center_y - perp_y)
        self.right_bound = (center_x + perp_x, center_y + perp_y)
        
        # Legal movement boundaries (set by lane manager)
        self.yellow_boundary = None  # Position of yellow line (cannot cross)
        self.white_boundary = None   # Position of white edge line
        self.can_change_left = True  # Can change to left lane
        self.can_change_right = True # Can change to right lane
        
    def is_position_in_lane(self, x, y):
        """Check if a position is within this lane boundaries"""
        # Calculate distance from lane center line
        angle_rad = math.radians(self.direction_angle)
        
        # Vector from lane center to position
        dx = x - self.center_x
        dy = y - self.center_y
        
        # Calculate perpendicular distance to lane center line
        perp_distance = abs(dx * math.sin(angle_rad) - dy * math.cos(angle_rad))
        
        return perp_distance <= self.width / 2
        
    def can_move_to_position(self, x, y):
        """Check if movement to position is legal (respects yellow lines)"""
        if self.yellow_boundary is None:
            return True  # No yellow line restriction
            
        # Check if position would cross yellow boundary
        if self.road_side in ['left', 'right']:
            # Horizontal roads - check Y position against yellow boundary
            if self.road_side == 'left':
                return y <= self.yellow_boundary  # Cannot go beyond yellow line
            else:  # right side
                return y >= self.yellow_boundary  # Cannot go beyond yellow line
        else:
            # Vertical roads - check X position against yellow boundary
            if self.road_side == 'top':
                return x <= self.yellow_boundary  # Cannot go beyond yellow line
            else:  # bottom side
                return x >= self.yellow_boundary  # Cannot go beyond yellow line

class VehicleBase(ABC):
    """Base class for all vehicles"""
    
    def __init__(self, x, y, angle, lane, destination):
        self.x = x
        self.y = y
        self.angle = angle
        self.original_angle = angle  # Store original lane direction - NEVER change this
        self.lane = lane  # Lane object
        self.destination = destination  # Direction enum

        # Physics
        self.speed = 0.0
        self.target_speed = random.uniform(0.7, 1.0) * self.get_max_speed()
        self.max_speed = self.get_max_speed()
        self.acceleration = self.get_acceleration()
        self.deceleration = self.get_deceleration()
        
        # Dimensions
        self.width = self.get_width()
        self.length = self.get_length()
        
        # Visual
        self.color = self.get_color()
        
        # Behavior
        self.following_distance = random.uniform(60, 100)
        
        # Lane discipline - strict angle control
        self.max_angle_deviation = 3  # Only 3 degrees deviation allowed
        self.lane_position_offset = 0  # Side offset within lane (for lane changing)
        self.lane_change_distance = random.uniform(40, 80)
        self.aggression = random.uniform(0.3, 0.8)
        self.min_gap = random.uniform(5, 10)  # Minimum gap to other vehicles
        
        # State
        self.is_changing_lanes = False
        self.target_lane = None
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
    
    def get_vehicle_type(self):
        return self.__class__.VEHICLE_TYPE
    
    def is_in_intersection(self, intersection_bounds):
        """Check if vehicle is in intersection area"""
        return (intersection_bounds['left'] <= self.x <= intersection_bounds['right'] and
                intersection_bounds['top'] <= self.y <= intersection_bounds['bottom'])
    
    def can_cross_lane_marking(self, current_pos, target_pos, road_config):
        """Check if vehicle can cross lane markings based on IRC rules - STRICT yellow line enforcement"""
        # RULE 1: NEVER cross yellow lines (center dividers)
        if self.lane and self.lane.yellow_boundary is not None:
            current_legal = self.lane.can_move_to_position(current_pos[0], current_pos[1])
            target_legal = self.lane.can_move_to_position(target_pos[0], target_pos[1])
            
            if not target_legal:
                return False  # Target position crosses yellow line - FORBIDDEN
        
        # RULE 2: Stay within white edge boundaries (don't go off road)
        if self.lane and self.lane.white_boundary is not None:
            if self.lane.road_side in ['left', 'right']:
                # Horizontal roads - check Y boundaries
                road_edge = self.lane.white_boundary
                if self.lane.road_side == 'left':
                    if target_pos[1] < road_edge:  # Going beyond road edge
                        return False
                else:  # right side
                    if target_pos[1] > road_edge:  # Going beyond road edge
                        return False
            else:
                # Vertical roads - check X boundaries
                road_edge = self.lane.white_boundary
                if self.lane.road_side == 'top':
                    if target_pos[0] < road_edge:  # Going beyond road edge
                        return False
                else:  # bottom side
                    if target_pos[0] > road_edge:  # Going beyond road edge
                        return False
        
        return True  # Movement is legal
    
    def get_valid_spawn_areas(self, road_config):
        """Get valid spawn areas based on lane markings"""
        valid_areas = []
        road_type = road_config.get('road_type', 'two_way_divided')
        lane_count = road_config.get('lane_count', 2)
        
        # Calculate lane widths and positions
        total_road_width = 200  # Approximate road width
        lane_width = total_road_width // (lane_count * 2)  # 2 directions
        
        center_x = 1920 // 2
        center_y = 1080 // 2
        
        if road_config.get('junction_type') == 'cross':
            # Cross junction - 4 directions
            # Left side lanes (going right)
            for i in range(lane_count):
                lane_y = center_y - (lane_width * (i + 0.5))
                valid_areas.append({
                    'x': 100, 'y': lane_y, 'angle': 0, 'side': 'left',
                    'lane_bounds': (lane_y - lane_width//2, lane_y + lane_width//2)
                })
            
            # Right side lanes (going left)  
            for i in range(lane_count):
                lane_y = center_y + (lane_width * (i + 0.5))
                valid_areas.append({
                    'x': 1820, 'y': lane_y, 'angle': 180, 'side': 'right',
                    'lane_bounds': (lane_y - lane_width//2, lane_y + lane_width//2)
                })
            
            # Top lanes (going down)
            for i in range(lane_count):
                lane_x = center_x - (lane_width * (i + 0.5))
                valid_areas.append({
                    'x': lane_x, 'y': 100, 'angle': 90, 'side': 'top',
                    'lane_bounds': (lane_x - lane_width//2, lane_x + lane_width//2)
                })
            
            # Bottom lanes (going up)
            for i in range(lane_count):
                lane_x = center_x + (lane_width * (i + 0.5))
                valid_areas.append({
                    'x': lane_x, 'y': 980, 'angle': 270, 'side': 'bottom',
                    'lane_bounds': (lane_x - lane_width//2, lane_x + lane_width//2)
                })
        
        return valid_areas
    
    def get_vehicle_ahead(self, all_vehicles, max_distance=150):
        """Find the nearest vehicle ahead in our lane direction with precise detection"""
        closest_vehicle = None
        min_distance = float('inf')
        
        # Calculate our direction vector using lane direction
        if self.lane:
            angle_rad = math.radians(self.lane.direction_angle)
        else:
            angle_rad = math.radians(self.angle)
            
        our_dx = math.cos(angle_rad)
        our_dy = math.sin(angle_rad)
        
        # Get our front position for more accurate detection
        front_x = self.x + (self.length / 2) * our_dx
        front_y = self.y + (self.length / 2) * our_dy
        
        for vehicle in all_vehicles:
            if vehicle == self:
                continue
            
            # Vector from our front to the other vehicle's rear
            other_rear_x = vehicle.x - (vehicle.length / 2) * math.cos(math.radians(vehicle.angle))
            other_rear_y = vehicle.y - (vehicle.length / 2) * math.sin(math.radians(vehicle.angle))
            
            dx = other_rear_x - front_x
            dy = other_rear_y - front_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > max_distance:
                continue
            
            # Check if vehicle is ahead of us (dot product > 0)
            dot_product = dx * our_dx + dy * our_dy
            if dot_product > 0:  # Vehicle is ahead
                # Check if it's in our lane using more precise lane detection
                cross_product = abs(dx * our_dy - dy * our_dx)
                
                # More strict lane width check
                lane_width = self.lane.width if self.lane else 40
                if cross_product < lane_width * 0.8:  # Must be within 80% of lane width
                    # Additional check: vehicles should be moving in similar direction
                    angle_diff = abs(vehicle.angle - self.angle)
                    while angle_diff > 180:
                        angle_diff -= 360
                    while angle_diff < -180:
                        angle_diff += 360
                    
                    if abs(angle_diff) < 45:  # Similar direction (within 45 degrees)
                        if distance < min_distance:
                            closest_vehicle = vehicle
                            min_distance = distance
        
        return closest_vehicle, min_distance if closest_vehicle else None
    
    def smooth_speed_control(self, all_vehicles, dt):
        """Smooth, intelligent speed control that responds properly to traffic"""
        # First, check for vehicles ahead
        vehicle_ahead, distance_ahead = self.get_vehicle_ahead(all_vehicles, max_distance=120)
        
        if vehicle_ahead and distance_ahead is not None:
            # Calculate appropriate following distance
            vehicle_type = self.get_vehicle_type()
            if vehicle_type == VehicleType.BIKE:
                min_distance = 15
                reaction_time = 1.0
            elif vehicle_type == VehicleType.AUTO:
                min_distance = 18
                reaction_time = 1.2
            elif vehicle_type == VehicleType.CAR:
                min_distance = 22
                reaction_time = 1.5
            else:  # BUS, TRUCK
                min_distance = 30
                reaction_time = 2.0
            
            # Dynamic following distance based on speed
            safe_following_distance = min_distance + (self.speed * reaction_time)
            
            # Calculate relative speed
            speed_difference = self.speed - vehicle_ahead.speed
            
            if distance_ahead < min_distance:
                # TOO CLOSE: Emergency braking
                brake_force = self.deceleration * 2.5
                self.speed = max(0, self.speed - brake_force * dt)
                return "emergency_stop"
            
            elif distance_ahead < safe_following_distance * 0.8:
                # CLOSE: Need to slow down significantly
                if speed_difference > 0:  # We're faster
                    # Match the speed of vehicle ahead with some buffer
                    target_speed = max(0, vehicle_ahead.speed * 0.8)
                    brake_force = self.deceleration * (1.5 + speed_difference / 5)
                    self.speed = max(target_speed, self.speed - brake_force * dt)
                return "heavy_braking"
            
            elif distance_ahead < safe_following_distance:
                # FOLLOWING: Maintain safe distance
                if speed_difference > 0:  # We're going faster
                    # Gentle braking to match speed
                    target_speed = vehicle_ahead.speed * 0.95
                    brake_force = self.deceleration * 0.8
                    self.speed = max(target_speed, self.speed - brake_force * dt)
                elif speed_difference < -0.5:  # Vehicle ahead is much faster
                    # Gentle acceleration to keep up
                    accel_force = self.acceleration * 0.6
                    target_speed = min(self.target_speed, vehicle_ahead.speed * 1.05)
                    self.speed = min(target_speed, self.speed + accel_force * dt)
                return "following"
            
            elif distance_ahead < safe_following_distance * 1.5:
                # COMFORTABLE: Gradual adjustment
                target_speed = min(self.target_speed, vehicle_ahead.speed * 1.1)
                if self.speed < target_speed:
                    # Gentle acceleration
                    accel_force = self.acceleration * 0.7
                    self.speed = min(target_speed, self.speed + accel_force * dt)
                elif self.speed > target_speed:
                    # Light braking
                    brake_force = self.deceleration * 0.5
                    self.speed = max(target_speed, self.speed - brake_force * dt)
                return "comfortable_following"
        
        # No vehicle ahead or safe distance - normal acceleration
        if self.speed < self.target_speed:
            # Normal acceleration with some randomness for realism
            accel_factor = 0.8 + (self.aggression * 0.4)  # 0.8 to 1.2 multiplier
            accel_force = self.acceleration * accel_factor
            self.speed = min(self.target_speed, self.speed + accel_force * dt)
            return "accelerating"
        
        elif self.speed > self.target_speed:
            # Gentle slowdown to target speed
            brake_force = self.deceleration * 0.3
            self.speed = max(self.target_speed, self.speed - brake_force * dt)
            return "cruising_slowdown"
        
        return "cruising"
    
    def calm_collision_avoidance(self, all_vehicles, road_config):
        """Calm, controlled collision avoidance - PREVENT OVERLAPPING with intersection awareness"""
        # FIRST CHECK: Simple collision detection with immediate stop
        for vehicle in all_vehicles:
            if vehicle == self:
                continue
            
            # Simple distance check
            distance = math.sqrt((self.x - vehicle.x)**2 + (self.y - vehicle.y)**2)
            if distance < 40:  # If any vehicle within 40 pixels, STOP IMMEDIATELY
                self.speed = 0
                return "emergency_collision_stop"
        
        # INDIAN TRAFFIC SQUEEZE: Check if we can squeeze into gaps
        squeeze_attempt = self.indian_squeeze_maneuver(all_vehicles)
        if squeeze_attempt:
            return squeeze_attempt
        
        # Check for any vehicles too close to us (360-degree check)
        nearby_vehicles = self.get_all_nearby_vehicles(all_vehicles, max_distance=60)
        
        # INTERSECTION DEADLOCK PREVENTION
        if self.at_intersection:
            # In intersection - be more aggressive about moving through
            # Don't stop unless absolutely necessary
            
            # Check if we're blocking the intersection
            vehicles_in_intersection = 0
            for vehicle, distance in nearby_vehicles:
                if vehicle.at_intersection:
                    vehicles_in_intersection += 1
            
            # If too many vehicles in intersection, try to clear it
            if vehicles_in_intersection > 4:
                # Intersection is crowded - be more aggressive
                self.speed = min(self.speed + 0.5, self.target_speed * 0.8)
                return "clearing_intersection"
        
        # IMMEDIATE COLLISION CHECK - but be smarter about it
        for vehicle, distance in nearby_vehicles:
            if self.check_collision_with_vehicle(vehicle):
                # Check if we're both in intersection - if so, one must yield
                if self.at_intersection and vehicle.at_intersection:
                    # Yield based on vehicle type (larger vehicles have priority)
                    my_size = max(self.length, self.width)
                    their_size = max(vehicle.length, vehicle.width)
                    
                    if my_size < their_size:
                        # We're smaller - yield
                        self.speed = 0
                        return "yielding_in_intersection"
                    else:
                        # We're larger or same size - keep moving slowly
                        self.speed = min(self.speed, 1.0)
                        return "priority_in_intersection"
                else:
                    # Normal collision - stop
                    self.speed = 0
                    return "collision_stop"
        
        # Find vehicle directly ahead in our lane
        vehicle_ahead, distance_ahead = self.get_vehicle_ahead(all_vehicles, max_distance=100)
        
        if vehicle_ahead and distance_ahead is not None:
            # Don't enter intersection if there's no room on the other side
            if not self.at_intersection:
                intersection_bounds = getattr(self, '_intersection_bounds', None)
                if intersection_bounds and not self.should_enter_intersection(all_vehicles, intersection_bounds):
                    self.speed = 0
                    return "waiting_for_intersection_space"            # Calculate safe following distance based on our speed and vehicle type
            vehicle_type = self.get_vehicle_type()
            if vehicle_type == VehicleType.BIKE:
                base_distance = 25  # Increased minimum distance
                speed_factor = 1.5
            elif vehicle_type == VehicleType.AUTO:
                base_distance = 30
                speed_factor = 1.8
            elif vehicle_type == VehicleType.CAR:
                base_distance = 35
                speed_factor = 2.0
            else:  # BUS, TRUCK
                base_distance = 45
                speed_factor = 2.5
            
            safe_distance = base_distance + (self.speed * speed_factor)
            
            # Calculate actual physical collision distance
            my_front = self.length / 2
            their_rear = vehicle_ahead.length / 2
            collision_distance = my_front + their_rear + 8  # Increased safety buffer
            
            if distance_ahead < collision_distance:
                # CRITICAL: About to physically collide
                self.speed = 0
                return "emergency_stop"
            
            elif distance_ahead < safe_distance * 0.4:
                # VERY CLOSE: Hard braking
                target_speed = max(0, vehicle_ahead.speed * 0.3)
                self.speed = max(target_speed, self.speed * 0.2)
                return "hard_brake"
            
            elif distance_ahead < safe_distance * 0.7:
                # CLOSE: Significant slowdown
                target_speed = max(vehicle_ahead.speed * 0.7, 2.0)
                self.speed = max(target_speed, self.speed * 0.5)
                return "moderate_brake"
            
            elif distance_ahead < safe_distance:
                # FOLLOWING: Match speed with buffer
                target_speed = min(vehicle_ahead.speed * 0.9, self.target_speed)
                if self.speed > target_speed:
                    self.speed = max(target_speed, self.speed * 0.8)
                return "controlled_following"
            
            else:
                # SAFE: Normal operation
                return "safe_distance"
        
        return "free_flow"
    
    def should_enter_intersection(self, all_vehicles, intersection_bounds):
        """Check if it's safe to enter intersection - prevent gridlock"""
        if self.at_intersection:
            return True  # Already in intersection
        
        # Check if we're about to enter intersection
        next_x = self.x + self.speed * math.cos(math.radians(self.angle)) * 2
        next_y = self.y + self.speed * math.sin(math.radians(self.angle)) * 2
        
        will_enter = (intersection_bounds['left'] <= next_x <= intersection_bounds['right'] and
                     intersection_bounds['top'] <= next_y <= intersection_bounds['bottom'])
        
        if not will_enter:
            return True  # Not entering intersection
        
        # Check if there's space on the other side of intersection
        # Look ahead in our direction beyond the intersection
        angle_rad = math.radians(self.lane.direction_angle if self.lane else self.angle)
        
        # Check multiple points beyond intersection
        for check_distance in [80, 100, 120]:
            check_x = next_x + check_distance * math.cos(angle_rad)
            check_y = next_y + check_distance * math.sin(angle_rad)
            
            # Check if any vehicle is blocking our exit path
            for vehicle in all_vehicles:
                if vehicle == self:
                    continue
                    
                distance_to_exit_point = math.sqrt((vehicle.x - check_x)**2 + (vehicle.y - check_y)**2)
                if distance_to_exit_point < 30:  # Exit path is blocked
                    return False
        
        # Check how many vehicles are already in intersection
        vehicles_in_intersection = 0
        for vehicle in all_vehicles:
            if vehicle != self and vehicle.at_intersection:
                vehicles_in_intersection += 1
        
        # Don't enter if intersection is too crowded
        if vehicles_in_intersection >= 6:
            return False
        
        return True  # Safe to enter
        """Keep vehicle gently centered in lane - MINIMAL corrections to prevent twitching"""
        if not self.lane:
            return
            
        # Calculate how far we are from lane center
        angle_rad = math.radians(self.lane.direction_angle)
        
        # Vector from lane center to our position
        dx = self.x - self.lane.center_x
        dy = self.y - self.lane.center_y
        
        # Calculate perpendicular distance from lane center line
        perp_distance = dx * math.sin(angle_rad) - dy * math.cos(angle_rad)
        
        # Only correct if we're significantly off center (more than 1/3 lane width)
        max_deviation = self.lane.width * 0.35  # Increased tolerance
        
        if abs(perp_distance) > max_deviation:
            # Very gentle correction towards lane center - reduced strength
            correction_strength = 0.05  # Much more gentle (was 0.1)
            
            if perp_distance > 0:
                # We're too far right, gently steer left
                self.angle -= correction_strength
            else:
                # We're too far left, gently steer right
                self.angle += correction_strength
            
            # Limit angle deviation from lane direction
            angle_deviation = self.angle - self.lane.direction_angle
            while angle_deviation > 180:
                angle_deviation -= 360
            while angle_deviation < -180:
                angle_deviation += 360
            
            # Maximum 1.5 degrees deviation allowed (reduced from 2.0)
            max_angle_deviation = 1.5
            if abs(angle_deviation) > max_angle_deviation:
                if angle_deviation > 0:
                    self.angle = self.lane.direction_angle + max_angle_deviation
                else:
                    self.angle = self.lane.direction_angle - max_angle_deviation
    
    def can_change_to_right_lane(self, all_vehicles, road_config):
        """Check if vehicle can safely move to right lane"""
        # Calculate right side position
        angle_rad = math.radians(self.original_angle)
        perp_angle = self.original_angle + 90
        perp_rad = math.radians(perp_angle)
        
        # Check positions to the right
        for side_distance in [25, 35, 45]:  # Check multiple distances
            check_x = self.x + side_distance * math.cos(perp_rad)
            check_y = self.y + side_distance * math.sin(perp_rad)
            
            # Check if this position would violate lane markings
            if not self.can_cross_lane_marking((self.x, self.y), (check_x, check_y), road_config):
                return False
            
            # Check if any vehicle is too close to this position
            for vehicle in all_vehicles:
                if vehicle == self:
                    continue
                distance = math.sqrt((vehicle.x - check_x)**2 + (vehicle.y - check_y)**2)
                if distance < 30:  # Too close
                    return False
        
        return True
    
    def can_change_to_left_lane(self, all_vehicles, road_config):
        """Check if vehicle can safely move to left lane"""
        # Calculate left side position
        angle_rad = math.radians(self.original_angle)
        perp_angle = self.original_angle - 90
        perp_rad = math.radians(perp_angle)
        
        # Check positions to the left
        for side_distance in [25, 35, 45]:
            check_x = self.x + side_distance * math.cos(perp_rad)
            check_y = self.y + side_distance * math.sin(perp_rad)
            
            # Check if this position would violate lane markings
            if not self.can_cross_lane_marking((self.x, self.y), (check_x, check_y), road_config):
                return False
            
            # Check if any vehicle is too close
            for vehicle in all_vehicles:
                if vehicle == self:
                    continue
                distance = math.sqrt((vehicle.x - check_x)**2 + (vehicle.y - check_y)**2)
                if distance < 30:
                    return False
        
        return True
    
    def can_squeeze_through_gap(self, all_vehicles):
        """Check if there's a gap between vehicles we can squeeze through"""
        # Look for gaps between vehicles ahead
        ahead_vehicles = []
        angle_rad = math.radians(self.original_angle)
        
        # Find vehicles ahead of us
        for vehicle in all_vehicles:
            if vehicle == self:
                continue
            
            # Check if vehicle is ahead
            dx = vehicle.x - self.x
            dy = vehicle.y - self.y
            dot_product = dx * math.cos(angle_rad) + dy * math.sin(angle_rad)
            
            if dot_product > 0:  # Vehicle is ahead
                distance = math.sqrt(dx*dx + dy*dy)
                if distance < 80:  # Within relevant distance
                    ahead_vehicles.append((vehicle, distance))
        
        # Check gaps between vehicles
        if len(ahead_vehicles) >= 2:
            ahead_vehicles.sort(key=lambda x: x[1])  # Sort by distance
            
            for i in range(len(ahead_vehicles) - 1):
                v1, d1 = ahead_vehicles[i]
                v2, d2 = ahead_vehicles[i + 1]
                
                # Calculate gap size
                gap_distance = math.sqrt((v2.x - v1.x)**2 + (v2.y - v1.y)**2)
                our_size = max(self.length, self.width)
                
                if gap_distance > our_size + 15:  # Gap is big enough
                    return True
        
        return False
    
    def get_front_position(self):
        """Get the front center position of vehicle"""
        angle_rad = math.radians(self.angle)
        front_x = self.x + (self.length / 2) * math.cos(angle_rad)
        front_y = self.y + (self.length / 2) * math.sin(angle_rad)
        return front_x, front_y
    
    def get_vehicle_ahead(self, vehicles, max_distance=150):
        """Find closest vehicle ahead in same lane"""
        closest_vehicle = None
        min_distance = max_distance
        
        front_x, front_y = self.get_front_position()
        
        for vehicle in vehicles:
            if vehicle == self or vehicle.lane != self.lane:
                continue
                
            # Check if vehicle is ahead
            to_vehicle_x = vehicle.x - front_x
            to_vehicle_y = vehicle.y - front_y
            distance = math.sqrt(to_vehicle_x**2 + to_vehicle_y**2)
            
            # Check if in front (using dot product with direction vector)
            angle_rad = math.radians(self.angle)
            forward_x = math.cos(angle_rad)
            forward_y = math.sin(angle_rad)
            
            dot_product = to_vehicle_x * forward_x + to_vehicle_y * forward_y
            
            if dot_product > 0 and distance < min_distance:
                min_distance = distance
                closest_vehicle = vehicle
        
        return closest_vehicle, min_distance
    
    def can_change_lane(self, target_lane, vehicles):
        """Check if lane change is safe"""
        if not target_lane:
            return False
            
        # Check for vehicles in target lane
        for vehicle in vehicles:
            if vehicle == self or vehicle.lane != target_lane:
                continue
                
            distance = math.sqrt((vehicle.x - self.x)**2 + (vehicle.y - self.y)**2)
            if distance < self.lane_change_distance + self.min_gap:
                return False
        
        return True
    
    def update_behavior(self, vehicles, intersection_bounds, dt):
        """Update vehicle behavior with CALM, CONTROLLED traffic rules and NO OVERLAPPING"""
        # Check if at intersection
        self.at_intersection = self.is_in_intersection(intersection_bounds)
        self._intersection_bounds = intersection_bounds  # Store for intersection checks
        
        # PRIORITY 0: Emergency collision separation (if vehicles are overlapping)
        self.emergency_separation(vehicles)
        
        # PRIORITY 1: Gentle lane keeping (no harsh corrections)
        self.gentle_lane_keeping()
        
        # PRIORITY 2: Calm collision avoidance (no panic)
        collision_status = self.calm_collision_avoidance(vehicles, {})
        
        # PRIORITY 3: Smooth speed control (proper following behavior)
        speed_status = self.smooth_speed_control(vehicles, dt)
        
        # PRIORITY 4: Update position smoothly
        self.update_position(dt)
        
        # PRIORITY 5: Ensure we never cross yellow lines
        if self.lane:
            current_pos = (self.x, self.y)
            if not self.lane.can_move_to_position(self.x, self.y):
                # We've crossed a yellow line - emergency correction
                # Move back towards lane center
                angle_rad = math.radians(self.lane.direction_angle)
                
                # Calculate vector towards lane center
                dx_to_center = self.lane.center_x - self.x
                dy_to_center = self.lane.center_y - self.y
                
                # Apply small correction towards lane center
                correction_strength = 2.0  # pixels per frame
                if abs(dx_to_center) > 1:
                    self.x += correction_strength * (1 if dx_to_center > 0 else -1)
                if abs(dy_to_center) > 1:
                    self.y += correction_strength * (1 if dy_to_center > 0 else -1)
                
                # Force angle back to lane direction
                self.angle = self.lane.direction_angle
    
    def emergency_separation(self, vehicles):
        """Emergency system to separate overlapping vehicles - NO SIDEWAYS MOVEMENT"""
        for vehicle in vehicles:
            if vehicle == self:
                continue
                
            if self.check_collision_with_vehicle(vehicle):
                # Vehicles are overlapping! Emergency separation
                dx = self.x - vehicle.x
                dy = self.y - vehicle.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < 1:  # Completely overlapping
                    # Move vehicles backward along their respective lane directions ONLY
                    if self.lane:
                        angle_rad = math.radians(self.lane.direction_angle)
                        # Move backward in our lane direction
                        self.x -= 15 * math.cos(angle_rad)
                        self.y -= 15 * math.sin(angle_rad)
                    
                    if vehicle.lane:
                        angle_rad = math.radians(vehicle.lane.direction_angle)
                        # Move the other vehicle backward in its lane direction
                        vehicle.x -= 15 * math.cos(angle_rad)
                        vehicle.y -= 15 * math.sin(angle_rad)
                else:
                    # Only separate if one vehicle is clearly behind the other
                    # Don't separate vehicles that are side-by-side in different lanes
                    
                    # Check if we're in the same lane or adjacent lanes
                    if self.lane and vehicle.lane:
                        # If different lanes, don't separate sideways
                        if self.lane.road_side != vehicle.lane.road_side:
                            continue  # Different roads, don't separate
                        
                        # If same road, check if one is behind the other
                        my_angle_rad = math.radians(self.lane.direction_angle)
                        my_forward_x = math.cos(my_angle_rad)
                        my_forward_y = math.sin(my_angle_rad)
                        
                        # Check if other vehicle is behind us in our direction
                        to_other_x = vehicle.x - self.x
                        to_other_y = vehicle.y - self.y
                        dot_product = to_other_x * my_forward_x + to_other_y * my_forward_y
                        
                        if dot_product < 0:  # Other vehicle is behind us
                            # Move the vehicle behind us backward in its lane direction
                            other_angle_rad = math.radians(vehicle.lane.direction_angle)
                            vehicle.x -= 8 * math.cos(other_angle_rad)
                            vehicle.y -= 8 * math.sin(other_angle_rad)
                            vehicle.speed = 0
                        else:  # Other vehicle is ahead of us
                            # Move us backward in our lane direction
                            self.x -= 8 * math.cos(my_angle_rad)
                            self.y -= 8 * math.sin(my_angle_rad)
                            self.speed = 0
    
    def attempt_lane_change(self, _vehicles):
        """Try to change lanes to overtake"""
        # Implementation depends on road structure - placeholder for now
        pass
    
    def update_position(self, dt):
        """Update position based on speed and angle"""
        angle_rad = math.radians(self.angle)
        self.x += self.speed * math.cos(angle_rad) * dt * 60
        self.y += self.speed * math.sin(angle_rad) * dt * 60
    
    def get_corners(self):
        """Get corner positions for collision detection"""
        angle_rad = math.radians(self.angle)
        half_length = self.length / 2
        half_width = self.width / 2
        
        corners = [
            (-half_length, -half_width),
            (half_length, -half_width),
            (half_length, half_width),
            (-half_length, half_width)
        ]
        
        rotated_corners = []
        for corner_x, corner_y in corners:
            rotated_x = corner_x * math.cos(angle_rad) - corner_y * math.sin(angle_rad)
            rotated_y = corner_x * math.sin(angle_rad) + corner_y * math.cos(angle_rad)
            final_x = self.x + rotated_x
            final_y = self.y + rotated_y
            rotated_corners.append((final_x, final_y))
        
        return rotated_corners
    
    def check_collision_with_vehicle(self, other_vehicle):
        """Check if this vehicle would collide with another vehicle - STRICTER CHECK"""
        # Calculate distance between vehicle centers
        dx = self.x - other_vehicle.x
        dy = self.y - other_vehicle.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Calculate minimum safe distance with LARGER buffer
        my_radius = max(self.length, self.width) / 2
        other_radius = max(other_vehicle.length, other_vehicle.width) / 2
        min_safe_distance = my_radius + other_radius + 30  # Increased buffer from 10 to 30
        
        return distance < min_safe_distance
    
    def get_all_nearby_vehicles(self, all_vehicles, max_distance=80):
        """Get all vehicles within collision range"""
        nearby = []
        for vehicle in all_vehicles:
            if vehicle != self:
                distance = math.sqrt((self.x - vehicle.x)**2 + (self.y - vehicle.y)**2)
                if distance <= max_distance:
                    nearby.append((vehicle, distance))
        return nearby
    
    def find_nearby_vehicles(self, all_vehicles, max_distance=80):
        """Find vehicles within a certain distance"""
        nearby = []
        for vehicle in all_vehicles:
            if vehicle != self:
                distance = math.sqrt((self.x - vehicle.x)**2 + (self.y - vehicle.y)**2)
                if distance <= max_distance:
                    nearby.append((vehicle, distance))
        
        # Sort by distance (closest first)
        nearby.sort(key=lambda x: x[1])
        return nearby
    
    def strict_lane_collision_avoidance(self, all_vehicles):
        """Strict lane-based collision avoidance - NO random angle changes"""
        # Check if there's a vehicle directly ahead in our lane
        front_vehicle = None
        min_distance = float('inf')
        
        angle_rad = math.radians(self.original_angle)  # Use ORIGINAL angle, not current
        
        # Check ahead in our lane direction only
        for distance in range(10, 50, 5):  # Check 10-50 pixels ahead
            check_x = self.x + distance * math.cos(angle_rad)
            check_y = self.y + distance * math.sin(angle_rad)
            
            for vehicle in all_vehicles:
                if vehicle == self:
                    continue
                
                vehicle_distance = math.sqrt((vehicle.x - check_x)**2 + (vehicle.y - check_y)**2)
                
                if vehicle_distance < 20 and distance < min_distance:  # Vehicle in our path
                    front_vehicle = vehicle
                    min_distance = distance
                    break
        
        if front_vehicle:
            # Vehicle ahead detected - ONLY slow down, DO NOT change angle
            if min_distance < 15:
                # Very close - emergency brake
                self.speed = max(self.speed * 0.1, 1)
            elif min_distance < 25:
                # Close - brake hard
                self.speed = max(self.speed * 0.3, 3)
            elif min_distance < 40:
                # Moderate distance - controlled slowdown
                self.speed = max(self.speed * 0.6, 6)
            
            return True  # Collision avoidance active
        
        return False  # No collision avoidance needed
    
    def indian_squeeze_maneuver(self, all_vehicles):
        """Indian traffic style - squeeze into any available gap, even off-lane"""
        my_width = self.width
        my_length = self.length
        
        # Check for gaps to the left and right (perpendicular to our direction)
        if not self.lane:
            return False
            
        angle_rad = math.radians(self.lane.direction_angle)
        # Perpendicular directions (left and right of our travel direction)
        left_angle = self.lane.direction_angle - 90
        right_angle = self.lane.direction_angle + 90
        
        left_x = math.cos(math.radians(left_angle))
        left_y = math.sin(math.radians(left_angle))
        right_x = math.cos(math.radians(right_angle))
        right_y = math.sin(math.radians(right_angle))
        
        # Check gaps to the left
        left_gap = self.check_gap_size(all_vehicles, left_x, left_y, max_check_distance=50)
        # Check gaps to the right  
        right_gap = self.check_gap_size(all_vehicles, right_x, right_y, max_check_distance=50)
        
        # Minimum gap needed (vehicle width + small buffer)
        min_gap_needed = my_width + 8  # 8 pixel buffer
        
        # If there's a gap on either side that we can fit into
        if left_gap > min_gap_needed:
            # Squeeze left - move into the gap
            squeeze_distance = min(10, left_gap - my_width - 5)  # Don't move too much at once
            self.x += squeeze_distance * left_x
            self.y += squeeze_distance * left_y
            # Keep moving forward while squeezing
            self.speed = max(self.speed * 0.8, 2.0)  # Slow down a bit while maneuvering
            return "squeezing_left"
            
        elif right_gap > min_gap_needed:
            # Squeeze right - move into the gap
            squeeze_distance = min(10, right_gap - my_width - 5)
            self.x += squeeze_distance * right_x  
            self.y += squeeze_distance * right_y
            # Keep moving forward while squeezing
            self.speed = max(self.speed * 0.8, 2.0)
            return "squeezing_right"
        
        return False  # No suitable gap found
    
    def check_gap_size(self, all_vehicles, direction_x, direction_y, max_check_distance=50):
        """Check how much space is available in a given direction"""
        # Check multiple points in the given direction
        for check_distance in range(5, max_check_distance, 5):
            check_x = self.x + check_distance * direction_x
            check_y = self.y + check_distance * direction_y
            
            # See if any vehicle is at this position
            for vehicle in all_vehicles:
                if vehicle == self:
                    continue
                    
                vehicle_distance = math.sqrt((vehicle.x - check_x)**2 + (vehicle.y - check_y)**2)
                vehicle_size = max(vehicle.width, vehicle.length) / 2
                
                if vehicle_distance < vehicle_size + 5:  # Vehicle is blocking this space
                    return check_distance - 5  # Return available gap size
        
        return max_check_distance  # No obstruction found in range
    
    def enforce_strict_lane_discipline(self):
        """Force vehicle to stay in lane direction"""
        # Calculate how far we've deviated from original lane direction
        angle_deviation = self.angle - self.original_angle
        
        # Normalize angle difference
        while angle_deviation > 180:
            angle_deviation -= 360
        while angle_deviation < -180:
            angle_deviation += 360
        
        # If we've deviated too much, force correction
        if abs(angle_deviation) > self.max_angle_deviation:
            # Hard correction back to lane direction
            if angle_deviation > 0:
                self.angle = self.original_angle + self.max_angle_deviation
            else:
                self.angle = self.original_angle - self.max_angle_deviation
        
        # Gradual correction towards original lane direction
        if abs(angle_deviation) > 1:  # Allow 1 degree natural variation
            correction_strength = 0.5  # Gentle correction
            if angle_deviation > 0:
                self.angle -= correction_strength
            else:
                self.angle += correction_strength
    
    def draw(self, screen):
        """Draw vehicle on screen"""
        corners = self.get_corners()
        
        # Draw body
        pygame.draw.polygon(screen, self.color, corners)
        # Draw outline
        pygame.draw.polygon(screen, (0, 0, 0), corners, 2)
        
        # Draw front indicator
        angle_rad = math.radians(self.angle)
        front_x = self.x + (self.length / 2) * math.cos(angle_rad)
        front_y = self.y + (self.length / 2) * math.sin(angle_rad)
        pygame.draw.circle(screen, (255, 255, 255), (int(front_x), int(front_y)), 3)
        
        # Draw destination indicator (small colored dot)
        dest_colors = {
            Direction.STRAIGHT: (0, 255, 0),
            Direction.LEFT: (255, 255, 0),
            Direction.RIGHT: (0, 0, 255),
            Direction.U_TURN: (255, 0, 255)
        }
        if self.destination in dest_colors:
            pygame.draw.circle(screen, dest_colors[self.destination], 
                            (int(self.x), int(self.y)), 4)

# ============================================================================
# THE 5 VEHICLE TYPES
# ============================================================================

class Bike(VehicleBase):
    """Motorcycles and scooters"""
    VEHICLE_TYPE = VehicleType.BIKE
    
    def get_max_speed(self): return random.uniform(4.0, 5.0)
    def get_acceleration(self): return 0.20
    def get_deceleration(self): return 0.50
    def get_width(self): return 8
    def get_length(self): return 16
    def get_color(self): return (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))

class Car(VehicleBase):
    """All passenger cars - sedans, hatchbacks, SUVs"""
    VEHICLE_TYPE = VehicleType.CAR
    
    def get_max_speed(self): return random.uniform(3.0, 4.0)
    def get_acceleration(self): return 0.15
    def get_deceleration(self): return 0.40
    def get_width(self): return 18
    def get_length(self): return 35
    def get_color(self): return (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

class Auto(VehicleBase):
    """Auto-rickshaw (three-wheeler)"""
    VEHICLE_TYPE = VehicleType.AUTO
    
    def get_max_speed(self): return random.uniform(2.0, 3.0)
    def get_acceleration(self): return 0.12
    def get_deceleration(self): return 0.35
    def get_width(self): return 12
    def get_length(self): return 22
    def get_color(self): return (255, 255, 0)  # Yellow auto

class Bus(VehicleBase):
    """All buses - city, school, etc."""
    VEHICLE_TYPE = VehicleType.BUS
    
    def get_max_speed(self): return random.uniform(1.5, 2.5)
    def get_acceleration(self): return 0.08
    def get_deceleration(self): return 0.25
    def get_width(self): return 25
    def get_length(self): return 65
    def get_color(self): return (255, 165, 0)  # Orange bus

class Truck(VehicleBase):
    """All trucks - small, large, delivery"""
    VEHICLE_TYPE = VehicleType.TRUCK
    
    def get_max_speed(self): return random.uniform(1.8, 2.8)
    def get_acceleration(self): return 0.10
    def get_deceleration(self): return 0.30
    def get_width(self): return 22
    def get_length(self): return 55
    def get_color(self): return (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))

# ============================================================================
# LANE MANAGEMENT SYSTEM
# ============================================================================

class LaneManager:
    """Manages lane structure for proper vehicle spawning and movement"""
    
    def __init__(self):
        self.lanes = []
        self.intersection_bounds = {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
    
    def setup_lanes(self, road_config, center_x=960, center_y=540):
        """Setup lanes based on road configuration"""
        self.lanes = []
        lane_width = 40
        total_lanes = road_config['lane_count']
        road_width = total_lanes * lane_width
        
        # Calculate intersection bounds
        intersection_padding = 5
        intersection_size = road_width + intersection_padding
        intersection_half = intersection_size // 2
        
        self.intersection_bounds = {
            'left': center_x - intersection_half,
            'right': center_x + intersection_half,
            'top': center_y - intersection_half,
            'bottom': center_y + intersection_half
        }
        
        if road_config['junction_type'] == 'cross':
            self._setup_cross_lanes(road_config, center_x, center_y, lane_width, total_lanes)
        else:
            self._setup_t_lanes(road_config, center_x, center_y, lane_width, total_lanes)
    
    def _setup_cross_lanes(self, road_config, center_x, center_y, lane_width, total_lanes):
        """Setup lanes for cross junction with proper lane boundaries based on road markings"""
        road_half_width = (total_lanes * lane_width) // 2
        
        # Determine lanes per direction based on road type
        if road_config['road_type'] == '1way':
            lanes_per_dir = total_lanes
        else:
            lanes_per_dir = total_lanes // 2
        
        # Calculate lane boundaries based on IRC lane marking rules
        # For 2way_with_divider: lanes are separated by yellow center line
        # For 2way_without_divider: lanes are separated by single yellow line
        # For 1way: all lanes go same direction
        
        if road_config['road_type'] == '2way_with_divider':
            # LEFT ROAD - vehicles moving RIGHT (before center)
            for i in range(lanes_per_dir):
                # Position lanes between white edge and yellow center divider
                lane_offset = -road_half_width + (i + 0.5) * lane_width
                lane_center_y = center_y + lane_offset
                
                # Create lane with proper boundaries
                lane = Lane(center_x - 400, lane_center_y, lane_width, 0, i, 'left')
                lane.yellow_boundary = center_y  # Cannot cross this line
                lane.white_boundary = center_y - road_half_width  # Road edge
                self.lanes.append(lane)
            
            # RIGHT ROAD - vehicles moving LEFT (after center)
            for i in range(lanes_per_dir):
                # Position lanes between yellow center divider and white edge
                lane_offset = road_half_width - (i + 0.5) * lane_width
                lane_center_y = center_y + lane_offset
                
                lane = Lane(center_x + 400, lane_center_y, lane_width, 180, i, 'right')
                lane.yellow_boundary = center_y  # Cannot cross this line
                lane.white_boundary = center_y + road_half_width  # Road edge
                self.lanes.append(lane)
            
            # TOP ROAD - vehicles moving DOWN (before center)
            for i in range(lanes_per_dir):
                lane_offset = -road_half_width + (i + 0.5) * lane_width
                lane_center_x = center_x + lane_offset
                
                lane = Lane(lane_center_x, center_y - 400, lane_width, 90, i, 'top')
                lane.yellow_boundary = center_x  # Cannot cross this line
                lane.white_boundary = center_x - road_half_width  # Road edge
                self.lanes.append(lane)
            
            # BOTTOM ROAD - vehicles moving UP (after center)
            for i in range(lanes_per_dir):
                lane_offset = road_half_width - (i + 0.5) * lane_width
                lane_center_x = center_x + lane_offset
                
                lane = Lane(lane_center_x, center_y + 400, lane_width, 270, i, 'bottom')
                lane.yellow_boundary = center_x  # Cannot cross this line
                lane.white_boundary = center_x + road_half_width  # Road edge
                self.lanes.append(lane)
                
        elif road_config['road_type'] == '2way_without_divider':
            # Similar setup but with single yellow center line
            # LEFT ROAD - vehicles moving RIGHT
            for i in range(lanes_per_dir):
                lane_offset = -road_half_width + (i + 0.5) * lane_width
                lane_center_y = center_y + lane_offset
                
                lane = Lane(center_x - 400, lane_center_y, lane_width, 0, i, 'left')
                lane.yellow_boundary = center_y  # Single yellow line
                lane.white_boundary = center_y - road_half_width
                self.lanes.append(lane)
            
            # RIGHT ROAD - vehicles moving LEFT
            for i in range(lanes_per_dir):
                lane_offset = road_half_width - (i + 0.5) * lane_width
                lane_center_y = center_y + lane_offset
                
                lane = Lane(center_x + 400, lane_center_y, lane_width, 180, i, 'right')
                lane.yellow_boundary = center_y  # Single yellow line
                lane.white_boundary = center_y + road_half_width
                self.lanes.append(lane)
            
            # TOP and BOTTOM roads similar setup
            for i in range(lanes_per_dir):
                # TOP ROAD
                lane_offset = -road_half_width + (i + 0.5) * lane_width
                lane_center_x = center_x + lane_offset
                
                lane = Lane(lane_center_x, center_y - 400, lane_width, 90, i, 'top')
                lane.yellow_boundary = center_x
                lane.white_boundary = center_x - road_half_width
                self.lanes.append(lane)
                
                # BOTTOM ROAD
                lane_offset = road_half_width - (i + 0.5) * lane_width
                lane_center_x = center_x + lane_offset
                
                lane = Lane(lane_center_x, center_y + 400, lane_width, 270, i, 'bottom')
                lane.yellow_boundary = center_x
                lane.white_boundary = center_x + road_half_width
                self.lanes.append(lane)
                
        else:  # 1way road
            # All lanes go same direction, no yellow center line restriction
            for i in range(total_lanes):
                lane_offset = -road_half_width + (i + 0.5) * lane_width
                
                # LEFT ROAD (all moving right)
                lane_center_y = center_y + lane_offset
                lane = Lane(center_x - 400, lane_center_y, lane_width, 0, i, 'left')
                lane.yellow_boundary = None  # No center line restriction
                lane.white_boundary = center_y - road_half_width
                self.lanes.append(lane)
    
    def _setup_t_lanes(self, road_config, center_x, center_y, lane_width, total_lanes):
        """Setup lanes for T-junction"""
        road_half_width = (total_lanes * lane_width) // 2
        lanes_per_dir = total_lanes // 2 if road_config['road_type'] != '1way' else total_lanes
        
        # Main horizontal road (left to right)
        for i in range(lanes_per_dir):
            lane_center_y = center_y - road_half_width + (i + 0.5) * lane_width
            lane = Lane(center_x - 400, lane_center_y, lane_width, 0, i, 'left')
            self.lanes.append(lane)
        
        # Main horizontal road (right to left)
        if road_config['road_type'] != '1way':
            for i in range(lanes_per_dir):
                lane_center_y = center_y + road_half_width - (i + 0.5) * lane_width
                lane = Lane(center_x + 400, lane_center_y, lane_width, 180, i, 'right')
                self.lanes.append(lane)
        
        # T-branch
        for i in range(lanes_per_dir):
            # Position lanes based on T angle
            angle_rad = math.radians(road_config['t_angle'])
            base_x = center_x - 400 * math.cos(angle_rad)
            base_y = center_y - 400 * math.sin(angle_rad)
            
            # Calculate perpendicular offset for lane positioning
            perp_x = (i - lanes_per_dir/2 + 0.5) * lane_width * math.sin(angle_rad)
            perp_y = -(i - lanes_per_dir/2 + 0.5) * lane_width * math.cos(angle_rad)
            
            lane = Lane(base_x + perp_x, base_y + perp_y, lane_width, road_config['t_angle'], i, 'branch')
            self.lanes.append(lane)
    
    def get_spawn_lanes(self):
        """Get lanes suitable for spawning (away from intersection)"""
        spawn_lanes = []
        for lane in self.lanes:
            # Only use lanes that are far from intersection
            distance_to_intersection = math.sqrt(
                (lane.center_x - self.intersection_bounds['left'])**2 + 
                (lane.center_y - self.intersection_bounds['top'])**2
            )
            if distance_to_intersection > 200:  # Far enough from intersection
                spawn_lanes.append(lane)
        return spawn_lanes
    
    def get_random_destination(self, _current_lane):
        """Get random destination for vehicle based on current lane"""
        # Simple destination selection - can be made more sophisticated
        destinations = [Direction.STRAIGHT, Direction.LEFT, Direction.RIGHT]
        
        # Less likely to U-turn
        if random.random() < 0.05:
            destinations.append(Direction.U_TURN)
        
        return random.choice(destinations)

# ============================================================================
# SIMPLE VEHICLE FACTORY
# ============================================================================

class VehicleFactory:
    """Simple factory to create the 5 vehicle types"""
    
    VEHICLE_CLASSES = {
        VehicleType.BIKE: Bike,
        VehicleType.CAR: Car,
        VehicleType.AUTO: Auto,
        VehicleType.BUS: Bus,
        VehicleType.TRUCK: Truck,
    }
    
    @classmethod
    def create_vehicle(cls, vehicle_type, x, y, angle, lane, destination):
        """Create specific vehicle type"""
        if vehicle_type not in cls.VEHICLE_CLASSES:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")
        
        vehicle_class = cls.VEHICLE_CLASSES[vehicle_type]
        return vehicle_class(x, y, angle, lane, destination)
    
    @classmethod
    def create_random_vehicle(cls, x, y, angle, lane, destination, distribution=None):
        """Create random vehicle with distribution"""
        if distribution is None:
            # Actual Indian traffic distribution (based on real data)
            distribution = {
                VehicleType.BIKE: 0.747,     # 74.7% bikes (two-wheelers)
                VehicleType.CAR: 0.136,      # 13.6% cars (including jeeps & taxis)
                VehicleType.TRUCK: 0.093,    # 9.3% trucks (goods vehicles)
                VehicleType.AUTO: 0.018,     # 1.8% autos (three-wheelers)
                VehicleType.BUS: 0.006,      # 0.6% buses
            }
        
        # Choose based on weights
        rand = random.random()
        cumulative = 0
        
        for vehicle_type, weight in distribution.items():
            cumulative += weight
            if rand <= cumulative:
                return cls.create_vehicle(vehicle_type, x, y, angle, lane, destination)
        
        # Fallback to bike (most common)
        return cls.create_vehicle(VehicleType.BIKE, x, y, angle, lane, destination)

# ============================================================================
# VEHICLE SPAWNING SYSTEM
# ============================================================================

class VehicleSpawner:
    """Manages spawning and updating vehicles with proper lane management"""
    
    def __init__(self):
        self.vehicles = []
        self.lane_manager = LaneManager()
        self.spawn_interval = 0.8  # Slower spawning to prevent crowding
        self.last_spawn_time = 0
        self.max_vehicles = 100  # Reduced max vehicles for better spacing
        self.spawning_enabled = False
        
        # Traffic distribution
        self.vehicle_distribution = {
            VehicleType.BIKE: 0.747,
            VehicleType.CAR: 0.136,
            VehicleType.TRUCK: 0.093,
            VehicleType.AUTO: 0.018,
            VehicleType.BUS: 0.006,
        }
    
    def set_road_config(self, road_config):
        """Setup lane system based on road configuration"""
        self.lane_manager.setup_lanes(road_config)
    
    def should_spawn_vehicle(self, current_time):
        """Check if we should spawn a new vehicle - Indian traffic style"""
        time_check = current_time - self.last_spawn_time > self.spawn_interval
        vehicle_check = len(self.vehicles) < self.max_vehicles
        lane_check = len(self.lane_manager.lanes) > 0
        spawning_check = self.spawning_enabled
        
        # For Indian traffic, also allow spawning if there's ANY space
        # Don't wait for completely clear areas
        return time_check and vehicle_check and lane_check and spawning_check
    
    def spawn_vehicle(self, current_time, road_config):
        """Spawn a new vehicle in proper lane respecting lane markings with NO OVERLAPPING"""
        spawn_lanes = self.lane_manager.get_spawn_lanes()
        if not spawn_lanes:
            return False
        
        # Try multiple times to find a spawn position
        max_attempts = 5
        for _ in range(max_attempts):
            # Choose random spawn lane
            spawn_lane = random.choice(spawn_lanes)
            
            # Calculate spawn position - keep vehicles in lane center
            spawn_x = spawn_lane.center_x  
            spawn_y = spawn_lane.center_y
            
            # Small variation within lane bounds (±3 pixels max for tighter control)
            if hasattr(spawn_lane, 'lane_bounds'):
                variation = random.uniform(-3, 3)
                if spawn_lane.road_side in ['left', 'right']:
                    spawn_y += variation
                else:
                    spawn_x += variation
            
            # STRICT SPACING CHECK - much larger minimum distance
            min_distance = 80  # Increased from 60 to 80 pixels
            too_close = False
            
            for vehicle in self.vehicles:
                distance = math.sqrt((vehicle.x - spawn_x)**2 + (vehicle.y - spawn_y)**2)
                if distance < min_distance:
                    too_close = True
                    break
            
            # ADDITIONAL CHECK: Make sure no vehicle is in the spawn area ahead
            # Check a wider area in the direction of traffic flow
            angle_rad = math.radians(spawn_lane.direction_angle)
            check_distance = 120  # Check 120 pixels ahead in traffic direction
            
            for check_dist in range(20, check_distance, 20):
                check_x = spawn_x + check_dist * math.cos(angle_rad)
                check_y = spawn_y + check_dist * math.sin(angle_rad)
                
                for vehicle in self.vehicles:
                    vehicle_distance = math.sqrt((vehicle.x - check_x)**2 + (vehicle.y - check_y)**2)
                    if vehicle_distance < 40:  # Vehicle in spawn path
                        too_close = True
                        break
                
                if too_close:
                    break
            
            if not too_close:
                # Get random destination
                destination = self.lane_manager.get_random_destination(spawn_lane)
                
                # Create vehicle
                new_vehicle = VehicleFactory.create_random_vehicle(
                    spawn_x, 
                    spawn_y, 
                    spawn_lane.direction_angle,
                    spawn_lane,
                    destination,
                    self.vehicle_distribution
                )
                
                # FINAL COLLISION CHECK before adding
                collision_detected = False
                for existing_vehicle in self.vehicles:
                    if new_vehicle.check_collision_with_vehicle(existing_vehicle):
                        collision_detected = True
                        break
                
                if not collision_detected:
                    self.vehicles.append(new_vehicle)
                    self.last_spawn_time = current_time
                    return True
        
        # If couldn't spawn after all attempts, still update spawn time to prevent spam
        self.last_spawn_time = current_time
        return False
    
    def update_vehicles(self, dt, current_time, road_config):
        """Update all vehicles with calm, controlled behavior"""
        # Remove off-screen vehicles
        self.vehicles = [v for v in self.vehicles if 
                        -150 <= v.x <= 2070 and -150 <= v.y <= 1230]
        
        # Update each vehicle with calm behavior
        for vehicle in self.vehicles:
            # Update vehicle behavior (includes all speed control and positioning)
            vehicle.update_behavior(self.vehicles, self.lane_manager.intersection_bounds, dt)
        
        # Spawn new vehicles at controlled rate
        if self.should_spawn_vehicle(current_time):
            self.spawn_vehicle(current_time, road_config)
    
    def draw_vehicles(self, screen):
        """Draw all vehicles"""
        for vehicle in self.vehicles:
            vehicle.draw(screen)
    
    def draw_debug_info(self, screen):
        """Draw lane boundaries and debug info"""
        # Draw lane center points
        for lane in self.lane_manager.lanes:
            # Draw lane center line
            pygame.draw.circle(screen, (255, 0, 0), 
                            (int(lane.center_x), int(lane.center_y)), 3)
            
            # Draw lane boundaries
            pygame.draw.line(screen, (255, 0, 0), lane.left_bound, lane.right_bound, 1)
        
        # Draw intersection bounds
        bounds = self.lane_manager.intersection_bounds
        pygame.draw.rect(screen, (255, 0, 0), 
                        (bounds['left'], bounds['top'], 
                        bounds['right'] - bounds['left'], 
                        bounds['bottom'] - bounds['top']), 2)
        
        # Draw vehicle debug info
        for vehicle in self.vehicles:
            # Draw collision detection radius
            collision_radius = max(vehicle.length, vehicle.width) / 2
            pygame.draw.circle(screen, (255, 255, 0), 
                            (int(vehicle.x), int(vehicle.y)), 
                            int(collision_radius), 1)
            
            # Draw original lane direction (should never change)
            original_angle_rad = math.radians(vehicle.original_angle)
            orig_end_x = vehicle.x + 40 * math.cos(original_angle_rad)
            orig_end_y = vehicle.y + 40 * math.sin(original_angle_rad)
            pygame.draw.line(screen, (0, 0, 255), 
                        (int(vehicle.x), int(vehicle.y)), 
                        (int(orig_end_x), int(orig_end_y)), 3)
            
            # Draw current direction (should be very close to original)
            current_angle_rad = math.radians(vehicle.angle)
            curr_end_x = vehicle.x + 35 * math.cos(current_angle_rad)
            curr_end_y = vehicle.y + 35 * math.sin(current_angle_rad)
            pygame.draw.line(screen, (0, 255, 0), 
                        (int(vehicle.x), int(vehicle.y)), 
                        (int(curr_end_x), int(curr_end_y)), 2)
            
            # Draw collision detection zone ahead
            for distance in range(10, 41, 10):
                front_x = vehicle.x + distance * math.cos(original_angle_rad)
                front_y = vehicle.y + distance * math.sin(original_angle_rad)
                pygame.draw.circle(screen, (255, 100, 100), 
                                (int(front_x), int(front_y)), 4, 1)
    
    def clear_vehicles(self):
        """Remove all vehicles"""
        self.vehicles = []
    
    def get_vehicle_count(self):
        """Get current number of vehicles"""
        return len(self.vehicles)
    
    def set_spawn_rate(self, interval):
        """Set spawn interval in seconds"""
        self.spawn_interval = max(0.1, interval)
    
    def set_max_vehicles(self, max_count):
        """Set maximum number of vehicles"""
        self.max_vehicles = max(1, max_count)
    
    def enable_spawning(self):
        """Enable vehicle spawning"""
        self.spawning_enabled = True
    
    def disable_spawning(self):
        """Disable vehicle spawning"""
        self.spawning_enabled = False
    
    def is_spawning_enabled(self):
        """Check if spawning is enabled"""
        return self.spawning_enabled

# ============================================================================
# LIBRARY INTERFACE - These functions can be used by other modules
# ============================================================================

# Global spawner instance
global_spawner = VehicleSpawner()

def create_vehicle_spawner():
    """Create a new VehicleSpawner instance"""
    return VehicleSpawner()

def get_global_spawner():
    """Get the global spawner instance"""
    return global_spawner

def create_vehicle(vehicle_type, x, y, angle, lane_id):
    """Create a single vehicle of specific type"""
    return VehicleFactory.create_vehicle(vehicle_type, x, y, angle, lane_id)

def create_random_vehicle(x, y, angle, lane_id, distribution=None):
    """Create a random vehicle"""
    return VehicleFactory.create_random_vehicle(x, y, angle, lane_id, distribution)

def get_vehicle_types():
    """Get all available vehicle types"""
    return list(VehicleType)

def get_indian_distribution():
    """Get the standard Indian traffic distribution"""
    return {
        VehicleType.BIKE: 0.747,
        VehicleType.CAR: 0.136,
        VehicleType.TRUCK: 0.093,
        VehicleType.AUTO: 0.018,
        VehicleType.BUS: 0.006,
    }

def setup_spawning(road_config, spawn_rate=2.0, max_vehicles=50):
    """Setup vehicle spawning with road configuration"""
    global_spawner.set_road_config(road_config)
    global_spawner.set_spawn_rate(spawn_rate)
    global_spawner.set_max_vehicles(max_vehicles)
    return global_spawner

def start_spawning():
    """Start vehicle spawning"""
    global_spawner.enable_spawning()

def stop_spawning():
    """Stop vehicle spawning"""
    global_spawner.disable_spawning()

def update_vehicles(dt, current_time):
    """Update all vehicles in global spawner"""
    global_spawner.update_vehicles(dt, current_time)

def draw_vehicles(screen):
    """Draw all vehicles from global spawner"""
    global_spawner.draw_vehicles(screen)

def clear_all_vehicles():
    """Clear all vehicles from global spawner"""
    global_spawner.clear_vehicles()

def get_vehicle_count():
    """Get current vehicle count from global spawner"""
    return global_spawner.get_vehicle_count()

def is_spawning_active():
    """Check if spawning is currently active"""
    return global_spawner.is_spawning_enabled()

# ============================================================================
# TEST FUNCTION
# ============================================================================

def main():
    """Test the vehicle system"""
    import pygame
    import time
    
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    pygame.display.set_caption("Vehicle System Test")
    clock = pygame.time.Clock()
    
    # Setup test road config
    test_road_config = {
        'junction_type': 'cross',
        'road_type': '2way',
        'lane_count': 2,
        'top_angle': 270,
        'bottom_angle': 90
    }
    
    # Setup spawning
    setup_spawning(test_road_config, spawn_rate=1.0, max_vehicles=30)
    start_spawning()
    
    print("Vehicle System Test")
    print("Controls:")
    print("- SPACE: Toggle spawning")
    print("- C: Clear all vehicles")
    print("- ESC: Exit")
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        current_time = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if is_spawning_active():
                        stop_spawning()
                        print("Spawning stopped")
                    else:
                        start_spawning()
                        print("Spawning started")
                elif event.key == pygame.K_c:
                    clear_all_vehicles()
                    print("All vehicles cleared")
        
        # Clear screen
        screen.fill((40, 40, 40))
        
        # Draw simple roads
        pygame.draw.rect(screen, (100, 100, 100), (0, 500, 1920, 80))  # Horizontal
        pygame.draw.rect(screen, (100, 100, 100), (920, 0, 80, 1080))  # Vertical
        
        # Update and draw vehicles
        update_vehicles(dt, current_time)
        draw_vehicles(screen)
        
        # Draw info
        font = pygame.font.Font(None, 36)
        info_text = f"Vehicles: {get_vehicle_count()} | Spawning: {'ON' if is_spawning_active() else 'OFF'}"
        text_surface = font.render(info_text, True, (255, 255, 255))
        screen.blit(text_surface, (50, 50))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
