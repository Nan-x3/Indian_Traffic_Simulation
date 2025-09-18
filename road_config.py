# road_config.py

import pygame
import tkinter as tk
from tkinter import ttk
import threading
import math

# ============================================================================
# CLASS DEFINITIONS (Must be defined before they are used)
# ============================================================================

class ConfigPanel:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Traffic Simulation Config")
        self.window.geometry("400x800")
        self.window.attributes("-topmost", True)
        
        self.setup_junction_controls()
        self.setup_angle_controls()
        self.setup_lane_controls()
        self.setup_traffic_light_controls()
        self.setup_event_bindings()
        
        self.apply_btn = ttk.Button(self.window, text="Apply Configuration", command=self.apply_config)
        self.apply_btn.pack(pady=20)
        self.config_frame = ttk.LabelFrame(self.window, text="Current Config", padding=10)
        self.config_frame.pack(fill="x", padx=10, pady=5)
        self.config_display = ttk.Label(self.config_frame, text="Default", wraplength=380)
        self.config_display.pack(anchor="w")
        self.apply_config() # Apply default config on startup

    def run(self):
        self.window.mainloop()
    
    def create_angle_control(self, parent, label, var_name, default_value, min_val=0, max_val=360):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=2)
        ttk.Label(frame, text=f"{label}:").pack(side="left", padx=(0, 5))
        var = tk.IntVar(value=default_value)
        setattr(self, var_name, var)
        scale = ttk.Scale(frame, from_=min_val, to=max_val, variable=var, orient="horizontal")
        scale.pack(side="left", fill="x", expand=True, padx=(0, 5))
        setattr(self, f"{var_name}_scale", scale)
        entry = ttk.Entry(frame, textvariable=var, width=5)
        entry.pack(side="right")
        setattr(self, f"{var_name}_entry", entry)
        ttk.Label(frame, text="°").pack(side="right")
        return var, scale, entry
    
    def setup_junction_controls(self):
        self.junction_frame = ttk.LabelFrame(self.window, text="Junction Type", padding=10)
        self.junction_frame.pack(fill="x", padx=10, pady=5)
        self.junction_type = tk.StringVar(value="cross")
        ttk.Radiobutton(self.junction_frame, text="+ Junction (Cross)", variable=self.junction_type, value="cross").pack(anchor="w")
        ttk.Radiobutton(self.junction_frame, text="T Junction", variable=self.junction_type, value="t").pack(anchor="w")
    
    def setup_angle_controls(self):
        self.angle_frame = ttk.LabelFrame(self.window, text="Angle Settings", padding=10)
        self.angle_frame.pack(fill="x", padx=10, pady=5)
        t_frame = ttk.Frame(self.angle_frame)
        t_frame.pack(fill="x", pady=5)
        ttk.Label(t_frame, text="T-Junction Offshoot Angle:").pack(anchor="w")
        self.create_angle_control(t_frame, "", "t_angle", 90, 30, 150)
        cross_frame = ttk.Frame(self.angle_frame)
        cross_frame.pack(fill="x", pady=5)
        ttk.Label(cross_frame, text="Cross Junction - Individual Road Angles:").pack(anchor="w")
        self.create_angle_control(cross_frame, "Top Road", "top_angle", 90)
        self.create_angle_control(cross_frame, "Right Road", "right_angle", 0)
        self.create_angle_control(cross_frame, "Bottom Road", "bottom_angle", 270)
    
    def setup_lane_controls(self):
        self.lane_frame = ttk.LabelFrame(self.window, text="Lane Configuration", padding=10)
        self.lane_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(self.lane_frame, text="Road Type:").pack(anchor="w")
        self.road_type = tk.StringVar(value="2way_with_divider")
        ttk.Radiobutton(self.lane_frame, text="1 Way (One Direction)", variable=self.road_type, value="1way").pack(anchor="w")
        ttk.Radiobutton(self.lane_frame, text="2 Way with Divider", variable=self.road_type, value="2way_with_divider").pack(anchor="w")
        ttk.Radiobutton(self.lane_frame, text="2 Way without Divider", variable=self.road_type, value="2way_without_divider").pack(anchor="w")
        ttk.Label(self.lane_frame, text="Total Lane Count:").pack(anchor="w", pady=(10,0))
        self.lane_count = tk.IntVar(value=2)
        self.lane_spinbox = ttk.Spinbox(self.lane_frame, from_=1, to=8, textvariable=self.lane_count, width=10)
        self.lane_spinbox.pack(anchor="w", pady=2)
        self.lane_info = ttk.Label(self.lane_frame, text="2 lanes: 1 each direction")
        self.lane_info.pack(anchor="w", pady=5)
    
    def setup_traffic_light_controls(self):
        self.traffic_frame = ttk.LabelFrame(self.window, text="Traffic Light System", padding=10)
        self.traffic_frame.pack(fill="x", padx=10, pady=5)
        self.traffic_light_mode = tk.StringVar(value="timer")
        ttk.Radiobutton(self.traffic_frame, text="Timer-Based (15s Cycle)", variable=self.traffic_light_mode, value="timer").pack(anchor="w")
        ttk.Radiobutton(self.traffic_frame, text="Smart Monitor (Not Implemented)", variable=self.traffic_light_mode, value="smart", state="disabled").pack(anchor="w")

    def setup_event_bindings(self):
        self.t_angle.trace_add("write", self.update_display)
        self.top_angle.trace_add("write", self.update_display)
        self.right_angle.trace_add("write", self.update_display)
        self.bottom_angle.trace_add("write", self.update_display)
        self.lane_count.trace_add("write", self.update_lane_info)
        self.road_type.trace_add("write", self.update_lane_info)
        self.junction_type.trace_add("write", self.update_display)
        self.traffic_light_mode.trace_add("write", self.update_display)
        
        self.t_angle_entry.bind('<Return>', self.validate_t_angle)
        self.top_angle_entry.bind('<Return>', lambda e: self.validate_angle(e, self.top_angle))
        self.right_angle_entry.bind('<Return>', lambda e: self.validate_angle(e, self.right_angle))
        self.bottom_angle_entry.bind('<Return>', lambda e: self.validate_angle(e, self.bottom_angle))
        
    def validate_t_angle(self, event=None):
        self.validate_angle_range(self.t_angle, 30, 150)
    
    def validate_angle(self, var, min_val=0, max_val=360):
        try:
            val = var.get()
            if not (min_val <= val <= max_val):
                var.set(max(min_val, min(max_val, val)))
        except tk.TclError:
            var.set(min_val)
    
    def update_display(self, *args):
        self.apply_config()
        
    def update_lane_info(self, *args):
        try:
            count = self.lane_count.get()
        except tk.TclError:
            count = 2
        road_type = self.road_type.get()
        info = ""
        if road_type == "1way": info = f"{count} lanes: all same direction"
        elif road_type == "2way_with_divider":
            info = f"{count} lanes: {count//2} each way (divider)" if count > 1 else "1 lane: not valid"
        else:
            info = f"{count} lanes: ~{count//2} each way (no divider)"
        self.lane_info.config(text=info)
        
    def apply_config(self):
        global current_config, road_renderer
        
        def safe_get(var, default):
            try: return var.get()
            except tk.TclError: return default

        config = {
            'junction_type': self.junction_type.get(),
            't_angle': safe_get(self.t_angle, 90),
            'top_angle': safe_get(self.top_angle, 90),
            'right_angle': safe_get(self.right_angle, 0),
            'bottom_angle': safe_get(self.bottom_angle, 270),
            'road_type': self.road_type.get(),
            'lane_count': safe_get(self.lane_count, 2),
            'traffic_light_mode': self.traffic_light_mode.get()
        }
        
        current_config.update(config)
        road_renderer.update_config(config)
        
        if config['junction_type'] == 'cross':
            angle_info = f"T:{config['top_angle']} R:{config['right_angle']} B:{config['bottom_angle']}"
        else:
            angle_info = f"{config['t_angle']}°"
        road_type_names = {'1way': '1-way', '2way_with_divider': '2-way divided', '2way_without_divider': '2-way undivided'}
        lane_info = f"{config['lane_count']}-lane {road_type_names[config['road_type']]}"
        traffic_info = f"Lights: {config['traffic_light_mode'].title()}"
        display_text = f"{config['junction_type'].title()}, {angle_info}\n{lane_info}\n{traffic_info}"
        self.config_display.config(text=display_text)

