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
from traffic_lights import TrafficLightManager

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
    vehicle_spawner.set_spawn_rate(0.8)
    vehicle_spawner.set_max_vehicles(100)
    
    # --- VEHICLE SPAWNING SETUP ---
    # vehicle_spawner.enable_spawning() # <-- Uncomment this line to start with vehicles enabled
    
    # Setup traffic light system
    print("Setting up traffic light system...")
    traffic_light_manager = TrafficLightManager()
    traffic_light = traffic_light_manager.add_traffic_light(960, 540, current_config, intersection_size=120)
    
    print("Traffic lights are now running! (15-second cycles)")
    print("Press V to enable vehicle spawning when ready.")
    
    # Main loop
    running = True
    show_info = True
    show_debug = False
    
    print("\nTraffic Simulation Started!")
    print("🚦 Traffic lights are cycling automatically (15s green, no yellow)")
    print("🚗 Vehicle spawning is OFF - press V to enable cars")
    print("\nControls:")
    print("- ESC: Exit simulation")
    print("- V: Toggle vehicle spawning on/off")
    print("- C: Clear all vehicles")
    print("- I: Toggle info display")
    print("- D: Toggle debug lane visualization")
    print("- R: Reset vehicle spawning with current road config")
    print("- GUI window allows real-time road configuration")
    print("\nSimulation running... Press V when ready for vehicles!")
    
    while running:
        dt = clock.tick(60) / 1000.0
        current_time = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_v:
                    if vehicle_spawner.is_spawning_enabled():
                        vehicle_spawner.disable_spawning()
                        print("Vehicle spawning stopped")
                    else:
                        vehicle_spawner.enable_spawning()
                        print("Vehicle spawning started")
                elif event.key == pygame.K_c:
                    vehicle_spawner.clear_vehicles()
                    print("All vehicles cleared")
                elif event.key == pygame.K_i:
                    show_info = not show_info
                elif event.key == pygame.K_d:
                    show_debug = not show_debug
                elif event.key == pygame.K_r:
                    current_config = road_config.get_current_config()
                    vehicle_spawner.set_road_config(current_config)
                    print("Vehicle spawning reset with current road configuration")
        
        screen.fill((40, 40, 40))
        
        current_config = road_config.get_current_config()
        road_renderer.update_config(current_config)
        traffic_light_manager.update_road_config(current_config)
        
        road_renderer.draw_complete_road_system(screen)
        
        traffic_light_manager.update_all()
        traffic_light_manager.draw_all(screen)
        
        vehicle_spawner.update_vehicles(dt, current_time, current_config, traffic_light_manager)
        vehicle_spawner.draw_vehicles(screen)
        
        if show_debug:
            vehicle_spawner.draw_debug_info(screen)
        
        if show_info:
            font = pygame.font.Font(None, 36)
            y_offset = 50
            
            vehicle_count = vehicle_spawner.get_vehicle_count()
            spawning_status = "ON" if vehicle_spawner.is_spawning_enabled() else "OFF"
            vehicle_info = f"Vehicles: {vehicle_count} | Spawning: {spawning_status}"
            
            junction_type = current_config['junction_type'].title()
            road_type = current_config['road_type'].replace('_', ' ').title()
            lane_count = current_config['lane_count']
            road_info = f"Road: {junction_type} | {road_type} | {lane_count} Lanes"
            
            # Get traffic light timing info
            timer_info = traffic_light.get_timer_info()
            current_green = timer_info['current_green']
            time_remaining = timer_info['time_remaining']
            traffic_info = f"Traffic Light: {current_green} Green | Next Change: {time_remaining:.1f}s"
            
            controls_info = "Controls: V=Toggle Spawning | C=Clear | I=Info | D=Debug | R=Reset | ESC=Exit"
            
            for text in [vehicle_info, road_info, traffic_info, controls_info]:
                text_surface = font.render(text, True, (255, 255, 255))
                screen.blit(text_surface, (50, y_offset))
                y_offset += 40
        
        pygame.display.flip()
    
    print("Traffic simulation ended.")
    pygame.quit()

if __name__ == "__main__":
    main()
