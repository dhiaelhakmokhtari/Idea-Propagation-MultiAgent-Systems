import numpy as np
from scipy.spatial import distance_matrix

class IrregularSpatialGame:
    def __init__(self, n_agents=500, b=1.8, p_c=0.5, r=2.0):
        self.n_agents = n_agents
        self.b = b
        self.r = r
        self.positions = np.random.rand(n_agents, 2) * 10
        self.strategies = np.random.choice([0,1], size=n_agents, p=[1-p_c, p_c])
        self.history = []
        
    def get_neighbors(self, idx):
        dists = distance_matrix([self.positions[idx]], self.positions)[0]
        return np.where(dists <= self.r)[0]
    
    def calculate_payoff(self, idx):
        neighbors = self.get_neighbors(idx)
        score = 0
        for n in neighbors:
            if self.strategies[idx] == 1 and self.strategies[n] == 1:
                score += 1
            elif self.strategies[idx] == 0 and self.strategies[n] == 1:
                score += self.b
        return score
    
    def update(self):
        new_strategies = np.copy(self.strategies)
        for i in range(self.n_agents):
            neighbors = self.get_neighbors(i)
            scores = [self.calculate_payoff(j) for j in neighbors]
            best_idx = neighbors[np.argmax(scores)]
            new_strategies[i] = self.strategies[best_idx]
            
        self.strategies = new_strategies
        self.history.append(np.copy(self.strategies))
        
    def visualize(self):
        plt.figure(figsize=(8,6))
        plt.scatter(self.positions[:,0], self.positions[:,1], 
                    c=self.strategies, cmap='coolwarm', s=50)
        plt.title(f"Irregular Spatial Game (r={self.r})")
        plt.show()