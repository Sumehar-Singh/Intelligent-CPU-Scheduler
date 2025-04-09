import pandas as pd
import numpy as np

def srtf_scheduling(processes):
    """Shortest Remaining Time First (SRTF) Scheduling Algorithm"""
    if not processes:
        return pd.DataFrame(columns=["PID", "Arrival", "Burst", "Priority", "Completion", "Turnaround", "Waiting", "Response"]), []
    
    # Convert list of dictionaries to list of tuples (PID, Arrival, Burst)
    processes = [(p["PID"], p["Arrival"], p["Burst"]) for p in processes]
    
    # Sort by arrival time
    processes.sort(key=lambda x: x[1])
    
    n = len(processes)
    completion_time = {}
    waiting_time = {}
    turnaround_time = {}
    first_response = {p[0]: -1 for p in processes}  # Track first response time
    
    remaining_burst = {p[0]: p[2] for p in processes}  # Track remaining burst time
    
    current_time = 0
    completed = 0
    gantt_chart = []
    last_process = None
    
    # Run until all processes are completed
    while completed < n:
        # Find process with minimum remaining burst time
        min_burst = float('inf')
        min_pid = None
        
        # Check all arrived processes
        for p in processes:
            pid, arrival, _ = p
            if arrival <= current_time and remaining_burst[pid] > 0 and remaining_burst[pid] < min_burst:
                min_burst = remaining_burst[pid]
                min_pid = pid
        
        if min_pid is None:
            # No process available, jump to next arrival time
            next_arrival = min([p[1] for p in processes if p[1] > current_time], default=current_time)
            if last_process is not None:
                gantt_chart.append((gantt_start, current_time, last_process))
                last_process = None
            current_time = next_arrival
            continue
        
        # If process changes or just starting, record gantt entry
        if last_process != min_pid:
            if last_process is not None:
                gantt_chart.append((gantt_start, current_time, last_process))
            gantt_start = current_time
            last_process = min_pid
            
            # Record first response time if not already set
            if first_response[min_pid] == -1:
                first_response[min_pid] = current_time
        
        # Execute for 1 time unit
        current_time += 1
        remaining_burst[min_pid] -= 1
        
        # Check if process is completed
        if remaining_burst[min_pid] == 0:
            completed += 1
            completion_time[min_pid] = current_time
            
            # Add the final gantt entry for this process
            gantt_chart.append((gantt_start, current_time, min_pid))
            last_process = None
            
            # Calculate turnaround and waiting time
            arrival_time = next(p[1] for p in processes if p[0] == min_pid)
            burst_time = next(p[2] for p in processes if p[0] == min_pid)
            
            turnaround_time[min_pid] = completion_time[min_pid] - arrival_time
            waiting_time[min_pid] = turnaround_time[min_pid] - burst_time
    
    # Prepare the result in a DataFrame
    result = []
    for p in processes:
        pid, arrival, burst = p
        result.append([
            pid, 
            arrival, 
            burst, 
            "-",  # Priority column set to "-"
            completion_time[pid], 
            turnaround_time[pid], 
            waiting_time[pid], 
            first_response[pid] - arrival
        ])
    
    # Create the DataFrame
    df = pd.DataFrame(result, columns=["PID", "Arrival", "Burst", "Priority", "Completion", "Turnaround", "Waiting", "Response"])
    
    return df, gantt_chart