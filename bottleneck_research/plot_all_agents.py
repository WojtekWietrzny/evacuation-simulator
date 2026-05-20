import matplotlib.pyplot as plt
import math
import os
import matplotlib.cm as cm
import numpy as np

def plot_all_agents(file_path):
    agents_data = {}
    
    # Read the data and group by agent ID
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 4:
                agent_id = int(parts[0])
                x = float(parts[2])
                y = float(parts[3])
                
                if agent_id not in agents_data:
                    agents_data[agent_id] = {'x': [], 'y': []}
                
                agents_data[agent_id]['x'].append(x)
                agents_data[agent_id]['y'].append(y)

    if not agents_data:
        print("No agent data found.")
        return

    plt.figure(figsize=(12, 10))
    
    # Use a colormap for different agents
    num_agents = len(agents_data)
    colors = cm.rainbow(np.linspace(0, 1, num_agents))
    
    total_distances = {}

    for i, (agent_id, coords) in enumerate(sorted(agents_data.items())):
        x_coords = coords['x']
        y_coords = coords['y']
        
        # Calculate distance
        distance = 0
        for j in range(1, len(x_coords)):
            dx = x_coords[j] - x_coords[j-1]
            dy = y_coords[j] - y_coords[j-1]
            distance += math.sqrt(dx**2 + dy**2)
        
        total_distances[agent_id] = distance
        
        # Plot path
        plt.plot(x_coords, y_coords, color=colors[i], alpha=0.6, linewidth=0.8)
        # Mark starts and ends with smaller markers
        plt.scatter(x_coords[0], y_coords[0], color=colors[i], marker='o', s=10)
        plt.scatter(x_coords[-1], y_coords[-1], color=colors[i], marker='x', s=10)

    plt.title(f'Trajectories of All Agents ({num_agents} total)\nFrom: {os.path.basename(file_path)}')
    plt.xlabel('X (cm)')
    plt.ylabel('Y (cm)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.axis('equal')
    
    output_path = os.path.join(os.path.dirname(file_path), 'all_agents_paths.png')
    plt.savefig(output_path, dpi=300)
    print(f"Plot saved to {output_path}")
    
    # Print summary of distances
    print("\nDistance Traveled Summary (Top 5 agents by distance):")
    sorted_distances = sorted(total_distances.items(), key=lambda x: x[1], reverse=True)
    for agent_id, dist in sorted_distances[:5]:
        print(f"Agent {agent_id}: {dist:.2f} cm")
    
    avg_dist = sum(total_distances.values()) / num_agents
    print(f"\nAverage Distance: {avg_dist:.2f} cm")
    print(f"Number of Agents: {num_agents}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, '09.txt')
    plot_all_agents(data_file)
