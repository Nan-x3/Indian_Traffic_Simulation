# Indian Traffic Simulation

A realistic pygame-based traffic simulation system designed for Indian road conditions. Originally developed for Smart India Hackathon, this simulation provides configurable road layouts and vehicle behaviors specific to Indian traffic patterns.

## Features

🚗 **Realistic Vehicle Types**: Cars, buses, trucks, motorcycles, auto-rickshaws, bicycles, and tempos
🛣️ **Indian Road Types**: Highway, city main roads, side streets, rural roads, and expressways
🚦 **Traffic Management**: Configurable traffic density from low to peak hour conditions
📊 **Real-time Statistics**: Live traffic data including vehicle counts and average speeds
🎮 **Interactive Controls**: Keyboard and mouse controls for simulation management

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Simulation**:
   ```bash
   python main.py
   ```

3. **Controls**:
   - `SPACE` - Pause/Resume
   - `1-4` - Traffic density levels
   - `S` - Toggle statistics
   - `C` - Clear vehicles
   - `ESC` - Exit

## Project Structure

- `main.py` - Main simulation entry point and UI
- `road_config.py` - Road layout and configuration management
- `vehicle_spawnconfig.py` - Vehicle spawning and traffic flow logic
- `CONFIG_GUIDE.md` - Detailed configuration documentation

## Customization

The simulation is designed to be easily customizable for different use cases:

- Adjust vehicle spawn probabilities
- Modify road layouts and types
- Configure traffic density parameters
- Add new vehicle types or road configurations

See `CONFIG_GUIDE.md` for detailed customization instructions.

## License

MIT License - see LICENSE file for details.
