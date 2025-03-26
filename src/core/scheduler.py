from abc import ABC, abstractmethod
from .process import Process
from typing import List, Tuple

class Scheduler(ABC):
    def __init__(self):
        self.processes: List[Process] = []
        self.current_time = 0
        
    @abstractmethod
    def schedule(self) -> List[Tuple[int, Process]]:
        """Returns a list of (time, process) pairs representing the schedule"""
        pass
        
class FCFSScheduler(Scheduler):
    def schedule(self) -> List[Tuple[int, Process]]:
        timeline = []
        sorted_processes = sorted(self.processes, key=lambda p: p.arrival_time)
        current_time = 0
        
        for process in sorted_processes:
            if current_time < process.arrival_time:
                current_time = process.arrival_time
            
            process.start_time = current_time
            process.waiting_time = current_time - process.arrival_time
            timeline.append((current_time, process))
            
            current_time += process.burst_time
            process.completion_time = current_time
            
        return timeline

class SJFScheduler(Scheduler):
    def schedule(self) -> List[Tuple[int, Process]]:
        timeline = []
        remaining_processes = [(p, p.burst_time) for p in self.processes]
        current_time = 0
        
        while remaining_processes:
            # Find ready processes
            ready_processes = [
                (p, rt) for p, rt in remaining_processes 
                if p.arrival_time <= current_time
            ]
            
            if not ready_processes:
                # Jump to next arrival time
                current_time = min(p.arrival_time for p, _ in remaining_processes)
                continue
            
            # Select process with shortest remaining time
            process, remaining_time = min(ready_processes, key=lambda x: (x[1], x[0].pid))
            
            # Update process state
            if process.start_time is None:
                process.start_time = current_time
                process.waiting_time = current_time - process.arrival_time
            
            timeline.append((current_time, process))
            current_time += remaining_time
            
            # Remove completed process
            remaining_processes.remove((process, remaining_time))
            process.completion_time = current_time
            # Update waiting time to include any gaps between executions
            if process.waiting_time is None:
                process.waiting_time = 0
            process.waiting_time = process.completion_time - process.arrival_time - process.burst_time
            
        return timeline

class RoundRobinScheduler(Scheduler):
    def __init__(self, time_quantum=2):
        super().__init__()
        self.time_quantum = time_quantum
        
    def schedule(self) -> List[Tuple[int, Process]]:
        timeline = []
        remaining_processes = [(p, p.burst_time) for p in self.processes]
        current_time = 0
        
        while remaining_processes:
            # Find ready processes
            ready_processes = [
                (p, rt) for p, rt in remaining_processes 
                if p.arrival_time <= current_time
            ]
            
            if not ready_processes:
                # Jump to next arrival time
                current_time = min(p.arrival_time for p, _ in remaining_processes)
                continue
            
            process, remaining_time = ready_processes[0]
            
            # Set start time if first execution
            if process.start_time is None:
                process.start_time = current_time
                process.waiting_time = current_time - process.arrival_time
            else:
                # Add waiting time since last execution
                last_execution = max(t for t, p in timeline if p == process)
                process.waiting_time += current_time - last_execution - self.time_quantum
            
            timeline.append((current_time, process))
            
            # Execute for time quantum or remaining time
            execution_time = min(self.time_quantum, remaining_time)
            current_time += execution_time
            remaining_time -= execution_time
            
            # Update process state
            remaining_processes.remove((process, remaining_time + execution_time))
            if remaining_time > 0:
                remaining_processes.append((process, remaining_time))
                # Move to the end of the queue
                remaining_processes = remaining_processes[1:] + [remaining_processes[0]]
            else:
                process.completion_time = current_time
                # Final waiting time calculation
                process.waiting_time = process.completion_time - process.arrival_time - process.burst_time
            
        return timeline

class PriorityScheduler(Scheduler):
    def schedule(self) -> List[Tuple[int, Process]]:
        timeline = []
        remaining_processes = self.processes.copy()
        current_time = 0
        
        while remaining_processes:
            # Find ready processes
            ready_processes = [
                p for p in remaining_processes 
                if p.arrival_time <= current_time
            ]
            
            if not ready_processes:
                # Jump to next arrival time
                current_time = min(p.arrival_time for p in remaining_processes)
                continue
            
            # Select process with highest priority (lower number = higher priority)
            # Break ties with arrival time and PID
            process = min(ready_processes, 
                        key=lambda p: (p.priority, p.arrival_time, p.pid))
            remaining_processes.remove(process)
            
            process.start_time = current_time
            process.waiting_time = current_time - process.arrival_time
            timeline.append((current_time, process))
            
            current_time += process.burst_time
            process.completion_time = current_time
            
        return timeline
