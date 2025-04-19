# Enhanced Spatial Prisoner's Dilemma Simulator

This project simulates the evolution of cooperation in a 2D spatial Prisoner's Dilemma (PD) environment. It features an interactive GUI built with `tkinter` and visualizes the state of a grid-based agent population playing PD games with neighbors over time.

---

## 🧠 Concept

In the spatial PD model, agents are placed on a grid and can either cooperate or defect. At each generation:
- They play the PD game with their neighbors.
- Accumulate payoffs based on interactions.
- Imitate the strategy of the most successful neighbor.

A **temptation to defect** parameter `b` controls the advantage defectors have over cooperators. The system evolves over time, and cooperation may survive or vanish depending on the value of `b`, neighborhood type, and boundary conditions.

---

## 🖥️ Features

- **Real-Time Visualization**: Observe spatial strategy dynamics.
- **Interactive GUI**: Modify parameters using sliders and buttons.
- **Time-Series Plot**: Tracks the fraction of cooperators over generations.
- **Cluster Statistics**: Displays average size, maximum size, and number of cooperative clusters.
- **Color-Coded Transitions**:
  - 🔴 Red: Defectors (0)
  - 🔵 Blue: Cooperators (1)
  - 🟡 Yellow: Cooperator → Defector (2)
  - 🟢 Green: Defector → Cooperator (3)

---

## 📊 Visualization Panels

### Grid (Left)
- Each cell is an agent.
- Colors show strategies and recent transitions.
- Transitions reveal dynamics at the edge of clusters.

### Time Series (Right)
- Blue line: Fraction of cooperators.
- Red dashed line: Theoretical equilibrium (~0.318).
- Watch how cooperation grows, shrinks, or stabilizes.

---

## ⚙️ Parameters

- **Grid Size**: `n = 100`
- **Temptation to Defect (b)**: Ranges from 1.0 to 2.5
- **Neighborhood**: Moore (default)
- **Boundary Conditions**: Periodic or Fixed
- **Initial Configurations**:
  - Random
  - All cooperators with one defector

---

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Install dependencies:
```bash
pip install numpy matplotlib scipy