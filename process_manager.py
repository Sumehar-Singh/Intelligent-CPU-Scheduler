from tkinter import ttk

class ProcessManager:
    def __init__(self, treeview):
        self.processes = []
        self.treeview = treeview

    def add_process(self, pid, arrival, burst, priority="-"):
        """Add a process to the internal list and display it in the TreeView."""
        # Check for duplicate PIDs
        if any(process["PID"] == pid for process in self.processes):
            print(f"Error: Process with PID {pid} already exists!")
            return False
        process = {"PID": pid, "Arrival": arrival, "Burst": burst, "Priority": priority}
        self.processes.append(process)

        # Insert into TreeView
        self.treeview.insert("", "end", values=(pid, arrival, burst, priority))
        return True
