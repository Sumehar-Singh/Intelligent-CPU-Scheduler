import tkinter as tk
from tkinter import ttk, Canvas
import time
import copy
import random
from threading import Thread

class SchedulerAnimationWindow:
    def __init__(self, parent, processes, algorithm, time_quantum=None):
        """Initialize the animation window with process data and selected algorithm"""
        self.top = tk.Toplevel(parent)
        self.top.title(f"CPU Scheduler Animation - {algorithm}")
        self.top.geometry("900x600")
        self.top.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Store scheduling parameters
        self.processes = copy.deepcopy(processes)  # Deep copy to prevent modifying original
        self.algorithm = algorithm
        self.time_quantum = time_quantum
        
        # Animation state variables
        self.current_time = 0
        self.animation_speed = 1.0  # seconds per time unit
        self.is_running = False
        self.animation_thread = None
        self.update_counter = 0  # Counter for visual updates
        
        # Add context switch counter
        self.context_switches = 0
        self.last_process_id = None
        
        # Process tracking
        self.incoming = []  # Processes not yet arrived
        self.ready_queue = []  # Processes in ready queue
        self.current_process = None  # Currently executing process
        self.completed = []  # Completed processes
        self.remaining_time = {}  # Track remaining burst time for each process
        
        # Initialize process colors with distinct colors for each process
        self.process_colors = {}
        
        # Initialize the process lists - all processes start in incoming section
        for proc in self.processes:
            pid = proc["PID"]
            self.incoming.append(proc)
            self.remaining_time[pid] = proc["Burst"]
            
            # Assign a unique color to each process
            # Generate distinct colors for each process
            r = random.randint(100, 240)
            g = random.randint(100, 240)
            b = random.randint(100, 240)
            self.process_colors[pid] = f'#{r:02x}{g:02x}{b:02x}'
        
        # Sort incoming processes by arrival time
        self.incoming.sort(key=lambda p: p["Arrival"])
        
        # Create UI components
        self._create_ui()
        
        # Initialize visualization without starting animation
        self._update_visualization()