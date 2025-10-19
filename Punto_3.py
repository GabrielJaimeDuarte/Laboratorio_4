import numpy as np
import matplotlib.pyplot as plt
import random
from matplotlib.patches import Circle, Rectangle

class Flower:
    def __init__(self, flower_id, position, maturity):
        self.id = flower_id
        self.position = np.array(position, dtype=float)
        self.maturity = maturity
        self.pollination_level = 0.0
        self.max_pollination = 100.0
        self.visited = False
    
    def update_maturity(self):
        self.maturity = min(1.0, self.maturity + random.uniform(0.01, 0.03))
    
    def pollinate(self, amount):
        self.pollination_level = min(self.max_pollination, self.pollination_level + amount)
        self.visited = True
        return self.pollination_level >= self.max_pollination

class BeeDrone:
    def __init__(self, drone_id, position, drone_type="worker"):
        self.id = drone_id
        self.position = np.array(position, dtype=float)
        self.drone_type = drone_type
        self.battery = 100.0
        self.max_battery = 100.0
        self.target_flower = None
        self.flowers_pollinated = 0
        self.trips_completed = 0
        self.is_charging = False
        self.charging_station = np.array([25, 25])
        self.velocity = np.random.uniform(-0.5, 0.5, 2)
        self.exploration_radius = 15.0
    
    def update_battery(self):
        if self.is_charging:
            self.battery = min(self.max_battery, self.battery + 15.0)
            if self.battery >= self.max_battery:
                self.is_charging = False
        else:
            self.battery = max(0.0, self.battery - 0.8)
            if self.battery <= 20.0 and not self.is_charging:
                self.is_charging = True
                self.target_flower = None
    
    def move_towards_target(self, target_pos):
        if self.is_charging:
            direction = self.charging_station - self.position
        elif self.target_flower:
            direction = self.target_flower.position - self.position
        else:
            direction = self.velocity
        
        distance = np.linalg.norm(direction)
        if distance > 0:
            direction = direction / distance
        
        self.position += direction * 1.2
        self.position = np.clip(self.position, [0, 0], [50, 50])
        
        if self.is_charging and distance < 2.0:
            self.battery = min(self.max_battery, self.battery + 20.0)
    
    def explore_random(self):
        angle = random.uniform(0, 2 * np.pi)
        distance = random.uniform(0.5, 2.0)
        new_x = self.position[0] + np.cos(angle) * distance
        new_y = self.position[1] + np.sin(angle) * distance
        
        self.position[0] = np.clip(new_x, 0, 50)
        self.position[1] = np.clip(new_y, 0, 50)
    
    def calculate_flower_fitness(self, flower):
        distance = np.linalg.norm(self.position - flower.position)
        maturity_bonus = flower.maturity * 30.0
        pollination_need = (flower.max_pollination - flower.pollination_level) * 0.5
        
        fitness = maturity_bonus + pollination_need - distance * 2.0
        
        if flower.visited:
            fitness *= 0.3
        
        return fitness
    
    def perform_pollination(self, flower):
        if self.target_flower and np.linalg.norm(self.position - self.target_flower.position) < 1.5:
            if flower.pollinate(15.0):
                self.flowers_pollinated += 1
                self.trips_completed += 1
                self.target_flower = None
                return True
        return False

