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

    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV color values to RGB"""
        if s == 0.0: 
            return v, v, v
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i %= 6
        if i == 0: return v, t, p
        if i == 1: return q, v, p
        if i == 2: return p, v, t
        if i == 3: return p, q, v
        if i == 4: return t, p, v
        if i == 5: return v, p, q

    def _create_ui(self):
        """Create all UI elements for the animation"""
        # Main frame
        main_frame = tk.Frame(self.top, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top info bar
        info_frame = tk.Frame(main_frame, bg="#f8f9fa", padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Time display
        time_label = tk.Label(info_frame, text="Time:", font=("Arial", 12, "bold"))
        time_label.pack(side=tk.LEFT, padx=(0, 5))
        self.time_var = tk.StringVar(value="0")
        time_display = tk.Label(info_frame, textvariable=self.time_var, 
                              font=("Arial", 12, "bold"), width=5, relief=tk.SUNKEN, bg="white")
        time_display.pack(side=tk.LEFT, padx=(0, 20))
        
        # Algorithm info
        algo_text = f"Algorithm: {self.algorithm}"
        if self.algorithm == "Round Robin":
            algo_text += f" (Time Quantum: {self.time_quantum})"
        tk.Label(info_frame, text=algo_text, font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        # Process sections
        self.sections_frame = tk.Frame(main_frame)
        self.sections_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the four main sections
        section_height = 120
        
        # Incoming processes section
        incoming_frame = tk.LabelFrame(self.sections_frame, text="Incoming Processes", padx=10, pady=10)
        incoming_frame.pack(fill=tk.X, pady=(0, 15))
        self.incoming_canvas = Canvas(incoming_frame, height=section_height, bg="#f0f0f0")
        self.incoming_canvas.pack(fill=tk.X)
        
        # Ready queue section
        ready_frame = tk.LabelFrame(self.sections_frame, text="Ready Queue", padx=10, pady=10)
        ready_frame.pack(fill=tk.X, pady=(0, 15))
        self.ready_canvas = Canvas(ready_frame, height=section_height, bg="#e6f7ff")
        self.ready_canvas.pack(fill=tk.X)
        
        # CPU section
        cpu_frame = tk.LabelFrame(self.sections_frame, text="CPU Execution", padx=10, pady=10)
        cpu_frame.pack(fill=tk.X, pady=(0, 15))
        self.cpu_canvas = Canvas(cpu_frame, height=section_height, bg="#e6ffe6")
        self.cpu_canvas.pack(fill=tk.X)
        
        # Completed section
        completed_frame = tk.LabelFrame(self.sections_frame, text="Completed Processes", padx=10, pady=10)
        completed_frame.pack(fill=tk.X)
        self.completed_canvas = Canvas(completed_frame, height=section_height, bg="#f0f0f0")
        self.completed_canvas.pack(fill=tk.X)
        
        # Controls panel
        controls_frame = tk.Frame(main_frame, pady=15)
        controls_frame.pack(fill=tk.X)
        
        # Speed slider
        speed_label = tk.Label(controls_frame, text="Speed:")
        speed_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.speed_scale = ttk.Scale(controls_frame, from_=0.2, to=2.0, 
                                   value=1.0, orient=tk.HORIZONTAL, 
                                   length=200, command=self._update_speed)
        self.speed_scale.pack(side=tk.LEFT)
        
        # Context switch counter
        context_label = tk.Label(controls_frame, text="Context Switches:", font=("Arial", 10, "bold"))
        context_label.pack(side=tk.LEFT, padx=(20, 5))
        
        self.context_var = tk.StringVar(value="0")
        context_display = tk.Label(controls_frame, textvariable=self.context_var, 
                                 font=("Arial", 10, "bold"), width=4, relief=tk.SUNKEN, bg="white")
        context_display.pack(side=tk.LEFT)
        
        # Start/Pause button (Initially "Start" since animation doesn't auto-start)
        self.play_btn = tk.Button(controls_frame, text="Start", 
                                command=self._toggle_playback,
                                width=10, bg="#28a745", fg="white")
        self.play_btn.pack(side=tk.RIGHT, padx=5)
        
        # Reset button
        self.reset_btn = tk.Button(controls_frame, text="Reset", 
                                 command=self.reset_animation,
                                 width=10, bg="#dc3545", fg="white")
        self.reset_btn.pack(side=tk.RIGHT, padx=5)
        
        # Status message
        self.status_var = tk.StringVar(value="Click Start to begin animation")
        status_label = tk.Label(main_frame, textvariable=self.status_var, 
                              anchor=tk.W, justify=tk.LEFT, relief=tk.SUNKEN,
                              padx=10, pady=5)
        status_label.pack(fill=tk.X, pady=(15, 0))

    def _update_speed(self, value):
        """Update animation speed from slider"""
        self.animation_speed = 1.0 / float(value)
    
    def _toggle_playback(self):
        """Start, pause or resume animation"""
        if self.is_running:
            # If running, pause it
            self.is_running = False
            self.play_btn.config(text="Resume", bg="#28a745")
        else:
            # If not running, either start or resume
            self.is_running = True
            self.play_btn.config(text="Pause", bg="#f0ad4e")
            
            # If not already started, start now
            if not self.animation_thread or not self.animation_thread.is_alive():
                self.animation_thread = Thread(target=self._run_animation)
                self.animation_thread.daemon = True
                self.animation_thread.start()
    
    def start_animation(self):
        """Start animation thread"""
        if not self.is_running and (not self.animation_thread or not self.animation_thread.is_alive()):
            self.is_running = True
            self.play_btn.config(text="Pause", bg="#f0ad4e")
            self.animation_thread = Thread(target=self._run_animation)
            self.animation_thread.daemon = True
            self.animation_thread.start()
    
    def _run_animation(self):
        """Main animation loop"""
        while True:
            # Check if animation should still be running
            if not self.is_running:
                time.sleep(0.1)  # Small delay when paused
                continue
            
            # 1. Check for newly arrived processes at the current time
            newly_arrived = []
            for proc in list(self.incoming):
                if proc["Arrival"] <= self.current_time:
                    self.incoming.remove(proc)
                    self.ready_queue.append(proc)
                    newly_arrived.append(proc)
            
            if newly_arrived:
                pids = [f"P{p['PID']}" for p in newly_arrived]
                self.status_var.set(f"Time {self.current_time}: {', '.join(pids)} arrived")
                self._update_visualization()
                time.sleep(self.animation_speed * 0.5)  # Brief pause to show arrival
            
            # 2. Check for process completion at this time point
            completion_occurred = False
            if self.current_process:
                pid = self.current_process["PID"]
                # Check if process is completing at this exact time
                if self.remaining_time[pid] == 0:
                    self.completed.append(self.current_process)
                    self.status_var.set(f"Time {self.current_time}: P{pid} completed")
                    self.current_process = None
                    self.last_process_id = None  # Reset last process since CPU is now idle
                    completion_occurred = True
                    self._update_visualization()
                    time.sleep(self.animation_speed * 0.5)  # Brief pause to show completion
            
            # 3. Update CPU state based on scheduling algorithm
            cpu_updated = self._update_cpu_state()
            if cpu_updated:
                self._update_visualization()
                time.sleep(self.animation_speed * 0.5)  # Brief pause to show CPU changes
            
            # 4. Check if all processes are completed
            if len(self.completed) == len(self.processes):
                self.status_var.set(f"All processes completed at time {self.current_time}")
                self._update_visualization()
                self.play_btn.config(text="Finished", state=tk.DISABLED)
                self.is_running = False
                break
            
            # 5. Decrement remaining time for the current process
            if self.current_process:
                pid = self.current_process["PID"]
                self.remaining_time[pid] -= 1
                
                # Update visualization to show the remaining time decreasing in real-time
                self._update_cpu_display()
            
            # 6. Increment time
            self.current_time += 1
            self.time_var.set(str(self.current_time))
            
            # 7. If CPU is idle and no events occurred, fast forward to next process arrival
            if not self.current_process and not newly_arrived and not cpu_updated and not completion_occurred and self.incoming:
                next_arrival = min(p["Arrival"] for p in self.incoming)
                if next_arrival > self.current_time:
                    self.status_var.set(f"CPU idle. Fast-forwarding to time {next_arrival}")
                    self.current_time = next_arrival
                    self.time_var.set(str(self.current_time))
                    continue
            
            # 8. Sleep based on speed setting before next time unit
            time.sleep(self.animation_speed)
    
    def _update_cpu_display(self):
        """Update just the CPU display to show decreasing remaining time"""
        if self.current_process:
            pid = self.current_process["PID"]
            x = 30
            y = 20
            
            # Clear just the remaining time area in CPU canvas
            self.cpu_canvas.delete("remaining_time")
            
            # Update the remaining time text
            self.cpu_canvas.create_text(x+50, y+45, 
                                      text=f"Remaining: {self.remaining_time[pid]}",
                                      font=("Arial", 10),
                                      tags="remaining_time")
            
            # Force update
            self.top.update_idletasks()
    
    def _update_cpu_state(self):
        """Update the CPU state based on the selected algorithm"""
        updated = False
        previous_process_id = self.last_process_id
        
        if self.algorithm == "FCFS":
            # First-Come-First-Served
            if not self.current_process and self.ready_queue:
                self.current_process = self.ready_queue.pop(0)
                pid = self.current_process["PID"]
                self.status_var.set(f"Time {self.current_time}: P{pid} started execution")
                
                # Check for context switch
                if self.last_process_id is not None and self.last_process_id != pid:
                    self.context_switches += 1
                    self.context_var.set(str(self.context_switches))
                
                self.last_process_id = pid
                updated = True
        
        elif self.algorithm == "SJF":
            # Shortest Job First (Non-preemptive)
            if not self.current_process and self.ready_queue:
                # Sort by burst time
                self.ready_queue.sort(key=lambda p: p["Burst"])
                self.current_process = self.ready_queue.pop(0)
                pid = self.current_process["PID"]
                self.status_var.set(f"Time {self.current_time}: P{pid} started execution (SJF)")
                
                # Check for context switch
                if self.last_process_id is not None and self.last_process_id != pid:
                    self.context_switches += 1
                    self.context_var.set(str(self.context_switches))
                
                self.last_process_id = pid
                updated = True
        
        elif self.algorithm == "SRTF":
            # Shortest Remaining Time First (Preemptive)
            if self.ready_queue:
                # Check if we need to preempt
                if self.current_process:
                    shortest_process = min(self.ready_queue, key=lambda p: self.remaining_time[p["PID"]])
                    if self.remaining_time[shortest_process["PID"]] < self.remaining_time[self.current_process["PID"]]:
                        # Preemption occurs
                        self.ready_queue.append(self.current_process)
                        self.ready_queue.remove(shortest_process)
                        previous_pid = self.current_process["PID"]
                        self.current_process = shortest_process
                        pid = self.current_process["PID"]
                        self.status_var.set(f"Time {self.current_time}: P{previous_pid} preempted by P{pid}")
                        
                        # Count context switch
                        if previous_pid != pid:
                            self.context_switches += 1
                            self.context_var.set(str(self.context_switches))
                        
                        self.last_process_id = pid
                        updated = True
                else:
                    # CPU is idle, find shortest remaining time
                    shortest_process = min(self.ready_queue, key=lambda p: self.remaining_time[p["PID"]])
                    self.ready_queue.remove(shortest_process)
                    self.current_process = shortest_process
                    pid = self.current_process["PID"]
                    self.status_var.set(f"Time {self.current_time}: P{pid} started execution (SRTF)")
                    
                    # Check for context switch
                    if self.last_process_id is not None and self.last_process_id != pid:
                        self.context_switches += 1
                        self.context_var.set(str(self.context_switches))
                    
                    self.last_process_id = pid
                    updated = True
        
        elif self.algorithm == "Round Robin":
            # Round Robin
            time_slice = getattr(self, "rr_time_slice", 0)
            
            if self.current_process and time_slice >= self.time_quantum:
                # Time quantum expired
                pid = self.current_process["PID"]
                if self.remaining_time[pid] > 0:
                    self.ready_queue.append(self.current_process)
                    self.status_var.set(f"Time {self.current_time}: P{pid} time quantum expired")
                    self.current_process = None
                    self.rr_time_slice = 0
                    updated = True
            
            if not self.current_process and self.ready_queue:
                # Start next process
                self.current_process = self.ready_queue.pop(0)
                pid = self.current_process["PID"]
                self.rr_time_slice = 0
                self.status_var.set(f"Time {self.current_time}: P{pid} started execution (RR)")
                
                # Check for context switch
                if self.last_process_id is not None and self.last_process_id != pid:
                    self.context_switches += 1
                    self.context_var.set(str(self.context_switches))
                
                self.last_process_id = pid
                updated = True
            
            if self.current_process:
                # Increment time slice
                self.rr_time_slice = getattr(self, "rr_time_slice", 0) + 1
        
        elif self.algorithm == "Priority(Non-Preemptive)":
            # Priority (Non-preemptive)
            if not self.current_process and self.ready_queue:
                # Sort by priority (lower number is higher priority)
                self.ready_queue.sort(key=lambda p: p["Priority"])
                self.current_process = self.ready_queue.pop(0)
                pid = self.current_process["PID"]
                self.status_var.set(f"Time {self.current_time}: P{pid} started execution (Priority)")
                
                # Check for context switch
                if self.last_process_id is not None and self.last_process_id != pid:
                    self.context_switches += 1
                    self.context_var.set(str(self.context_switches))
                
                self.last_process_id = pid
                updated = True
        
        elif self.algorithm == "Priority(Preemptive)":
            # Priority (Preemptive)
            if self.ready_queue:
                # Check if we need to preempt
                if self.current_process:
                    self.ready_queue.sort(key=lambda p: p["Priority"])
                    highest_priority = self.ready_queue[0]
                    if highest_priority["Priority"] < self.current_process["Priority"]:
                        # Preemption occurs
                        self.ready_queue.append(self.current_process)
                        self.ready_queue.remove(highest_priority)
                        previous_pid = self.current_process["PID"]
                        self.current_process = highest_priority
                        pid = self.current_process["PID"]
                        self.status_var.set(f"Time {self.current_time}: P{previous_pid} preempted by higher priority P{pid}")
                        
                        # Count context switch
                        if previous_pid != pid:
                            self.context_switches += 1
                            self.context_var.set(str(self.context_switches))
                        
                        self.last_process_id = pid
                        updated = True
                else:
                    # CPU is idle, find highest priority
                    self.ready_queue.sort(key=lambda p: p["Priority"])
                    self.current_process = self.ready_queue.pop(0)
                    pid = self.current_process["PID"]
                    self.status_var.set(f"Time {self.current_time}: P{pid} started execution (Priority)")
                    
                    # Check for context switch
                    if self.last_process_id is not None and self.last_process_id != pid:
                        self.context_switches += 1
                        self.context_var.set(str(self.context_switches))
                    
                    self.last_process_id = pid
                    updated = True
                    
        return updated
    
    def _update_visualization(self):
        """Update the visualization of all processes"""
        # Clear all canvases
        for canvas in [self.incoming_canvas, self.ready_canvas, self.cpu_canvas, self.completed_canvas]:
            canvas.delete("all")
        
        # Draw incoming processes
        self._draw_processes(self.incoming_canvas, self.incoming)
        
        # Draw ready queue processes
        self._draw_processes(self.ready_canvas, self.ready_queue)
        
        # Draw CPU process
        if self.current_process:
            pid = self.current_process["PID"]
            x = 30
            y = 20
            
            # Draw process box
            self.cpu_canvas.create_rectangle(x, y, x+100, y+80, 
                                           fill=self.process_colors[pid], outline="black", width=2)
            
            # Draw process ID
            self.cpu_canvas.create_text(x+50, y+25, text=f"P{pid}", 
                                      font=("Arial", 14, "bold"))
            
            # Draw remaining time (with tag for updating)
            self.cpu_canvas.create_text(x+50, y+45, text=f"Remaining: {self.remaining_time[pid]}",
                                      font=("Arial", 10), tags="remaining_time")
            
            # Draw burst time
            self.cpu_canvas.create_text(x+50, y+65, text=f"Burst: {self.current_process['Burst']}",
                                      font=("Arial", 10))
            
            # Add CPU busy indicator
            self.cpu_canvas.create_oval(x+130, y+30, x+150, y+50, 
                                      fill="#FF5252")
            self.cpu_canvas.create_text(x+210, y+40, 
                                      text="CPU BUSY", 
                                      font=("Arial", 10, "bold"), fill="#FF5252")
            
        else:
            # CPU is idle
            self.cpu_canvas.create_text(150, 60, text="CPU IDLE", 
                                      font=("Arial", 18, "bold"), fill="gray")
        
        # Draw completed processes
        self._draw_processes(self.completed_canvas, self.completed)
        
        # Force update
        self.top.update_idletasks()
    
    def _draw_processes(self, canvas, process_list):
        """Draw a list of processes on the given canvas"""
        if not process_list:
            canvas.create_text(150, 60, text="No Processes", 
                             font=("Arial", 12), fill="gray")
            return
            
        # Draw processes horizontally with spacing
        x_spacing = 110
        x = 10
        y = 20
        max_width = canvas.winfo_width() - x_spacing
        
        for process in process_list:
            pid = process["PID"]
            
            # Check if we need to wrap to next row
            if max_width > 0 and x > max_width:  # Ensure canvas has been drawn
                x = 10
                y += 85
            
            # Draw process box with its unique color
            canvas.create_rectangle(x, y, x+100, y+80, fill=self.process_colors[pid], outline="black")
            
            # Draw process ID
            canvas.create_text(x+50, y+20, text=f"P{pid}", font=("Arial", 14, "bold"))
            
            # Draw process info based on where it is
            if canvas == self.incoming_canvas:
                canvas.create_text(x+50, y+40, text=f"Arrival: {process['Arrival']}", font=("Arial", 10))
                canvas.create_text(x+50, y+60, text=f"Burst: {process['Burst']}", font=("Arial", 10))
            elif canvas == self.ready_canvas:
                canvas.create_text(x+50, y+40, text=f"Remaining: {self.remaining_time[pid]}", font=("Arial", 10))
                if "Priority" in process and process["Priority"] != "-":
                    canvas.create_text(x+50, y+60, text=f"Priority: {process['Priority']}", font=("Arial", 10))
                else:
                    canvas.create_text(x+50, y+60, text=f"Burst: {process['Burst']}", font=("Arial", 10))
            elif canvas == self.completed_canvas:
                canvas.create_text(x+50, y+40, text="Completed", font=("Arial", 10, "bold"))
                canvas.create_text(x+50, y+60, text=f"Burst: {process['Burst']}", font=("Arial", 10))
            
            # Move to next position
            x += x_spacing
    
    def reset_animation(self):
        """Reset the animation to initial state"""
        # Stop current animation
        self.is_running = False
        if self.animation_thread and self.animation_thread.is_alive():
            self.animation_thread.join(timeout=0.1)
        
        # Reset state variables
        self.current_time = 0
        self.incoming = []
        self.ready_queue = []
        self.current_process = None
        self.completed = []
        
        # Reset context switches
        self.context_switches = 0
        self.context_var.set("0")
        self.last_process_id = None
        
        # Reset remaining times
        for proc in self.processes:
            pid = proc["PID"]
            self.incoming.append(proc)
            self.remaining_time[pid] = proc["Burst"]
        
        # Sort incoming processes by arrival time
        self.incoming.sort(key=lambda p: p["Arrival"])
        
        # Update UI
        self.time_var.set("0")
        self.status_var.set("Animation reset. Click Start to begin.")
        self.play_btn.config(text="Start", bg="#28a745", state=tk.NORMAL)
        self._update_visualization()

    def on_closing(self):
        """Handle window closing"""
        self.is_running = False
        if self.animation_thread and self.animation_thread.is_alive():
            self.animation_thread.join(timeout=0.1)
        self.top.destroy()
