import tkinter as tk
from tkinter import ttk
from src.ui.main_window import MainWindow

def main():
    root = tk.Tk()
    root.title("CPU Scheduler Simulator")
    root.geometry("1000x800")  # Set initial window size
    app = MainWindow(root)
    app.pack(fill=tk.BOTH, expand=True)  # Pack the main window
    root.mainloop()

if __name__ == "__main__":
    main()
