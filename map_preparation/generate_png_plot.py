import os
import sys
import glob
import matplotlib.pyplot as plt
import numpy as np

def parse_netlogo_plot(csv_path):
    """
    Parses a NetLogo exported plot CSV file.
    Finds the line containing '"x","y"' and reads all subsequent lines.
    """
    x_data = []
    y_data = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Find the start of the data points
    start_idx = -1
    for idx, line in enumerate(lines):
        if '"x","y"' in line:
            start_idx = idx + 1
            break
            
    if start_idx == -1:
        raise ValueError("Could not find the start of the plot data in the CSV file.")
        
    for line in lines[start_idx:]:
        line = line.strip()
        if not line:
            continue
        # Format is "x","y","color","pen down?"
        parts = line.split(',')
        if len(parts) >= 2:
            try:
                x = float(parts[0].replace('"', ''))
                y = float(parts[1].replace('"', ''))
                x_data.append(x)
                y_data.append(y)
            except ValueError:
                # Skip header or malformed lines
                continue
                
    return np.array(x_data), np.array(y_data)

def generate_beautiful_plot(csv_path, output_path):
    print(f"Parsing data from {csv_path}...")
    x, y = parse_netlogo_plot(csv_path)
    
    if len(x) == 0:
        print("Error: No data parsed.")
        return False
        
    print(f"Parsed {len(x)} data points. Max ticks: {x[-1]}, Max agents: {y[-1]}")
    
    # Modern premium design setup
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    # Modern minimalist styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')
    
    # Plot the curve with a premium gradient-like look (using area fill)
    line_color = '#1e40af'  # Deep elegant cobalt blue
    fill_color = '#3b82f6'  # Vibrant blue
    
    ax.plot(x, y, color=line_color, linewidth=2.5, label='Sparametryzowana symulacja')
    ax.fill_between(x, y, color=fill_color, alpha=0.15)
    
    # Titles and Labels
    ax.set_title('Krzywa ewakuacji – Wyniki symulacji (Wersja Ulepszona)', fontsize=14, fontweight='bold', pad=15, color='#1e293b')
    ax.set_xlabel('Czas (ticki)', fontsize=11, fontweight='medium', labelpad=10, color='#334155')
    ax.set_ylabel('Liczba ewakuowanych osób (agenci)', fontsize=11, fontweight='medium', labelpad=10, color='#334155')
    
    # Customize grid
    ax.grid(True, linestyle='--', alpha=0.5, color='#cbd5e1')
    
    # Set axis limits
    ax.set_xlim(0, max(x) * 1.02)
    ax.set_ylim(-5, max(y) * 1.08)
    
    # Tick formatting
    ax.tick_params(colors='#475569', labelsize=10)
    
    # Add a legend/marker for key stats
    info_text = f"Łącznie wyewakuowano: {int(max(y))} osób\nCzas ewakuacji: {int(max(x))} ticków (~{max(x)/100:.1f} s)"
    ax.text(0.05, 0.90, info_text, transform=ax.transAxes, fontsize=10, 
            verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8fafc', edgecolor='#e2e8f0', alpha=0.9))
            
    plt.tight_layout()
    
    # Ensure directory for output exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Save the real PNG image
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Successfully saved premium PNG plot to: {output_path}")
    return True

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    plots_dir = os.path.join(script_dir, "plots")
    simulation_runs_dir = os.path.join(script_dir, "simulation_runs")
    
    # Ensure directories exist
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(simulation_runs_dir, exist_ok=True)
    
    # If a command line argument is provided, use it
    if len(sys.argv) > 1:
        target_csvs = [sys.argv[1]]
    else:
        # Find all evacuation_plot_*.csv files in simulation_runs/
        pattern = os.path.join(simulation_runs_dir, "evacuation_plot_*.csv")
        files = glob.glob(pattern)
        
        # Filter: only process files that haven't been converted to PNG yet
        target_csvs = []
        for f in files:
            basename = os.path.basename(f)
            name_no_ext, _ = os.path.splitext(basename)
            png_name = f"{name_no_ext}.png"
            png_path = os.path.join(plots_dir, png_name)
            
            if not os.path.exists(png_path):
                target_csvs.append((f, png_path))
                
        if not target_csvs:
            print("No new NetLogo exported plot CSV files found to convert.")
            sys.exit(0)
            
        # Sort them by modification time so that the latest one is processed last
        # (meaning the latest one will be the one copied to reports/nasz-wykres.png)
        target_csvs.sort(key=lambda item: os.path.getmtime(item[0]))
        
    print(f"Found {len(target_csvs)} new NetLogo exported CSV files to process.")
    
    latest_png = None
    if len(sys.argv) > 1:
        for csv_path in target_csvs:
            basename = os.path.basename(csv_path)
            name_no_ext, _ = os.path.splitext(basename)
            png_path = os.path.join(plots_dir, f"{name_no_ext}.png")
            print(f"\nProcessing argument file: {csv_path}")
            success = generate_beautiful_plot(csv_path, png_path)
            if success:
                latest_png = png_path
    else:
        for csv_path, png_path in target_csvs:
            print(f"\nProcessing: {csv_path}")
            success = generate_beautiful_plot(csv_path, png_path)
            if success:
                latest_png = png_path
                
    if latest_png:
        # Copy the latest one to reports/nasz-wykres.png
        nasz_wykres_path = os.path.join(project_dir, "reports", "nasz-wykres.png")
        import shutil
        shutil.copy2(latest_png, nasz_wykres_path)
        print(f"\nSuccessfully copied the latest plot ({os.path.basename(latest_png)}) to: {nasz_wykres_path}")

if __name__ == "__main__":
    main()
