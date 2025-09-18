import pygame
import tkinter as tk
from tkinter import ttk
import threading
import math

class ConfigPanel:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Traffic Simulation Config")
        self.window.geometry("400x800")
        self.window.attributes("-topmost", True)
        
        self.setup_junction_controls()
        self.setup_angle_controls()
        self.setup_lane_controls()
        self.setup_event_bindings()
    
    def run(self):
        """Start the GUI main loop"""
        self.window.mainloop()
    
    def create_angle_control(self, parent, label, var_name, default_value, min_val=0, max_val=360):
        """Helper function to create angle slider + entry controls"""
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=2)
        ttk.Label(frame, text=f"{label}:").pack(side="left", padx=(0, 5))
        
        # Create the variable and store it as an attribute
        var = tk.IntVar(value=default_value)
        setattr(self, var_name, var)
        
        # Create slider
        scale = ttk.Scale(frame, from_=min_val, to=max_val, variable=var, orient="horizontal")
        scale.pack(side="left", fill="x", expand=True, padx=(0, 5))
        setattr(self, f"{var_name}_scale", scale)
        
        # Create entry
        entry = ttk.Entry(frame, textvariable=var, width=5)
        entry.pack(side="right")
        setattr(self, f"{var_name}_entry", entry)
        
        ttk.Label(frame, text="°").pack(side="right")
        
        return var, scale, entry
    
    def setup_junction_controls(self):
        """Setup junction type selection"""
        self.junction_frame = ttk.LabelFrame(self.window, text="Junction Type", padding=10)
        self.junction_frame.pack(fill="x", padx=10, pady=5)
        
        self.junction_type = tk.StringVar(value="cross")
        ttk.Radiobutton(self.junction_frame, text="+ Junction (Cross)", 
                       variable=self.junction_type, value="cross").pack(anchor="w")
        ttk.Radiobutton(self.junction_frame, text="T Junction", 
                       variable=self.junction_type, value="t").pack(anchor="w")
    
    def setup_angle_controls(self):
        """Setup all angle controls using helper function"""
        self.angle_frame = ttk.LabelFrame(self.window, text="Angle Settings", padding=10)
        self.angle_frame.pack(fill="x", padx=10, pady=5)
        
        # T-Junction control
        t_frame = ttk.Frame(self.angle_frame)
        t_frame.pack(fill="x", pady=5)
        ttk.Label(t_frame, text="T-Junction Offshoot Angle:").pack(anchor="w")
        self.create_angle_control(t_frame, "", "t_angle", 90, 30, 150)
        
        # Cross-Junction controls
        cross_frame = ttk.Frame(self.angle_frame)
        cross_frame.pack(fill="x", pady=5)
        ttk.Label(cross_frame, text="Cross Junction - Individual Road Angles:").pack(anchor="w")
        
        self.create_angle_control(cross_frame, "Top Road", "top_angle", 90)      # DOWN
        self.create_angle_control(cross_frame, "Right Road", "right_angle", 0)   # RIGHT  
        self.create_angle_control(cross_frame, "Bottom Road", "bottom_angle", 270) # UP
    
    def setup_lane_controls(self):
        self.lane_frame = ttk.LabelFrame(self.window, text="Lane Configuration", padding=10)
        self.lane_frame.pack(fill="x", padx=10, pady=5)
        
        # Road Direction Type
        ttk.Label(self.lane_frame, text="Road Type:").pack(anchor="w")
        self.road_type = tk.StringVar(value="2way_with_divider")
        ttk.Radiobutton(self.lane_frame, text="1 Way (One Direction)", 
                       variable=self.road_type, value="1way").pack(anchor="w")
        ttk.Radiobutton(self.lane_frame, text="2 Way with Divider", 
                       variable=self.road_type, value="2way_with_divider").pack(anchor="w")
        ttk.Radiobutton(self.lane_frame, text="2 Way without Divider", 
                       variable=self.road_type, value="2way_without_divider").pack(anchor="w")
        
        # Lane Count
        ttk.Label(self.lane_frame, text="Total Lane Count:").pack(anchor="w", pady=(10,0))
        self.lane_count = tk.IntVar(value=2)
        self.lane_spinbox = ttk.Spinbox(self.lane_frame, from_=1, to=8, 
                                       textvariable=self.lane_count, width=10)
        self.lane_spinbox.pack(anchor="w", pady=2)
        
        # Lane Distribution Info
        self.lane_info = ttk.Label(self.lane_frame, text="2 lanes: 1 each direction")
        self.lane_info.pack(anchor="w", pady=5)
        
        # Apply Button
        self.apply_btn = ttk.Button(self.window, text="Apply Configuration", 
                                   command=self.apply_config)
        self.apply_btn.pack(pady=20)
        
        # Current Config Display
        self.config_frame = ttk.LabelFrame(self.window, text="Current Config", padding=10)
        self.config_frame.pack(fill="x", padx=10, pady=5)
        self.config_display = ttk.Label(self.config_frame, text="Default: Cross, 90°, 2-lane 2-way divided")
        self.config_display.pack(anchor="w")
    
    def setup_event_bindings(self):
        """Setup all event bindings for real-time updates"""
        # Bind events for real-time updates
        self.t_angle.trace("w", self.update_display)
        self.top_angle.trace("w", self.update_display)
        self.right_angle.trace("w", self.update_display)
        self.bottom_angle.trace("w", self.update_display)
        self.lane_count.trace("w", self.update_lane_info)
        self.road_type.trace("w", self.update_lane_info)
        self.junction_type.trace("w", self.update_display)
        
        # Bind entry validation
        self.t_angle_entry.bind('<Return>', self.validate_t_angle)
        self.top_angle_entry.bind('<Return>', lambda e: self.validate_angle(e, self.top_angle, self.top_angle_entry))
        self.right_angle_entry.bind('<Return>', lambda e: self.validate_angle(e, self.right_angle, self.right_angle_entry))
        self.bottom_angle_entry.bind('<Return>', lambda e: self.validate_angle(e, self.bottom_angle, self.bottom_angle_entry))
        
    def validate_t_angle(self, event=None):
        """Validate T-junction angle (30-150 degrees)"""
        self.validate_angle_range(self.t_angle_entry, self.t_angle, 30, 150)
            
    def validate_angle(self, event=None, var=None, entry=None):
        """Validate general angle (0-360 degrees)"""
        if var and entry:
            self.validate_angle_range(entry, var, 0, 360)
    
    def validate_angle_range(self, entry, var, min_val, max_val):
        """Generic angle validation helper"""
        try:
            entry_value = entry.get().strip()
            if entry_value == "":
                return  # Don't update if empty
            value = int(entry_value)
            if min_val <= value <= max_val:
                var.set(value)
            else:
                self.reset_entry(entry, var)
        except ValueError:
            self.reset_entry(entry, var)
    
    def reset_entry(self, entry, var):
        """Reset entry to current variable value"""
        entry.delete(0, tk.END)
        entry.insert(0, str(var.get()))
        
    def update_display(self, *args):
        # Update current config display automatically
        self.apply_config()
        
    def update_angle_labels(self, *args):
        pass  # No longer needed since we have entry fields
        
    def update_lane_info(self, *args):
        try:
            count = self.lane_count.get()
            if count == 0:  # Handle empty field
                count = 2  # Default value
        except:
            count = 2  # Default value if field is empty or invalid
        road_type = self.road_type.get()
        
        if road_type == "1way":
            info = f"{count} lanes: all same direction"
        elif road_type == "2way_with_divider":
            if count == 1:
                info = "1 lane: not valid for divided road"
            else:
                per_dir = count // 2
                remainder = count % 2
                if remainder == 0:
                    info = f"{count} lanes: {per_dir} each direction (with divider)"
                else:
                    info = f"{count} lanes: {per_dir+1}/{per_dir} split (with divider)"
        else:  # 2way_without_divider
            if count == 1:
                info = "1 lane: shared by both directions"
            elif count == 2:
                info = "2 lanes: 1 each direction (no divider)"
            else:
                per_dir = count // 2
                info = f"{count} lanes: ~{per_dir} each direction (no divider)"
        
        self.lane_info.config(text=info)
        
    def apply_config(self):
        global current_config, road_renderer
        
        # Safe getter with fallback to default values
        def safe_get_angle(var, default):
            try:
                return var.get()
            except tk.TclError:
                return default
        
        config = {
            'junction_type': self.junction_type.get(),
            't_angle': safe_get_angle(self.t_angle, 90),
            'top_angle': safe_get_angle(self.top_angle, 90),
            'right_angle': safe_get_angle(self.right_angle, 180),
            'bottom_angle': safe_get_angle(self.bottom_angle, 270),
            'road_type': self.road_type.get(),
            'lane_count': safe_get_angle(self.lane_count, 2)
        }
        
        # Update global config
        current_config.update(config)
        
        # Update road renderer
        road_renderer.update_config(config)
        
        # Update display
        if config['junction_type'] == 'cross':
            angle_info = f"T:{config['top_angle']}° R:{config['right_angle']}° B:{config['bottom_angle']}°"
        else:
            angle_info = f"{config['t_angle']}° offshoot"
            
        # Road type display names
        road_type_names = {
            '1way': '1-way',
            '2way_with_divider': '2-way divided',
            '2way_without_divider': '2-way undivided'
        }
        
        lane_info = f"{config['lane_count']}-lane {road_type_names[config['road_type']]}"
        display_text = f"{config['junction_type'].title()}, {angle_info}, {lane_info}"
        self.config_display.config(text=display_text)
        
    def run(self):
        self.window.mainloop()

