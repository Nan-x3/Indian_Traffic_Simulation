"""
Road Configuration Module for Indian Traffic Simulation

This module handles the road setup and configuration for Indian traffic patterns.
It provides flexible configuration options for different road types and layouts.
"""

import pygame
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class RoadType(Enum):
    """Types of roads commonly found in Indian traffic systems"""
    HIGHWAY = "highway"
    CITY_MAIN = "city_main"
    CITY_SIDE = "city_side"
    RURAL = "rural"
    EXPRESSWAY = "expressway"

class LaneDirection(Enum):
    """Lane direction definitions"""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

@dataclass
class LaneConfig:
    """Configuration for individual lanes"""
    direction: LaneDirection
    width: int
    speed_limit: int  # km/h
    position: Tuple[int, int]
    length: int

@dataclass
class RoadSegment:
    """Configuration for road segments"""
    start_pos: Tuple[int, int]
    end_pos: Tuple[int, int]
    lanes: List[LaneConfig]
    road_type: RoadType
    has_divider: bool = True
    has_traffic_light: bool = False
    traffic_light_pos: Tuple[int, int] = None

class RoadConfig:
    """Main road configuration class for Indian traffic simulation"""
    
    def __init__(self, screen_width: int = 1200, screen_height: int = 800):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.road_segments: List[RoadSegment] = []
        self.intersections: List[Tuple[int, int]] = []
        
        # Colors for different road elements
        self.colors = {
            'road': (60, 60, 60),
            'lane_marker': (255, 255, 255),
            'divider': (255, 255, 0),
            'traffic_light': (255, 0, 0),
            'intersection': (80, 80, 80)
        }
        
        # Lane configurations for different road types
        self.lane_configs = {
            RoadType.HIGHWAY: {
                'lane_width': 80,
                'lanes_per_direction': 3,
                'speed_limit': 100,
                'has_divider': True
            },
            RoadType.CITY_MAIN: {
                'lane_width': 60,
                'lanes_per_direction': 2,
                'speed_limit': 60,
                'has_divider': True
            },
            RoadType.CITY_SIDE: {
                'lane_width': 50,
                'lanes_per_direction': 1,
                'speed_limit': 40,
                'has_divider': False
            },
            RoadType.RURAL: {
                'lane_width': 70,
                'lanes_per_direction': 1,
                'speed_limit': 50,
                'has_divider': False
            },
            RoadType.EXPRESSWAY: {
                'lane_width': 90,
                'lanes_per_direction': 4,
                'speed_limit': 120,
                'has_divider': True
            }
        }
    
    def create_default_indian_road_layout(self):
        """Create a default road layout representing typical Indian traffic scenarios"""
        # Main horizontal road (city main road)
        main_road = self._create_horizontal_road(
            y_center=self.screen_height // 2,
            road_type=RoadType.CITY_MAIN,
            length=self.screen_width
        )
        self.road_segments.append(main_road)
        
        # Vertical intersection road
        intersection_road = self._create_vertical_road(
            x_center=self.screen_width // 2,
            road_type=RoadType.CITY_SIDE,
            length=self.screen_height
        )
        self.road_segments.append(intersection_road)
        
        # Add intersection point
        self.intersections.append((self.screen_width // 2, self.screen_height // 2))
        
        # Add traffic light at intersection
        main_road.has_traffic_light = True
        main_road.traffic_light_pos = (self.screen_width // 2, self.screen_height // 2)
    
    def _create_horizontal_road(self, y_center: int, road_type: RoadType, length: int) -> RoadSegment:
        """Create a horizontal road segment"""
        config = self.lane_configs[road_type]
        lanes = []
        
        # Create lanes for each direction
        lane_width = config['lane_width']
        lanes_per_direction = config['lanes_per_direction']
        total_width = lane_width * lanes_per_direction * 2
        
        # Northbound lanes (going right)
        for i in range(lanes_per_direction):
            lane_y = y_center - (total_width // 2) + (i * lane_width) + (lane_width // 2)
            lane = LaneConfig(
                direction=LaneDirection.EAST,
                width=lane_width,
                speed_limit=config['speed_limit'],
                position=(0, lane_y),
                length=length
            )
            lanes.append(lane)
        
        # Southbound lanes (going left)
        for i in range(lanes_per_direction):
            lane_y = y_center + (i * lane_width) + (lane_width // 2)
            lane = LaneConfig(
                direction=LaneDirection.WEST,
                width=lane_width,
                speed_limit=config['speed_limit'],
                position=(length, lane_y),
                length=length
            )
            lanes.append(lane)
        
        return RoadSegment(
            start_pos=(0, y_center - total_width // 2),
            end_pos=(length, y_center + total_width // 2),
            lanes=lanes,
            road_type=road_type,
            has_divider=config['has_divider']
        )
    
    def _create_vertical_road(self, x_center: int, road_type: RoadType, length: int) -> RoadSegment:
        """Create a vertical road segment"""
        config = self.lane_configs[road_type]
        lanes = []
        
        lane_width = config['lane_width']
        lanes_per_direction = config['lanes_per_direction']
        total_width = lane_width * lanes_per_direction * 2
        
        # Eastbound lanes (going down)
        for i in range(lanes_per_direction):
            lane_x = x_center - (total_width // 2) + (i * lane_width) + (lane_width // 2)
            lane = LaneConfig(
                direction=LaneDirection.SOUTH,
                width=lane_width,
                speed_limit=config['speed_limit'],
                position=(lane_x, 0),
                length=length
            )
            lanes.append(lane)
        
        # Westbound lanes (going up)
        for i in range(lanes_per_direction):
            lane_x = x_center + (i * lane_width) + (lane_width // 2)
            lane = LaneConfig(
                direction=LaneDirection.NORTH,
                width=lane_width,
                speed_limit=config['speed_limit'],
                position=(lane_x, length),
                length=length
            )
            lanes.append(lane)
        
        return RoadSegment(
            start_pos=(x_center - total_width // 2, 0),
            end_pos=(x_center + total_width // 2, length),
            lanes=lanes,
            road_type=road_type,
            has_divider=config['has_divider']
        )
    
    def add_custom_road_segment(self, segment: RoadSegment):
        """Add a custom road segment to the configuration"""
        self.road_segments.append(segment)
    
    def add_intersection(self, position: Tuple[int, int]):
        """Add an intersection at the specified position"""
        self.intersections.append(position)
    
    def get_lane_by_direction(self, direction: LaneDirection) -> List[LaneConfig]:
        """Get all lanes with a specific direction"""
        lanes = []
        for segment in self.road_segments:
            for lane in segment.lanes:
                if lane.direction == direction:
                    lanes.append(lane)
        return lanes
    
    def draw_roads(self, screen: pygame.Surface):
        """Draw all road segments on the screen"""
        for segment in self.road_segments:
            self._draw_road_segment(screen, segment)
        
        # Draw intersections
        for intersection in self.intersections:
            pygame.draw.circle(screen, self.colors['intersection'], intersection, 20)
    
    def _draw_road_segment(self, screen: pygame.Surface, segment: RoadSegment):
        """Draw a single road segment"""
        # Draw road base
        road_rect = pygame.Rect(
            segment.start_pos[0],
            segment.start_pos[1],
            segment.end_pos[0] - segment.start_pos[0],
            segment.end_pos[1] - segment.start_pos[1]
        )
        pygame.draw.rect(screen, self.colors['road'], road_rect)
        
        # Draw lane markers
        for lane in segment.lanes:
            self._draw_lane_markers(screen, lane)
        
        # Draw divider if present
        if segment.has_divider:
            self._draw_divider(screen, segment)
        
        # Draw traffic light if present
        if segment.has_traffic_light and segment.traffic_light_pos:
            pygame.draw.circle(screen, self.colors['traffic_light'], segment.traffic_light_pos, 15)
    
    def _draw_lane_markers(self, screen: pygame.Surface, lane: LaneConfig):
        """Draw lane markers for a specific lane"""
        if lane.direction in [LaneDirection.EAST, LaneDirection.WEST]:
            # Horizontal lane markers
            start_x = lane.position[0] if lane.direction == LaneDirection.EAST else 0
            end_x = lane.length if lane.direction == LaneDirection.EAST else lane.position[0]
            y = lane.position[1]
            
            # Draw dashed line
            dash_length = 20
            gap_length = 15
            current_x = start_x
            
            while current_x < end_x:
                dash_end = min(current_x + dash_length, end_x)
                pygame.draw.line(screen, self.colors['lane_marker'], 
                               (current_x, y), (dash_end, y), 2)
                current_x += dash_length + gap_length
        
        else:  # Vertical lanes
            # Vertical lane markers
            start_y = lane.position[1] if lane.direction == LaneDirection.SOUTH else 0
            end_y = lane.length if lane.direction == LaneDirection.SOUTH else lane.position[1]
            x = lane.position[0]
            
            # Draw dashed line
            dash_length = 20
            gap_length = 15
            current_y = start_y
            
            while current_y < end_y:
                dash_end = min(current_y + dash_length, end_y)
                pygame.draw.line(screen, self.colors['lane_marker'], 
                               (x, current_y), (x, dash_end), 2)
                current_y += dash_length + gap_length
    
    def _draw_divider(self, screen: pygame.Surface, segment: RoadSegment):
        """Draw road divider"""
        center_x = (segment.start_pos[0] + segment.end_pos[0]) // 2
        center_y = (segment.start_pos[1] + segment.end_pos[1]) // 2
        
        # Draw solid yellow line as divider
        if segment.start_pos[0] == segment.end_pos[0]:  # Vertical road
            pygame.draw.line(screen, self.colors['divider'],
                           (center_x, segment.start_pos[1]),
                           (center_x, segment.end_pos[1]), 3)
        else:  # Horizontal road
            pygame.draw.line(screen, self.colors['divider'],
                           (segment.start_pos[0], center_y),
                           (segment.end_pos[0], center_y), 3)
    
    def get_spawn_points(self) -> List[Tuple[int, int, LaneDirection]]:
        """Get all valid spawn points for vehicles"""
        spawn_points = []
        
        for segment in self.road_segments:
            for lane in segment.lanes:
                if lane.direction == LaneDirection.EAST:
                    spawn_points.append((0, lane.position[1], lane.direction))
                elif lane.direction == LaneDirection.WEST:
                    spawn_points.append((self.screen_width, lane.position[1], lane.direction))
                elif lane.direction == LaneDirection.SOUTH:
                    spawn_points.append((lane.position[0], 0, lane.direction))
                elif lane.direction == LaneDirection.NORTH:
                    spawn_points.append((lane.position[0], self.screen_height, lane.direction))
        
        return spawn_points