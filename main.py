import tkinter as tk
import pandas as pd
from tkinter import ttk
from process_manager import ProcessManager

class CPUSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduler Simulator")
        self.root.geometry("1250x650")

        # ---------------- Main Layout ----------------
        frame_left = tk.Frame(root, padx=3, pady=12, relief=tk.RIDGE, width=360, height=630)  
        frame_left.grid(row=0, column=0, sticky="nsw")
        frame_left.grid_propagate(False)

        frame_right = tk.Frame(root, padx=20, pady=20, relief=tk.RIDGE)
        frame_right.grid(row=0, column=1, sticky="nsew")

        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)

        # ---------------- Left Panel: Process Input Section ----------------
        input_frame = tk.LabelFrame(frame_left, text="Process Input", padx=10, pady=10)
        input_frame.grid(row=0, column=0, sticky="ew", pady=10, padx=(10, 27))

        tk.Label(input_frame, text="Process ID:").grid(row=0, column=0, sticky="w", pady=6)
        self.pid_entry = tk.Entry(input_frame, width=18)
        self.pid_entry.grid(row=0, column=1, pady=5, padx=6)

        tk.Label(input_frame, text="Arrival Time:").grid(row=1, column=0, sticky="w", pady=6)
        self.arrival_entry = tk.Entry(input_frame, width=18)
        self.arrival_entry.grid(row=1, column=1, pady=5, padx=6)

        tk.Label(input_frame, text="Burst Time:").grid(row=2, column=0, sticky="w", pady=6)
        self.burst_entry = tk.Entry(input_frame, width=18)
        self.burst_entry.grid(row=2, column=1, pady=5, padx=6)

        # Priority Input Field (Initially Disabled)
        tk.Label(input_frame, text="Priority:").grid(row=3, column=0, sticky="w", pady=6)
        self.priority_entry = tk.Entry(input_frame, width=18, state=tk.DISABLED)  # Initially Disabled
        self.priority_entry.grid(row=3, column=1, pady=5, padx=6)

        self.add_button = tk.Button(input_frame, text="Add Process", command=self.add_process,
                                    bg="#28a745", fg="white", relief=tk.RAISED)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=8, sticky="ew", padx=110)

        # ---------------- Left Panel: Process List Section ----------------
        list_frame = tk.Frame(frame_left, padx=0, pady=5)
        list_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=10)

        list_scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        list_scrollbar.grid(row=0, column=1, sticky="ns")

        self.process_tree = ttk.Treeview(
            list_frame, columns=("PID", "Arrival", "Burst", "Priority"),
            show="headings", height=10, yscrollcommand=list_scrollbar.set
        )

        # Configure Column Headers
        self.process_tree.heading("PID", text="PID", anchor="center")
        self.process_tree.heading("Arrival", text="Arrival", anchor="center")
        self.process_tree.heading("Burst", text="Burst", anchor="center")
        self.process_tree.heading("Priority", text="Priority", anchor="center")

        # Configure Column Widths
        self.process_tree.column("PID", width=80, anchor="center")
        self.process_tree.column("Arrival", width=80, anchor="center")
        self.process_tree.column("Burst", width=80, anchor="center")
        self.process_tree.column("Priority", width=80, anchor="center")

        self.process_tree.grid(row=0, column=0, sticky="nsew")
        list_scrollbar.config(command=self.process_tree.yview)

        # Delete Button
        self.delete_button = tk.Button(frame_left, text="Delete Selected Process", command=self.delete_selected_process,
                                       bg="#dc3545", fg="white", relief=tk.RAISED)
        self.delete_button.grid(row=2, column=0, sticky="w", pady=5, padx=100)

        # ---------------- Left Panel: Algorithm Selection ----------------
        algo_frame = tk.LabelFrame(frame_left, text="Algorithm Selection", padx=10, pady=10)
        algo_frame.grid(row=3, column=0, sticky="ew", pady=10, padx=(10, 27))

        self.algo_var = tk.StringVar(value="FCFS")
        tk.Label(algo_frame, text="Algorithm:").grid(row=0, column=0, pady=5, sticky="w")

        self.algo_dropdown = ttk.Combobox(algo_frame, textvariable=self.algo_var, 
                                        values=("FCFS", "SJF", "SRTF","Round Robin", "Priority(Non-Preemptive)","Priority(Preemptive)"))
        self.algo_dropdown.grid(row=0, column=1, padx=10, pady=5)

        # Bind Algorithm Selection to Function
        self.algo_var.trace_add("write", self.on_algorithm_change)

        # ---------------- Left Panel: Simulation Controls ----------------
        button_frame = tk.LabelFrame(frame_left, text="Controls", padx=10, pady=10)
        button_frame.grid(row=4, column=0, sticky="ew", pady=10, padx=(10, 27))

        # Time Quantum Entry
        tk.Label(button_frame, text="Time Quantum:").grid(row=0, column=0, pady=10, sticky="ew")
        self.time_quantum_entry = tk.Entry(button_frame, state=tk.DISABLED)  # Initially Disabled
        self.time_quantum_entry.grid(row=0, column=1, padx=10, pady=5)

        self.run_button = tk.Button(button_frame, text="Run Simulation",
                                    bg="#007bff", fg="white", relief=tk.RAISED)
        self.run_button.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew", padx=100)

        self.reset_button = tk.Button(button_frame, text="Reset", command=self.reset_all,
                                      bg="#dc3545", fg="white", relief=tk.RAISED)
        self.reset_button.grid(row=2, column=0, columnspan=2, pady=6, sticky="ew", padx=100)

        # ---------------- Scheduling Table (TreeView) ----------------
        self.schedule_tree_frame = tk.Frame(frame_right)  # Create a frame for the Treeview and Scrollbar

        # Create a scrollbar for the scheduling table
        self.tree_scroll_y = tk.Scrollbar(self.schedule_tree_frame, orient="vertical")

        # Create the Treeview (Scheduling Table)
        self.schedule_tree = ttk.Treeview(self.schedule_tree_frame, columns=(
            "PID", "Arrival", "Burst", "Priority", "Completion", "Turnaround", "Waiting", "Response"),
            show="headings", height=6, yscrollcommand=self.tree_scroll_y.set)

        # Define column headings
        columns = ["PID", "Arrival", "Burst", "Priority", "Completion", "Turnaround", "Waiting", "Response"]
        for col in columns:
            self.schedule_tree.heading(col, text=col, anchor="center")
            self.schedule_tree.column(col, width=137, anchor="center")

        # Grid placement
        self.schedule_tree.grid(row=0, column=0, sticky="nsew")

        # Configure vertical scrollbar
        self.tree_scroll_y.config(command=self.schedule_tree.yview)
        self.tree_scroll_y.grid(row=0, column=1, sticky="ns")

        # Pack the scheduling table frame
        self.schedule_tree_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # ---------------- Gantt Chart Frame ----------------
        self.canvas_frame = tk.Frame(frame_right, height=160, width=520, bg="white", relief="solid")
        self.canvas_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # ---------------- Statistics Chart Frame ----------------
        self.stats_frame = tk.Frame(frame_right, height=160, width=500, bg="white", relief="solid")
        self.stats_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Ensure right panel layout is balanced
        frame_right.grid_rowconfigure(1, weight=1)
        frame_right.grid_rowconfigure(2, weight=1)
        frame_right.grid_columnconfigure(0, weight=1)


        # Process Manager Instance
        self.process_manager = ProcessManager(self.process_tree)

    # ---------------- Event Handlers ----------------

    def on_algorithm_change(self, *args):
        """Enable/Disable Time Quantum and Priority Input based on Algorithm Selection"""

        # Handle Time Quantum Entry for Round Robin
        if self.algo_var.get() == "Round Robin":
            self.time_quantum_entry.config(state=tk.NORMAL)
        else:
            self.time_quantum_entry.config(state=tk.DISABLED)

        # Handle Priority Input for Priority Scheduling
        if self.algo_var.get() in ["Priority(Non-Preemptive)", "Priority(Preemptive)"]:
            self.priority_entry.config(state=tk.NORMAL)  # Enable Priority field
        else:
            self.priority_entry.config(state=tk.DISABLED)  # Disable Priority field

    def get_time_quantum(self):
        """Retrieve time quantum value safely from the input box"""
        try:
            return int(self.time_quantum_entry.get())
        except ValueError:
            return -1  # Return -1 if invalid input

    def add_process(self):
        """Add a process to the process list and display it in the table"""
        pid = self.pid_entry.get()
        arrival_time = self.arrival_entry.get()
        burst_time = self.burst_entry.get()

        # Get priority input if applicable
        if self.algo_var.get() in ["Priority(Non-Preemptive)", "Priority(Preemptive)"]:
            priority = self.priority_entry.get()
        else:
            priority = "-"  # Default value for non-priority algorithms

        # Validate the input fields
        if not pid or not arrival_time or not burst_time:
            print("Please enter all required fields!")
            return

        try:
            pid = int(pid)
            arrival_time = int(arrival_time)
            burst_time = int(burst_time)
            if self.algo_var.get() in ["Priority(Non-Preemptive)", "Priority(Preemptive)"]:
                priority = int(priority)
                if priority < 0:  # Prevent negative priority
                    print("Error: Priority cannot be negative!")
                    return
            else:
                priority = "-"  # Keep as '-' if not Priority Scheduling
        except ValueError:
            print("Please enter valid integers!")
            return

        # Add process to ProcessManager (removing duplicate insertion)
        success = self.process_manager.add_process(pid, arrival_time, burst_time, priority)

        # No need to insert again into TreeView; it's handled in ProcessManager

        # Clear input fields after adding a process
        if success:
            self.pid_entry.delete(0, tk.END)
            self.arrival_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)
            if self.algo_var.get() in ["Priority(Non-Preemptive)", "Priority(Preemptive)"]:
                self.priority_entry.delete(0, tk.END)

    def delete_selected_process(self):
            selected_item = self.process_tree.selection()
            if not selected_item:
                print("No process selected!")
                return  

            for item in selected_item:
                values = self.process_tree.item(item, "values")
                if values:
                    pid = values[0]  
                    try:
                        self.process_manager.remove_process(int(pid))  
                        self.process_tree.delete(item)  
                        print(f"Deleted process {pid}")  
                    except ValueError:
                        print(f"Invalid PID {pid}, cannot delete")

    def reset_all(self):
        self.process_manager.processes.clear()
        self.process_tree.delete(*self.process_tree.get_children())
        self.schedule_tree.delete(*self.schedule_tree.get_children())
        for widget in self.canvas_frame.winfo_children() + self.stats_frame.winfo_children():
            widget.destroy()
            
if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSchedulerApp(root)
    root.mainloop()