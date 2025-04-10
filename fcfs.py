import pandas as pd

def fcfs_scheduling(processes):
    processes.sort(key=lambda x: x['Arrival'])  # Sort by Arrival Time
    completion_time = 0
    result = []

    for p in processes:
        pid, arrival, burst = p['PID'], p['Arrival'], p['Burst']

        if completion_time < arrival:
            completion_time = arrival  # CPU remains idle until process arrives

        start_time = completion_time  # Track start time for Gantt chart
        completion_time += burst
        turnaround_time = completion_time - arrival
        waiting_time = turnaround_time - burst
        response_time = waiting_time  # Same as waiting time in FCFS

        # Adding 'Priority' column (assuming FCFS does not use priority, we set it as '-')
        priority = '-'  # Since FCFS does not use priority

        result.append([pid, arrival, burst, priority, start_time, completion_time, turnaround_time, waiting_time, response_time])

    # Create DataFrame
    df = pd.DataFrame(result, columns=["PID", "Arrival", "Burst", "Priority", "Start", "Completion", "Turnaround", "Waiting", "Response"])
    return df