class RoadRenderer:
    """Main road rendering class - can be used independently of GUI"""
    def __init__(self, config=None):
        """Initialize with default or provided config"""
        self.config = config or self.get_default_config()
        
    @staticmethod
    def get_default_config():
        """Get default road configuration"""
        return {
            'junction_type': 'cross',
            't_angle': 90,
            'top_angle': 90,      # Vehicles going DOWN (90 degrees)
            'right_angle': 0,     # Vehicles going RIGHT (0 degrees)  
            'bottom_angle': 270,  # Vehicles going UP (270 degrees)
            'road_type': '2way_with_divider',
            'lane_count': 2
        }
    
    def update_config(self, new_config):
        """Update road configuration"""
        self.config.update(new_config)
    
    def get_config(self):
        """Get current configuration"""
        return self.config.copy()
    
    def get_road_dimensions(self):
        """Get calculated road dimensions based on current config"""
        lane_width = 40
        total_lanes = self.config['lane_count']
        road_width = total_lanes * lane_width
        
        if self.config['road_type'] == '1way':
            lanes_per_direction = total_lanes
        else:  # 2way roads
            lanes_per_direction = total_lanes // 2
            
        return {
            'lane_width': lane_width,
            'total_lanes': total_lanes,
            'road_width': road_width,
            'lanes_per_direction': lanes_per_direction,
            'road_half_width': road_width // 2
        }
    
    def draw_roads(self, screen, center_x=960, center_y=540):
        """Draw roads with current configuration"""
        dimensions = self.get_road_dimensions()
        road_width = dimensions['road_width']
        road_half_width = dimensions['road_half_width']
        
        if self.config['junction_type'] == 'cross':
            # Cross junction roads
            angles = {
                'top': self.config['top_angle'],
                'right': self.config['right_angle'],
                'bottom': self.config['bottom_angle']
            }
            
            # LEFT ROAD (horizontal)
            left_road_rect = pygame.Rect(0, center_y - road_half_width, center_x, road_width)
            pygame.draw.rect(screen, (100, 100, 100), left_road_rect)
            
            # Draw other roads
            for road_name, angle in angles.items():
                draw_angled_road(screen, center_x, center_y, angle, road_half_width, 1000)
                
        else:  # T-junction
            # Main horizontal road
            pygame.draw.rect(screen, (100, 100, 100), 
                           (0, center_y - road_half_width, 1920, road_width))
            
            # T-branch
            draw_angled_road(screen, center_x, center_y, self.config['t_angle'], road_half_width, 1000)
    
    def draw_lane_markings(self, screen, center_x=960, center_y=540):
        """Draw IRC lane markings with current configuration"""
        dimensions = self.get_road_dimensions()
        draw_lane_markings(screen, self.config, center_x, center_y, 
                         dimensions['road_width'], dimensions['total_lanes'], 
                         dimensions['lanes_per_direction'], dimensions['lane_width'])
    
    def draw_intersection(self, screen, center_x=960, center_y=540):
        """Draw intersection square for cross junctions"""
        if self.config['junction_type'] == 'cross':
            dimensions = self.get_road_dimensions()
            intersection_size = dimensions['road_width'] + 5
            intersection_half = intersection_size // 2
            
            intersection_rect = pygame.Rect(center_x - intersection_half, center_y - intersection_half, 
                                          intersection_size, intersection_size)
            pygame.draw.rect(screen, (120, 120, 120), intersection_rect)
    
    def draw_complete_road_system(self, screen, center_x=960, center_y=540):
        """Draw complete road system: roads + markings + intersection"""
        # Draw roads first
        self.draw_roads(screen, center_x, center_y)
        
        # Draw lane markings
        self.draw_lane_markings(screen, center_x, center_y)
        
        # Draw intersection square on top
        self.draw_intersection(screen, center_x, center_y)

