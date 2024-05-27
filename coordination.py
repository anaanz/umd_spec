#!/usr/bin/env python3
# coding: utf-8
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import sys

def find_files(current_dir,r):
    umd_files = []
    bonding_files = []
    for filename in os.listdir(current_dir):
        if filename.endswith('.outcar.umd.dat'):
            umd_files.append(filename)
        elif filename.endswith(f'.outcar.bonding.r={r}.stat.dat'):
            bonding_files.append(filename)
    matching_pairs = []
    for umd_file in umd_files:
        common_prefix = extract_common_prefix([umd_file])
        matching_bonding_files = [file for file in bonding_files if file.startswith(common_prefix)]
        for matching_bonding_file in matching_bonding_files:
            matching_pairs.append((umd_file, matching_bonding_file))
    n = len(matching_pairs)
    return matching_pairs, n

def extract_common_prefix(file_list):
    common_prefix = os.path.commonprefix(file_list)
    return re.sub(r'\.umd\.dat$|\.bonding\.dat$', '', common_prefix)

def read_umd(file_path):
    density_list = []
    pressure_list = []
    temperature_list = []
    simulation_time = 0
    acell = []
    elements = []

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('Density'):
                density_value = float(line.split()[1])
                density_list.append(density_value)
            elif line.startswith('Pressure'):
                pressure_value = float(line.split()[1])
                pressure_list.append(pressure_value)
            elif line.startswith('Temperature'):
                temperature_value = float(line.split()[1])
                temperature_list.append(temperature_value)
            elif line.startswith('time'):
                time_value = float(line.split()[1])
                simulation_time = max(simulation_time, time_value)
            elif line.startswith('acell'):
                acell_value = float(line.split()[1])
                acell.append(acell_value)
            elif line.startswith('elements'):
                elements_value = line.split()[1:]   
                elements.extend(elements_value)
    return {
        'Density': np.array(density_list),
        'Pressure': np.array(pressure_list),
        'Temperature': np.array(temperature_list),
        'time': simulation_time,
        'acell': acell,
        'elements': elements,
        'elements_value': elements_value  
    }

def grep_pattern(FileName, Pattern, SkipSteps): 
    data = []
    average = 0 
    stdev = 0 
    variance = 0
    anchor=Pattern.split()[0]
    patterns=subprocess.check_output(['grep',Pattern,FileName]).decode("utf-8")
    greps=patterns.split('\n')
    for isteps in range(SkipSteps+1,len(greps)):
        elems=greps[isteps].split()
        for ii in range(len(elems)):
            if elems[ii] == anchor:
                for jj in range(ii+1,len(elems)):
                        data.append(float(elems[jj]))
                        break
    average = sum(data)/len(data)
    for ii in range(len(data)):
        variance = variance + (data[ii]-average)**2
    variance = variance/len(data)
    stdev = np.sqrt(variance)
    return data, average, stdev

def read_statfile(file_path):
    clusters_data = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines[2:]:
            data = line.strip().split()
            cluster_name = data[0]
            cluster_time = float(data[1])
            atomic_types = re.findall(r'([A-Za-z]+)_\d+', cluster_name)
            atomic_numbers = [int(num) for num in re.findall(r'(\d+)', cluster_name)]
            clusters_data.append({
                'cluster_name': cluster_name,
                'cluster_time': cluster_time,
                'atomic_types': atomic_types, # names of atoms
                'atomic_numbers': atomic_numbers, # numbers of atoms in a cluster
            })
    return clusters_data

def find_clusters_with_two_atomic_types_containg_atom(clusters_data, file_name, umd_data, pressure_mean, atomic_type_flag):
    with open("output.txt", "a") as output_file:
        for cluster in clusters_data:
            atomic_numbers = cluster['atomic_numbers']
            if len(cluster['atomic_types']) == 2 and atomic_type_flag in cluster['cluster_name']:
                atomic_types = ''.join(cluster['atomic_types'])
                atomic_numbers = ' '.join([str(num) for num in cluster['atomic_numbers']])
                cluster_info = [cluster['cluster_name'], str(cluster['cluster_time']), atomic_types, atomic_numbers]
                output_text = f"{file_name} {pressure_mean} {' '.join(cluster_info)}\n"
                output_file.write(output_text)
                # print('output_text is',output_text)

