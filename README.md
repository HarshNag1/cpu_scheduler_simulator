# CPU Scheduler Simulator

An interactive CPU scheduling simulator with real-time visualizations supporting multiple algorithms.

## Features
- Multiple CPU scheduling algorithms:
  - First Come First Serve (FCFS)
  - Shortest Job First (SJF)
  - Round Robin (RR) with configurable time quantum
  - Priority Scheduling
- Real-time visualization:
  - Interactive Gantt chart
  - Timeline view
  - Queue state visualization
- Performance metrics:
  - Average waiting time
  - Average turnaround time
  - CPU utilization
- Modern user interface:
  - Dark/Light theme support
  - Process import/export
  - PDF report generation
- Interactive process management:
  - Add processes manually
  - Generate random processes
  - Import/Export process data

## Requirements
- Python 3.x
- PyQt6
- Matplotlib
- NumPy/Pandas
- ReportLab (for PDF generation)

## Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate virtual environment:
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application
```bash
python main.py
```

## Usage Guide
1. Adding Processes:
   - Click "Add Process" to manually add a process
   - Use "Generate Random" for test data
   - Import processes from JSON/CSV files

2. Running Simulations:
   - Select a scheduling algorithm
   - Set time quantum for Round Robin
   - Click "Run Simulation"

3. Analyzing Results:
   - View the Gantt chart
   - Check process statistics
   - Download detailed PDF report

4. Customization:
   - Toggle between light/dark themes
   - Adjust animation speed
   - Switch between visualization views

## Project Structure
```
CPU_Scheduler/
├── main.py              # Application entry point
├── requirements.txt     # Project dependencies
├── src/
│   ├── core/           # Core scheduling algorithms
│   ├── ui/             # User interface components
│   ├── visualization/  # Visualization modules
│   └── utils/          # Utility functions
└── CPU Schedule Downloads/ # Generated reports
```

## Contributing
Feel free to submit issues and enhancement requests!
