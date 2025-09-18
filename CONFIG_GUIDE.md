# Indian Traffic Simulation - Configuration Guide

This pygame-based traffic simulation system provides realistic Indian road traffic patterns with configurable settings.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the simulation:
```bash
python main.py
```

## Configuration Files

### 1. `main.py`
Main simulation entry point with game loop and user interface.

**Features:**
- Interactive UI with mouse and keyboard controls
- Real-time statistics display
- Pause/resume functionality
- Traffic density adjustment

**Controls:**
- `SPACE` - Pause/Resume simulation
- `S` - Toggle statistics display
- `1-4` - Change traffic density (Low, Medium, High, Peak Hour)
- `C` - Clear all vehicles
- `ESC` - Exit simulation

### 2. `road_config.py`
Road setup and configuration management for Indian traffic patterns.

**Road Types:**
- `HIGHWAY` - 3 lanes per direction, 100 km/h speed limit
- `CITY_MAIN` - 2 lanes per direction, 60 km/h speed limit
- `CITY_SIDE` - 1 lane per direction, 40 km/h speed limit
- `RURAL` - 1 lane per direction, 50 km/h speed limit
- `EXPRESSWAY` - 4 lanes per direction, 120 km/h speed limit

**Customization Example:**
```python
from road_config import RoadConfig, RoadType

# Create custom road configuration
road_config = RoadConfig(1200, 800)
road_config.create_default_indian_road_layout()

# Add custom road segment
# (implementation details in road_config.py)
```

### 3. `vehicle_spawnconfig.py`
Vehicle spawning and flow configuration with Indian vehicle types.

**Vehicle Types:**
- `CAR` - Standard passenger car (35% spawn rate)
- `BUS` - Public transport bus (15% spawn rate)
- `TRUCK` - Commercial truck (20% spawn rate)
- `MOTORCYCLE` - Two-wheeler (15% spawn rate)
- `AUTO_RICKSHAW` - Three-wheeler (10% spawn rate)
- `BICYCLE` - Bicycle (3% spawn rate)
- `TEMPO` - Small commercial vehicle (2% spawn rate)

**Traffic Density Levels:**
- `LOW` - Sparse traffic, vehicles move at 80% of max speed
- `MEDIUM` - Normal traffic, vehicles move at 70% of max speed
- `HIGH` - Heavy traffic, vehicles move at 60% of max speed
- `PEAK_HOUR` - Congested traffic, vehicles move at 40% of max speed

**Customization Example:**
```python
from vehicle_spawnconfig import VehicleSpawnConfig, VehicleType, TrafficDensity

# Set custom spawn probabilities
custom_probabilities = {
    VehicleType.CAR: 0.5,
    VehicleType.MOTORCYCLE: 0.3,
    VehicleType.BUS: 0.2
}
vehicle_config.set_custom_spawn_probabilities(custom_probabilities)

# Change traffic density
vehicle_config.set_traffic_density(TrafficDensity.PEAK_HOUR)
```

## Features

### Realistic Indian Traffic Simulation
- Mixed vehicle types common on Indian roads
- Lane-based traffic flow with overtaking behavior
- Speed variations based on vehicle type and traffic conditions
- Traffic light intersections
- Following distance and collision avoidance

### Configurable Parameters
- Road types and layouts
- Vehicle spawn rates and probabilities
- Traffic density levels
- Speed limits and vehicle properties
- Visual styling and colors

### Interactive Interface
- Real-time traffic statistics
- Manual traffic density control
- Pause/resume simulation
- Vehicle clearing functionality
- Mouse and keyboard controls

## System Requirements

- Python 3.7+
- pygame 2.1.0+
- numpy 1.21.0+

## File Structure

```
Indian_Traffic_Simulation/
├── main.py                 # Main simulation entry point
├── road_config.py         # Road configuration and rendering
├── vehicle_spawnconfig.py # Vehicle spawning and behavior
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
└── .gitignore           # Git ignore rules
```

## Future Enhancements

Possible improvements to extend the simulation:

1. **Advanced Lane Changing**: More sophisticated lane changing algorithms
2. **Traffic Signals**: Timed traffic light control systems
3. **Weather Effects**: Rain/fog impact on traffic behavior
4. **Accident Simulation**: Random events affecting traffic flow
5. **Route Planning**: Vehicles with specific destinations
6. **Data Export**: CSV export of traffic statistics
7. **Sound Effects**: Audio feedback for realistic experience
8. **Multiple Intersections**: Complex road networks

This simulation provides a solid foundation for studying Indian traffic patterns and can be easily extended for specific research or educational purposes.