import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import ttk
import numpy as np

class GanttChart:
    def __init__(self, master):
        # Create frame for chart and controls
        self.frame = ttk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Create figure and canvas
        self.figure = Figure(figsize=(10, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add navigation toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame)
        self.toolbar.update()
        
        # Add animation controls
        self.control_frame = ttk.Frame(self.frame)
        self.control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Animation speed
        ttk.Label(self.control_frame, text="Animation Speed:").pack(side=tk.LEFT, padx=5)
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_scale = ttk.Scale(
            self.control_frame, from_=0.1, to=2.0,
            variable=self.speed_var, orient=tk.HORIZONTAL,
            length=100
        )
        self.speed_scale.pack(side=tk.LEFT, padx=5)
        
        # View controls
        self.view_var = tk.StringVar(value="Gantt")
        ttk.Label(self.control_frame, text="View:").pack(side=tk.LEFT, padx=5)
        views = ttk.OptionMenu(
            self.control_frame, self.view_var,
            "Gantt", "Gantt", "Timeline", "Queue",
            command=self._change_view
        )
        views.pack(side=tk.LEFT, padx=5)
        
        # Define a color palette
        self.colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', 
                      '#FF99CC', '#99FFCC', '#FFB366', '#FF99FF']
                      
        # Initialize state
        self.timeline = None
        self.current_view = "Gantt"
        self.animation_speed = 1.0
        
    def _change_view(self, view):
        self.current_view = view
        if self.timeline:
            self.update(self.timeline)
            
    def _draw_gantt_view(self, timeline, processes):
        self.ax.clear()
        
        if not timeline or len(timeline) == 0:
            self._draw_empty_chart()
            return
            
        # Get unique processes and assign colors
        processes = sorted(list(set(process for _, process in timeline)), 
                         key=lambda p: p.pid)
        process_colors = {p: self.colors[i % len(self.colors)] 
                         for i, p in enumerate(processes)}
        
        # Track process rows
        process_rows = {p: i for i, p in enumerate(processes)}
        num_processes = len(processes)
        
        # Plot each process
        for i, (start_time, process) in enumerate(timeline):
            # Calculate duration
            if i < len(timeline) - 1:
                duration = timeline[i + 1][0] - start_time
            else:
                remaining_time = process.burst_time
                for t, p in timeline[:-1]:
                    if p == process:
                        next_start = next((s for s, pr in timeline if pr != p and s > t), timeline[-1][0])
                        remaining_time -= next_start - t
                duration = remaining_time
            
            row = process_rows[process]
            
            # Draw process block with border
            self.ax.barh(y=row, width=duration, left=start_time,
                        color=process_colors[process], alpha=0.7,
                        edgecolor='black', linewidth=1)
            
            # Add process label
            self.ax.text(start_time + duration/2, row, f'P{process.pid}',
                        ha='center', va='center',
                        color='black', fontweight='bold')
        
        # Customize the chart
        self.ax.set_title('CPU Scheduling Gantt Chart', pad=10)
        self.ax.set_xlabel('Time Units', labelpad=10)
        self.ax.set_ylabel('Processes', labelpad=10)
        
        # Set y-axis ticks and labels
        self.ax.set_yticks(range(num_processes))
        self.ax.set_yticklabels([f'Process {p.pid}' for p in processes])
        
        # Add grid
        self.ax.grid(True, axis='x', alpha=0.3)
        
        # Set x-axis to show integer ticks
        max_time = max(t[0] for t in timeline) + max(p.burst_time for _, p in timeline)
        self.ax.set_xticks(range(0, int(max_time) + 1))
        
    def _draw_timeline_view(self, timeline, processes):
        self.ax.clear()
        
        if not timeline or len(timeline) == 0:
            self._draw_empty_chart()
            return
            
        # Get unique processes and assign colors
        processes = sorted(list(set(process for _, process in timeline)), 
                         key=lambda p: p.pid)
        process_colors = {p: self.colors[i % len(self.colors)] 
                         for i, p in enumerate(processes)}
        
        # Create timeline points
        for i, (time, process) in enumerate(timeline):
            self.ax.scatter(time, process.pid, 
                          color=process_colors[process],
                          s=100, zorder=2)
            
            # Draw connecting lines
            if i > 0:
                prev_time, prev_process = timeline[i-1]
                if prev_process == process:
                    self.ax.plot([prev_time, time], 
                               [prev_process.pid, process.pid],
                               color=process_colors[process],
                               linestyle='--', alpha=0.5)
        
        # Customize the chart
        self.ax.set_title('Process Timeline View', pad=10)
        self.ax.set_xlabel('Time Units', labelpad=10)
        self.ax.set_ylabel('Process ID', labelpad=10)
        
        # Set y-axis ticks
        self.ax.set_yticks([p.pid for p in processes])
        
        # Add grid
        self.ax.grid(True, alpha=0.3)
        
    def _draw_queue_view(self, timeline, processes):
        self.ax.clear()
        
        if not timeline or len(timeline) == 0:
            self._draw_empty_chart()
            return
            
        # Get unique processes and assign colors
        processes = sorted(list(set(process for _, process in timeline)), 
                         key=lambda p: p.pid)
        process_colors = {p: self.colors[i % len(self.colors)] 
                         for i, p in enumerate(processes)}
        
        # Track ready queue at each time point
        max_time = max(t[0] for t in timeline) + max(p.burst_time for _, p in timeline)
        queue_states = []
        
        for t in range(int(max_time) + 1):
            ready = [p for p in processes if p.arrival_time <= t and 
                    (p.completion_time is None or p.completion_time > t)]
            queue_states.append((t, ready))
        
        # Plot queue states
        for t, queue in queue_states:
            for i, process in enumerate(queue):
                self.ax.scatter(t, i, color=process_colors[process],
                              s=100, label=f'P{process.pid}')
        
        # Customize the chart
        self.ax.set_title('Ready Queue States', pad=10)
        self.ax.set_xlabel('Time Units', labelpad=10)
        self.ax.set_ylabel('Queue Position', labelpad=10)
        
        # Add grid
        self.ax.grid(True, alpha=0.3)
        
        # Add legend
        handles, labels = self.ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        self.ax.legend(by_label.values(), by_label.keys(),
                      title="Processes", bbox_to_anchor=(1.05, 1),
                      loc='upper left')
        
    def _draw_empty_chart(self):
        self.ax.set_title('CPU Scheduling Chart')
        self.ax.set_xlabel('Time Units')
        self.ax.set_ylabel('Processes')
        self.ax.grid(True, alpha=0.3)
        
    def update(self, timeline):
        self.timeline = timeline
        processes = list(set(process for _, process in timeline)) if timeline else []
        
        if self.current_view == "Gantt":
            self._draw_gantt_view(timeline, processes)
        elif self.current_view == "Timeline":
            self._draw_timeline_view(timeline, processes)
        else:  # Queue view
            self._draw_queue_view(timeline, processes)
        
        # Set reasonable margins
        self.figure.tight_layout()
        
        # Update the display
        self.canvas.draw()
