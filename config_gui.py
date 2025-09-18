# config_gui.py

import tkinter as tk
from tkinter import ttk
import threading

class ConfigPanel:
    def __init__(self, config_callback=None):
        self.config_callback = config_callback  # Callback function to update config
        
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
        self.apply_config()

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

        # Fixed the GUI labels to match pygame coordinate system
        # In pygame: 0°=right, 90°=down, 180°=left, 270°=up
        self.create_angle_control(cross_frame, "Top Road (270° = up)",    "top_angle",    270)     # UP
        self.create_angle_control(cross_frame, "Right Road (0° = right)", "right_angle",  0)       # RIGHT
        self.create_angle_control(cross_frame, "Bottom Road (90° = down)", "bottom_angle", 90)     # DOWN
    
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
        
        self.t_angle_entry.bind('<Return>', lambda e: self.validate_angle(self.t_angle, 30, 150))
        self.top_angle_entry.bind('<Return>', lambda e: self.validate_angle(self.top_angle))
        self.right_angle_entry.bind('<Return>', lambda e: self.validate_angle(self.right_angle))
        self.bottom_angle_entry.bind('<Return>', lambda e: self.validate_angle(self.bottom_angle))
    
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
        if road_type == "1way": 
            info = f"{count} lanes: all same direction"
        elif "2way" in road_type:
            info = f"{count} lanes: {count//2} each way" if count > 1 else "1 lane: not valid for 2-way"
        self.lane_info.config(text=info)
        
    def apply_config(self):
        def safe_get(var, default):
            try: 
                return var.get()
            except tk.TclError: 
                return default

        config = {
            'junction_type': self.junction_type.get(),
            't_angle': safe_get(self.t_angle, 90),
            'top_angle': safe_get(self.top_angle, 270),
            'right_angle': safe_get(self.right_angle, 0),
            'bottom_angle': safe_get(self.bottom_angle, 90),
            'road_type': self.road_type.get(),
            'lane_count': safe_get(self.lane_count, 2),
            'traffic_light_mode': self.traffic_light_mode.get()
        }
        
        # Call the callback function to update the main config
        if self.config_callback:
            self.config_callback(config)
        
        # Update display
        if config['junction_type'] == 'cross':
            angle_info = f"T:{config['top_angle']} R:{config['right_angle']} B:{config['bottom_angle']}"
        else:
            angle_info = f"{config['t_angle']}°"
        
        road_type_names = {
            '1way': '1-way', 
            '2way_with_divider': '2-way divided', 
            '2way_without_divider': '2-way undivided'
        }
        lane_info = f"{config['lane_count']}-lane {road_type_names[config['road_type']]}"
        traffic_info = f"Lights: {config['traffic_light_mode'].title()}"
        display_text = f"{config['junction_type'].title()}, {angle_info}\n{lane_info}\n{traffic_info}"
        self.config_display.config(text=display_text)


def start_config_gui(config_callback=None, threaded=True):
    """Start the configuration GUI
    
    Args:
        config_callback: Function to call when configuration changes
        threaded: Whether to run GUI in a separate thread
    """
    def run_gui():
        panel = ConfigPanel(config_callback)
        panel.run()
    
    if threaded:
        thread = threading.Thread(target=run_gui, daemon=True)
        thread.start()
        return thread
    else:
        run_gui()


if __name__ == "__main__":
    # Test the GUI standalone
    def test_callback(config):
        print("Config updated:", config)
    
    start_config_gui(test_callback, threaded=False)
