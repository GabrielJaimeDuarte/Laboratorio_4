import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
import time

class Drone:
    def __init__(self, drone_id, position):
        self.id = drone_id
        self.position = np.array(position, dtype=float)
        self.velocity = np.random.uniform(-0.1, 0.1, 3)
        self.best_position = self.position.copy()
        self.best_fitness = float('inf')
        self.active = True
    
    def update_velocity(self, global_best_position, w=0.7, c1=1.5, c2=1.5):
        r1, r2 = random.random(), random.random()
        cognitive_component = c1 * r1 * (self.best_position - self.position)
        social_component = c2 * r2 * (global_best_position - self.position)
        self.velocity = w * self.velocity + cognitive_component + social_component
        max_velocity = 0.5
        velocity_norm = np.linalg.norm(self.velocity)
        if velocity_norm > max_velocity:
            self.velocity = (self.velocity / velocity_norm) * max_velocity
    
    def update_position(self):
        if self.active:
            self.position += self.velocity
            self.position = np.clip(self.position, [-15, -15, 0], [15, 15, 25])

class Obstacle:
    def __init__(self, position, radius):
        self.position = np.array(position, dtype=float)
        self.radius = radius

class PSODroneSwarm:
    def __init__(self, num_drones=25):
        self.num_drones = num_drones
        self.drones = []
        self.obstacles = []
        self.global_best_position = None
        self.global_best_fitness = float('inf')
        self.figures = {
            'star': self._create_star_formation(),
            'dragon': self._create_dragon_formation(),
            'robot': self._create_robot_formation()
        }
        self.current_figure = 'star'
        self.failed_drones = set()
        self.initialize_swarm()
        self.create_obstacles()
    
    def create_obstacles(self):
        self.obstacles.append(Obstacle([0, 0, 8], 2.0))
        self.obstacles.append(Obstacle([5, 5, 12], 1.5))
        self.obstacles.append(Obstacle([-4, -3, 15], 1.8))
        self.obstacles.append(Obstacle([3, -4, 6], 2.2))
    
    def initialize_swarm(self):
        for i in range(self.num_drones):
            position = np.random.uniform(-8, 8, 3)
            position[2] = np.random.uniform(3, 12)
            self.drones.append(Drone(i, position))
        self._update_global_best()
    
    def _create_star_formation(self):
        points = []
        for i in range(8):
            angle = 2 * np.pi * i / 8
            x_out = 5 * np.cos(angle)
            y_out = 5 * np.sin(angle)
            points.append([x_out, y_out, 12])
            angle_inner = angle + np.pi / 8
            x_in = 3 * np.cos(angle_inner)
            y_in = 3 * np.sin(angle_inner)
            points.append([x_in, y_in, 12])
        return np.array(points)
    
    def _create_dragon_formation(self):
        points = []
        t = np.linspace(0, 6*np.pi, self.num_drones)
        for i in range(self.num_drones):
            x = 4 * np.sin(t[i]) * np.cos(0.3*t[i])
            y = 4 * np.sin(t[i]) * np.sin(0.3*t[i])
            z = 10 + 3 * np.cos(t[i])
            points.append([x, y, z])
        return np.array(points)
    
    def _create_robot_formation(self):
        points = []
        head_points = [[-1.5, -1.5, 16], [1.5, -1.5, 16], [1.5, 1.5, 16], [-1.5, 1.5, 16]]
        body_points = [[-2.5, -1.5, 10], [2.5, -1.5, 10], [2.5, 1.5, 10], [-2.5, 1.5, 10]]
        arm_points = [[-4, -3, 13], [-2.5, -3, 13], [-4, 3, 13], [2.5, 3, 13], [4, -3, 13], [4, 3, 13]]
        leg_points = [[-1.5, -1.5, 8], [1.5, -1.5, 8], [-1.5, -1.5, 10], [1.5, -1.5, 10]]
        all_points = head_points + body_points + arm_points + leg_points
        while len(all_points) < self.num_drones:
            all_points.extend(all_points[:self.num_drones - len(all_points)])
        return np.array(all_points[:self.num_drones])
    
    def fitness_function(self, drone, target_points):
        if not drone.active:
            return float('inf')
        
        target_point = target_points[drone.id % len(target_points)]
        distance_fitness = np.linalg.norm(drone.position - target_point)
        
        collision_penalty = 0
        min_safe_distance = 1.2
        for other in self.drones:
            if other.id != drone.id and other.active:
                distance = np.linalg.norm(drone.position - other.position)
                if distance < min_safe_distance:
                    collision_penalty += (min_safe_distance - distance) * 15
        
        obstacle_penalty = 0
        for obstacle in self.obstacles:
            distance_to_obstacle = np.linalg.norm(drone.position - obstacle.position)
            if distance_to_obstacle < obstacle.radius:
                obstacle_penalty += (obstacle.radius - distance_to_obstacle) * 20
        
        energy_penalty = np.linalg.norm(drone.velocity) * 0.1
        
        total_fitness = distance_fitness + collision_penalty + obstacle_penalty + energy_penalty
        return total_fitness
    
    def _update_global_best(self):
        target_points = self.figures[self.current_figure]
        active_drones = [drone for drone in self.drones if drone.active]
        
        if not active_drones:
            return
        
        for drone in active_drones:
            fitness = self.fitness_function(drone, target_points)
            if fitness < drone.best_fitness:
                drone.best_fitness = fitness
                drone.best_position = drone.position.copy()
            if fitness < self.global_best_fitness:
                self.global_best_fitness = fitness
                self.global_best_position = drone.position.copy()
    
    def avoid_collisions_and_obstacles(self):
        for i, drone1 in enumerate(self.drones):
            if not drone1.active:
                continue
                
            for j, drone2 in enumerate(self.drones[i+1:], i+1):
                if not drone2.active:
                    continue
                    
                distance = np.linalg.norm(drone1.position - drone2.position)
                min_distance = 1.0
                if distance < min_distance:
                    repulsion_dir = drone1.position - drone2.position
                    if np.linalg.norm(repulsion_dir) > 0:
                        repulsion_dir = repulsion_dir / np.linalg.norm(repulsion_dir)
                    repulsion_force = (min_distance - distance) * 0.2
                    drone1.velocity += repulsion_dir * repulsion_force
                    drone2.velocity -= repulsion_dir * repulsion_force
            
            for obstacle in self.obstacles:
                distance_to_obstacle = np.linalg.norm(drone1.position - obstacle.position)
                if distance_to_obstacle < obstacle.radius + 0.5:
                    avoidance_dir = drone1.position - obstacle.position
                    if np.linalg.norm(avoidance_dir) > 0:
                        avoidance_dir = avoidance_dir / np.linalg.norm(avoidance_dir)
                    avoidance_force = (obstacle.radius + 0.5 - distance_to_obstacle) * 0.3
                    drone1.velocity += avoidance_dir * avoidance_force
    
    def adapt_to_failures(self):
        active_drones = [drone for drone in self.drones if drone.active]
        if len(active_drones) < self.num_drones:
            target_points = self.figures[self.current_figure]
            active_indices = [i for i, drone in enumerate(self.drones) if drone.active]
            
            for i, drone in enumerate(self.drones):
                if not drone.active:
                    continue
                
                current_target_idx = i % len(target_points)
                nearest_active = min(active_indices, key=lambda x: abs(x - current_target_idx))
                adjusted_target_idx = nearest_active % len(target_points)
    
    def simulate_random_failure(self):
        if random.random() < 0.02 and len(self.failed_drones) < self.num_drones // 3:
            active_drones = [drone for drone in self.drones if drone.active]
            if active_drones:
                failed_drone = random.choice(active_drones)
                failed_drone.active = False
                self.failed_drones.add(failed_drone.id)
                print(f"¡Drone {failed_drone.id} ha fallado! Drones activos: {len(active_drones)-1}")
                self.adapt_to_failures()
    
    def update_formation(self, target_figure=None):
        if target_figure:
            self.current_figure = target_figure
        
        self.simulate_random_failure()
        
        target_points = self.figures[self.current_figure]
        active_drones = [drone for drone in self.drones if drone.active]
        
        if not active_drones:
            return 0, 0
        
        for drone in active_drones:
            drone.update_velocity(self.global_best_position)
            drone.update_position()
        
        self.avoid_collisions_and_obstacles()
        self._update_global_best()
        
        return self.calculate_formation_quality(target_points)
    
    def calculate_formation_quality(self, target_points):
        total_error = 0
        active_count = 0
        for i, drone in enumerate(self.drones):
            if drone.active:
                target_point = target_points[i % len(target_points)]
                total_error += np.linalg.norm(drone.position - target_point)
                active_count += 1
        
        if active_count == 0:
            return 0, 0
        
        avg_error = total_error / active_count
        
        collisions = 0
        for i, drone1 in enumerate(self.drones):
            if not drone1.active:
                continue
            for drone2 in self.drones[i+1:]:
                if drone2.active and np.linalg.norm(drone1.position - drone2.position) < 1.0:
                    collisions += 1
        
        return avg_error, collisions
    
    def visualize_formation(self, iteration, ax):
        ax.clear()
        
        active_positions = []
        inactive_positions = []
        for drone in self.drones:
            if drone.active:
                active_positions.append(drone.position)
            else:
                inactive_positions.append(drone.position)
        
        if active_positions:
            active_positions = np.array(active_positions)
            ax.scatter(active_positions[:, 0], active_positions[:, 1], active_positions[:, 2], 
                      c='green', s=60, label='Drones Activos', alpha=0.8)
        
        if inactive_positions:
            inactive_positions = np.array(inactive_positions)
            ax.scatter(inactive_positions[:, 0], inactive_positions[:, 1], inactive_positions[:, 2], 
                      c='red', s=40, label='Drones Fallados', alpha=0.6, marker='x')
        
        target_points = self.figures[self.current_figure]
        ax.scatter(target_points[:, 0], target_points[:, 1], target_points[:, 2],
                  c='blue', s=40, label='Objetivo', alpha=0.6)
        
        for obstacle in self.obstacles:
            u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
            x = obstacle.position[0] + obstacle.radius * np.cos(u) * np.sin(v)
            y = obstacle.position[1] + obstacle.radius * np.sin(u) * np.sin(v)
            z = obstacle.position[2] + obstacle.radius * np.cos(v)
            ax.plot_surface(x, y, z, color='orange', alpha=0.3)
        
        for i, drone in enumerate(self.drones):
            if drone.active:
                target_point = target_points[i % len(target_points)]
                ax.plot([drone.position[0], target_point[0]],
                       [drone.position[1], target_point[1]],
                       [drone.position[2], target_point[2]], 
                       'gray', alpha=0.2, linewidth=0.5)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'Show de Drones - {self.current_figure.capitalize()}\nIteración: {iteration} - Activos: {len([d for d in self.drones if d.active])}/{self.num_drones}')
        ax.legend()
        ax.set_xlim([-15, 15])
        ax.set_ylim([-15, 15])
        ax.set_zlim([0, 25])
    
    def run_animated_show(self, total_iterations=300):
        fig = plt.figure(figsize=(15, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        figures_sequence = ['star', 'dragon', 'robot']
        iterations_per_figure = total_iterations // len(figures_sequence)
        
        current_figure_index = 0
        iteration_count = 0
        
        plt.ion()
        
        results = {}
        
        while iteration_count < total_iterations:
            if iteration_count % iterations_per_figure == 0 and current_figure_index < len(figures_sequence):
                self.current_figure = figures_sequence[current_figure_index]
                current_figure_index += 1
            
            error, collisions = self.update_formation()
            
            self.visualize_formation(iteration_count, ax)
            
            figure_name = self.current_figure
            if figure_name not in results:
                results[figure_name] = {'errors': [], 'collisions': []}
            
            results[figure_name]['errors'].append(error)
            results[figure_name]['collisions'].append(collisions)
            
            if iteration_count % 10 == 0:
                active_drones = len([d for d in self.drones if d.active])
                print(f"Iteración {iteration_count}: {self.current_figure} - Error: {error:.3f}, Colisiones: {collisions}, Activos: {active_drones}")
            
            plt.pause(0.05)
            iteration_count += 1
        
        plt.ioff()
        
        print("\n=== RESUMEN FINAL ===")
        for figure, data in results.items():
            if data['errors']:
                final_error = data['errors'][-1]
                avg_error = np.mean(data['errors'])
                max_collisions = max(data['collisions'])
                final_collisions = data['collisions'][-1]
                print(f"\n{figure.upper()}:")
                print(f"  Error final: {final_error:.3f}")
                print(f"  Error promedio: {avg_error:.3f}")
                print(f"  Colisiones finales: {final_collisions}")
                print(f"  Máximo de colisiones: {max_collisions}")
        
        plt.show()
        return results

def main():
    print("=== SHOW DE DRONES CON TOLERANCIA A FALLOS ===")
    print("Características:")
    print("- 25 drones en formación")
    print("- 4 obstáculos evitables")
    print("- Tolerancia a fallos de drones")
    print("- Figuras: Estrella → Dragón → Robot")
    print("- Animación en tiempo real")
    
    swarm = PSODroneSwarm(num_drones=25)
    results = swarm.run_animated_show(total_iterations=300)

if __name__ == "__main__":
    main()
