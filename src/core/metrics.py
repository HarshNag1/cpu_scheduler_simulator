class PerformanceMetrics:
    def __init__(self, processes, timeline):
        self.processes = processes
        self.timeline = timeline
        self.total_time = self._calculate_total_time()
        
    def _calculate_total_time(self):
        if not self.timeline:
            return 0
        return max(p.completion_time for p in self.processes)
        
    def average_waiting_time(self):
        if not self.processes:
            return 0
        total_waiting = sum(p.waiting_time for p in self.processes)
        return total_waiting / len(self.processes)
        
    def average_turnaround_time(self):
        if not self.processes:
            return 0
        total_turnaround = sum(p.turnaround_time for p in self.processes)
        return total_turnaround / len(self.processes)
        
    def average_response_time(self):
        if not self.processes:
            return 0
        total_response = sum(p.start_time - p.arrival_time for p in self.processes)
        return total_response / len(self.processes)
        
    def cpu_utilization(self):
        if not self.total_time:
            return 0
        total_burst = sum(p.burst_time for p in self.processes)
        return (total_burst / self.total_time) * 100
        
    def throughput(self):
        if not self.total_time:
            return 0
        return len(self.processes) / self.total_time
        
    def context_switches(self):
        if not self.timeline:
            return 0
        switches = 0
        for i in range(1, len(self.timeline)):
            if self.timeline[i][1] != self.timeline[i-1][1]:
                switches += 1
        return switches
        
    def get_all_metrics(self):
        return {
            "Average Waiting Time": f"{self.average_waiting_time():.2f}",
            "Average Turnaround Time": f"{self.average_turnaround_time():.2f}",
            "Average Response Time": f"{self.average_response_time():.2f}",
            "CPU Utilization": f"{self.cpu_utilization():.2f}%",
            "Throughput": f"{self.throughput():.2f} processes/unit time",
            "Context Switches": f"{self.context_switches()}"
        }
