import math
import os

def calculate_average_y_distance(file_path):
    agents_data = {}
    
    # Read the data and group by agent ID
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 4:
                agent_id = int(parts[0])
                y = float(parts[3])
                
                if agent_id not in agents_data:
                    agents_data[agent_id] = []
                
                agents_data[agent_id].append(y)

    if not agents_data:
        print("No agent data found.")
        return

    y_distances = {}

    for agent_id, y_coords in agents_data.items():
        # Calculate total distance along Y axis (sum of absolute differences)
        y_dist = 0
        for i in range(1, len(y_coords)):
            y_dist += abs(y_coords[i] - y_coords[i-1])
        
        y_distances[agent_id] = y_dist

    num_agents = len(y_distances)
    avg_y_dist = sum(y_distances.values()) / num_agents
    
    print(f"Analysis of Y-axis distance for {num_agents} agents:")
    print(f"Average Y-axis distance: {avg_y_dist:.2f} cm")
    
    # Optional: print top 5
    print("\nTop 5 agents by Y-axis distance:")
    sorted_y = sorted(y_distances.items(), key=lambda x: x[1], reverse=True)
    for agent_id, dist in sorted_y[:5]:
        print(f"Agent {agent_id}: {dist:.2f} cm")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, '09.txt')
    calculate_average_y_distance(data_file)
