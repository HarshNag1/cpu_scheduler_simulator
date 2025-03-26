import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from ..core.scheduler import FCFSScheduler, SJFScheduler, RoundRobinScheduler, PriorityScheduler
from ..visualization.gantt_chart import GanttChart
from ..utils.pdf_generator import PDFGenerator
from ..utils.process_io import ProcessIO
from ..utils.theme_manager import ThemeManager
from ..core.metrics import PerformanceMetrics
from .process_form import ProcessForm
import copy
import os

class MainWindow(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("CPU Scheduler Simulator")
        self.master.geometry("1000x800")  # Increased size for new features
        
        # Initialize managers
        downloads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                   "CPU Schedule Downloads")
        self.pdf_generator = PDFGenerator(downloads_dir)
        self.theme_manager = ThemeManager()
        self.theme_manager.add_theme_listener(self._apply_theme)  
        self.process_io = ProcessIO()
        
        # Create main container with padding
        self.main_container = ttk.Frame(self, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create frames
        self.control_frame = ttk.LabelFrame(self.main_container, text="Controls", padding="5")
        self.control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.process_frame = ttk.LabelFrame(self.main_container, text="Process List", padding="5")
        self.process_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.viz_frame = ttk.LabelFrame(self.main_container, text="Visualization", padding="5")
        self.viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.metrics_frame = ttk.LabelFrame(self.main_container, text="Performance Metrics", padding="5")
        self.metrics_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Setup components
        self._setup_controls()
        self._setup_process_list()
        self._setup_visualization()
        self._setup_metrics()
        
        # Initialize state
        self.processes = []
        self.scheduler = None
        self.next_pid = 1
        self.current_timeline = None
        self.metrics = None
        
        # Apply initial theme
        self._apply_theme(self.theme_manager.current_theme)
        
    def _setup_controls(self):
        # Top control panel
        top_controls = ttk.Frame(self.control_frame)
        top_controls.pack(fill=tk.X, pady=5)
        
        # Algorithm selection
        algo_frame = ttk.LabelFrame(top_controls, text="Algorithm", padding="5")
        algo_frame.pack(side=tk.LEFT, padx=5)
        
        self.algorithm = ttk.Combobox(algo_frame, values=[
            "FCFS", "SJF", "Round Robin", "Priority"
        ], state="readonly", width=15)
        self.algorithm.set("FCFS")
        self.algorithm.pack(side=tk.LEFT, padx=5)
        
        # Time Quantum for RR
        quantum_frame = ttk.LabelFrame(top_controls, text="Time Quantum", padding="5")
        quantum_frame.pack(side=tk.LEFT, padx=5)
        
        self.time_quantum = ttk.Entry(quantum_frame, width=5)
        self.time_quantum.insert(0, "2")
        self.time_quantum.pack(side=tk.LEFT, padx=5)
        
        # Theme toggle
        theme_frame = ttk.Frame(top_controls)
        theme_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(theme_frame, text="Toggle Theme",
                  command=self._toggle_theme).pack(side=tk.RIGHT, padx=5)
        
        # Bottom control panel
        bottom_controls = ttk.Frame(self.control_frame)
        bottom_controls.pack(fill=tk.X, pady=5)
        
        # Process management buttons
        process_btn_frame = ttk.LabelFrame(bottom_controls, text="Process Management", padding="5")
        process_btn_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(process_btn_frame, text="Add Process",
                  command=self._show_process_form).pack(side=tk.LEFT, padx=2)
        ttk.Button(process_btn_frame, text="Import",
                  command=self._import_processes).pack(side=tk.LEFT, padx=2)
        ttk.Button(process_btn_frame, text="Export",
                  command=self._export_processes).pack(side=tk.LEFT, padx=2)
        ttk.Button(process_btn_frame, text="Generate Random",
                  command=self._generate_random).pack(side=tk.LEFT, padx=2)
        
        # Simulation buttons
        sim_btn_frame = ttk.LabelFrame(bottom_controls, text="Simulation", padding="5")
        sim_btn_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(sim_btn_frame, text="Run Simulation",
                  command=self._run_simulation).pack(side=tk.LEFT, padx=2)
        ttk.Button(sim_btn_frame, text="Download Report",
                  command=self._download_report).pack(side=tk.LEFT, padx=2)
    
    def _setup_process_list(self):
        # Create process list with scrollbar
        list_frame = ttk.Frame(self.process_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("pid", "arrival", "burst", "priority", "start", "completion", "waiting", "turnaround")
        self.process_tree = ttk.Treeview(list_frame, columns=columns,
                                       show="headings", selectmode="extended",
                                       yscrollcommand=scrollbar.set)
        
        # Configure columns
        headers = {
            "pid": "Process ID",
            "arrival": "Arrival Time",
            "burst": "Burst Time",
            "priority": "Priority",
            "start": "Start Time",
            "completion": "Completion Time",
            "waiting": "Waiting Time",
            "turnaround": "Turnaround Time"
        }
        
        for col, header in headers.items():
            self.process_tree.heading(col, text=header)
            self.process_tree.column(col, width=100)
        
        self.process_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.process_tree.yview)
        
        # Buttons
        btn_frame = ttk.Frame(self.process_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Remove Selected",
                  command=self._remove_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear All",
                  command=self._clear_all).pack(side=tk.LEFT, padx=5)
    
    def _setup_visualization(self):
        self.gantt_chart = GanttChart(self.viz_frame)
    
    def _setup_metrics(self):
        self.metrics_text = tk.Text(self.metrics_frame, height=5, width=50)
        self.metrics_text.pack(fill=tk.X, padx=5, pady=5)
    
    def _show_process_form(self):
        ProcessForm(self.master, self._add_process)
    
    def _add_process(self, process):
        process.pid = self.next_pid
        self.next_pid += 1
        self.processes.append(process)
        self._update_process_tree()
    
    def _update_process_tree(self):
        # Clear existing items
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        # Add all processes
        for process in sorted(self.processes, key=lambda p: p.pid):
            values = [
                process.pid,
                process.arrival_time,
                process.burst_time,
                process.priority,
                process.start_time if process.start_time is not None else '',
                process.completion_time if process.completion_time is not None else '',
                process.waiting_time if process.waiting_time is not None else '',
                process.turnaround_time if process.completion_time is not None else ''
            ]
            self.process_tree.insert("", tk.END, values=values)
            
    def _remove_selected(self):
        selected = self.process_tree.selection()
        if not selected:
            return
        
        # Remove from processes list and update tree
        for item in selected:
            pid = int(self.process_tree.item(item)["values"][0])
            self.processes = [p for p in self.processes if p.pid != pid]
        
        self._update_process_tree()
    
    def _clear_all(self):
        self.processes = []
        self.next_pid = 1
        self._update_process_tree()
    
    def _run_simulation(self):
        if not self.processes:
            messagebox.showwarning("Warning", "Please add some processes first!")
            return
        
        # Create a deep copy of processes to preserve original state
        simulation_processes = copy.deepcopy(self.processes)
        
        # Reset process states
        for process in simulation_processes:
            process.start_time = None
            process.completion_time = None
            process.waiting_time = 0
            process.remaining_time = process.burst_time
        
        # Create appropriate scheduler based on selection
        algorithm = self.algorithm.get()
        if algorithm == "FCFS":
            self.scheduler = FCFSScheduler()
        elif algorithm == "SJF":
            self.scheduler = SJFScheduler()
        elif algorithm == "Round Robin":
            try:
                quantum = int(self.time_quantum.get())
                if quantum < 1:
                    raise ValueError("Time quantum must be positive")
                self.scheduler = RoundRobinScheduler(time_quantum=quantum)
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
        elif algorithm == "Priority":
            self.scheduler = PriorityScheduler()
        
        # Run scheduling algorithm
        self.scheduler.processes = simulation_processes
        self.current_timeline = self.scheduler.schedule()
        
        # Update visualization
        self.gantt_chart.update(self.current_timeline)
        
        # Calculate and display metrics
        self.metrics = PerformanceMetrics(simulation_processes, self.current_timeline)
        metrics_data = self.metrics.get_all_metrics()
        
        # Update metrics display
        self.metrics_text.delete(1.0, tk.END)
        for metric, value in metrics_data.items():
            self.metrics_text.insert(tk.END, f"{metric}: {value}\n")
        
        # Store simulation results and update process tree
        self.processes = simulation_processes
        self._update_process_tree()
    
    def _download_report(self):
        if not hasattr(self, 'current_timeline') or not self.current_timeline:
            messagebox.showwarning("Warning", "Please run a simulation first!")
            return
        
        try:
            metrics_text = self.metrics_text.get(1.0, tk.END)
            filename = self.pdf_generator.generate_report(
                algorithm=self.algorithm.get(),
                processes=self.processes,
                timeline=self.current_timeline,
                gantt_chart=self.gantt_chart,
                metrics=metrics_text
            )
            
            messagebox.showinfo("Success", 
                              f"Report saved successfully!\nLocation: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def _import_processes(self):
        file_types = [
            ('JSON files', '*.json'),
            ('CSV files', '*.csv'),
            ('All files', '*.*')
        ]
        filename = filedialog.askopenfilename(
            title="Import Processes",
            filetypes=file_types
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    processes = ProcessIO.import_from_json(filename)
                else:
                    processes = ProcessIO.import_from_csv(filename)
                
                self.processes.extend(processes)
                self._update_process_tree()
                messagebox.showinfo("Success", "Processes imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import processes: {str(e)}")
    
    def _export_processes(self):
        if not self.processes:
            messagebox.showwarning("Warning", "No processes to export!")
            return
        
        file_types = [
            ('JSON files', '*.json'),
            ('CSV files', '*.csv'),
            ('All files', '*.*')
        ]
        filename = filedialog.asksaveasfilename(
            title="Export Processes",
            filetypes=file_types,
            defaultextension=".json"
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    ProcessIO.export_to_json(self.processes, filename)
                else:
                    ProcessIO.export_to_csv(self.processes, filename)
                messagebox.showinfo("Success", "Processes exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export processes: {str(e)}")
    
    def _generate_random(self):
        try:
            count = simpledialog.askinteger("Random Processes",
                                          "Enter number of processes to generate:",
                                          initialvalue=5,
                                          minvalue=1,
                                          maxvalue=20)
            if count:
                new_processes = ProcessIO.generate_random_processes(count)
                self.processes.extend(new_processes)
                self._update_process_tree()
                messagebox.showinfo("Success", f"Generated {count} random processes!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate processes: {str(e)}")
    
    def _toggle_theme(self):
        self.theme_manager.toggle_theme()
        
    def _apply_theme(self, theme):
        style = ttk.Style()
        
        # Configure ttk styles
        style.configure(".", background=theme['bg'], foreground=theme['fg'])
        
        # Frame styles
        style.configure("TFrame", background=theme['frame_bg'])
        style.configure("TLabelframe", background=theme['frame_bg'])
        style.configure("TLabelframe.Label", 
                       background=theme['frame_bg'],
                       foreground=theme['fg'])
        
        # Label styles
        style.configure("TLabel", 
                       background=theme['label_bg'],
                       foreground=theme['label_fg'])
        
        # Button styles
        style.configure("TButton", 
                       background=theme['button_bg'],
                       foreground=theme['fg'])
        style.map("TButton",
                 background=[("active", theme['button_active']),
                           ("pressed", theme['button_pressed'])],
                 foreground=[("active", theme['fg']),
                           ("pressed", theme['fg'])])
        
        # Treeview styles
        style.configure("Treeview",
                       background=theme['bg'],
                       fieldbackground=theme['bg'],
                       foreground=theme['fg'])
        style.map("Treeview",
                 background=[("selected", theme['selection_bg'])],
                 foreground=[("selected", theme['selection_fg'])])
        
        # Entry styles - always white bg with black text for readability
        style.configure("TEntry",
                       fieldbackground='#ffffff',
                       foreground='#000000')
        style.map("TEntry",
                 fieldbackground=[("readonly", '#ffffff')],
                 foreground=[("readonly", '#000000')])
        
        # Combobox styles - white bg with black text for input area
        style.configure("TCombobox",
                       fieldbackground='#ffffff',
                       foreground='#000000',
                       selectbackground=theme['selection_bg'],
                       selectforeground=theme['selection_fg'],
                       background=theme['button_bg'])  # Arrow button background
        style.map("TCombobox",
                 fieldbackground=[("readonly", '#ffffff')],
                 foreground=[("readonly", '#000000')],
                 selectbackground=[("readonly", theme['selection_bg'])],
                 selectforeground=[("readonly", theme['selection_fg'])])
        
        # Configure dropdown menu style
        self.master.option_add('*TCombobox*Listbox.background', '#ffffff')
        self.master.option_add('*TCombobox*Listbox.foreground', '#000000')
        self.master.option_add('*TCombobox*Listbox.selectBackground', theme['selection_bg'])
        self.master.option_add('*TCombobox*Listbox.selectForeground', theme['selection_fg'])
        
        # Scale style
        style.configure("TScale",
                       background=theme['scale_bg'],
                       troughcolor=theme['scale_trough'])
        
        # Configure text widgets
        self.metrics_text.configure(
            bg='#ffffff',
            fg='#000000',
            insertbackground='#000000',
            selectbackground=theme['selection_bg'],
            selectforeground=theme['selection_fg']
        )
        
        # Update main window and container backgrounds
        self.configure(style='TFrame')
        self.main_container.configure(style='TFrame')
        self.master.configure(bg=theme['bg'])
        
        # Update all frames recursively
        def update_widget_styles(widget):
            if isinstance(widget, ttk.Frame):
                widget.configure(style='TFrame')
            elif isinstance(widget, ttk.Label):
                widget.configure(style='TLabel')
            
            for child in widget.winfo_children():
                update_widget_styles(child)
        
        update_widget_styles(self.main_container)
        
        # Update Gantt chart colors
        if hasattr(self, 'gantt_chart'):
            self.gantt_chart.figure.set_facecolor(theme['bg'])
            self.gantt_chart.ax.set_facecolor(theme['gantt_bg'])
            self.gantt_chart.ax.tick_params(colors=theme['fg'])
            self.gantt_chart.ax.grid(True, color=theme['gantt_grid'], alpha=0.3)
            
            for spine in self.gantt_chart.ax.spines.values():
                spine.set_color(theme['fg'])
                
            self.gantt_chart.ax.title.set_color(theme['fg'])
            self.gantt_chart.ax.xaxis.label.set_color(theme['fg'])
            self.gantt_chart.ax.yaxis.label.set_color(theme['fg'])
            
            if hasattr(self.gantt_chart, 'toolbar'):
                self.gantt_chart.toolbar.config(background=theme['frame_bg'])
                for button in self.gantt_chart.toolbar.winfo_children():
                    if isinstance(button, (tk.Button, ttk.Button)):
                        button.configure(background=theme['button_bg'],
                                      foreground=theme['fg'])
            
            self.gantt_chart.canvas.draw()
