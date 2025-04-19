import numpy as np
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import ListedColormap
from scipy.ndimage import label
from scipy.signal import convolve2d

class EnhancedPDSimulator:
    def __init__(self, master):
        self.master = master
        self.master.title("Enhanced Spatial PD Simulator")
        
        # Simulation parameters
        self.n = 100
        self.b = 1.8
        self.running = False
        self.neighborhood = 'Moore'
        self.boundary = 'periodic'
        self.initial_config = 'random'
        self.strategy_mode = 'local'  # 'always_d', 'always_c', 'local'
        self.prev_grid = None

        # Visualization parameters
        self.cmap = ListedColormap(['red', 'blue', 'yellow', 'green'])
        self.colors = {0:0, 1:1, 2:2, 3:3}  # D, C, D←C, C←D
        self.ts_data = []

        # Initialize grid
        self.grid = self.initialize_grid()

        # Setup GUI
        self.setup_controls()
        self.setup_visualization()

    def initialize_grid(self):
        grid = np.ones((self.n, self.n))  # Start with all cooperators
        if self.initial_config == 'random':
            grid = np.random.choice([0, 1], size=(self.n, self.n))
        elif self.initial_config == 'single_d':
            grid[self.n//2, self.n//2] = 0
        return grid

    def setup_controls(self):
        control_frame = tk.Frame(self.master)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Parameter slider
        self.b_slider = tk.Scale(control_frame, from_=1.0, to=2.5, resolution=0.1,
                                 label="Defector Advantage (b)", orient=tk.HORIZONTAL,
                                 command=lambda v: self.on_param_change())
        self.b_slider.set(self.b)
        self.b_slider.pack(side=tk.LEFT, padx=5)

        # Buttons
        tk.Button(control_frame, text="Start", command=self.toggle_simulation).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Reset", command=self.reset_grid).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Toggle Boundary", command=self.toggle_boundary).pack(side=tk.LEFT, padx=5)

        # Strategy selection
        strategy_frame = tk.LabelFrame(control_frame, text="Stratégie", padx=5, pady=2)
        strategy_frame.pack(side=tk.LEFT, padx=5)

        strategy_options = [("Défection Pure", 'always_d'),
                            ("Coopération Pure", 'always_c'),
                            ("Locale", 'local')]

        self.strategy_var = tk.StringVar(value=self.strategy_mode)
        for text, value in strategy_options:
            tk.Radiobutton(strategy_frame, text=text, variable=self.strategy_var, value=value,
                           command=self.on_strategy_change).pack(anchor=tk.W)

        # Presets
        presets = [
            ("Static (b=1.75)", 1.75),
            ("Chaos (b=1.9)", 1.9),
            ("D Domination (b=2.1)", 2.1)
        ]
        for text, val in presets:
            tk.Button(control_frame, text=text, command=lambda v=val: self.set_preset(v)).pack(side=tk.LEFT, padx=2)

    def setup_visualization(self):
        self.fig = Figure(figsize=(12, 6))
        self.grid_ax = self.fig.add_subplot(121)
        self.ts_ax = self.fig.add_subplot(122)

        # Grid plot setup
        self.grid_ax.set_xticks([])
        self.grid_ax.set_yticks([])

        # Time series setup
        self.ts_ax.set_xlabel("Generation")
        self.ts_ax.set_ylabel("Fraction Cooperators")
        self.ts_ax.set_ylim(0, 1)
        self.ts_line, = self.ts_ax.plot([], [], 'b-')
        self.ts_ax.axhline(0.318, color='r', linestyle='--', label="Theoretical limit")
        self.ts_ax.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.update_plot()

    def toggle_simulation(self):
        self.running = not self.running
        if self.running:
            self.run_simulation()

    def run_simulation(self):
        if self.running:
            self.update_grid()
            self.update_plot()
            self.master.after(50, self.run_simulation)

    def update_grid(self):
        self.prev_grid = self.grid.copy()
        new_grid = np.zeros_like(self.grid)
        scores = self.calculate_scores()

        for i in range(self.n):
            for j in range(self.n):
                if self.strategy_mode == 'always_d':
                    new_grid[i, j] = 0  # Toujours défecteur
                elif self.strategy_mode == 'always_c':
                    new_grid[i, j] = 1  # Toujours coopérateur
                else:  # Stratégie locale
                    nbrs = []
                    for di in (-1, 0, 1):
                        for dj in (-1, 0, 1):
                            ii = (i + di) % self.n if self.boundary == 'periodic' else i + di
                            jj = (j + dj) % self.n if self.boundary == 'periodic' else j + dj
                            if 0 <= ii < self.n and 0 <= jj < self.n:
                                nbrs.append((ii, jj))

                    local_scores = [scores[ii, jj] for (ii, jj) in nbrs]
                    max_score = max(local_scores)
                    best_nbrs = [nbrs[k] for k, s in enumerate(local_scores) if s == max_score]

                    ii_star, jj_star = best_nbrs[np.random.randint(len(best_nbrs))]
                    new_grid[i, j] = self.prev_grid[ii_star, jj_star]

        self.grid = new_grid

    def calculate_scores(self):
        kernel = np.ones((3, 3)) if self.neighborhood == 'Moore' else np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
        boundary = 'wrap' if self.boundary == 'periodic' else 'fill'

        c_scores = convolve2d(self.grid, kernel, mode='same', boundary=boundary)
        d_scores = self.b * c_scores

        return np.where(self.grid == 1, c_scores, d_scores)

    def update_plot(self):
        transition_grid = np.zeros_like(self.grid)
        if self.prev_grid is not None:
            transition_grid = np.where((self.grid == 0) & (self.prev_grid == 1), 2,
                                       np.where((self.grid == 1) & (self.prev_grid == 0), 3, self.grid))

        self.grid_ax.clear()
        self.grid_ax.imshow(transition_grid, cmap=self.cmap, vmin=0, vmax=3)

        coop_frac = np.mean(self.grid)
        self.ts_data.append(coop_frac)
        self.ts_line.set_data(range(len(self.ts_data)), self.ts_data)
        self.ts_ax.relim()
        self.ts_ax.autoscale_view(scalex=True, scaley=False)
        self.ts_ax.set_xlim(0, len(self.ts_data) + 1)

        cluster_stats = self.get_cluster_stats()
        stats_text = (f"Avg Cluster Size: {cluster_stats['avg_c_size']:.1f}\n"
                      f"Max Cluster Size: {cluster_stats['max_c_size']}\n"
                      f"Total Clusters: {cluster_stats['n_clusters']}")
        self.grid_ax.text(0.05, 0.95, stats_text, transform=self.grid_ax.transAxes,
                          verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8))

        self.canvas.draw()

    def get_cluster_stats(self):
        labeled, n_clusters = label(self.grid, structure=np.ones((3, 3)))
        cluster_sizes = [np.sum(labeled == i) for i in range(1, n_clusters + 1)]
        return {
            'avg_c_size': np.mean(cluster_sizes) if cluster_sizes else 0,
            'max_c_size': np.max(cluster_sizes) if cluster_sizes else 0,
            'n_clusters': n_clusters
        }

    def reset_grid(self):
        self.grid = self.initialize_grid()
        self.ts_data = []
        self.update_plot()

    def toggle_boundary(self):
        self.boundary = 'periodic' if self.boundary == 'fixed' else 'fixed'
        self.reset_grid()

    def set_preset(self, b_value):
        self.b_slider.set(b_value)
        self.on_param_change()

    def on_param_change(self):
        self.b = float(self.b_slider.get())
        self.ts_data = []
        self.reset_grid()

    def on_strategy_change(self):
        self.strategy_mode = self.strategy_var.get()
        self.reset_grid()


if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedPDSimulator(root)
    root.mainloop()