class ABCGreenhouse:
    def __init__(self, width=50, height=50):
        self.width = width
        self.height = height
        self.flowers = []
        self.drones = []
        self.charging_stations = []
        self.iteration = 0
        self.total_pollination = 0.0
        self.max_pollination = 0.0
        self.initialize_environment()
    
    def initialize_environment(self):
        self.flowers = []
        for i in range(30):
            x = random.uniform(5, 45)
            y = random.uniform(5, 45)
            maturity = random.uniform(0.1, 0.9)
            self.flowers.append(Flower(i, (x, y), maturity))
            self.max_pollination += 100.0
        
        num_workers = 8
        num_observers = 4
        num_explorers = 3
        
        for i in range(num_workers):
            pos = [random.uniform(20, 30), random.uniform(20, 30)]
            self.drones.append(BeeDrone(i, pos, "worker"))
        
        for i in range(num_observers):
            pos = [random.uniform(20, 30), random.uniform(20, 30)]
            self.drones.append(BeeDrone(num_workers + i, pos, "observer"))
        
        for i in range(num_explorers):
            pos = [random.uniform(20, 30), random.uniform(20, 30)]
            self.drones.append(BeeDrone(num_workers + num_observers + i, pos, "explorer"))
        
        self.charging_stations = [(25, 25), (10, 10), (40, 40), (10, 40), (40, 10)]
    
    def update_flowers(self):
        for flower in self.flowers:
            flower.update_maturity()
    
    def employed_bee_phase(self):
        workers = [drone for drone in self.drones if drone.drone_type == "worker"]
        
        for drone in workers:
            if drone.is_charging or drone.battery < 25:
                continue
            
            if not drone.target_flower:
                available_flowers = [f for f in self.flowers if f.pollination_level < 100]
                if available_flowers:
                    best_flower = max(available_flowers, key=drone.calculate_flower_fitness)
                    drone.target_flower = best_flower
            
            if drone.target_flower:
                drone.move_towards_target(drone.target_flower.position)
                drone.perform_pollination(drone.target_flower)
            else:
                drone.explore_random()
    
    def onlooker_bee_phase(self):
        observers = [drone for drone in self.drones if drone.drone_type == "observer"]
        workers = [drone for drone in self.drones if drone.drone_type == "worker"]
        
        successful_workers = [w for w in workers if w.flowers_pollinated > 2]
        
        for drone in observers:
            if drone.is_charging or drone.battery < 25:
                continue
            
            if successful_workers and random.random() < 0.7:
                best_worker = max(successful_workers, key=lambda w: w.flowers_pollinated)
                if best_worker.target_flower and not drone.target_flower:
                    drone.target_flower = best_worker.target_flower
            
            if drone.target_flower:
                drone.move_towards_target(drone.target_flower.position)
                if drone.perform_pollination(drone.target_flower):
                    drone.target_flower = None
            else:
                high_maturity_flowers = [f for f in self.flowers if f.maturity > 0.7 and f.pollination_level < 80]
                if high_maturity_flowers:
                    target = random.choice(high_maturity_flowers)
                    drone.target_flower = target
                    drone.move_towards_target(target.position)
                else:
                    drone.explore_random()
    
    def scout_bee_phase(self):
        explorers = [drone for drone in self.drones if drone.drone_type == "explorer"]
        
        for drone in explorers:
            if drone.is_charging or drone.battery < 25:
                continue
            
            if random.random() < 0.3 or not drone.target_flower:
                unexplored_flowers = [f for f in self.flowers if not f.visited and f.maturity > 0.5]
                if unexplored_flowers:
                    drone.target_flower = random.choice(unexplored_flowers)
                else:
                    low_pollination_flowers = [f for f in self.flowers if f.pollination_level < 40]
                    if low_pollination_flowers:
                        drone.target_flower = random.choice(low_pollination_flowers)
            
            if drone.target_flower:
                drone.move_towards_target(drone.target_flower.position)
                drone.perform_pollination(drone.target_flower)
            else:
                drone.explore_random()
    
    def update_drones(self):
        for drone in self.drones:
            drone.update_battery()
    
    def calculate_fitness(self):
        current_pollination = sum(flower.pollination_level for flower in self.flowers)
        self.total_pollination = current_pollination
        
        pollination_rate = current_pollination / self.max_pollination
        
        active_drones = len([d for d in self.drones if not d.is_charging and d.battery > 20])
        efficiency_score = sum(d.flowers_pollinated for d in self.drones) / (self.iteration + 1)
        
        mature_flowers_pollinated = len([f for f in self.flowers if f.maturity > 0.8 and f.pollination_level > 80])
        maturity_score = mature_flowers_pollinated / len([f for f in self.flowers if f.maturity > 0.8])
        
        total_fitness = pollination_rate * 0.5 + efficiency_score * 0.2 + maturity_score * 0.3
        return total_fitness
    
    def simulate_iteration(self):
        self.iteration += 1
        
        self.update_flowers()
        self.employed_bee_phase()
        self.onlooker_bee_phase()
        self.scout_bee_phase()
        self.update_drones()
        
        fitness = self.calculate_fitness()
        return fitness
    
    def visualize(self, ax):
        ax.clear()
        
        ax.set_facecolor('#f0f7e0')
        
        for station in self.charging_stations:
            ax.plot(station[0], station[1], 'ks', markersize=15, markerfacecolor='yellow', markeredgewidth=2)
        
        for flower in self.flowers:
            color_intensity = flower.pollination_level / 100.0
            size = 50 + flower.maturity * 30
            
            if flower.pollination_level >= 100:
                color = 'purple'
            elif flower.maturity > 0.8:
                color = (1.0, 0.5 - color_intensity * 0.3, 0.0)
            elif flower.maturity > 0.5:
                color = (1.0 - color_intensity * 0.5, 0.8, 0.0)
            else:
                color = (0.7, 0.9, 0.3)
            
            ax.plot(flower.position[0], flower.position[1], 'o', 
                   color=color, markersize=size/20, alpha=0.8)
            
            if flower.visited:
                ax.plot(flower.position[0], flower.position[1], 'o', 
                       markersize=size/15, markerfacecolor='none', 
                       markeredgecolor='blue', markeredgewidth=2)
        
        drone_colors = {'worker': 'red', 'observer': 'blue', 'explorer': 'green'}
        
        for drone in self.drones:
            color = drone_colors[drone.drone_type]
            marker = '^' if drone.drone_type == 'worker' else 's' if drone.drone_type == 'observer' else 'D'
            
            ax.plot(drone.position[0], drone.position[1], marker, 
                   color=color, markersize=10, markerfacecolor=color)
            
            if drone.is_charging:
                ax.plot(drone.position[0], drone.position[1], 'o', 
                       markersize=15, markerfacecolor='none', 
                       markeredgecolor='orange', markeredgewidth=2)
            
            if drone.target_flower:
                ax.plot([drone.position[0], drone.target_flower.position[0]],
                       [drone.position[1], drone.target_flower.position[1]],
                       '--', color=color, alpha=0.5, linewidth=1)
            
            battery_color = 'green' if drone.battery > 50 else 'orange' if drone.battery > 25 else 'red'
            ax.text(drone.position[0] + 1, drone.position[1] - 1, 
                   f'{drone.battery:.0f}%', fontsize=8, color=battery_color)
        
        pollination_percentage = (self.total_pollination / self.max_pollination) * 100
        active_drones = len([d for d in self.drones if not d.is_charging])
        total_pollinations = sum(d.flowers_pollinated for d in self.drones)
        
        ax.set_title(f'Sistema de Polinización con ABC\nIteración: {self.iteration} | Polinización: {pollination_percentage:.1f}%\nDrones activos: {active_drones}/{len(self.drones)} | Polinizaciones: {total_pollinations}')
        ax.set_xlabel('X (metros)')
        ax.set_ylabel('Y (metros)')
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.grid(True, alpha=0.3)
        
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='red', label='Obreras'),
            Patch(facecolor='blue', label='Observadoras'),
            Patch(facecolor='green', label='Exploradoras'),
            Patch(facecolor='yellow', label='Estación Carga'),
            Patch(facecolor='purple', label='Flor Polinizada'),
            Patch(facecolor='orange', label='Flor Madura')
        ]
        ax.legend(handles=legend_elements, loc='upper right')

