# 🧠 Intelligent CPU Scheduler Simulator

A comprehensive graphical simulator for understanding and visualizing various CPU Scheduling Algorithms — an essential component of operating systems.

---

## 📌 Overview

The **Intelligent CPU Scheduler Simulator** is a Python-based desktop application that allows users to simulate, visualize, and compare different CPU scheduling algorithms.

This tool is ideal for:

- 🎓 Students exploring OS scheduling concepts  
- 🧑‍🏫 Educators conducting labs or demonstrations  
- 👨‍💻 Developers simulating process execution strategies  

---

## ✨ Key Features

- Intuitive GUI using Tkinter  
- Supports FCFS, SJF, Round Robin, SRTF, Preemptive & Non-Preemptive Priority Scheduling  
- Real-time process animation and CPU context switching  
- Gantt Chart display for process timelines  
- Algorithm Optimizer to suggest the best scheduling strategy  
- Performance statistics: Average Waiting, Turnaround, and Response Times  
- Bar Graph visualizations with Matplotlib  
- Reset, delete, and modify inputs dynamically  

---

## 🧠 Core Concepts Implemented

- First-Come First-Served (FCFS) Scheduling  
- Shortest Job First (SJF) Scheduling  
- Round Robin Scheduling  
- Shortest Remaining Time First (SRTF)  
- Priority Scheduling (Preemptive & Non-Preemptive)  
- Gantt Chart and statistical output  
- Algorithm performance comparison and optimization suggestion  

---

## 🗂️ Project Structure
```bash
intelligent-cpu-scheduler-simulator/
├── README.md → Project documentation (you're here)
├── main.py → Entry point and GUI handler
├── fcfs.py → FCFS scheduling algorithm
├── sjf.py → SJF scheduling algorithm
├── round_robin.py → Round Robin algorithm
├── srtf.py → SRTF scheduling algorithm
├── preemptive_priority.py → Preemptive Priority algorithm
├── non_preemptive_priority.py → Non-Preemptive Priority algorithm
├── process_manager.py → Process input handler
├── gantt_chart.py → Gantt chart generator
├── stats_chart.py → Performance graph generator
├── scheduler_animation.py → Real-time animation logic
├── optimizer.py → Algorithm recommendation system
```

---

## 👥 Developer Roles

### Sumehar Singh Grewal
- Implemented: `main.py`, `gantt_chart.py`, `process_manager.py`  
- Designed: GUI layout, input handling, bar chart integration, and animation base(`scheduler_animation.py`)  
- Integrated: Algorithm optimizer system in `optimizer.py`  

### Nitin Kumar
- Implemented: `round_robin.py`, `srtf.py`, `non_preemptive_priority.py`, `preemptive_priority.py`  
- Contributed to: `scheduler_animation.py`, `optimizer.py`  
- Designed: Complex scheduling logic and animation interactions  

### Gaurav Choudhary
- Implemented: `fcfs.py`, `sjf.py`, `stats_chart.py`  
- Enhanced: Reset/delete function, algorithm switching, optimizer visuals  
- Contributed to: `scheduler_animation.py`, `optimizer.py`  

---

## 🛠️ Built With

- **Python 3.6+**  
- **Tkinter** – for GUI  
- **Matplotlib** – for Gantt and bar graphs  
- **Pandas & NumPy** – for data handling  
- **Threading, Time, Random, Copy** – for simulation & transitions  

---

## ⚙️ Installation

### ✅ Prerequisites

- Python 3.6 or higher installed   

### 📦 Install Dependencies

```bash
pip install matplotlib pandas numpy
```
---

## 🛠️ Setup
### Clone the repository:
```bash
git clone https://github.com/Sumehar-Singh/Intelligent-CPU-Scheduler.git
cd Intelligent-CPU-Scheduler
```
---

## 🚀 Running the Simulator
### Launch the application:
```bash
python main.py
```
---
## 💡 What You Can Do
- 📊 Enter process details (arrival time, burst time, priority)

- 🔄 Select and switch between scheduling algorithms

- 📈 View Gantt chart and performance metrics

- ⚡ Use the Optimizer to get the most efficient algorithm suggestion

- 🎞️ Watch process execution in animated form

### 🔍 Example Workflow
- Start the simulator with python main.py

- Enter process details manually or load test data

- Select scheduling algorithm from dropdown

- Click Simulate to view Gantt chart and stats

- Use Optimizer to compare and choose the best strategy

- Reset or switch algorithms anytime

---
## GUI Preview

![Screenshot 2025-04-15 145907](https://github.com/user-attachments/assets/02a0989c-ec3d-4945-8f5f-2436d4370021)
![Screenshot 2025-04-15 150107](https://github.com/user-attachments/assets/f6cacc84-79a2-4e93-acb9-5a459b0d1903)
![Screenshot 2025-04-15 150147](https://github.com/user-attachments/assets/e54ba9fc-76af-4364-a4ab-3c174ae8d0dd)


---
## 🤝 Contributing
### Fork the repository:
```bash
git clone <your-fork-url>
cd intelligent-cpu-scheduler-simulator

# Create a new branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Add: your feature description"

# Push and open a Pull Request
git push origin feature/your-feature-name
```
---
## 👨‍💻 Made with ❤️ by
**Sumehar Singh Grewal**

**Nitin Kumar**

**Gaurav Choudhary**
