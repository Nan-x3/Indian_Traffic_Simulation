# Indian Traffic Simulation

This is a pygame-based traffic simulation system developed for the Smart India Hackathon. It simulates Indian traffic scenarios with vehicles, traffic lights, and road configurations that can be customized for specific use cases.

## Features

- Interactive traffic simulation with various vehicle types (bikes, cars, autos, buses, trucks)
- Dynamic traffic light management system
- Configurable road layouts and junction types
- Real-time vehicle spawning and movement
- GUI-based road configuration panel

## Requirements

- Python 3.7 or higher
- pygame library

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Indian_Traffic_Simulation
```

### 2. Create and Activate Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

Or install pygame directly:
```bash
pip install pygame
```

### 4. Run the Simulation
```bash
python main.py
```

## Project Structure

- `main.py` - Main simulation entry point
- `road_config.py` - Road configuration and GUI controls
- `traffic_lights.py` - Traffic light management system
- `vehicle_spawnconfig.py` - Vehicle spawning and movement logic
- `requirements.txt` - Python dependencies

## Usage

1. Run `python main.py` to start the simulation
2. Use the configuration GUI to adjust road layouts and parameters
3. The simulation will display vehicles moving through intersections with traffic light control
4. Press ESC or close the window to exit

## Development

This project was developed for the Smart India Hackathon and can be extended or modified for specific traffic simulation needs. The modular design allows for easy customization of vehicle types, road layouts, and traffic management systems.
