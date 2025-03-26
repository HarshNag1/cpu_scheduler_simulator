import tkinter as tk
from tkinter import ttk, messagebox
from ..core.process import Process

class ProcessForm(tk.Toplevel):
    def __init__(self, master, callback):
        super().__init__(master)
        self.title("Add New Process")
        self.callback = callback
        
        # Configure window
        self.geometry("300x250")
        self.configure(bg="#2b2b2b")
        self.resizable(False, False)
        
        # Process ID (auto-generated)
        self.pid = 1
        
        # Create main frame
        main_frame = ttk.Frame(self, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form fields
        # Arrival Time
        ttk.Label(main_frame, text="Arrival Time:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.arrival_time = ttk.Entry(main_frame, width=15)
        self.arrival_time.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(main_frame, text="(0-100)").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        
        # Burst Time
        ttk.Label(main_frame, text="Burst Time:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.burst_time = ttk.Entry(main_frame, width=15)
        self.burst_time.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(main_frame, text="(1-100)").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        
        # Priority
        ttk.Label(main_frame, text="Priority:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.priority = ttk.Entry(main_frame, width=15)
        self.priority.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(main_frame, text="(0-10)").grid(row=2, column=2, padx=5, pady=5, sticky='w')
        self.priority.insert(0, "0")
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        ttk.Button(btn_frame, text="Add", command=self._on_submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
        # Center window
        self.transient(master)
        self.grab_set()
        
    def _validate_inputs(self):
        """Validate process input values"""
        try:
            arrival_time = int(self.arrival_time.get())
            burst_time = int(self.burst_time.get())
            priority = int(self.priority.get())
            
            if arrival_time < 0:
                raise ValueError("Arrival time must be non-negative")
            if burst_time <= 0:
                raise ValueError("Burst time must be positive")
            if priority < 0:
                raise ValueError("Priority must be non-negative")
                
            return True
        except ValueError as e:
            if str(e).startswith("invalid literal"):
                messagebox.showerror("Error", "Please enter valid numbers")
            else:
                messagebox.showerror("Error", str(e))
            return False
        
    def _on_submit(self):
        if not self._validate_inputs():
            return
            
        try:
            process = Process(
                pid=self.pid,
                arrival_time=int(self.arrival_time.get()),
                burst_time=int(self.burst_time.get()),
                priority=int(self.priority.get())
            )
            self.callback(process)
            self.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