def run_config_panel():
    config = ConfigPanel()
    config.run()

# Global config for sharing between threads (for backward compatibility)
current_config = {
    'junction_type': 'cross',
    't_angle': 90,
    'top_angle': 90,      # Vehicles going DOWN (90 degrees)
    'right_angle': 0,     # Vehicles going RIGHT (0 degrees)
    'bottom_angle': 270,  # Vehicles going UP (270 degrees)
    'road_type': '2way_with_divider',
    'lane_count': 2
}

# Global road renderer instance
road_renderer = RoadRenderer(current_config)

def draw_angled_road(screen, center_x, center_y, angle, road_half_width, road_length, color=(100, 100, 100)):
    """Helper function to draw an angled road from center point"""
    angle_rad = math.radians(angle)
    
    # Direction vector for the road
    dx = road_length * math.cos(angle_rad)
    dy = road_length * math.sin(angle_rad)
    
    # Perpendicular vector for road width
    perp_x = road_half_width * math.sin(angle_rad)
    perp_y = -road_half_width * math.cos(angle_rad)
    
    # Calculate road corners
    road_points = [
        (center_x - perp_x, center_y - perp_y),
        (center_x + perp_x, center_y + perp_y),
        (center_x + perp_x + dx, center_y + perp_y + dy),
        (center_x - perp_x + dx, center_y - perp_y + dy)
    ]
    pygame.draw.polygon(screen, color, road_points)

