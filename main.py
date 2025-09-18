#!/usr/bin/env python3
"""
Main Traffic Simulation - Integration of roads and vehicles
"""

import pygame
import sys
import os
import time

# Import our libraries
import road_config
import vehicle_spawnconfig

def main():
    """Main traffic simulation program with vehicles"""
    
    # Initialize pygame
    pygame.init()
    pygame.font.init()
    
    # Set up display
    flags = pygame.FULLSCREEN | pygame.SCALED
    screen = pygame.display.set_mode((1920, 1080), flags)
    pygame.display.set_caption("Traffic Simulation - Roads + Vehicles")
    clock = pygame.time.Clock()
    
    # Setup road renderer
    print("Creating road renderer...")
    road_renderer = road_config.create_road_renderer()
    
    # Start the road config GUI (optional)
    print("Starting road configuration GUI...")
    road_config.start_config_gui(threaded=True)
    
    # Setup vehicle spawning
    print("Setting up vehicle spawning...")
    current_config = road_config.get_current_config()
    vehicle_spawner = vehicle_spawnconfig.VehicleSpawner()
    vehicle_spawner.set_road_config(current_config)
    vehicle_spawner.set_spawn_rate(0.8)  # Slower spawning to prevent overlaps
    vehicle_spawner.set_max_vehicles(100)  # Reduced vehicle count for better spacing
    vehicle_spawner.enable_spawning()
    
    # Main loop
    running = True
    show_info = True
    show_debug = False
    
    print("\nTraffic Simulation Controls:")
    print("- ESC: Exit")
    print("- V: Toggle vehicle spawning on/off")
    print("- C: Clear all vehicles")
    print("- I: Toggle info display")
    print("- D: Toggle debug lane visualization")
    print("- R: Reset vehicle spawning with current road config")
    print("- GUI window allows real-time road configuration")
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        current_time = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_v:
                    # Toggle vehicle spawning
                    if vehicle_spawner.is_spawning_enabled():
                        vehicle_spawner.disable_spawning()
                        print("Vehicle spawning stopped")
                    else:
                        vehicle_spawner.enable_spawning()
                        print("Vehicle spawning started")
                elif event.key == pygame.K_c:
                    # Clear all vehicles
                    vehicle_spawner.clear_vehicles()
                    print("All vehicles cleared")
                elif event.key == pygame.K_i:
                    # Toggle info display
                    show_info = not show_info
                    print(f"Info display: {'ON' if show_info else 'OFF'}")
                elif event.key == pygame.K_d:
                    # Toggle debug visualization
                    show_debug = not show_debug
                    print(f"Debug visualization: {'ON' if show_debug else 'OFF'}")
                elif event.key == pygame.K_r:
                    # Reset spawning with current road config
                    current_config = road_config.get_current_config()
                    vehicle_spawner.set_road_config(current_config)
                    print("Vehicle spawning reset with current road configuration")
        
        # Clear screen
        screen.fill((40, 40, 40))
        
        # Get current road configuration and update road renderer
        current_config = road_config.get_current_config()
        road_renderer.update_config(current_config)
        
        # Draw complete road system
        road_renderer.draw_complete_road_system(screen)
        
        # Update and draw vehicles
        vehicle_spawner.update_vehicles(dt, current_time, current_config)
        vehicle_spawner.draw_vehicles(screen)
        
        # Draw debug visualization if enabled
        if show_debug:
            vehicle_spawner.draw_debug_info(screen)
        
        # Display information
        if show_info:
            font = pygame.font.Font(None, 36)
            y_offset = 50
            
            # Vehicle info
            vehicle_count = vehicle_spawner.get_vehicle_count()
            spawning_status = "ON" if vehicle_spawner.is_spawning_enabled() else "OFF"
            vehicle_info = f"Vehicles: {vehicle_count} | Spawning: {spawning_status}"
            
            # Road info
            junction_type = current_config['junction_type'].title()
            road_type = current_config['road_type'].replace('_', ' ').title()
            lane_count = current_config['lane_count']
            road_info = f"Road: {junction_type} Junction | {road_type} | {lane_count} Lanes"
            
            # Controls reminder
            controls_info = "Controls: V=Toggle Spawning | C=Clear | I=Toggle Info | D=Debug | R=Reset | ESC=Exit"
            
            # Draw info texts
            for text in [vehicle_info, road_info, controls_info]:
                text_surface = font.render(text, True, (255, 255, 255))
                screen.blit(text_surface, (50, y_offset))
                y_offset += 40
        
        # Update display
        pygame.display.flip()
    
    print("Traffic simulation ended.")
    pygame.quit()

if __name__ == "__main__":
    main()
