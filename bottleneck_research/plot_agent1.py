import matplotlib.pyplot as plt
import math
import os

def plot_agent_path(file_path, agent_id):
    x_coords = []
    y_coords = []
    
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 4:
                curr_id = int(parts[0])
                if curr_id == agent_id:
                    x_coords.append(float(parts[2]))
                    y_coords.append(float(parts[3]))
                elif curr_id > agent_id:
                    # Since files are usually sorted by ID, we can stop early
                    break

    if not x_coords:
        print(f"No data found for agent {agent_id}")
        return

    # Calculate total distance
    total_distance = 0
    for i in range(1, len(x_coords)):
        dx = x_coords[i] - x_coords[i-1]
        dy = y_coords[i] - y_coords[i-1]
        total_distance += math.sqrt(dx**2 + dy**2)

    # Plotting
    plt.figure(figsize=(10, 8))
    plt.plot(x_coords, y_coords, marker='o', markersize=2, linestyle='-', linewidth=1, label=f'Agent {agent_id} Path')
    plt.scatter([x_coords[0]], [y_coords[0]], color='green', label='Start', zorder=5)
    plt.scatter([x_coords[-1]], [y_coords[-1]], color='red', label='End', zorder=5)
    
    plt.title(f'Path of Agent {agent_id}\nTotal Distance Traveled: {total_distance:.2f} cm')
    plt.xlabel('X (cm)')
    plt.ylabel('Y (cm)')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    
    output_path = os.path.join(os.path.dirname(file_path), f'agent{agent_id}_path.png')
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")
    print(f"Total distance traveled by Agent {agent_id}: {total_distance:.2f} cm")

if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, '09.txt')
    plot_agent_path(data_file, 1)