def draw_solid_line(screen, start_pos, end_pos, width=3, color=(255, 255, 255)):
    """Draw a solid line (for edge markings and center lines)"""
    pygame.draw.line(screen, color, start_pos, end_pos, width)

def draw_dashed_line(screen, start_pos, end_pos, dash_length=20, gap_length=30, width=3, color=(255, 255, 255)):
    """Draw a dashed line (for lane dividers)"""
    # Calculate line direction and length
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    total_length = math.sqrt(dx*dx + dy*dy)
    
    if total_length == 0:
        return
        
    # Normalize direction
    dx_norm = dx / total_length
    dy_norm = dy / total_length
    
    # Draw dashes
    current_length = 0
    dash_cycle = dash_length + gap_length
    
    while current_length < total_length:
        # Start of current dash
        dash_start_x = start_pos[0] + current_length * dx_norm
        dash_start_y = start_pos[1] + current_length * dy_norm
        
        # End of current dash
        dash_end_length = min(current_length + dash_length, total_length)
        dash_end_x = start_pos[0] + dash_end_length * dx_norm
        dash_end_y = start_pos[1] + dash_end_length * dy_norm
        
        # Draw the dash
        pygame.draw.line(screen, color, (dash_start_x, dash_start_y), (dash_end_x, dash_end_y), width)
        
        # Move to next dash
        current_length += dash_cycle

