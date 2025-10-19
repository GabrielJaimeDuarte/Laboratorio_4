import numpy as np
import matplotlib.pyplot as plt
import random
from matplotlib.patches import Rectangle

class Terrain:
    def __init__(self, width=50, height=50):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width))
        self.survivors = []
        self.resources = []
        self.obstacles = []
        self.dynamic_obstacles = []
        self.initialize_terrain()
    
    def initialize_terrain(self):
        self.survivors = [(10, 15), (35, 40), (45, 10), (15, 35), (40, 25)]
        self.resources = [(5, 5), (45, 45), (25, 25), (10, 40), (40, 5)]
        
        static_obstacles = [(20, 20, 8, 8), (30, 10, 6, 6), (10, 30, 5, 5)]
        for x, y, w, h in static_obstacles:
            self.obstacles.append((x, y, w, h))
            for i in range(x, x + w):
                for j in range(y, y + h):
                    if 0 <= i < self.width and 0 <= j < self.height:
                        self.grid[j, i] = 1
    
    def add_dynamic_obstacle(self, x, y, width, height):
        obstacle = {'pos': (x, y), 'size': (width, height), 'active': True}
        self.dynamic_obstacles.append(obstacle)
        for i in range(x, x + width):
            for j in range(y, y + height):
                if 0 <= i < self.width and 0 <= j < self.height:
                    self.grid[j, i] = 2
    
    def remove_dynamic_obstacle(self, index):
        if 0 <= index < len(self.dynamic_obstacles):
            obstacle = self.dynamic_obstacles[index]
            x, y = obstacle['pos']
            w, h = obstacle['size']
            for i in range(x, x + w):
                for j in range(y, y + h):
                    if 0 <= i < self.width and 0 <= j < self.height and self.grid[j, i] == 2:
                        self.grid[j, i] = 0
            self.dynamic_obstacles.pop(index)
    
    def is_obstacle(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        return self.grid[y, x] in [1, 2]
    
    def get_survivor_at(self, x, y):
        for i, (sx, sy) in enumerate(self.survivors):
            if abs(sx - x) <= 1 and abs(sy - y) <= 1:
                return i
        return -1
    
    def get_resource_at(self, x, y):
        for i, (rx, ry) in enumerate(self.resources):
            if abs(rx - x) <= 1 and abs(ry - y) <= 1:
                return i
        return -1
    
    def rescue_survivor(self, index):
        if 0 <= index < len(self.survivors):
            return self.survivors.pop(index)
        return None
    
    def collect_resource(self, index):
        if 0 <= index < len(self.resources):
            return self.resources.pop(index)
        return None

class AntDrone:
    def __init__(self, drone_id, start_pos, terrain):
        self.id = drone_id
        self.position = np.array(start_pos, dtype=float)
        self.path = [start_pos]
        self.carrying_survivor = False
        self.carrying_resource = False
        self.energy = 100
        self.found_targets = []
        self.terrain = terrain
        self.last_pheromone_drop = 0
    
    def move_towards(self, target_pos, pheromone_map):
        current_x, current_y = int(self.position[0]), int(self.position[1])
        target_x, target_y = target_pos
        
        possible_moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                new_x, new_y = current_x + dx, current_y + dy
                
                if not self.terrain.is_obstacle(new_x, new_y):
                    distance_to_target = np.sqrt((new_x - target_x)**2 + (new_y - target_y)**2)
                    pheromone_level = pheromone_map[new_y, new_x]
                    
                    attractiveness = (1.0 / (distance_to_target + 0.1)) + pheromone_level * 2.0
                    possible_moves.append(((new_x, new_y), attractiveness))
        
        if possible_moves:
            positions, attractions = zip(*possible_moves)
            total_attraction = sum(attractions)
            probabilities = [att / total_attraction for att in attractions]
            
            chosen_index = np.random.choice(len(positions), p=probabilities)
            new_pos = positions[chosen_index]
            
            self.position = np.array(new_pos, dtype=float)
            self.path.append(new_pos)
            self.energy -= 1
            
            return True
        return False
    
    def explore_random(self, pheromone_map):
        current_x, current_y = int(self.position[0]), int(self.position[1])
        
        possible_moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                new_x, new_y = current_x + dx, current_y + dy
                
                if not self.terrain.is_obstacle(new_x, new_y):
                    pheromone_level = pheromone_map[new_y, new_x]
                    exploration_bonus = 2.0 if pheromone_level < 0.1 else 0.1
                    
                    attractiveness = exploration_bonus + random.random() * 0.5
                    possible_moves.append(((new_x, new_y), attractiveness))
        
        if possible_moves:
            positions, attractions = zip(*possible_moves)
            total_attraction = sum(attractions)
            probabilities = [att / total_attraction for att in attractions]
            
            chosen_index = np.random.choice(len(positions), p=probabilities)
            new_pos = positions[chosen_index]
            
            self.position = np.array(new_pos, dtype=float)
            self.path.append(new_pos)
            self.energy -= 1
            
            return True
        return False
    
    def check_for_targets(self):
        x, y = int(self.position[0]), int(self.position[1])
        
        survivor_idx = self.terrain.get_survivor_at(x, y)
        if survivor_idx != -1 and not self.carrying_survivor:
            self.found_targets.append(('survivor', self.terrain.survivors[survivor_idx]))
            return 'survivor', survivor_idx
        
        resource_idx = self.terrain.get_resource_at(x, y)
        if resource_idx != -1 and not self.carrying_resource:
            self.found_targets.append(('resource', self.terrain.resources[resource_idx]))
            return 'resource', resource_idx
        
        return None, -1

class ACORescueSystem:
    def __init__(self, terrain, num_drones=10):
        self.terrain = terrain
        self.num_drones = num_drones
        self.drones = []
        self.pheromone_map = np.zeros((terrain.height, terrain.width))
        self.base_position = (5, 5)
        self.iteration = 0
        self.rescued_survivors = 0
        self.collected_resources = 0
        self.total_coverage = set()
        
        self.initialize_drones()
    
    def initialize_drones(self):
        for i in range(self.num_drones):
            start_pos = (self.base_position[0] + random.randint(-2, 2), 
                        self.base_position[1] + random.randint(-2, 2))
            self.drones.append(AntDrone(i, start_pos, self.terrain))
    
    def update_pheromones(self):
        self.pheromone_map *= 0.95
        
        for drone in self.drones:
            path_length = len(drone.path)
            if path_length > 1:
                pheromone_strength = 10.0 / path_length
                
                for pos in drone.path[-10:]:
                    x, y = int(pos[0]), int(pos[1])
                    if 0 <= x < self.terrain.width and 0 <= y < self.terrain.height:
                        self.pheromone_map[y, x] += pheromone_strength
        
        self.pheromone_map = np.clip(self.pheromone_map, 0, 50)
    
    def get_nearest_target(self, drone_pos, target_type='survivor'):
        if target_type == 'survivor':
            targets = self.terrain.survivors
        else:
            targets = self.terrain.resources
        
        if not targets:
            return None
        
        min_dist = float('inf')
        nearest_target = None
        
        for target in targets:
            dist = np.sqrt((drone_pos[0] - target[0])**2 + (drone_pos[1] - target[1])**2)
            if dist < min_dist:
                min_dist = dist
                nearest_target = target
        
        return nearest_target
    
    def simulate_iteration(self):
        self.iteration += 1
        
        if self.iteration % 50 == 0 and len(self.terrain.dynamic_obstacles) < 3:
            x = random.randint(10, 40)
            y = random.randint(10, 40)
            w = random.randint(3, 8)
            h = random.randint(3, 8)
            self.terrain.add_dynamic_obstacle(x, y, w, h)
            print(f"¡Nuevo obstáculo dinámico apareció en ({x}, {y})!")
        
        if self.iteration % 80 == 0 and self.terrain.dynamic_obstacles:
            idx = random.randint(0, len(self.terrain.dynamic_obstacles) - 1)
            self.terrain.remove_dynamic_obstacle(idx)
            print("¡Obstáculo dinámico removido!")
        
        for drone in self.drones:
            if drone.energy <= 0:
                drone.position = np.array(self.base_position, dtype=float)
                drone.path = [tuple(drone.position)]
                drone.energy = 100
                drone.carrying_survivor = False
                drone.carrying_resource = False
                continue
            
            target_type, target_idx = drone.check_for_targets()
            
            if target_type == 'survivor' and not drone.carrying_survivor:
                rescued = self.terrain.rescue_survivor(target_idx)
                if rescued:
                    drone.carrying_survivor = True
                    self.rescued_survivors += 1
                    print(f"¡Drone {drone.id} rescató superviviente en {rescued}!")
            
            elif target_type == 'resource' and not drone.carrying_resource:
                resource = self.terrain.collect_resource(target_idx)
                if resource:
                    drone.carrying_resource = True
                    self.collected_resources += 1
                    drone.energy += 30
                    print(f"¡Drone {drone.id} recolectó recurso en {resource}!")
            
            if drone.carrying_survivor or drone.carrying_resource:
                success = drone.move_towards(self.base_position, self.pheromone_map)
                if success and np.linalg.norm(drone.position - self.base_position) < 3:
                    if drone.carrying_survivor:
                        print(f"Drone {drone.id} entregó superviviente en base!")
                    if drone.carrying_resource:
                        print(f"Drone {drone.id} entregó recurso en base!")
                    drone.carrying_survivor = False
                    drone.carrying_resource = False
                    drone.energy = 100
            
            else:
                nearest_survivor = self.get_nearest_target(drone.position, 'survivor')
                nearest_resource = self.get_nearest_target(drone.position, 'resource')
                
                if nearest_survivor and random.random() < 0.7:
                    drone.move_towards(nearest_survivor, self.pheromone_map)
                elif nearest_resource and drone.energy < 50:
                    drone.move_towards(nearest_resource, self.pheromone_map)
                else:
                    drone.explore_random(self.pheromone_map)
            
            self.total_coverage.add((int(drone.position[0]), int(drone.position[1])))
        
        self.update_pheromones()
        
        coverage_percentage = len(self.total_coverage) / (self.terrain.width * self.terrain.height) * 100
        
        return coverage_percentage
    
    def calculate_fitness(self):
        coverage_score = len(self.total_coverage) / (self.terrain.width * self.terrain.height)
        rescue_score = self.rescued_survivors / 5.0
        resource_score = self.collected_resources / 5.0
        
        total_fitness = coverage_score * 0.4 + rescue_score * 0.4 + resource_score * 0.2
        return total_fitness
    
    def visualize(self, ax):
        ax.clear()
        
        ax.imshow(self.pheromone_map, cmap='YlOrBr', alpha=0.6, extent=[0, self.terrain.width, 0, self.terrain.height])
        
        for obstacle in self.terrain.obstacles:
            x, y, w, h = obstacle
            ax.add_patch(Rectangle((x, y), w, h, color='gray', alpha=0.7))
        
        for obstacle in self.terrain.dynamic_obstacles:
            x, y = obstacle['pos']
            w, h = obstacle['size']
            ax.add_patch(Rectangle((x, y), w, h, color='red', alpha=0.7))
        
        for survivor in self.terrain.survivors:
            ax.plot(survivor[0], survivor[1], 'ro', markersize=8, label='Supervivientes' if survivor == self.terrain.survivors[0] else "")
        
        for resource in self.terrain.resources:
            ax.plot(resource[0], resource[1], 'bs', markersize=8, label='Recursos' if resource == self.terrain.resources[0] else "")
        
        ax.plot(self.base_position[0], self.base_position[1], 'g^', markersize=12, label='Base')
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(self.drones)))
        for i, drone in enumerate(self.drones):
            x, y = drone.position
            color = colors[i]
            
            ax.plot(x, y, 'o', color=color, markersize=8)
            
            if len(drone.path) > 1:
                path_x, path_y = zip(*drone.path[-20:])
                ax.plot(path_x, path_y, '-', color=color, alpha=0.5, linewidth=1)
            
            if drone.carrying_survivor:
                ax.plot(x, y, 'o', color=color, markersize=12, markerfacecolor='none', markeredgewidth=2)
            if drone.carrying_resource:
                ax.plot(x, y, 's', color=color, markersize=10, markerfacecolor='none', markeredgewidth=2)
        
        coverage = len(self.total_coverage) / (self.terrain.width * self.terrain.height) * 100
        ax.set_title(f'Operación de Rescate ACO\nIteración: {self.iteration} | Cobertura: {coverage:.1f}%\nSupervivientes rescatados: {self.rescued_survivors} | Recursos: {self.collected_resources}')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, self.terrain.width)
        ax.set_ylim(0, self.terrain.height)