def main():
    if len(sys.argv) != 3:
        print("coordination.py <write 0 or 1, depending on the r file you want to use> <atom type and number>, for example 0 Si_1")
        sys.exit(1)
    r = sys.argv[1]
    atomic_type_flag = sys.argv[2]
    print(f"Plotting coordination of clusters containing {atomic_type_flag} from r={r} files")
    # vapor_time_sum = 0
    # liquid_time_sum = 0
    current_dir = os.getcwd()
    matching_pairs, _ = find_files(current_dir,r)
    for umd_file, bonding_file in matching_pairs:
        umd_path = os.path.join(current_dir, umd_file)
        bonding_path = os.path.join(current_dir, bonding_file)
        umd_data = read_umd(umd_path)
        clusters_data = read_statfile(bonding_path)
        _, pressure_mean, _ = grep_pattern(umd_path, 'Pressure', 0)

        find_clusters_with_two_atomic_types_containg_atom(clusters_data, bonding_file, umd_data, pressure_mean, atomic_type_flag)
        

    sum_dict = {}
    second_entries = []
    third_entries = []
    normalized_values = []
    cluster_colors = {}
    unique_clusters = set()

    with open("output.txt", "r") as file:
        for line in file:
            parts = line.split()
            first_entry = parts[0]  
            fourth_entry = float(parts[3])  
            if first_entry in sum_dict: 
                sum_dict[first_entry] += fourth_entry
            else:
                sum_dict[first_entry] = fourth_entry

    with open("output.txt", "r") as file:
        with open("plotclusters.txt", "w") as output_file:
            for line in file:
                parts = line.split()
                first_entry = parts[0] # name of stat.dat file
                second_entry = round(float(parts[1]), 2) # pressure mean from umd 
                cluster = parts[2]   # cluster name
                fourth_entry = float(parts[3]) # cluster time
                # # fifth enttry is atom numbers and sixth entry atom 
                match = re.search(r'O_(\d+)', cluster)
                if match:
                    color_number = int(match.group(1))
                else:
                    continue
                if color_number not in cluster_colors:
                    colors = ['#0D3A2C', '#1A5441', '#00876c', '#82b1a1', '#dadada', '#dec2c1', '#D09697', '#da5d66', '#AE3540','#4B1516', '#443da8', '#695ab7', '#a799d4', '#c5bae3'] 
                    cluster_colors[color_number] = colors[color_number % len(colors)]  
                sum_value = sum_dict[first_entry]
                normalized_value = fourth_entry / sum_value
                output_file.write(f"{line.strip()} {sum_value} {normalized_value}\n")
                second_entries.append(second_entry)
                third_entries.append(cluster)
                normalized_values.append(normalized_value)
                unique_clusters.add(cluster)
    plt.figure(figsize=(8, 6))
    legend_order = sorted(unique_clusters, key=lambda x: int(re.search(r'O_(\d+)', x).group(1)))
    for cluster in legend_order:
        color_number = int(re.search(r'O_(\d+)', cluster).group(1))
        cluster_color = cluster_colors[color_number]
        cluster_data = [(second_entry, norm_value) for second_entry, norm_value, clust in zip(second_entries, normalized_values, third_entries) if clust == cluster]
        sorted_cluster_data = sorted(cluster_data, key=lambda x: x[0])    
        sorted_pressure, sorted_normalized_values = zip(*sorted_cluster_data)    
        # Calculate upper and lower bounds for error bars
        upper_bound = [min(1.0, val + 0.1) for val in sorted_normalized_values]  # Adjust 0.1 according to your needs
        lower_bound = [max(0.0, val - 0.1) for val in sorted_normalized_values]  # Adjust 0.1 according to your needs
        plt.plot(sorted_pressure, sorted_normalized_values, marker='o', label=cluster, color=cluster_color)
        plt.fill_between(sorted_pressure, lower_bound, upper_bound, color=cluster_color, alpha=0.3)  # Adding the shaded error bars
        if r == '0':
            plt.xlim(-1,3)
        else:
            plt.xlim(-1,46)
        plt.ylim(0,1)
    plt.xlabel('Pressure (GPa)')
    plt.ylabel('Relative Abundance')
    plt.legend()
    plt.savefig(f"r{r}_{atomic_type_flag}_cluster%.pdf",transparent=True)
    os.remove("output.txt")
    os.remove("plotclusters.txt")

if __name__ == "__main__":
    main()
