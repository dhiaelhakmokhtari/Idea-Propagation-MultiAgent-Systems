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
        self.strategy_mode = 'imitate_best'  # 'pure_c', 'pure_d', 'imitate_best', 'tft'
        
        # Visualization parameters
        self.cmap = ListedColormap(['red', 'blue', 'yellow', 'green'])
        self.ts_data = []
        
        # Initialize grid and previous grid
        self.grid = self.initialize_grid()
        self.prev_grid = None
        
        # Setup GUI
        self.setup_controls()
        self.setup_visualization()
        self.reset_grid()  # ensure prev_grid is set correctly for TFT

    def initialize_grid(self):
        # initial random or single defector
        if self.initial_config == 'random':
            grid = np.random.choice([0, 1], size=(self.n, self.n))
        else:  # 'single_d'
            grid = np.ones((self.n, self.n), dtype=int)
            grid[self.n//2, self.n//2] = 0

        # override for pure strategies
        if self.strategy_mode == 'pure_c':
            return np.ones_like(grid)
        elif self.strategy_mode == 'pure_d':
            return np.zeros_like(grid)
        else:  # imitate_best or tft
            return grid

    def setup_controls(self):
        cf = tk.Frame(self.master)
        cf.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # b slider
        self.b_slider = tk.Scale(cf, from_=1.0, to=2.5, resolution=0.1,
                                label="Defector Advantage (b)", orient=tk.HORIZONTAL,
                                command=lambda v: self.on_param_change())
        self.b_slider.set(self.b)
        self.b_slider.pack(side=tk.LEFT, padx=5)
        
        # strategy buttons
        for text, mode in [
            ("Pure C", 'pure_c'),
            ("Pure D", 'pure_d'),
            ("Imitate Best", 'imitate_best'),
            ("Tit-for-Tat", 'tft'),
        ]:
            tk.Button(cf, text=text, command=lambda m=mode: self.set_strategy(m))\
              .pack(side=tk.LEFT, padx=3)
        
        # control buttons
        tk.Button(cf, text="Start",  command=self.toggle_simulation).pack(side=tk.LEFT, padx=5)
        tk.Button(cf, text="Reset",  command=self.reset_grid).pack(side=tk.LEFT, padx=5)
        tk.Button(cf, text="Toggle Boundary", command=self.toggle_boundary).pack(side=tk.LEFT, padx=5)

        # presets
        for txt, val in [("Static (1.75)",1.75),("Chaos (1.9)",1.9),("D Dom (2.1)",2.1)]:
            tk.Button(cf, text=txt, command=lambda v=val: self.set_preset(v))\
              .pack(side=tk.LEFT, padx=2)

    def setup_visualization(self):
        self.fig = Figure(figsize=(12,6))
        self.ax_grid = self.fig.add_subplot(121)
        self.ax_ts   = self.fig.add_subplot(122)
        self.ax_grid.set_xticks([]); self.ax_grid.set_yticks([])
        self.ax_ts.set_xlabel("Generation"); self.ax_ts.set_ylabel("Fraction C")
        self.ts_line, = self.ax_ts.plot([],[],'b-')
        self.ax_ts.axhline(0.318, color='r', linestyle='--', label="Theoretical limit")
        self.ax_ts.legend()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def toggle_simulation(self):
        self.running = not self.running
        if self.running:
            self.run_simulation()
    
    def run_simulation(self):
        if not self.running: return
        self.update_grid()
        self.update_plot()
        self.master.after(50, self.run_simulation)

    def update_grid(self):
        new = np.zeros_like(self.grid)
        scores = None
        if self.strategy_mode == 'imitate_best':
            self.prev_grid = self.grid.copy()
            scores = self.calculate_scores()
        elif self.strategy_mode == 'tft':
            # For TFT, ensure prev_grid exists
            old = self.prev_grid.copy() if self.prev_grid is not None else np.ones_like(self.grid)
        else:
            # pure strategies: no need prev_grid
            self.prev_grid = None

        for i in range(self.n):
            for j in range(self.n):
                mode = self.strategy_mode
                if mode == 'pure_c':
                    new[i,j] = 1
                elif mode == 'pure_d':
                    new[i,j] = 0
                elif mode == 'tft':
                    # inspect neighbors (3×3)
                    neigh = [
                        ((i+di)%self.n if self.boundary=='periodic' else i+di,
                         (j+dj)%self.n if self.boundary=='periodic' else j+dj)
                        for di in (-1,0,1) for dj in (-1,0,1)
                        if 0 <= i+di < self.n and 0 <= j+dj < self.n
                    ]
                    defect_count = sum(1 for x,y in neigh if old[x,y] == 0)
                    # defect only if majority defected
                    new[i,j] = 0 if defect_count > len(neigh)/2 else 1
                else:  # imitate_best
                    neigh = [
                        ((i+di)%self.n if self.boundary=='periodic' else i+di,
                         (j+dj)%self.n if self.boundary=='periodic' else j+dj)
                        for di in (-1,0,1) for dj in (-1,0,1)
                        if 0 <= i+di < self.n and 0 <= j+dj < self.n
                    ]
                    local_scores = [scores[x,y] for x,y in neigh]
                    max_s = max(local_scores)
                    best = [neigh[k] for k,s in enumerate(local_scores) if s==max_s]
                    x,y = best[np.random.randint(len(best))]
                    new[i,j] = self.prev_grid[x,y]

        self.grid = new

    def calculate_scores(self):
        kernel = np.ones((3,3)) if self.neighborhood=='Moore' else np.array([[0,1,0],[1,1,1],[0,1,0]])
        bdry   = 'wrap' if self.boundary=='periodic' else 'fill'
        cs = convolve2d(self.grid, kernel, mode='same', boundary=bdry)
        ds = self.b * cs
        return np.where(self.grid==1, cs, ds)

    def update_plot(self):
        # transitions only for imitate_best
        if self.strategy_mode == 'imitate_best' and self.prev_grid is not None:
            vis = np.where((self.grid==0)&(self.prev_grid==1),2,
                   np.where((self.grid==1)&(self.prev_grid==0),3,self.grid))
        else:
            vis = self.grid
        self.ax_grid.clear()
        self.ax_grid.imshow(vis, cmap=self.cmap, vmin=0, vmax=3)
        self.ax_grid.set_xticks([]); self.ax_grid.set_yticks([])

        frac = np.mean(self.grid)
        self.ts_data.append(frac)
        self.ts_line.set_data(range(len(self.ts_data)), self.ts_data)
        self.ax_ts.relim(); self.ax_ts.autoscale_view(scalex=True, scaley=False)
        self.ax_ts.set_xlim(0, len(self.ts_data)+1)

        self.canvas.draw()

    def get_cluster_stats(self):
        lab, n = label(self.grid, structure=np.ones((3,3)))
        sizes = [np.sum(lab==i) for i in range(1,n+1)]
        return {
            'avg_c_size': np.mean(sizes) if sizes else 0,
            'max_c_size': np.max(sizes) if sizes else 0,
            'n_clusters': n
        }

    def reset_grid(self):
        # Initialize grids
        self.grid = self.initialize_grid()
        self.ts_data = []
        # For TFT, seed prev_grid as all-cooperate
        if self.strategy_mode == 'tft':
            self.prev_grid = np.ones((self.n, self.n), dtype=int)
        else:
            self.prev_grid = None
        self.update_plot()

    def toggle_boundary(self):
        self.boundary = 'periodic' if self.boundary=='fixed' else 'fixed'
        self.reset_grid()

    def set_preset(self, v):
        self.b_slider.set(v)
        self.on_param_change()

    def set_strategy(self, mode):
        self.strategy_mode = mode
        self.running = False
        self.reset_grid()

    def on_param_change(self):
        self.b = float(self.b_slider.get())
        self.reset_grid()

if __name__=="__main__":
    root = tk.Tk()
    app = EnhancedPDSimulator(root)
    root.mainloop()
