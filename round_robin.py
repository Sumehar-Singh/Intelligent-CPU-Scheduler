import pandas as pd
from collections import deque

def round_robin_scheduling(processes, time_quantum):
    """Round Robin Scheduling Algorithm"""

    if not processes:
        return pd.DataFrame(columns=["PID", "Arrival", "Burst", "Priority", "Completion", "Turnaround", "Waiting", "Response"]), []

    # Convert list of dictionaries to list of tuples (PID, Arrival, Burst)
    processes = [(p["PID"], p["Arrival"], p["Burst"]) for p in processes]

    processes.sort(key=lambda x: x[1])  # Sort by arrival time

    queue = deque()
    time, idx = 0, 0
    completion_time = {}
    waiting_time = {p[0]: 0 for p in processes}
    turnaround_time = {}

    remaining_burst = {p[0]: p[2] for p in processes}  # Track remaining burst time
    first_response = {p[0]: -1 for p in processes}  # Track first response time

    gantt_chart = []

    while queue or idx < len(processes):
        while idx < len(processes) and processes[idx][1] <= time:
            queue.append(processes[idx][0])  # Add process ID to queue
            idx += 1

        if not queue:
            time = processes[idx][1]  # Jump to next arrival time
            continue

        pid = queue.popleft()
        if first_response[pid] == -1:
            first_response[pid] = time  # Set first response time

        execute_time = min(time_quantum, remaining_burst[pid])
        remaining_burst[pid] -= execute_time
        time += execute_time

        gantt_chart.append((time - execute_time, time, pid))  # Include Start, Completion, PID

        while idx < len(processes) and processes[idx][1] <= time:
            queue.append(processes[idx][0])
            idx += 1

        if remaining_burst[pid] > 0:
            queue.append(pid)  # Re-add process to queue if not finished
        else:
            completion_time[pid] = time
            turnaround_time[pid] = completion_time[pid] - [p[1] for p in processes if p[0] == pid][0]
            waiting_time[pid] = turnaround_time[pid] - [p[2] for p in processes if p[0] == pid][0]

    # Now we need to prepare the result in a DataFrame
    result = []
    for p in processes:
        pid, arrival, burst = p
        result.append([pid, arrival, burst, "-", completion_time[pid], turnaround_time[pid], waiting_time[pid], first_response[pid] - arrival])

    # Create a DataFrame with a 'Priority' column, set to "-"
    df = pd.DataFrame(result, columns=["PID", "Arrival", "Burst", "Priority", "Completion", "Turnaround", "Waiting", "Response"])
    return df, gantt_chart
