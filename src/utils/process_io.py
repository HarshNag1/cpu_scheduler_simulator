import json
import csv
import os
from ..core.process import Process

class ProcessIOError(Exception):
    pass

class ProcessIO:
    @staticmethod
    def export_to_json(processes, filename):
        try:
            data = []
            for p in processes:
                data.append({
                    'pid': p.pid,
                    'arrival_time': p.arrival_time,
                    'burst_time': p.burst_time,
                    'priority': p.priority
                })
            
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            raise ProcessIOError(f"Failed to export to JSON: {str(e)}")
            
    @staticmethod
    def import_from_json(filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            processes = []
            for p in data:
                try:
                    process = Process(
                        pid=int(p['pid']),
                        arrival_time=int(p['arrival_time']),
                        burst_time=int(p['burst_time']),
                        priority=int(p['priority'])
                    )
                    processes.append(process)
                except (KeyError, ValueError) as e:
                    raise ProcessIOError(f"Invalid process data: {str(e)}")
                    
            return processes
        except json.JSONDecodeError as e:
            raise ProcessIOError(f"Invalid JSON file: {str(e)}")
        except Exception as e:
            raise ProcessIOError(f"Failed to import from JSON: {str(e)}")
        
    @staticmethod
    def export_to_csv(processes, filename):
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['PID', 'Arrival Time', 'Burst Time', 'Priority'])
                for p in processes:
                    writer.writerow([p.pid, p.arrival_time, p.burst_time, p.priority])
        except Exception as e:
            raise ProcessIOError(f"Failed to export to CSV: {str(e)}")
                
    @staticmethod
    def import_from_csv(filename):
        try:
            processes = []
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        process = Process(
                            pid=int(row['PID']),
                            arrival_time=int(row['Arrival Time']),
                            burst_time=int(row['Burst Time']),
                            priority=int(row['Priority'])
                        )
                        processes.append(process)
                    except (KeyError, ValueError) as e:
                        raise ProcessIOError(f"Invalid process data in CSV: {str(e)}")
                        
            return processes
        except csv.Error as e:
            raise ProcessIOError(f"Invalid CSV file: {str(e)}")
        except Exception as e:
            raise ProcessIOError(f"Failed to import from CSV: {str(e)}")
        
    @staticmethod
    def generate_random_processes(count, max_arrival=20, max_burst=10, max_priority=10):
        try:
            import random
            processes = []
            for i in range(count):
                process = Process(
                    pid=i+1,
                    arrival_time=random.randint(0, max_arrival),
                    burst_time=random.randint(1, max_burst),
                    priority=random.randint(0, max_priority)
                )
                processes.append(process)
            return processes
        except Exception as e:
            raise ProcessIOError(f"Failed to generate random processes: {str(e)}")