def run_rescue_simulation():
    terrain = Terrain(50, 50)
    aco_system = ACORescueSystem(terrain, num_drones=8)
    
    fig, ax = plt.subplots(figsize=(12, 10))
    plt.ion()
    
    fitness_history = []
    coverage_history = []
    
    max_iterations = 200
    
    for iteration in range(max_iterations):
        coverage = aco_system.simulate_iteration()
        fitness = aco_system.calculate_fitness()
        
        fitness_history.append(fitness)
        coverage_history.append(coverage)
        
        if iteration % 10 == 0:
            print(f"Iteración {iteration}: Fitness={fitness:.3f}, Cobertura={coverage:.1f}%")
        
        if iteration % 5 == 0:
            aco_system.visualize(ax)
            plt.pause(0.1)
        
        if aco_system.rescued_survivors >= 5 and aco_system.collected_resources >= 5:
            print("¡Misión completada!")
            break
    
    plt.ioff()
    
    print("\n=== RESULTADOS FINALES ===")
    print(f"Total de iteraciones: {aco_system.iteration}")
    print(f"Supervivientes rescatados: {aco_system.rescued_survivors}/5")
    print(f"Recursos recolectados: {aco_system.collected_resources}/5")
    print(f"Cobertura del terreno: {coverage_history[-1]:.1f}%")
    print(f"Fitness final: {fitness_history[-1]:.3f}")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    ax1.plot(fitness_history)
    ax1.set_title('Evolución del Fitness')
    ax1.set_xlabel('Iteración')
    ax1.set_ylabel('Fitness')
    ax1.grid(True)
    
    ax2.plot(coverage_history)
    ax2.set_title('Cobertura del Terreno')
    ax2.set_xlabel('Iteración')
    ax2.set_ylabel('Cobertura (%)')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    return aco_system, fitness_history, coverage_history

if __name__ == "__main__":
    print("=== SISTEMA DE RESCATE CON DRONES-HORMIGA ===")
    print("Características:")
    print("- 8 drones exploradores")
    print("- 5 supervivientes y 5 recursos")
    print("- Obstáculos estáticos y dinámicos")
    print("- Mapa de feromonas en tiempo real")
    print("- Algoritmo ACO para optimización de rutas")
    
    aco_system, fitness_history, coverage_history = run_rescue_simulation()
