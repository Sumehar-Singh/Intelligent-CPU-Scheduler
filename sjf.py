import pandas as pd

def sjf_scheduling(processes):
    """Shortest Job First (SJF) Non-Preemptive Scheduling Algorithm"""
    
    # Sort processes by Arrival Time first, then by Burst Time
    processes.sort(key=lambda x: (x['Arrival'], x['Burst']))
    
    completion_time = 0
    result = []

    # Track remaining processes for scheduling
    remaining_processes = processes[:]
    
    while remaining_processes:
        # Select processes that have arrived by the current time
        available_processes = [p for p in remaining_processes if p['Arrival'] <= completion_time]

        if not available_processes:
            # If no process is available, jump to the next arrival time
            next_arrival = min(p['Arrival'] for p in remaining_processes)
            completion_time = next_arrival
            continue

        # Choose the process with the shortest burst time
        current_process = min(available_processes, key=lambda p: p['Burst'])
        pid, arrival, burst = current_process['PID'], current_process['Arrival'], current_process['Burst']
        remaining_processes.remove(current_process)

        # Calculate the start time for the Gantt chart
        start_time = completion_time
        completion_time += burst
        
        # Calculate turnaround, waiting, and response times
        turnaround_time = completion_time - arrival
        waiting_time = turnaround_time - burst
        response_time = waiting_time  # Same as waiting time for SJF

        # Adding 'Priority' column (assuming SJF does not use priority, we set it as '-')
        priority = '-'  # Since SJF does not use priority

        # Store the results for the current process
        result.append([pid, arrival, burst, priority, start_time, completion_time, turnaround_time, waiting_time, response_time])

    # Create DataFrame with 'Priority' included
    df = pd.DataFrame(result, columns=["PID", "Arrival", "Burst", "Priority", "Start", "Completion", "Turnaround", "Waiting", "Response"])
    return df
