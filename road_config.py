# road_config.py

import pygame
import math
from config_gui import start_config_gui as start_gui

# ============================================================================
# ROAD RENDERER CLASS
# ============================================================================

class RoadRenderer:
    def __init__(self, config=None):
        self.config = config or RoadRenderer.get_default_config()
        
    @staticmethod
    def get_default_config():
        return {
            'junction_type': 'cross', 't_angle': 90, 'top_angle': 270,
            'right_angle': 0, 'bottom_angle': 90, 'road_type': '2way_with_divider',
            'lane_count': 2, 'traffic_light_mode': 'timer'
        }
    
    def update_config(self, new_config):
        self.config.update(new_config)
    
    def get_road_dimensions(self):
        lane_width = 40
        total_lanes = self.config['lane_count']
        road_width = total_lanes * lane_width
        lanes_per_dir = total_lanes // 2 if '2way' in self.config['road_type'] else total_lanes
        return {'lane_width': lane_width, 'total_lanes': total_lanes, 'road_width': road_width,
                'lanes_per_direction': lanes_per_dir, 'road_half_width': road_width // 2}
    
    def draw_roads(self, screen, center_x=960, center_y=540):
        dims = self.get_road_dimensions()
        half_width = dims['road_half_width']
        if self.config['junction_type'] == 'cross':
            angles = {
                'top': self.config['top_angle'], 
                'right': self.config['right_angle'],
                'bottom': self.config['bottom_angle'], 
                'left': 180  # Fixed at 180° - independent of right road
            }
            for name, angle in angles.items():
                draw_angled_road(screen, center_x, center_y, angle, half_width, 1200)
        else:
            pygame.draw.rect(screen, (100, 100, 100), (0, center_y - half_width, 1920, dims['road_width']))
            draw_angled_road(screen, center_x, center_y, self.config['t_angle'], half_width, 1200)
    
    def draw_lane_markings(self, screen, center_x=960, center_y=540):
        dims = self.get_road_dimensions()
        draw_lane_markings(screen, self.config, center_x, center_y, dims)
    
    def draw_intersection(self, screen, center_x=960, center_y=540):
        if self.config['junction_type'] == 'cross':
            dims = self.get_road_dimensions()
            size = dims['road_width'] + 5
            pygame.draw.rect(screen, (120, 120, 120), (center_x - size/2, center_y - size/2, size, size))
    
    def draw_complete_road_system(self, screen, center_x=960, center_y=540):
        self.draw_roads(screen, center_x, center_y)
        self.draw_lane_markings(screen, center_x, center_y)
        self.draw_intersection(screen, center_x, center_y)

# ============================================================================
# GLOBAL INSTANCES AND HELPER FUNCTIONS
# ============================================================================

current_config = RoadRenderer.get_default_config()
road_renderer = RoadRenderer(current_config)

def draw_angled_road(screen, cx, cy, angle, half_width, length, color=(100, 100, 100)):
    rad = math.radians(angle)
    dx, dy = length * math.cos(rad), length * math.sin(rad)
    px, py = half_width * math.sin(rad), -half_width * math.cos(rad)
    points = [(cx - px, cy - py), (cx + px, cy + py), (cx + px + dx, cy + py + dy), (cx - px + dx, cy - py + dy)]
    pygame.draw.polygon(screen, color, points)

def draw_solid_line(screen, start, end, width=3, color=(255, 255, 255)):
    pygame.draw.line(screen, color, start, end, width)

def draw_dashed_line(screen, start, end, dash=20, gap=30, width=3, color=(255, 255, 255)):
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    if not length: return
    ux, uy = dx / length, dy / length
    pos = 0
    while pos < length:
        start_p = (start[0] + pos * ux, start[1] + pos * uy)
        end_p_len = min(pos + dash, length)
        end_p = (start[0] + end_p_len * ux, start[1] + end_p_len * uy)
        pygame.draw.line(screen, color, start_p, end_p, width)
        pos += dash + gap

def draw_center_divider(screen, start, end, width=12, color=(80, 80, 80)):
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    if not length: return
    px, py = -dy / length * (width / 2), dx / length * (width / 2)
    points = [(start[0]-px, start[1]-py), (start[0]+px, start[1]+py), (end[0]+px, end[1]+py), (end[0]-px, end[1]-py)]
    pygame.draw.polygon(screen, color, points)

def draw_lane_markings(screen, config, cx, cy, dims):
    road_type = config['road_type']
    road_w, total_l, l_per_dir, lane_w = dims['road_width'], dims['total_lanes'], dims['lanes_per_direction'], dims['lane_width']
    
    if config['junction_type'] == 'cross':
        angles = {'top': config['top_angle'], 'right': config['right_angle'],
                  'bottom': config['bottom_angle'], 'left': 180}
        for name, angle in angles.items():
            draw_angled_road_markings(screen, cx, cy, angle, road_w, total_l, l_per_dir, lane_w, road_type)
    else:
        draw_horizontal_road_markings(screen, cx, cy, road_w, total_l, l_per_dir, lane_w, road_type)
        draw_angled_road_markings(screen, cx, cy, config['t_angle'], road_w, total_l, l_per_dir, lane_w, road_type)

def draw_angled_road_markings(screen, cx, cy, angle, road_w, total_l, l_per_dir, lane_w, road_type):
    rad, half_w = math.radians(angle), road_w / 2
    dx, dy, px, py = math.cos(rad), math.sin(rad), math.sin(rad), -math.cos(rad)
    length = 1200
    
    draw_solid_line(screen, (cx - half_w*px, cy - half_w*py), (cx - half_w*px + length*dx, cy - half_w*py + length*dy))
    draw_solid_line(screen, (cx + half_w*px, cy + half_w*py), (cx + half_w*px + length*dx, cy + half_w*py + length*dy))

    if '2way' in road_type:
        center_start = (cx, cy)
        center_end = (cx + length*dx, cy + length*dy)
        if road_type == '2way_with_divider':
            draw_center_divider(screen, center_start, center_end)
            for offset in [-6, 6]:
                start_p = (cx + offset*px, cy + offset*py)
                end_p = (start_p[0] + length*dx, start_p[1] + length*dy)
                draw_solid_line(screen, start_p, end_p, 3, (255,255,0))
        else:
            draw_solid_line(screen, center_start, center_end, 3, (255,255,0))

    for i in range(1, total_l):
        if '2way' in road_type and i == l_per_dir: continue
        offset = i * lane_w - half_w
        start_p = (cx + offset*px, cy + offset*py)
        end_p = (start_p[0] + length*dx, start_p[1] + length*dy)
        draw_dashed_line(screen, start_p, end_p)

def draw_horizontal_road_markings(screen, cx, cy, road_w, total_l, l_per_dir, lane_w, road_type):
    half_w = road_w / 2
    draw_solid_line(screen, (0, cy - half_w), (1920, cy - half_w))
    draw_solid_line(screen, (0, cy + half_w), (1920, cy + half_w))
    if '2way' in road_type:
        if road_type == '2way_with_divider':
            draw_center_divider(screen, (0, cy), (1920, cy))
            draw_solid_line(screen, (0, cy-6), (1920, cy-6), 3, (255,255,0))
            draw_solid_line(screen, (0, cy+6), (1920, cy+6), 3, (255,255,0))
        else:
            draw_solid_line(screen, (0, cy), (1920, cy), 3, (255,255,0))
    for i in range(1, total_l):
        if '2way' in road_type and i == l_per_dir: continue
        y = cy - half_w + i * lane_w
        draw_dashed_line(screen, (0, y), (1920, y))

# ============================================================================
# LIBRARY INTERFACE
# ============================================================================

def create_road_renderer(config=None):
    return road_renderer

def get_default_road_config():
    return RoadRenderer.get_default_config()

def start_config_gui(threaded=True):
    """Start the configuration GUI using the separate config_gui module"""
    return start_gui(update_global_config, threaded)

def get_current_config():
    return current_config.copy()

def update_global_config(new_config):
    global current_config, road_renderer
    current_config.update(new_config)
    road_renderer.update_config(new_config)