def run_pollination_simulation():
    greenhouse = ABCGreenhouse()
    
    fig, ax = plt.subplots(figsize=(12, 10))
    plt.ion()
    
    fitness_history = []
    pollination_history = []
    active_drones_history = []
    
    max_iterations = 150
    
    for iteration in range(max_iterations):
        fitness = greenhouse.simulate_iteration()
        current_pollination = (greenhouse.total_pollination / greenhouse.max_pollination) * 100
        
        fitness_history.append(fitness)
        pollination_history.append(current_pollination)
        active_drones = len([d for d in greenhouse.drones if not d.is_charging])
        active_drones_history.append(active_drones)
        
        if iteration % 10 == 0:
            print(f"Iteración {iteration}: Fitness={fitness:.3f}, Polinización={current_pollination:.1f}%")
        
        if iteration % 3 == 0:
            greenhouse.visualize(ax)
            plt.pause(0.1)
        
        if current_pollination >= 85:
            print("¡Polinización óptima alcanzada!")
            break
    
    plt.ioff()
    
    print("\n=== RESULTADOS FINALES ===")
    print(f"Total de iteraciones: {greenhouse.iteration}")
    print(f"Polinización final: {pollination_history[-1]:.1f}%")
    print(f"Fitness final: {fitness_history[-1]:.3f}")
    print(f"Total de polinizaciones: {sum(d.flowers_pollinated for d in greenhouse.drones)}")
    print(f"Drones activos promedio: {np.mean(active_drones_history):.1f}")
    
    fully_pollinated = len([f for f in greenhouse.flowers if f.pollination_level >= 100])
    mature_flowers = len([f for f in greenhouse.flowers if f.maturity > 0.8])
    print(f"Flores completamente polinizadas: {fully_pollinated}/{len(greenhouse.flowers)}")
    print(f"Flores maduras: {mature_flowers}/{len(greenhouse.flowers)}")
    
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))
    
    ax1.plot(fitness_history)
    ax1.set_title('Evolución del Fitness')
    ax1.set_xlabel('Iteración')
    ax1.set_ylabel('Fitness')
    ax1.grid(True)
    
    ax2.plot(pollination_history)
    ax2.set_title('Progreso de Polinización')
    ax2.set_xlabel('Iteración')
    ax2.set_ylabel('Polinización (%)')
    ax2.grid(True)
    
    ax3.plot(active_drones_history)
    ax3.set_title('Drones Activos')
    ax3.set_xlabel('Iteración')
    ax3.set_ylabel('Número de Drones Activos')
    ax3.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    return greenhouse, fitness_history, pollination_history

if __name__ == "__main__":
    print("=== SISTEMA DE POLINIZACIÓN CON DRONES-ABEJA ===")
    print("Características:")
    print("- 8 drones obreros, 4 observadores, 3 exploradores")
    print("- 30 flores con diferentes niveles de madurez")
    print("- 5 estaciones de carga automática")
    print("- Algoritmo ABC para optimización de polinización")
    print("- Gestión inteligente de batería")
    
    greenhouse, fitness_history, pollination_history = run_pollination_simulation()
