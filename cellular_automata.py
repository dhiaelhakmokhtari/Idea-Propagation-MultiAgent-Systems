import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button
import time

class CellularAutomata:
    def __init__(self, size=50, b=1.8, p_c=0.3):
        self.size = size
        self.b = b
        self.grid = np.random.choice([0, 1], (size, size), p=[1-p_c, p_c])
        self.fig = plt.figure(figsize=(12, 7))
        
        # Main grid plot
        self.ax1 = plt.subplot2grid((4, 2), (0, 0), rowspan=3, colspan=2)
        self.im = self.ax1.imshow(self.grid, cmap='coolwarm', vmin=0, vmax=1)
        self.ax1.set_title("Cellular Automata - Cooperators (Blue) vs Defectors (Red)")
        self.ax1.axis('off')
        
        # History plot
        self.ax2 = plt.subplot2grid((4, 2), (3, 0))
        self.line, = self.ax2.plot([], [], 'b-')
        self.ax2.set_xlim(0, 100)
        self.ax2.set_ylim(0, 1)
        self.ax2.set_title("Cooperator Proportion Over Time")
        self.ax2.set_xlabel("Generations")
        
        # Control panel
        self.ax3 = plt.subplot2grid((4, 2), (3, 1))
        plt.axis('off')
        
        # Sliders
        self.b_slider = Slider(
            plt.axes([0.65, 0.05, 0.3, 0.03]),
            'Defector Power (b)', 1.0, 2.5, valinit=b
        )
        self.speed_slider = Slider(
            plt.axes([0.65, 0.01, 0.3, 0.03]),
            'Speed (steps/sec)', 0.1, 10.0, valinit=2.0
        )
        
        # Simulation control
        self.last_update = time.time()
        self.history = [np.mean(self.grid)]
        self.paused = False
        self.animation = None

    def get_neighbors(self, i, j):
        """Moore neighborhood with periodic boundaries"""
        return [
            ((i-1) % self.size, (j-1) % self.size),
            ((i-1) % self.size, j),
            ((i-1) % self.size, (j+1) % self.size),
            (i, (j-1) % self.size),
            (i, (j+1) % self.size),
            ((i+1) % self.size, (j-1) % self.size),
            ((i+1) % self.size, j),
            ((i+1) % self.size, (j+1) % self.size)
        ]

    def update_grid(self, frame):
        if not self.paused and (time.time() - self.last_update) > (1/self.speed_slider.val):
            new_grid = np.copy(self.grid)
            for i in range(self.size):
                for j in range(self.size):
                    neighbors = self.get_neighbors(i, j)
                    scores = []
                    for ni, nj in neighbors:
                        if self.grid[ni, nj] == 1:  # Cooperators
                            score = sum(self.grid[x,y] == 1 
                                   for x,y in self.get_neighbors(ni, nj))
                        else:  # Defectors
                            score = self.b * sum(self.grid[x,y] == 1 
                                              for x,y in self.get_neighbors(ni, nj))
                        scores.append(score)
                    
                    best_idx = np.argmax(scores)
                    new_grid[i,j] = self.grid[neighbors[best_idx]]
            
            self.grid = new_grid
            self.history.append(np.mean(self.grid))
            self.last_update = time.time()
        
        # Always update display
        self.im.set_data(self.grid)
        self.line.set_data(range(len(self.history)), self.history)
        self.ax2.set_xlim(0, len(self.history)+1)
        return self.im, self.line

    def toggle_pause(self, event):
        self.paused = not self.paused

    def start(self):
        # Add pause button
        pause_ax = plt.axes([0.45, 0.01, 0.1, 0.05])
        pause_button = Button(pause_ax, 'Pause/Resume')
        pause_button.on_clicked(self.toggle_pause)
        
        # Set up animation
        self.animation = FuncAnimation(
            self.fig, self.update_grid, 
            interval=50, blit=True, cache_frame_data=False
        )
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    print("Starting Enhanced Cellular Automata Simulation...")
    print("Features:")
    print("- Speed control slider (steps per second)")
    print("- Defector power adjustment")
    print("- Pause/Resume button")
    automata = CellularAutomata(size=60)
    automata.start()