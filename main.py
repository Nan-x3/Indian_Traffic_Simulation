"""
Main Module for Indian Traffic Simulation

This is the main entry point for the pygame-based Indian traffic simulation system.
It manages the game loop, user interface, and coordinates between road configuration
and vehicle spawning systems.
"""

import pygame
import sys
from typing import Optional
from road_config import RoadConfig, RoadType
from vehicle_spawnconfig import VehicleSpawnConfig, TrafficDensity, VehicleType

class TrafficSimulation:
    """Main traffic simulation class"""
    
    def __init__(self, width: int = 1200, height: int = 800):
        # Initialize Pygame
        pygame.init()
        
        # Screen setup
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Indian Traffic Simulation")
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Initialize simulation components
        self.road_config = RoadConfig(width, height)
        self.vehicle_spawn_config = VehicleSpawnConfig(self.road_config)
        
        # Setup default road layout
        self.road_config.create_default_indian_road_layout()
        
        # Simulation state
        self.running = True
        self.paused = False
        self.show_stats = True
        
        # UI setup
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Colors
        self.colors = {
            'background': (40, 40, 40),
            'text': (255, 255, 255),
            'panel_bg': (60, 60, 60),
            'button': (100, 100, 100),
            'button_hover': (120, 120, 120)
        }
        
        # UI elements
        self.buttons = self._create_ui_buttons()
        
        print("Indian Traffic Simulation initialized successfully!")
        print("Controls:")
        print("  SPACE - Pause/Resume simulation")
        print("  S - Toggle statistics display")
        print("  1-4 - Change traffic density (Low, Medium, High, Peak Hour)")
        print("  C - Clear all vehicles")
        print("  ESC - Exit simulation")
    
    def _create_ui_buttons(self) -> dict:
        """Create UI buttons for simulation control"""
        buttons = {}
        
        # Traffic density buttons
        button_width, button_height = 120, 30
        start_x, start_y = 10, 10
        
        densities = [
            (TrafficDensity.LOW, "Low Traffic"),
            (TrafficDensity.MEDIUM, "Medium Traffic"),
            (TrafficDensity.HIGH, "High Traffic"),
            (TrafficDensity.PEAK_HOUR, "Peak Hour")
        ]
        
        for i, (density, label) in enumerate(densities):
            button_rect = pygame.Rect(start_x, start_y + i * (button_height + 5), button_width, button_height)
            buttons[f'density_{density.value}'] = {
                'rect': button_rect,
                'label': label,
                'action': lambda d=density: self.vehicle_spawn_config.set_traffic_density(d),
                'active': density == TrafficDensity.MEDIUM
            }
        
        # Control buttons
        control_start_y = start_y + len(densities) * (button_height + 5) + 20
        
        control_buttons = [
            ('pause', "Pause/Resume", self.toggle_pause),
            ('stats', "Toggle Stats", self.toggle_stats),
            ('clear', "Clear Vehicles", self.clear_vehicles)
        ]
        
        for i, (key, label, action) in enumerate(control_buttons):
            button_rect = pygame.Rect(start_x, control_start_y + i * (button_height + 5), button_width, button_height)
            buttons[key] = {
                'rect': button_rect,
                'label': label,
                'action': action,
                'active': False
            }
        
        return buttons
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keyboard_input(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self._handle_mouse_click(event.pos)
    
    def _handle_keyboard_input(self, key):
        """Handle keyboard input"""
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_SPACE:
            self.toggle_pause()
        elif key == pygame.K_s:
            self.toggle_stats()
        elif key == pygame.K_c:
            self.clear_vehicles()
        elif key == pygame.K_1:
            self.vehicle_spawn_config.set_traffic_density(TrafficDensity.LOW)
            self._update_button_states('density_low')
        elif key == pygame.K_2:
            self.vehicle_spawn_config.set_traffic_density(TrafficDensity.MEDIUM)
            self._update_button_states('density_medium')
        elif key == pygame.K_3:
            self.vehicle_spawn_config.set_traffic_density(TrafficDensity.HIGH)
            self._update_button_states('density_high')
        elif key == pygame.K_4:
            self.vehicle_spawn_config.set_traffic_density(TrafficDensity.PEAK_HOUR)
            self._update_button_states('density_peak_hour')
    
    def _handle_mouse_click(self, pos):
        """Handle mouse clicks on UI elements"""
        for button_key, button_data in self.buttons.items():
            if button_data['rect'].collidepoint(pos):
                button_data['action']()
                
                # Update button states for density buttons
                if button_key.startswith('density_'):
                    self._update_button_states(button_key)
                break
    
    def _update_button_states(self, active_button):
        """Update button active states"""
        for button_key in self.buttons:
            if button_key.startswith('density_'):
                self.buttons[button_key]['active'] = (button_key == active_button)
    
    def toggle_pause(self):
        """Toggle simulation pause state"""
        self.paused = not self.paused
        print(f"Simulation {'paused' if self.paused else 'resumed'}")
    
    def toggle_stats(self):
        """Toggle statistics display"""
        self.show_stats = not self.show_stats
        print(f"Statistics display {'enabled' if self.show_stats else 'disabled'}")
    
    def clear_vehicles(self):
        """Clear all vehicles from simulation"""
        self.vehicle_spawn_config.clear_all_vehicles()
        print("All vehicles cleared from simulation")
    
    def update(self, dt: float):
        """Update simulation state"""
        if not self.paused:
            # Spawn new vehicles
            self.vehicle_spawn_config.spawn_vehicle()
            
            # Update existing vehicles
            self.vehicle_spawn_config.update_vehicles(dt)
    
    def draw(self):
        """Draw the simulation"""
        # Clear screen
        self.screen.fill(self.colors['background'])
        
        # Draw roads
        self.road_config.draw_roads(self.screen)
        
        # Draw vehicles
        self.vehicle_spawn_config.draw_vehicles(self.screen)
        
        # Draw UI
        self._draw_ui()
        
        # Draw statistics
        if self.show_stats:
            self._draw_statistics()
        
        # Draw pause indicator
        if self.paused:
            self._draw_pause_indicator()
        
        pygame.display.flip()
    
    def _draw_ui(self):
        """Draw user interface elements"""
        # Draw title
        title_text = self.font.render("Indian Traffic Simulation", True, self.colors['text'])
        self.screen.blit(title_text, (self.width - title_text.get_width() - 10, 10))
        
        # Draw buttons
        for button_key, button_data in self.buttons.items():
            button_color = self.colors['button_hover'] if button_data['active'] else self.colors['button']
            pygame.draw.rect(self.screen, button_color, button_data['rect'])
            pygame.draw.rect(self.screen, self.colors['text'], button_data['rect'], 2)
            
            # Draw button text
            text_surface = self.small_font.render(button_data['label'], True, self.colors['text'])
            text_rect = text_surface.get_rect(center=button_data['rect'].center)
            self.screen.blit(text_surface, text_rect)
    
    def _draw_statistics(self):
        """Draw traffic statistics"""
        stats = self.vehicle_spawn_config.get_traffic_stats()
        
        # Statistics panel background
        panel_width, panel_height = 250, 200
        panel_x = self.width - panel_width - 10
        panel_y = 50
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, self.colors['panel_bg'], panel_rect)
        pygame.draw.rect(self.screen, self.colors['text'], panel_rect, 2)
        
        # Draw statistics text
        y_offset = panel_y + 10
        line_height = 20
        
        # Title
        title = self.small_font.render("Traffic Statistics", True, self.colors['text'])
        self.screen.blit(title, (panel_x + 10, y_offset))
        y_offset += line_height + 5
        
        # Total vehicles
        total_vehicles = self.small_font.render(f"Total Vehicles: {stats['total_vehicles']}", True, self.colors['text'])
        self.screen.blit(total_vehicles, (panel_x + 10, y_offset))
        y_offset += line_height
        
        # Average speed
        avg_speed = self.small_font.render(f"Avg Speed: {stats['average_speed']:.1f} km/h", True, self.colors['text'])
        self.screen.blit(avg_speed, (panel_x + 10, y_offset))
        y_offset += line_height
        
        # Traffic density
        density = self.small_font.render(f"Density: {stats['traffic_density'].title()}", True, self.colors['text'])
        self.screen.blit(density, (panel_x + 10, y_offset))
        y_offset += line_height + 5
        
        # Vehicle types
        if stats['vehicle_types']:
            types_title = self.small_font.render("Vehicle Types:", True, self.colors['text'])
            self.screen.blit(types_title, (panel_x + 10, y_offset))
            y_offset += line_height
            
            for vehicle_type, count in stats['vehicle_types'].items():
                type_text = self.small_font.render(f"  {vehicle_type}: {count}", True, self.colors['text'])
                self.screen.blit(type_text, (panel_x + 10, y_offset))
                y_offset += line_height - 2
    
    def _draw_pause_indicator(self):
        """Draw pause indicator"""
        pause_text = self.font.render("PAUSED", True, (255, 255, 0))
        text_rect = pause_text.get_rect(center=(self.width // 2, 50))
        
        # Draw background
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
        pygame.draw.rect(self.screen, (255, 255, 0), bg_rect, 2)
        
        self.screen.blit(pause_text, text_rect)
    
    def run(self):
        """Main simulation loop"""
        print("Starting Indian Traffic Simulation...")
        
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(self.fps) / 1000.0  # Convert to seconds
            
            # Handle events
            self.handle_events()
            
            # Update simulation
            self.update(dt)
            
            # Draw everything
            self.draw()
        
        print("Simulation ended. Goodbye!")
        pygame.quit()
        sys.exit()

def main():
    """Main function to start the simulation"""
    try:
        # Create and run the simulation
        simulation = TrafficSimulation()
        simulation.run()
    
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
        pygame.quit()
        sys.exit()
    
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()