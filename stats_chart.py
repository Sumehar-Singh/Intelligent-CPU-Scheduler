import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def plot_stats_chart(fcfs_df, frame):
    avg_tat = fcfs_df["Turnaround"].mean()
    avg_wt = fcfs_df["Waiting"].mean()
    avg_rt = fcfs_df["Response"].mean()

    stats = ["Avg Turnaround", "Avg Waiting", "Avg Response"]
    values = [avg_tat, avg_wt, avg_rt]

    fig, ax = plt.subplots(figsize=(2, 3)) 
    ax.bar(stats, values, color=["#FF9999", "#66B3FF", "#99FF99"])

    # Labels
    for i, v in enumerate(values):
        ax.text(i, v + 0.2, f"{v:.2f}", color="black", ha="center", fontweight="bold")

    ax.set_ylim(0, max(values) * 1.2)
    ax.set_ylabel("Time (ms)")
    ax.set_title("Performance Metrics")
    
    # Remove grid lines
    ax.grid(False)

    # Clear previous graph and display new one
    for widget in frame.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)