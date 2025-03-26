# CPU Scheduler Simulator

A dynamic web-based CPU scheduling simulator that provides real-time visualization of various scheduling algorithms. Built with Flask and modern web technologies.

## Features
- Multiple CPU scheduling algorithms:
  - First Come First Serve (FCFS)
  - Shortest Job First (SJF)
  - Round Robin (RR) with configurable time quantum
  - Priority Scheduling
- Real-time visualization:
  - Interactive Gantt chart using Chart.js
  - Dynamic metrics calculation
  - Beautiful UI with glass-morphism design
- Performance metrics:
  - Average waiting time
  - Average turnaround time
- Modern user interface:
  - Dark/Light theme toggle
  - Responsive design
  - Particle.js background
  - Smooth animations
  - PDF report generation
- Interactive process management:
  - Add/Edit/Delete processes
  - Generate random processes
  - Clear all processes

## Tech Stack
### Frontend
- HTML5, CSS3, JavaScript
- Bootstrap 5.1.3
- Chart.js for Gantt chart
- Particles.js for background
- AOS (Animate On Scroll) library
- Font Awesome icons
- jsPDF for report generation

### Backend
- Python 3.x
- Flask web framework
- Custom scheduling algorithm implementations

## Requirements
```
Flask==2.0.1
Werkzeug==2.0.1
```

## Setup and Installation
1. Clone the repository
```bash
git clone https://github.com/yourusername/cpu-scheduler-simulator.git
cd cpu-scheduler-simulator
```

2. Create and activate virtual environment (optional but recommended)
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the application
```bash
cd web
python app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Usage
1. Select a scheduling algorithm from the dropdown
2. Add processes manually or generate random ones
3. For Round Robin, specify the time quantum
4. Click "Run Simulation" to see the results
5. View the Gantt chart and performance metrics
6. Download PDF report if needed

## Project Structure
```
web/
├── app.py              # Flask application
├── static/
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript files
│   └── particles.json  # Particles configuration
├── templates/         # HTML templates
└── src/
    └── core/         # Core scheduling algorithms
```

## Contributing
Feel free to open issues and pull requests for any improvements.


## Author
Harsh Nag
