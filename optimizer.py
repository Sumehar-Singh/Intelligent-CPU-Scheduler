import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import copy
from fcfs import fcfs_scheduling
from sjf import sjf_scheduling
from srtf import srtf_scheduling
from round_robin import round_robin_scheduling
from non_preemptive_priority import priority_scheduling
from preemptive_priority import preemptive_priority_scheduling

class AlgorithmOptimizerWindow:
    def __init__(self, parent, processes):
        self.parent = parent
        # Create a deep copy of processes to avoid modifying original data
        self.processes = copy.deepcopy(processes)
        
        # Create new window
        self.window = tk.Toplevel(parent)
        self.window.title("CPU Scheduling Algorithm Optimizer")
        self.window.geometry("1000x700")
        self.window.grab_set()  # Make window modal
        
        # Add a stylish header
        header_frame = tk.Frame(self.window, bg="#3498db", pady=10)
        header_frame.pack(fill="x")
        
        header_label = tk.Label(
            header_frame,
            text="CPU Scheduling Algorithm Optimizer",
            font=("Arial", 16, "bold"),
            bg="#3498db",
            fg="white"
        )
        header_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Find the most efficient scheduling algorithm for your processes",
            font=("Arial", 10),
            bg="#3498db",
            fg="white"
        )
        subtitle_label.pack()
        
        # Main content area
        content_frame = tk.Frame(self.window, padx=15, pady=15)
        content_frame.pack(fill="both", expand=True)
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Tab 1: Results Overview
        overview_tab = tk.Frame(self.notebook)
        self.notebook.add(overview_tab, text="Results Overview")
        
        # Tab 2: Detailed Comparison
        details_tab = tk.Frame(self.notebook)
        self.notebook.add(details_tab, text="Detailed Comparison")
        
        # Tab 3: Graph Analysis
        graph_tab = tk.Frame(self.notebook)
        self.notebook.add(graph_tab, text="Graph Analysis")
        
        # Setup Overview Tab
        overview_frame = tk.Frame(overview_tab, padx=10, pady=10)
        overview_frame.pack(fill="both", expand=True)
        
        # Recommendation panel in overview tab
        recommendation_frame = tk.LabelFrame(
            overview_frame, 
            text="Recommended Algorithm", 
            padx=15, 
            pady=15,
            font=("Arial", 11, "bold")
        )
        recommendation_frame.pack(fill="x", pady=15)
        
        self.recommendation_label = tk.Label(
            recommendation_frame,
            text="Analyzing processes...",
            font=("Arial", 14, "bold"),
            fg="#2980b9",
            justify="left",
            anchor="w"
        )
        self.recommendation_label.pack(fill="x", padx=10, pady=10)
        
        self.recommendation_details = tk.Label(
            recommendation_frame,
            text="",
            font=("Arial", 12),
            justify="left",
            wraplength=800
        )
        self.recommendation_details.pack(fill="x", padx=10, pady=5)
        
        # Quick metrics section
        metrics_frame = tk.Frame(overview_frame)
        metrics_frame.pack(fill="x", pady=10)
        
        self.metric_frames = []
        metric_titles = ["Average Waiting Time", "Average Turnaround Time", "Average Response Time"]
        
        for i, title in enumerate(metric_titles):
            frame = tk.LabelFrame(metrics_frame, text=title, padx=10, pady=10)
            frame.grid(row=0, column=i, padx=5, sticky="ew")
            metrics_frame.columnconfigure(i, weight=1)
            
            value_label = tk.Label(frame, text="-", font=("Arial", 16, "bold"), fg="#e74c3c")
            value_label.pack(pady=5)
            
            self.metric_frames.append(value_label)
        
        # Add metric selection options with radio buttons
        metric_selection_frame = tk.LabelFrame(
            overview_frame,
            text="Select Performance Metric for Recommendation",
            padx=15,
            pady=15,
            font=("Arial", 11, "bold")
        )
        metric_selection_frame.pack(fill="x", pady=15)
        
        self.selected_metric = tk.StringVar(value="avg_turnaround")
        
        metrics_options = [
            ("Average Turnaround Time", "avg_turnaround"),
            ("Average Waiting Time", "avg_waiting"),
            ("Average Response Time", "avg_response")
        ]
        
        for i, (text, value) in enumerate(metrics_options):
            rb = tk.Radiobutton(
                metric_selection_frame,
                text=text,
                value=value,
                variable=self.selected_metric,
                font=("Arial", 11),
                command=self.update_recommendation,
                padx=20
            )
            rb.grid(row=0, column=i, padx=10, sticky="w")
        
        # Setup Details Tab
        details_frame = tk.Frame(details_tab, padx=10, pady=10)
        details_frame.pack(fill="both", expand=True)
        
        # Results table
        table_frame = tk.Frame(details_frame)
        table_frame.pack(fill="both", expand=True, pady=10)
        
        self.results_tree = ttk.Treeview(
            table_frame, 
            columns=("Algorithm", "Avg Turnaround", "Avg Waiting", "Avg Response"),
            show="headings",
            height=8
        )
        
        # Configure columns
        self.results_tree.heading("Algorithm", text="Algorithm")
        self.results_tree.heading("Avg Turnaround", text="Avg Turnaround Time")
        self.results_tree.heading("Avg Waiting", text="Avg Waiting Time")
        self.results_tree.heading("Avg Response", text="Avg Response Time")
        
        # Configure column widths
        self.results_tree.column("Algorithm", width=150, anchor="center")
        self.results_tree.column("Avg Turnaround", width=150, anchor="center")
        self.results_tree.column("Avg Waiting", width=150, anchor="center")
        self.results_tree.column("Avg Response", width=150, anchor="center")
        
        # Add scrollbars to results tree
        y_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.results_tree.yview)
        x_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        self.results_tree.pack(side="left", fill="both", expand=True)
        y_scrollbar.pack(side="right", fill="y")
        x_scrollbar.pack(side="bottom", fill="x")
        
        # Add event handler for clicking on a result
        self.results_tree.bind("<Double-1>", self.show_algorithm_details)
        
        # Algorithm explanation section
        explanation_frame = tk.LabelFrame(details_frame, text="Algorithm Details", padx=10, pady=10)
        explanation_frame.pack(fill="x", pady=10)
        
        self.explanation_text = tk.Text(explanation_frame, height=8, wrap="word", bg="#f8f9fa")
        self.explanation_text.pack(fill="both", expand=True, pady=5)
        self.explanation_text.insert("1.0", "Double-click on any algorithm in the table above to see details about how it works.")
        self.explanation_text.config(state="disabled")
        
        # Setup Graph Tab
        self.graph_frame = tk.Frame(graph_tab, padx=10, pady=10)
        self.graph_frame.pack(fill="both", expand=True)
        
        # Chart container
        self.chart_container = tk.Frame(self.graph_frame)
        self.chart_container.pack(fill="both", expand=True, pady=10)
        
        # Button frame at bottom
        button_frame = tk.Frame(self.window, bg="#f5f5f5", padx=15, pady=10)
        button_frame.pack(fill="x", side="bottom")
        
        # Close button
        close_button = tk.Button(
            button_frame,
            text="Close",
            command=self.window.destroy,
            bg="#e74c3c",
            fg="white",
            relief=tk.RAISED,
            padx=10
        )
        close_button.pack(side="right", padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            self.window, 
            textvariable=self.status_var, 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            bg="#f0f0f0"
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Store analysis results
        self.results = {}
        
        # Analyze algorithms if processes exist
        if self.processes:
            self.analyze_algorithms()
        else:
            self.status_var.set("No processes to analyze")
            messagebox.showinfo("No Data", "No processes to analyze. Please add processes first.")

    def analyze_algorithms(self):
        """Run all algorithms and compare their performance"""
        self.status_var.set("Analyzing algorithms...")
        self.results = {}
        
        # Check if any process has Priority field as "-"
        has_priority = all(p.get("Priority", "-") != "-" for p in self.processes)
        
        # Run algorithms
        try:
            # FCFS
            self.status_var.set("Analyzing FCFS algorithm...")
            fcfs_result = fcfs_scheduling(copy.deepcopy(self.processes))
            fcfs_metrics = self.calculate_metrics(fcfs_result)
            self.results["FCFS"] = fcfs_metrics
            
            # SJF
            self.status_var.set("Analyzing SJF algorithm...")
            sjf_result = sjf_scheduling(copy.deepcopy(self.processes))
            sjf_metrics = self.calculate_metrics(sjf_result)
            self.results["SJF"] = sjf_metrics
            
            # SRTF
            self.status_var.set("Analyzing SRTF algorithm...")
            srtf_result, _ = srtf_scheduling(copy.deepcopy(self.processes))
            srtf_metrics = self.calculate_metrics(srtf_result)
            self.results["SRTF"] = srtf_metrics
            
            # Try different time quantums for Round Robin (dynamic range)
            best_rr_metrics = None
            best_rr_tq = 1
            best_rr_score = float('inf')
            
            max_burst = max(int(p.get("Burst", 1)) for p in self.processes)
            # Try time quantums from 1 up to max burst time (capped at 20 to avoid excessive calculations)
            tq_range = range(1, min(max_burst + 1, 21))
            
            for tq in tq_range:
                self.status_var.set(f"Analyzing Round Robin (q={tq}) algorithm...")
                rr_result, _ = round_robin_scheduling(copy.deepcopy(self.processes), tq)
                metrics = self.calculate_metrics(rr_result)
                
                # Track the best RR configuration - using waiting time as the standard metric
                if metrics["avg_waiting"] < best_rr_score:
                    best_rr_metrics = metrics
                    best_rr_tq = tq
                    best_rr_score = metrics["avg_waiting"]
            
            # Add only the best RR configuration to results
            if best_rr_metrics:
                rr_algo_name = f"RR (TQ={best_rr_tq})"
                self.results[rr_algo_name] = best_rr_metrics
            
            # Priority algorithms (only if all processes have priority values)
            if has_priority:
                # Priority (Non-Preemptive)
                self.status_var.set("Analyzing Priority (Non-Preemptive) algorithm...")
                pnp_result = priority_scheduling(copy.deepcopy(self.processes))
                pnp_metrics = self.calculate_metrics(pnp_result)
                self.results["Priority (NP)"] = pnp_metrics
                
                # Priority (Preemptive)
                self.status_var.set("Analyzing Priority (Preemptive) algorithm...")
                pp_result, _ = preemptive_priority_scheduling(copy.deepcopy(self.processes))
                pp_metrics = self.calculate_metrics(pp_result)
                self.results["Priority (P)"] = pp_metrics
                
        except Exception as e:
            self.status_var.set(f"Error in algorithm analysis: {e}")
            messagebox.showerror("Analysis Error", f"An error occurred during analysis: {e}")
            return
            
        # Clear existing results in tree
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        # Display results in table
        for algo, metrics in self.results.items():
            self.results_tree.insert(
                "", "end", values=(
                    algo,
                    f"{metrics['avg_turnaround']:.2f}",
                    f"{metrics['avg_waiting']:.2f}",
                    f"{metrics['avg_response']:.2f}"
                )
            )
        
        # Update recommendation
        self.update_recommendation()
        # Update graph
        self.update_graph()
        self.status_var.set("Analysis complete")

    def update_recommendation(self):
        """Update the recommendation based on selected metric"""
        if not self.results:
            return
        
        # Get the selected metric to use for recommendation
        selected_metric = self.selected_metric.get()
        
        # Find algorithm with the best individual metric
        best_algo_name = min(self.results.items(), key=lambda x: x[1][selected_metric])[0]
        
        # Map the metric to a user-friendly name
        metric_names = {
            "avg_turnaround": "Average Turnaround Time",
            "avg_waiting": "Average Waiting Time",
            "avg_response": "Average Response Time"
        }
        metric_name = metric_names[selected_metric]
        
        best_algo_metrics = self.results[best_algo_name]
        
        # Update recommendation labels
        self.recommendation_label.config(
            text=f"Best Algorithm for {metric_name}: {best_algo_name}"
        )
        
        # Update recommendation details
        details_text = (
            f"Based on {metric_name.lower()}, "
            f"{best_algo_name} is recommended as the most efficient algorithm.\n\n"
            f"This algorithm achieves the following metrics:\n"
            f"• Average Waiting Time: {best_algo_metrics['avg_waiting']:.2f}\n"
            f"• Average Turnaround Time: {best_algo_metrics['avg_turnaround']:.2f}\n"
            f"• Average Response Time: {best_algo_metrics['avg_response']:.2f}\n\n"
        )
        
        self.recommendation_details.config(text=details_text)
        
        # Update quick metrics
        self.metric_frames[0].config(text=f"{best_algo_metrics['avg_waiting']:.2f}")
        self.metric_frames[1].config(text=f"{best_algo_metrics['avg_turnaround']:.2f}")
        self.metric_frames[2].config(text=f"{best_algo_metrics['avg_response']:.2f}")
        self.status_var.set("Analysis complete")

    def show_algorithm_details(self, event):
        """Show details about the selected algorithm when clicked"""
        item = self.results_tree.identify('item', event.x, event.y)
        if not item:
            return
            
        algo = self.results_tree.item(item, "values")[0]
        
        # Enable text editing
        self.explanation_text.config(state="normal")
        self.explanation_text.delete("1.0", tk.END)
        
        # Algorithm explanations
        explanations = {
            "FCFS": (
                "First-Come, First-Served (FCFS) is the simplest CPU scheduling algorithm. "
                "In this algorithm, processes are executed in the order they arrive in the ready queue. "
                "It is non-preemptive, meaning once a process begins execution, it runs until completion.\n\n"
                "Advantages: Simple to implement, fair in terms of arrival order.\n"
                "Disadvantages: Can lead to the 'convoy effect' where short processes wait for long ones."
            ),
            "SJF": (
                "Shortest Job First (SJF) selects the process with the smallest burst time first. "
                "It is non-preemptive, so once a process starts executing, it runs to completion.\n\n"
                "Advantages: Provides minimum average waiting time among non-preemptive algorithms.\n"
                "Disadvantages: May cause starvation for longer processes if short processes keep arriving."
            ),
            "SRTF": (
                "Shortest Remaining Time First (SRTF) is the preemptive version of SJF. "
                "The process with the smallest remaining time is always selected for execution. "
                "If a new process arrives with a shorter burst time, the current process is preempted.\n\n"
                "Advantages: Optimal average waiting time among all scheduling algorithms.\n"
                "Disadvantages: High overhead due to frequent context switches, potential starvation issues."
            ),
            "Priority (NP)": (
                "Non-preemptive Priority scheduling assigns priorities to processes and selects the highest priority process first. "
                "Once a process starts execution, it runs to completion.\n\n"
                "Advantages: Important processes get CPU time first.\n"
                "Disadvantages: May lead to starvation of lower-priority processes, priority inversion problems."
            ),
            "Priority (P)": (
                "Preemptive Priority scheduling also uses priorities but preempts the current process if a higher-priority process arrives. "
                "The highest priority process always gets the CPU.\n\n"
                "Advantages: Responsive to high-priority processes.\n"
                "Disadvantages: More context switches, potential starvation of lower-priority processes."
            ),
            "RR (TQ=)": (
                "This is Round Robin that has been selected as the most suitable configuration "
                "for the given set of processes. The time quantum represents the maximum time "
                "a process can execute before being preempted and moved to the end of the queue.\n\n"
                "Advantages: Fair allocation of CPU, good response time for short processes.\n"
                "Disadvantages: Performance depends on time quantum selection."
            )
        }
        
        # Handle Round Robin explanation separately due to time quantum
        if "RR" in algo and "FCFS" not in algo:
            time_quantum = algo.split("=")[1].strip(")")
            explanation = (
                f"Round Robin (RR) with time quantum q={time_quantum} allocates the CPU to each process for a fixed time slice (quantum). "
                f"When the time quantum expires, the process is preempted and added to the end of the ready queue.\n\n"
                f"Advantages: Fair allocation of CPU, good response time for short processes.\n"
                f"Disadvantages: Performance depends on time quantum selection, higher average waiting time than SJF."
            )
        else:
            explanation = explanations.get(algo, "No detailed information available for this algorithm.")
        
        # Add metrics to the explanation
        if algo in self.results:
            metrics = self.results[algo]
            explanation += f"\n\nPerformance Metrics:\n"
            explanation += f"• Average Waiting Time: {metrics['avg_waiting']:.2f}\n"
            explanation += f"• Average Turnaround Time: {metrics['avg_turnaround']:.2f}\n"
            explanation += f"• Average Response Time: {metrics['avg_response']:.2f}"
        
        self.explanation_text.insert("1.0", explanation)
        self.explanation_text.config(state="disabled")

    def update_graph(self):
        """Update the bar graph comparing all algorithms"""
        # Clear existing chart
        for widget in self.chart_container.winfo_children():
            widget.destroy()
            
        if not self.results:
            return
            
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 5))
            
        # Prepare data for plotting
        algorithms = list(self.results.keys())
        turnaround_times = [self.results[algo]["avg_turnaround"] for algo in algorithms]
        waiting_times = [self.results[algo]["avg_waiting"] for algo in algorithms]
        response_times = [self.results[algo]["avg_response"] for algo in algorithms]
        
        # Bar chart
        bar_width = 0.25
        x = np.arange(len(algorithms))
        
        ax.bar(x - bar_width, turnaround_times, bar_width, label='Avg Turnaround', color='#3498db')
        ax.bar(x, waiting_times, bar_width, label='Avg Waiting', color='#e74c3c')
        ax.bar(x + bar_width, response_times, bar_width, label='Avg Response', color='#2ecc71')
        
        # Get selected metric to highlight best algorithm
        selected_metric = self.selected_metric.get()
        
        # Map the metric names
        metric_map = {
            "avg_turnaround": "Turnaround Time",
            "avg_waiting": "Waiting Time",
            "avg_response": "Response Time"
        }
        
        best_algo = min(self.results.items(), key=lambda x: x[1][selected_metric])[0]
        highlight_label = f'Best for {metric_map[selected_metric]}: {best_algo}'
            
        best_idx = algorithms.index(best_algo)
        ax.axvline(x=best_idx, color='#f39c12', linestyle='--', alpha=0.7, label=highlight_label)
        
        ax.set_xlabel('Algorithm')
        ax.set_ylabel('Time (units)')
        ax.set_title('CPU Scheduling Algorithm Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms, rotation=45, ha='right')
        ax.legend(loc='upper right')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # Embed the plot in tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def calculate_metrics(self, result_df):
        """Calculate average metrics from a result dataframe"""
        return {
            "avg_turnaround": result_df["Turnaround"].mean(),
            "avg_waiting": result_df["Waiting"].mean(),
            "avg_response": result_df["Response"].mean() if "Response" in result_df.columns else result_df["Waiting"].mean()
        }