import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

def plot_gantt_chart(df, frame, is_preemptive=False):  # Flag for preemptive algorithms
    print("Gantt Chart Data:", df)  # Debugging Line

    # Close any existing figures to prevent memory leak
    plt.close('all')

    # Handle empty Gantt chart scenario
    if df.empty:
        print("No data to plot in Gantt Chart!")
        return

    # Determine total execution time dynamically
    total_time = max(df['Completion']) + 1  # Fix potential error with empty DataFrame

    # Adjust figure size to fit all processes
    fig, ax = plt.subplots(figsize=(max(10, total_time / 2), 1.5))  # Ensure minimum size

    # Define a large list of unique colors for processes
    colors = [
        '#FFD700', '#FFA07A', '#98FB98', '#87CEFA', '#DDA0DD', '#FF6347', '#4682B4', '#3CB371', '#DAA520',
        '#FF4500', '#8A2BE2', '#A52A2A', '#5F9EA0', '#D2691E', '#FF1493', '#1E90FF', '#32CD32', '#B22222',
        '#7FFF00'
    ]
    idle_color = "#D3D3D3"  # Light gray for IDLE time
    completion_times = [0]  # Start x-axis at 0
    legend_labels = {}

    prev_time = 0  # Track previous process execution time
    process_colors = {}  # Dictionary to store process colors
    last_end_time = 0  # Track the last process's end time

    # Iterate over the Gantt data to plot each process
    for i, row in enumerate(df.itertuples()):
        pid = f"P{row.PID}"  # Create label for PID, e.g., "P1"
        start_time = row.Start  
        end_time = row.Completion  

        # Assign a unique color to each process (only once)
        if pid not in process_colors:
            process_colors[pid] = colors[i % len(colors)]  # Assign a color from the list (cyclic)

        color = process_colors[pid]  # Color of the current process

        # If there's an idle gap, insert an "IDLE" bar
        if start_time > prev_time:
            idle_start = prev_time
            idle_end = start_time
            ax.barh(y=0, width=idle_end - idle_start, left=idle_start, color=idle_color, edgecolor="black", height=0.4)
            ax.text(idle_start + (idle_end - idle_start) / 2, 0, "IDLE", ha='center', va='center', fontsize=9, fontweight="bold")
            
            # Ensure idle times are recorded in x-ticks
            completion_times.append(idle_end)  

        # Draw process execution bar
        ax.barh(y=0, width=end_time - start_time, left=start_time, color=color, edgecolor="black", height=0.4)
        ax.text(start_time + (end_time - start_time) / 2, 0, pid, ha='center', va='center', fontsize=9, fontweight="bold")

        # Store x-axis ticks correctly
        if is_preemptive:  
            completion_times.append(start_time)  # Show time at **start** of execution (context switch)
        completion_times.append(end_time)  # Ensure end time is recorded

        # Add dotted line if not preemptive
        if not is_preemptive:
            ax.axvline(x=end_time, color='black', linestyle='dotted', linewidth=1)

        # Store legend entry if not already added
        if pid not in legend_labels:
            legend_labels[pid] = color

        prev_time = end_time  
        last_end_time = max(last_end_time, end_time)  

    # Formatting
    ax.set_yticks([])  # Hide y-axis ticks (only time is relevant)
    ax.set_xlabel("Time")
    ax.set_title("Gantt Chart")

    # Ensure idle end times are included in x-axis
    ax.set_xticks(sorted(set(completion_times)))
    ax.set_xticklabels(sorted(set(completion_times)))

    # Fix: Ensure last completion time is visible but without unnecessary space
    ax.set_xlim(left=0, right=last_end_time)  

    # Remove grid lines
    ax.grid(False)

    # Add Legend
    legend_patches = [plt.Rectangle((0, 0), 1, 1, color=color) for color in legend_labels.values()]
    legend_patches.append(plt.Rectangle((0, 0), 1, 1, color=idle_color))  # Add IDLE color to legend
    legend_labels["IDLE"] = idle_color  # Add IDLE to legend

    legend = ax.legend(legend_patches, legend_labels.keys(), loc="upper left", fontsize=9, frameon=True, bbox_to_anchor=(1, 1))
    legend.get_frame().set_alpha(0.8)  # Make legend background slightly transparent

    # Clear Previous Chart and Display New One
    for widget in frame.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)  

    # Make sure to close this figure if the canvas is destroyed
    def on_destroy(event):
        plt.close(fig)
    
    canvas.get_tk_widget().bind("<Destroy>", on_destroy)
    