def draw_center_divider(screen, start_pos, end_pos, divider_width=8, divider_color=(80, 80, 80)):
    """Draw a raised median divider for divided roads"""
    # Calculate perpendicular vector for divider width
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    length = math.sqrt(dx*dx + dy*dy)
    
    if length == 0:
        return
        
    # Perpendicular unit vector
    perp_x = -dy / length * (divider_width // 2)
    perp_y = dx / length * (divider_width // 2)
    
    # Draw divider as a thick line or rectangle
    divider_points = [
        (start_pos[0] - perp_x, start_pos[1] - perp_y),
        (start_pos[0] + perp_x, start_pos[1] + perp_y),
        (end_pos[0] + perp_x, end_pos[1] + perp_y),
        (end_pos[0] - perp_x, end_pos[1] - perp_y)
    ]
    pygame.draw.polygon(screen, divider_color, divider_points)

def draw_lane_markings(screen, config, center_x, center_y, road_width, total_lanes, lanes_per_direction, lane_width):
    """Draw IRC standard lane markings for all roads"""
    road_half_width = road_width // 2
    
    if config['junction_type'] == 'cross':
        # Cross junction markings - match the road drawing logic
        # Draw left road markings (horizontal)
        draw_horizontal_road_markings(screen, center_x, center_y, road_width, total_lanes, 
                                    lanes_per_direction, lane_width, config['road_type'])
        
        # Draw markings for angled roads
        angles = {
            'top': config['top_angle'],
            'right': config['right_angle'],
            'bottom': config['bottom_angle']
        }
        
        for road_name, angle in angles.items():
            draw_road_lane_markings(screen, center_x, center_y, angle, road_width, total_lanes, 
                                  lanes_per_direction, lane_width, config['road_type'], road_name)
    
    else:  # T-junction
        # Main horizontal road markings
        draw_horizontal_road_markings(screen, center_x, center_y, road_width, total_lanes, 
                                    lanes_per_direction, lane_width, config['road_type'])
        
        # T-branch markings
        draw_road_lane_markings(screen, center_x, center_y, config['t_angle'], road_width, total_lanes,
                              lanes_per_direction, lane_width, config['road_type'], 'branch')

def draw_road_lane_markings(screen, center_x, center_y, angle, road_width, total_lanes, lanes_per_direction, lane_width, road_type, road_name):
    """Draw lane markings for a single angled road"""
    angle_rad = math.radians(angle)
    road_half_width = road_width // 2
    road_length = 1000 if road_name != 'left' else center_x
    
    # Calculate road direction vectors
    dx_norm = math.cos(angle_rad)
    dy_norm = math.sin(angle_rad)
    perp_x = math.sin(angle_rad)
    perp_y = -math.cos(angle_rad)
    
    # 1. SOLID WHITE EDGE LINES (outer boundaries)
    # Top edge of road
    edge_top_start = (center_x - road_half_width * perp_x, center_y - road_half_width * perp_y)
    edge_top_end = (center_x - road_half_width * perp_x + road_length * dx_norm, 
                    center_y - road_half_width * perp_y + road_length * dy_norm)
    draw_solid_line(screen, edge_top_start, edge_top_end, 3, (255, 255, 255))
    
    # Bottom edge of road
    edge_bottom_start = (center_x + road_half_width * perp_x, center_y + road_half_width * perp_y)
    edge_bottom_end = (center_x + road_half_width * perp_x + road_length * dx_norm,
                       center_y + road_half_width * perp_y + road_length * dy_norm)
    draw_solid_line(screen, edge_bottom_start, edge_bottom_end, 3, (255, 255, 255))
    
    # 2. CENTER LINES AND LANE DIVIDERS
    if road_type == '2way_with_divider':
        # Physical raised median divider
        divider_start = (center_x, center_y)
        divider_end = (center_x + road_length * dx_norm, center_y + road_length * dy_norm)
        draw_center_divider(screen, divider_start, divider_end, 12, (80, 80, 80))
        
        # Yellow no-overtake lines on both sides of divider
        divider_offset = 6
        yellow_top_start = (center_x - divider_offset * perp_x, center_y - divider_offset * perp_y)
        yellow_top_end = (center_x - divider_offset * perp_x + road_length * dx_norm,
                          center_y - divider_offset * perp_y + road_length * dy_norm)
        draw_solid_line(screen, yellow_top_start, yellow_top_end, 3, (255, 255, 0))
        
        yellow_bottom_start = (center_x + divider_offset * perp_x, center_y + divider_offset * perp_y)
        yellow_bottom_end = (center_x + divider_offset * perp_x + road_length * dx_norm,
                             center_y + divider_offset * perp_y + road_length * dy_norm)
        draw_solid_line(screen, yellow_bottom_start, yellow_bottom_end, 3, (255, 255, 0))
        
    elif road_type == '2way_without_divider':
        # Single yellow center line (no overtaking)
        center_start = (center_x, center_y)
        center_end = (center_x + road_length * dx_norm, center_y + road_length * dy_norm)
        draw_solid_line(screen, center_start, center_end, 3, (255, 255, 0))
    
    # 3. LANE DIVIDERS (white dashed lines within same direction)
    if total_lanes > 1:
        for i in range(1, total_lanes):
            # Skip center line for 2-way roads (already drawn)
            if road_type in ['2way_with_divider', '2way_without_divider'] and i == lanes_per_direction:
                continue
                
            # Calculate lane divider position
            lane_offset = (i * lane_width - road_half_width)
            divider_start = (center_x + lane_offset * perp_x, center_y + lane_offset * perp_y)
            divider_end = (center_x + lane_offset * perp_x + road_length * dx_norm,
                          center_y + lane_offset * perp_y + road_length * dy_norm)
            
            # White dashed lines for lane dividers
            draw_dashed_line(screen, divider_start, divider_end, 20, 30, 2, (255, 255, 255))

def draw_horizontal_road_markings(screen, center_x, center_y, road_width, total_lanes, lanes_per_direction, lane_width, road_type):
    """Draw lane markings for the main horizontal road in T-junction"""
    road_half_width = road_width // 2
    
    # 1. SOLID WHITE EDGE LINES
    # Top edge
    draw_solid_line(screen, (0, center_y - road_half_width), (1920, center_y - road_half_width), 3, (255, 255, 255))
    # Bottom edge  
    draw_solid_line(screen, (0, center_y + road_half_width), (1920, center_y + road_half_width), 3, (255, 255, 255))
    
    # 2. CENTER LINES AND DIVIDERS
    if road_type == '2way_with_divider':
        # Physical raised median
        draw_center_divider(screen, (0, center_y), (1920, center_y), 12, (80, 80, 80))
        # Yellow lines on both sides
        draw_solid_line(screen, (0, center_y - 6), (1920, center_y - 6), 3, (255, 255, 0))
        draw_solid_line(screen, (0, center_y + 6), (1920, center_y + 6), 3, (255, 255, 0))
        
    elif road_type == '2way_without_divider':
        # Single yellow center line
        draw_solid_line(screen, (0, center_y), (1920, center_y), 3, (255, 255, 0))
    
    # 3. LANE DIVIDERS
    if total_lanes > 1:
        for i in range(1, total_lanes):
            if road_type in ['2way_with_divider', '2way_without_divider'] and i == lanes_per_direction:
                continue
                
            lane_y = center_y - road_half_width + i * lane_width
            draw_dashed_line(screen, (0, lane_y), (1920, lane_y), 20, 30, 2, (255, 255, 255))

def draw_road_preview(screen, config):
    """Draw a simple preview of the road configuration"""
    center_x, center_y = 960, 540  # Center of 1920x1080
    
    # Draw background
    screen.fill((40, 40, 40))
    
    # Use the road renderer for drawing
    temp_renderer = RoadRenderer(config)
    temp_renderer.draw_complete_road_system(screen, center_x, center_y)
    
    # Draw info text
    font = pygame.font.Font(None, 36)
    junction_text = f"Junction: {config['junction_type'].title()}"
    if config['junction_type'] == 'cross':
        angle_text = f"Angles - Top:{config['top_angle']}° Right:{config['right_angle']}° Bottom:{config['bottom_angle']}°"
    else:
        angle_text = f"Branch Angle: {config['t_angle']}°"
    
    # Calculate dimensions for display
    lane_width = 40
    total_lanes = config['lane_count']
    road_width = total_lanes * lane_width
    
    if config['road_type'] == '1way':
        lanes_per_direction = total_lanes
    else:
        lanes_per_direction = total_lanes // 2
    
    # Show lane info with actual width and proper road type
    road_type_descriptions = {
        '1way': 'One direction only',
        '2way_with_divider': f'{lanes_per_direction} each direction (divided)',
        '2way_without_divider': f'{lanes_per_direction} each direction (undivided)'
    }
    
    lane_text = f"Lanes: {total_lanes} total - {road_type_descriptions[config['road_type']]} - {lane_width}px per lane"
    road_width_text = f"Total Road Width: {road_width}px"
    
    y_offset = 50
    for text in [junction_text, angle_text, lane_text, road_width_text]:
        text_surface = font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (50, y_offset))
        y_offset += 40

def main():
    # Start config panel in separate thread
    config_thread = threading.Thread(target=run_config_panel, daemon=True)
    config_thread.start()
    
    pygame.init()
    pygame.font.init()
    flags = pygame.FULLSCREEN | pygame.SCALED
    screen = pygame.display.set_mode((1920, 1080), flags)
    pygame.display.set_caption("Traffic Simulation (Fullscreen 1080p)")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Draw road preview based on current config
        draw_road_preview(screen, current_config)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

# ============================================================================
# LIBRARY INTERFACE - These functions can be used by other modules
# ============================================================================

def create_road_renderer(config=None):
    """Create a new RoadRenderer instance with optional config"""
    return RoadRenderer(config)

def get_default_road_config():
    """Get default road configuration dictionary"""
    return RoadRenderer.get_default_config()

def draw_roads_on_surface(surface, config, center_x=960, center_y=540):
    """Convenience function to draw roads on any pygame surface"""
    renderer = RoadRenderer(config)
    renderer.draw_complete_road_system(surface, center_x, center_y)

def get_road_dimensions(config):
    """Get road dimensions for given configuration"""
    renderer = RoadRenderer(config)
    return renderer.get_road_dimensions()

def start_config_gui(threaded=True):
    """Start the configuration GUI panel"""
    if threaded:
        config_thread = threading.Thread(target=run_config_panel, daemon=True)
        config_thread.start()
        return config_thread
    else:
        run_config_panel()

def get_current_config():
    """Get the current global configuration"""
    return current_config.copy()

def update_global_config(new_config):
    """Update the global configuration"""
    global current_config, road_renderer
    current_config.update(new_config)
    road_renderer.update_config(new_config)


if __name__ == "__main__":
    main()
