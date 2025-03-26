import sys
import os
from typing import List, Dict, Any
import traceback

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify
from src.core.process import Process
from src.core.scheduler import FCFSScheduler, SJFScheduler, RoundRobinScheduler, PriorityScheduler

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/schedule', methods=['POST'])
def schedule():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Extract and validate algorithm
        algorithm = data.get('algorithm')
        if not algorithm:
            return jsonify({'error': 'No algorithm specified'}), 400

        # Extract and validate processes
        processes_data = data.get('processes', [])
        if not processes_data:
            return jsonify({'error': 'No processes provided'}), 400

        # Extract and validate time quantum
        try:
            time_quantum = int(data.get('timeQuantum', 2))
            if time_quantum < 1:
                return jsonify({'error': 'Time quantum must be at least 1'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid time quantum value'}), 400

        # Create scheduler based on algorithm
        scheduler_map = {
            'FCFS': FCFSScheduler,
            'SJF': SJFScheduler,
            'RR': lambda: RoundRobinScheduler(time_quantum),
            'Priority': PriorityScheduler
        }

        scheduler_class = scheduler_map.get(algorithm)
        if not scheduler_class:
            return jsonify({'error': f'Invalid algorithm: {algorithm}'}), 400

        scheduler = scheduler_class()

        # Create processes
        processes: List[Process] = []
        for p in processes_data:
            try:
                # Validate required fields
                if any(key not in p for key in ['pid', 'arrivalTime', 'burstTime']):
                    return jsonify({'error': 'Missing required process fields'}), 400

                # Extract and validate process values
                pid = str(p['pid']).replace('P', '')  
                arrival_time = int(p['arrivalTime'])
                burst_time = int(p['burstTime'])
                priority = int(p.get('priority', 1))

                if burst_time < 1:
                    return jsonify({'error': f'Process {str(pid)}: Burst time must be at least 1'}), 400
                if arrival_time < 0:
                    return jsonify({'error': f'Process {str(pid)}: Arrival time cannot be negative'}), 400

                process = Process(
                    pid=pid,
                    arrival_time=arrival_time,
                    burst_time=burst_time,
                    priority=priority
                )
                processes.append(process)
            except ValueError as e:
                return jsonify({'error': f'Invalid process data: {str(e)}'}), 400

        if not processes:
            return jsonify({'error': 'No valid processes provided'}), 400

        # Run scheduler
        scheduler.processes = processes
        timeline = scheduler.schedule()

        # Format response
        response: Dict[str, Any] = {
            'timeline': [
                {'time': t, 'pid': str(pid)} for t, pid in timeline  
            ],
            'processes': [
                {
                    'pid': str(p),  
                    'arrivalTime': p.arrival_time,
                    'burstTime': p.burst_time,
                    'priority': p.priority,
                    'waitingTime': p.waiting_time,
                    'turnaroundTime': p.turnaround_time
                }
                for p in processes
            ],
            'metrics': {
                'avgWaitingTime': sum(p.waiting_time for p in processes) / len(processes),
                'avgTurnaroundTime': sum(p.turnaround_time for p in processes) / len(processes)
            }
        }

        return jsonify(response)

    except Exception as e:
        app.logger.error(f'Error in schedule endpoint: {str(e)}')
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