class RoadRenderer:
    def __init__(self, config=None):
        self.config = config or RoadRenderer.get_default_config()
        
    @staticmethod
    def get_default_config():
        return {
            'junction_type': 'cross', 't_angle': 90, 'top_angle': 90,
            'right_angle': 0, 'bottom_angle': 270, 'road_type': '2way_with_divider',
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
        road_width, half_width = dims['road_width'], dims['road_half_width']
        
        if self.config['junction_type'] == 'cross':
            pygame.draw.rect(screen, (100, 100, 100), (0, center_y - half_width, center_x, road_width))
            angles = {'top': self.config['top_angle'], 'right': self.config['right_angle'], 'bottom': self.config['bottom_angle']}
            for name, angle in angles.items():
                draw_angled_road(screen, center_x, center_y, angle, half_width, 1000)
        else:
            pygame.draw.rect(screen, (100, 100, 100), (0, center_y - half_width, 1920, road_width))
            draw_angled_road(screen, center_x, center_y, self.config['t_angle'], half_width, 1000)
    
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
        draw_horizontal_road_markings(screen, cx, cy, road_w, total_l, l_per_dir, lane_w, road_type)
        angles = {'top': config['top_angle'], 'right': config['right_angle'], 'bottom': config['bottom_angle']}
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
        if road_type == '2way_with_divider':
            draw_center_divider(screen, (cx, cy), (cx+length*dx, cy+dy*length))
            for offset in [-6, 6]:
                draw_solid_line(screen, (cx+offset*px, cy+offset*py), (cx+offset*px+length*dx, cy+offset*py+length*dy), 3, (255,255,0))
        else:
            draw_solid_line(screen, (cx,cy), (cx+length*dx, cy+length*dy), 3, (255,255,0))

    for i in range(1, total_l):
        if '2way' in road_type and i == l_per_dir: continue
        offset = i * lane_w - half_w
        draw_dashed_line(screen, (cx+offset*px, cy+offset*py), (cx+offset*px+length*dx, cy+offset*py+length*dy))

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
    if threaded:
        thread = threading.Thread(target=lambda: ConfigPanel().run(), daemon=True)
        thread.start()
        return thread
    else:
        ConfigPanel().run()

def get_current_config():
    return current_config.copy()

def update_global_config(new_config):
    global current_config, road_renderer
    current_config.update(new_config)
    road_renderer.update_config(new_config)
