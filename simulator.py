import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.animation import FuncAnimation

class SpatialGame:
    def __init__(self, grid_size=100, b=1.8, p_c=0.5, 
                 neighborhood='moore', boundary='fixed'):
        self.grid_size = grid_size
        self.b = b
        self.neighborhood = neighborhood
        self.boundary = boundary
        self.grid = np.random.choice([0, 1], size=(grid_size, grid_size), 
                    p=[1-p_c, p_c])
        self.history = []
        self.c_proportions = []
        
        # Create data directory if not exists
        if not os.path.exists('data'):
            os.makedirs('data')

    def get_neighbors(self, i, j):
        """Get neighbor indices based on neighborhood type"""
        if self.neighborhood == 'moore':
            neighbors = [(i-1, j-1), (i-1, j), (i-1, j+1),
                         (i, j-1),   (i, j),   (i, j+1),
                         (i+1, j-1), (i+1, j), (i+1, j+1)]
        else:  # von Neumann
            neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1), (i, j)]
            
        valid = []
        for ni, nj in neighbors:
            if self.boundary == 'periodic':
                valid.append((ni % self.grid_size, nj % self.grid_size))
            elif 0 <= ni < self.grid_size and 0 <= nj < self.grid_size:
                valid.append((ni, nj))
        return valid

    def calculate_payoff(self, grid):
        scores = np.zeros_like(grid, dtype=float)
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                neighbors = self.get_neighbors(i, j)
                score = 0
                for ni, nj in neighbors:
                    if grid[i,j] == 1 and grid[ni,nj] == 1:
                        score += 1
                    elif grid[i,j] == 0 and grid[ni,nj] == 1:
                        score += self.b
                scores[i,j] = score
        return scores

    def update(self):
        scores = self.calculate_payoff(self.grid)
        new_grid = np.copy(self.grid)
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                neighbors = self.get_neighbors(i, j)
                max_score = -np.inf
                best_strategy = self.grid[i,j]
                
                for ni, nj in neighbors:
                    if scores[ni, nj] > max_score:
                        max_score = scores[ni, nj]
                        best_strategy = self.grid[ni, nj]
                        
                new_grid[i,j] = best_strategy
                
        self.grid = new_grid
        self.history.append(self.grid.copy())
        self.c_proportions.append(np.mean(self.grid))
        
    def run(self, steps=100):
        for _ in range(steps):
            self.update()
            
    def visualize(self, save=False):
        plt.figure(figsize=(12,5))
        
        plt.subplot(1,2,1)
        plt.imshow(self.grid, cmap='coolwarm', vmin=0, vmax=1)
        plt.title(f"Final State (b={self.b})")
        
        plt.subplot(1,2,2)
        plt.plot(self.c_proportions)
        plt.xlabel("Generation")
        plt.ylabel("Cooperators Proportion")
        plt.ylim(0,1)
        
        if save:
            plt.savefig(f'data/simulation_b{self.b}.png')
        plt.show()
        
    def save_results(self):
        np.save('data/grid_history.npy', np.array(self.history))
        np.save('data/c_proportions.npy', np.array(self.c_proportions))

if __name__ == "__main__":
    sim = SpatialGame(grid_size=50, b=1.8, p_c=0.5)
    sim.run(steps=100)
    sim.visualize(save=True)
    sim.save_results()