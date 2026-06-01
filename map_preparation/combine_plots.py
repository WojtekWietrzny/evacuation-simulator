import os
import sys
import glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd  # Wymagane do obsługi CSV magisterki i zapisu połączonych danych

def parse_netlogo_plot(csv_path):
    """Parsuje standardowy wykres wyeksportowany z NetLogo."""
    x_data = []
    y_data = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
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
        parts = line.split(',')
        if len(parts) >= 2:
            try:
                x = float(parts[0].replace('"', ''))
                y = float(parts[1].replace('"', ''))
                x_data.append(x)
                y_data.append(y)
            except ValueError:
                continue
                
    return np.array(x_data), np.array(y_data)

def generate_beautiful_plot(csv_path, output_path, magisterka_csv_path=None):
    print(f"Parsing data from {csv_path}...")
    x, y = parse_netlogo_plot(csv_path)
    
    if len(x) == 0:
        print("Error: No data parsed.")
        return False
        
    # Setup stylu
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')
    
    # 1. RYSOWANIE WASZEGO WYKRESU
    line_color = '#1e40af'  # Cobalt blue
    fill_color = '#3b82f6'  # Vibrant blue
    ax.plot(x, y, color=line_color, linewidth=2.5, label='Wersja Ulepszona (Nasza)', zorder=3)
    ax.fill_between(x, y, color=fill_color, alpha=0.15)
    
    max_x_magisterka = 0
    
    # 2. WCZYTYWANIE I NAKŁADANIE MAGISTERKI
    if magisterka_csv_path and os.path.exists(magisterka_csv_path):
        try:
            print(f"Wczytywanie danych z magisterki: {magisterka_csv_path}...")
            # Wczytujemy CSV magisterki (zakładamy nagłówki lub ich brak - dostosuj w razie potrzeby)
            df_mag = pd.read_csv(magisterka_csv_path)
            
            # Pobieramy pierwszą kolumnę jako X i drugą jako Y
            x_mag = df_mag.iloc[:, 0].to_numpy()
            y_mag = df_mag.iloc[:, 1].to_numpy()
            
            # PRZELICZENIE SKALI (900 jedn. = 430s = 43000 ticków -> mnożnik 47.78)
            mnoznik_czasu = 43000.0 / 900.0  # wychodzi ~47.7777...
            x_mag_scaled = x_mag * mnoznik_czasu
            max_x_magisterka = max(x_mag_scaled)
            
            # Rysowanie linii magisterki (kolor pomarańczowy dla kontrastu, linia przerywana)
            mag_color = '#ea580c'  # Elegant orange
            ax.plot(x_mag_scaled, y_mag, color=mag_color, linewidth=2, linestyle='--', 
                    label='Wersja Oryginalna (Magisterka)', zorder=2)
            
            # ZAPIS POŁĄCZONYCH DANYCH DO NOWEGO PLIKU CSV
            # Ponieważ osie X się różnią, najczystszym sposobem jest zapisanie obu serii obok siebie 
            # do jednego pliku (osobne kolumny dla przejrzystości, np. do Excela)
            combined_csv_path = output_path.replace('.png', '_porownanie_dane.csv')
            
            df_nasze_out = pd.DataFrame({'Nasze_Czas_Ticki': x, 'Nasze_Ewakuowani': y})
            df_mag_out = pd.DataFrame({'Magisterka_Czas_Przeskalowany': x_mag_scaled, 'Magisterka_Ewakuowani': y_mag})
            
            # Zapisujemy do jednego pliku za pomocą generatora Excela lub jako połączony CSV zewnętrznie
            # Tutaj tworzymy dwa pliki w jednym folderze lub łączymy je pustymi wartościami (Outer join) 
            # dla idealnego zgrania czasowego w jednym pliku:
            df_nasze_out['Klucz_Czas'] = df_nasze_out['Nasze_Czas_Ticki'].round(0)
            df_mag_out['Klucz_Czas'] = df_mag_out['Magisterka_Czas_Przeskalowany'].round(0)
            
            df_combined = pd.merge(df_nasze_out, df_mag_out, on='Klucz_Czas', how='outer').sort_values('Klucz_Czas')
            df_combined.drop(columns=['Klucz_Czas'], inplace=True)
            df_combined.to_csv(combined_csv_path, index=False)
            print(f"Pomyślnie zapisano połączone surowe dane do: {combined_csv_path}")
            
        except Exception as e:
            print(f"Błąd przetwarzania danych magisterki: {e}")
            
    # Reszta stylizacji wykresu
    ax.set_title('Krzywa ewakuacji – Porównanie Symulacji', fontsize=14, fontweight='bold', pad=15, color='#1e293b')
    ax.set_xlabel('Czas (ticki)', fontsize=11, fontweight='medium', labelpad=10, color='#334155')
    ax.set_ylabel('Liczba wyewakuowanych osób', fontsize=11, fontweight='medium', labelpad=10, color='#334155')
    ax.grid(True, linestyle='--', alpha=0.5, color='#cbd5e1')
    
    global_max_x = max(max(x), max_x_magisterka)
    ax.set_xlim(0, global_max_x * 1.02)
    ax.set_ylim(-5, max(max(y), max(y) if 'y_mag' not in locals() else max(y_mag)) * 1.08)
    ax.tick_params(colors='#475569', labelsize=10)
    
    # Legenda
    ax.legend(loc='lower right', frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0')
    
    # Okienko informacyjne
    info_text = f"Nasza symulacja:\n• Łącznie: {int(max(y))} osób\n• Czas: {int(max(x))} ticków (~{max(x)/100:.1f} s)"
    ax.text(0.05, 0.90, info_text, transform=ax.transAxes, fontsize=10, 
            verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8fafc', edgecolor='#e2e8f0', alpha=0.9))
            
    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Zapisano wykres porównawczy do: {output_path}")
    return True

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    plots_dir = os.path.join(script_dir, "plots")
    simulation_runs_dir = os.path.join(script_dir, "simulation_runs")
    
    # !!! TUTAJ PODAJ NAZWĘ SWOJEGO PLIKU Z MAGISTERKI !!!
    # Umieść plik 'magisterka_dane.csv' w folderze 'simulation_runs'
    magisterka_csv = os.path.join(simulation_runs_dir, "magisterka-data.csv")
    
    pattern = os.path.join(simulation_runs_dir, "evacuation_plot_*.csv")
    files = glob.glob(pattern)
    
    target_csvs = []
    for f in files:
        basename = os.path.basename(f)
        if "magisterka" in basename: # Pomijamy plik magisterki przy szukaniu nowych przebiegów NetLogo
            continue
        name_no_ext, _ = os.path.splitext(basename)
        png_path = os.path.join(plots_dir, f"{name_no_ext}.png")
        target_csvs.append((f, png_path))
            
    if not target_csvs:
        print("Nie znaleziono plików evacuation_plot_*.csv do przetworzenia.")
        sys.exit(0)
        
    # Przetwórz pliki
    latest_png = None
    for csv_path, png_path in target_csvs:
        success = generate_beautiful_plot(csv_path, png_path, magisterka_csv_path=magisterka_csv)
        if success:
            latest_png = png_path
                
    if latest_png:
        nasz_wykres_path = os.path.join(project_dir, "reports", "nasz-wykres.png")
        os.makedirs(os.path.dirname(nasz_wykres_path), exist_ok=True)
        import shutil
        shutil.copy2(latest_png, nasz_wykres_path)
        print(f"\nSkopiowano najnowszy wykres do raportów: {nasz_wykres_path}")

if __name__ == "__main__":
    main()