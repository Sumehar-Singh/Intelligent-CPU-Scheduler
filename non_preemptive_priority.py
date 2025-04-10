import pandas as pd

def priority_scheduling(processes):
    """Priority Scheduling (Non-Preemptive)"""

    # Convert list of dictionaries to list of tuples (PID, Arrival, Burst, Priority)
    processes = [(p["PID"], p["Arrival"], p["Burst"], p["Priority"]) for p in processes]

    # Sort by Arrival Time first to ensure correct order when processes arrive
    processes.sort(key=lambda x: x[1])

    time, completed = 0, []
    remaining_processes = processes[:]

    while remaining_processes:
        # Get processes that have already arrived
        available = [p for p in remaining_processes if p[1] <= time]

        if not available:
            time = remaining_processes[0][1]  # Jump to the next arriving process
            continue

        # Select the process with the **highest priority (smallest priority number)**
        highest_priority = min(available, key=lambda x: x[3])
        remaining_processes.remove(highest_priority)

        pid, arrival, burst, priority = highest_priority

        start_time = max(time, arrival)  # Ensure we do not start before arrival
        completion_time = start_time + burst
        turnaround_time = completion_time - arrival
        waiting_time = turnaround_time - burst
        response_time = waiting_time  # Response time = waiting time in non-preemptive scheduling

        completed.append([pid, arrival, burst, priority, start_time, completion_time, turnaround_time, waiting_time, response_time])

        time = completion_time  # Move time forward

    df = pd.DataFrame(completed, columns=["PID", "Arrival", "Burst", "Priority", "Start", "Completion", "Turnaround", "Waiting", "Response"])
    return df
